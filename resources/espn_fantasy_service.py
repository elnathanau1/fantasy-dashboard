from espn_api.basketball import League, Team, Matchup
import requests

CATEGORIES = ['TO', 'PTS', 'BLK', 'STL', 'AST', 'REB', '3PTM', 'FG%', 'FT%']

r = requests.get(
    url='https://fantasy.espn.com/apis/v3/games/fba/seasons/2022/players?scoringPeriodId=0&view=players_wl',
    headers={'x-fantasy-filter': '{"filterActive":{"value":true}}'}
)
player_map = r.json()


def get_league_info(league_id: str, season: int, swid: str, espn_s2: str):
    url = 'https://fantasy.espn.com/apis/v3/games/fba/seasons/{0}/segments/0/leagues/{1}?view=mRoster&view=mTeam'.format(
        season, league_id)
    req = requests.get(
        url,
        headers={'cookie': 'espnAuth={{"swid":"{0}"}}; espn_s2={1};'.format(swid, espn_s2)}
    )
    return req.json()


def get_team(league: League, team_id: int) -> Team:
    return [team for team in league.teams if team.team_id == team_id][0]


def get_matchup_cats(league: League, matchup_period: int, team_id: int):
    team = get_team(league, team_id)

    current_matchup: Matchup = team.schedule[matchup_period - 1]
    if current_matchup.home_team.team_id == team_id:
        cats = current_matchup.home_team_cats
    else:
        cats = current_matchup.away_team_cats

    cat_dict = {}
    for category in CATEGORIES:
        cat_dict[category] = cats[category]['score']

    return cat_dict


def compare_team_stats(team_1, team_2):
    return_dict = {
        'home_team': team_1[0],
        'away_team': team_2[0]
    }

    win = []
    lose = []
    tie = []

    for category in CATEGORIES:
        multiplier = 1
        if category == 'TO':
            multiplier = -1

        if team_1[1][category] * multiplier > team_2[1][category] * multiplier:
            win.append(category)
        elif team_1[1][category] * multiplier < team_2[1][category] * multiplier:
            lose.append(category)
        else:
            tie.append(category)

    return_dict.update({
        'win_cats': win,
        'lose_cats': lose,
        'tie_cats': tie,
        'wins': len(win),
        'losses': len(lose),
        'ties': len(tie)
    })

    return return_dict


def get_power_rankings(league: League, matchup_period):
    team_stats_list = list(
        map(lambda team: [team.team_name, get_matchup_cats(league, matchup_period, team.team_id)], league.teams))

    results_list = []
    for i in range(0, len(team_stats_list)):
        total_win = 0
        total_lose = 0
        total_tie = 0

        matchup_win = 0
        matchup_lose = 0
        matchup_tie = 0

        matchups = []
        for j in range(0, len(team_stats_list)):
            if j != i:
                result = compare_team_stats(team_stats_list[i], team_stats_list[j])
                total_win += result['wins']
                total_lose += result['losses']
                total_tie += result['ties']
                matchups.append(result)
                if result['wins'] > result['losses']:
                    matchup_win += 1
                elif result['wins'] == result['losses']:
                    matchup_tie += 1
                else:
                    matchup_lose += 1

        results_list.append(
            {
                'team': team_stats_list[i][0],
                'total_record': '{0}-{1}-{2}'.format(total_win, total_lose, total_tie),
                'record_vs_others': '{0}-{1}-{2}'.format(matchup_win, matchup_lose, matchup_tie),
                'score': total_win + total_tie / 2.0,
                'stats': team_stats_list[i][1],
                'matchups': matchups
            }
        )

    return sorted(results_list, key=lambda x: x['score'] * -1)


def get_player_info(player_id: int):
    for player in player_map:
        if str(player['id']) == str(player_id):
            return player

    return None


def get_player_headshot(player_id: int):
    return 'https://a.espncdn.com/combiner/i?img=%2Fi%2Fheadshots%2Fnba%2Fplayers%2Ffull%2F{0}.png&w=96&h=70&cb=1'.format(
        player_id)


def get_trade_block(league_info):
    trade_block = []
    for team in league_info['teams']:
        if 'players' in team['tradeBlock'].keys():
            for player_id in team['tradeBlock']['players'].keys():
                if team['tradeBlock']['players'][player_id] == 'ON_THE_BLOCK':
                    trade_block.append({
                        'player_id': player_id,
                        'team_id': team['location'] + ' ' + team['nickname']
                        })
    return trade_block
