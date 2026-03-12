import pandas as pd

def clean_dl_stats(player_stats):
    edge_Player = ["DE", "EDGE", "OLB"]
    interior_Player = ["DT", "NT"]
    keep_cols = [
        'player_id',
        'player_name',
        'player_display_name',
        'position',
        'position_group',
        'headshot_url',
        'season',
        'week',
        'team',

        'def_tackles_solo',
        'def_tackles_with_assist',
        'def_tackle_assists',
        'def_tackles_for_loss',
        'def_tackles_for_loss_yards',
        'def_fumbles_forced',
        'def_sacks',
        'def_sack_yards',
        'def_qb_hits',
        'def_interceptions',
        'def_interception_yards',
        'def_pass_defended',
        'def_tds',
        'def_fumbles',
        'def_safeties',
        'misc_yards',
        'fumble_recovery_own',
        'fumble_recovery_yards_own',
        'fumble_recovery_opp',
        'fumble_recovery_yards_opp',
        'fumble_recovery_tds',
        'penalties']    
    player_stats = player_stats[keep_cols] ##remove unnecessary stats


    player_stats.loc[player_stats["player_id"]=="00-0036932","position"]="EDGE" #edge case because we have to move Micah Parsons to edge since some seasons are listed at LB
    player_stats.loc[player_stats["player_id"]=="00-0036989","position"]="EDGE" ##Also have to move M.Koonce
    player_stats.loc[player_stats["player_id"]=="0-0027949","position"]="EDGE" ##Potentially fix JJ. Watt seems to be a bug 


    

    

    dl_stats = player_stats[player_stats["position"].isin(edge_Player + interior_Player)].copy()
    edge_stats = dl_stats[dl_stats["position"].isin(edge_Player)].copy()
    interior_stats = dl_stats[dl_stats["position"].isin(interior_Player)].copy() ##seperate into edge v interior

    print("EDGE players:", edge_stats["player_id"].nunique())
    print("Interior players:", interior_stats["player_id"].nunique())

    edge_stats = edge_stats.groupby(
        ['player_id', 'player_name', 'season', 'position']
    ).sum(numeric_only=True).reset_index()    #combined into stats by season

    interior_stats = interior_stats.groupby(
        ['player_id', 'player_name', 'season', 'position']  #combined into stats by season
    ).sum(numeric_only=True).reset_index()
    

    return edge_stats, interior_stats

def clean_edge_data(df):
            ##removes Middle Linebackers
        lb_ids = [
            "00-0029562","00-0034431","00-0029607","00-0033571",
            "00-0032442","00-0031596","00-0032401","00-0031550",
            "00-0032437","00-0034674","00-0031361","00-0034846",
            "00-0034723","00-0030761","00-0032269","00-0027686",
            "00-0030463","00-0032892"
        ]

        df = df[~df["player_id"].isin(lb_ids)]
        return df


def clean_pbp(pbp):
    keep_cols = [

    # --- Game / Context ---
    'play_id',
    'game_id',
    'season',
    'week',
    'defteam',
    'posteam',
    'play_type',

    # --- Situation / Down & Distance ---
    'down',
    'ydstogo',
    'yardline_100',
    'score_differential',
    'quarter_seconds_remaining',
    'third_down_converted',
    'third_down_failed',
    'fourth_down_converted',
    'fourth_down_failed',

    # --- Play Type Flags ---
    'pass',
    'rush',
    'qb_dropback',
    'rush_attempt',
    'pass_attempt',

    # --- Impact Metrics ---
    'epa',
    'wpa',
    'def_wp',
    'opp_fg_prob',
    'opp_safety_prob',
    'opp_td_prob',

    # --- Core Defensive Outcomes ---
    'sack',
    'qb_hit',
    'tackled_for_loss',
    'solo_tackle',
    'assist_tackle',
    'tackle_with_assist',
    'fumble_forced',
    'interception',
    'safety',
    'return_touchdown',
    'touchdown',
    'defensive_two_point_attempt',
    'defensive_two_point_conv',
    'defensive_extra_point_attempt',
    'defensive_extra_point_conv',

    # --- Sack Attribution ---
    'sack_player_id',
    'sack_player_name',
    'half_sack_1_player_id',
    'half_sack_1_player_name',
    'half_sack_2_player_id',
    'half_sack_2_player_name',
    'lateral_sack_player_id',
    'lateral_sack_player_name',

    # --- QB Hits Attribution ---
    'qb_hit_1_player_id',
    'qb_hit_1_player_name',
    'qb_hit_2_player_id',
    'qb_hit_2_player_name',

    # --- TFL Attribution ---
    'tackle_for_loss_1_player_id',
    'tackle_for_loss_1_player_name',
    'tackle_for_loss_2_player_id',
    'tackle_for_loss_2_player_name',

    # --- Solo Tackles ---
    'solo_tackle_1_player_id',
    'solo_tackle_1_player_name',
    'solo_tackle_1_team',
    'solo_tackle_2_player_id',
    'solo_tackle_2_player_name',
    'solo_tackle_2_team',

    # --- Assist Tackles ---
    'assist_tackle_1_player_id',
    'assist_tackle_1_player_name',
    'assist_tackle_1_team',
    'assist_tackle_2_player_id',
    'assist_tackle_2_player_name',
    'assist_tackle_2_team',
    'assist_tackle_3_player_id',
    'assist_tackle_3_player_name',
    'assist_tackle_3_team',
    'assist_tackle_4_player_id',
    'assist_tackle_4_player_name',
    'assist_tackle_4_team',

    # --- Tackle With Assist Attribution ---
    'tackle_with_assist_1_player_id',
    'tackle_with_assist_1_player_name',
    'tackle_with_assist_1_team',
    'tackle_with_assist_2_player_id',
    'tackle_with_assist_2_player_name',
    'tackle_with_assist_2_team',

    # --- Forced Fumbles Attribution ---
    'forced_fumble_player_1_player_id',
    'forced_fumble_player_1_player_name',
    'forced_fumble_player_1_team',
    'forced_fumble_player_2_player_id',
    'forced_fumble_player_2_player_name',
    'forced_fumble_player_2_team',

    # --- Interception Attribution ---
    'interception_player_id',
    'interception_player_name',
    'lateral_interception_player_id',
    'lateral_interception_player_name',

    # --- Pass Deflections ---
    'pass_defense_1_player_id',
    'pass_defense_1_player_name',
    'pass_defense_2_player_id',
    'pass_defense_2_player_name',

    # --- Fumble Recoveries ---
    'fumble_recovery_1_player_id',
    'fumble_recovery_1_player_name',
    'fumble_recovery_1_team',
    'fumble_recovery_1_yards',
    'fumble_recovery_2_player_id',
    'fumble_recovery_2_player_name',
    'fumble_recovery_2_team',
    'fumble_recovery_2_yards',

    # --- Safeties ---
    'safety_player_id',
    'safety_player_name'
]
    pbp = pbp[keep_cols].copy()
    print("PBP cleaned:", pbp.shape)
    return pbp


    
















