from resources.constants import *
import pandas as pd
from pandas import Series
from resources.services.espn_fantasy_service import *
from datetime import date
import calendar


# TODO: WEEK 18 MONDAY IS BROKEN
def join_schedule_team_tables(team_id: int, week: int, exclude_out: bool = True, exclude_dtd: bool = False) -> Series:
    schedule_table = get_week_schedule(week)

    roster = get_team(team_id).roster
    team_schedule_list = []
    for player in roster:
        row = {
            'Player': player.name,
            'Team': player.proTeam,
            'Status': player.injuryStatus
        }

        for day in DAYS:
            if player.lineupSlot == 'IR':
                row[day] = 0
            else:
                row[day] = 0 if pd.isnull(schedule_table.loc[player.proTeam][day]) else 1

            if exclude_out and player.injuryStatus == 'OUT':
                row[day] = 0

            if exclude_dtd and player.injuryStatus == 'DAY_TO_DAY':
                row[day] = row[day] / 2.0

        team_schedule_list.append(row)

    team_schedule_df = pd.DataFrame.from_dict(team_schedule_list)
    total_team_week_games = team_schedule_df.sum(axis=0, numeric_only=True)
    return total_team_week_games


def get_estimated_total_games(team_id: int, week: int, exclude_out: bool = True, exclude_dtd: bool = False) -> int:
    total_team_week_games = join_schedule_team_tables(team_id, week, exclude_out, exclude_dtd)
    total_team_week_games = total_team_week_games.apply(lambda game_count: 10 if game_count >= 10 else game_count)

    return total_team_week_games.sum()


def get_current_week_remaining_games(team_id: int, exclude_out: bool = True, exclude_dtd: bool = False) -> int:
    total_team_week_games = join_schedule_team_tables(team_id, get_league_obj().currentMatchupPeriod, exclude_out, exclude_dtd)
    today_day = calendar.day_name[date.today().weekday()]

    in_past = True
    for day in DAYS:
        if day == today_day:
            in_past = False
        if in_past:
            total_team_week_games.drop(day, inplace=True)

    total_team_week_games = total_team_week_games.apply(lambda game_count: 10 if game_count >= 10 else game_count)

    return total_team_week_games.sum()
