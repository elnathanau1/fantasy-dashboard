from espn_api.basketball import League, Team, Matchup


CATEGORIES = ['TO', 'PTS', 'BLK', 'STL', 'AST', 'REB', '3PTM', 'FG%', 'FT%']


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

    win = 0
    lose = 0
    tie = 0

    for category in CATEGORIES:
        multiplier = 1
        if category == 'TO':
            multiplier = -1

        if team_1[1][category] * multiplier > team_2[1][category] * multiplier:
            win += 1
        elif team_1[1][category] * multiplier < team_2[1][category] * multiplier:
            lose += 1
        else:
            tie += 1

    return_dict['win'] = win
    return_dict['lose'] = lose
    return_dict['tie'] = tie

    return return_dict


def get_power_rankings(league: League, matchup_period):
    team_stats_list = list(map(lambda team: [team.team_name, get_matchup_cats(league, 1, team.team_id)], league.teams))

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
                total_win += result['win']
                total_lose += result['lose']
                total_tie += result['tie']
                matchups.append(result)
                if result['win'] > result['lose']:
                    matchup_win += 1
                elif result['win'] == result['lose']:
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
