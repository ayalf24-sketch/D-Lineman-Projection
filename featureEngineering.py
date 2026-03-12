import pandas as pd
import numpy as np


def build_player_features(df, position_type, clean_pbp,snaps):
    df = df.copy()

    ##1st edge cases being manually fixed: this is an error in the base datasets
    df.loc[df["player_id"] == "00-0036220", "player_name"] = "D.Brown"
    df.loc[df["player_id"] == "00-0032889", "player_name"] = "A.Robinson" ##fix Ashawn Robinson
    df.loc[df["player_id"] == "00-0035642", "player_name"] = "J.Hines-Allen" ##J.Allen changed his name to J.Hines..

    player_map = df[["player_id","player_name"]].drop_duplicates()  #drops dupes
    #Core whole stats
    # Tackles 

    df["total_tackles"] = df["def_tackles_solo"] + df["def_tackle_assists"]

    def convert_to_initial(name):
        parts = name.split()
        if len(parts) < 2:
            return name
        return f"{parts[0][0]}.{ ' '.join(parts[1:]) }"  ##fixes name issues and differences in between diff datasets

    snaps = snaps.copy()

    snaps["player_name"] = snaps["player"].apply(convert_to_initial) #standerizing name format

    ##EDGE CASES BEING MANUALLY FIXED
    snaps.loc[snaps["player"].str.contains("Karlaftis", na=False), "player_name"] = "G.Karlaftis"
    df.loc[df["player_id"] == "00-0036220", "player_name"] = "D.Brown"

    snaps = snaps.merge(player_map, on="player_name", how="left")
    snaps = snaps.dropna(subset=["player_id"])
    total_def_snaps = (
        snaps.groupby(["player_id","season"])["defense_snaps"]
        .sum()
        .reset_index()
        .rename(columns={"defense_snaps":"defense_snaps_total"})
    )
    df = df.merge(total_def_snaps, on=["player_id","season"], how="left")
    df["defense_snaps_total"] = df["defense_snaps_total"].fillna(np.nan)

    
    if position_type == "EDGE":

        df["PR_score"] = (6*df["def_sacks"] + 2*df["def_qb_hits"] + 2*df["def_pass_defended"])
        df['RunD_score']= (2*df["total_tackles"] + 4*df['def_tackles_for_loss'])
        df["Turnover_score"] = (6*df["def_fumbles_forced"] + 6*df["def_interceptions"] + 2*df["def_safeties"] + 1*df['fumble_recovery_opp'])


        #per-100-snap calculations using total snaps
        df["sacks_per_100"] = np.where(
            df["defense_snaps_total"] > 0,
            df["def_sacks"] / df["defense_snaps_total"] * 100,
            0
        )
        ##TFL
        df["tfl_per_100"] = np.where(
            df["defense_snaps_total"] > 0,
            df["def_tackles_for_loss"] / df["defense_snaps_total"] * 100,
            0
        )
        ##PENALTY
        df["penalty_score"] = np.where(
            df["defense_snaps_total"] > 0,
            df["penalties"] / df["defense_snaps_total"] * 100,
            0
        )
        # Efficiency score (weighted)
        df["Efficency_score"] = 3*df["sacks_per_100"] + 2*df["tfl_per_100"]
        
        #PR scores per 100 to help those who got bigtime injuries
        df["PR_per100"] = np.where(df["defense_snaps_total"] > 200,df["PR_score"] / df["defense_snaps_total"] * 100,np.nan
)
        
        df["RunD_per100"] = np.where(df["defense_snaps_total"] > 200,df["RunD_score"] / df["defense_snaps_total"] * 100,np.nan
)
        


    elif position_type == "INTERIOR":

        df["PR_score"] = (4*df["def_sacks"] + 2*df["def_qb_hits"] + 2*df["def_pass_defended"])
        df['RunD_score']= (4*df["total_tackles"] + 6*df['def_tackles_for_loss'])
        df["Turnover_score"] = (5*df["def_fumbles_forced"] + 6*df["def_interceptions"] + df["def_safeties"] + 2*df['fumble_recovery_opp'])
        ##e calc

        #per-100-snap calculations using total snaps
        df["sacks_per_100"] = np.where(
            df["defense_snaps_total"] > 0,
            df["def_sacks"] / df["defense_snaps_total"] * 100,
            0
        )
        ##TFL
        df["tfl_per_100"] = np.where(
            df["defense_snaps_total"] > 0,
            df["def_tackles_for_loss"] / df["defense_snaps_total"] * 100,
            0
        )
        ##PENALTY
        df["penalty_score"] = np.where(
            df["defense_snaps_total"] > 0,
            df["penalties"] / df["defense_snaps_total"] * 100,
            0
        )
        # Efficiency score (weighted)
        df["Efficency_score"] = 2*df["sacks_per_100"] + 3*df["tfl_per_100"]

        df["PR_per100"] = np.where(df["defense_snaps_total"] > 200,df["PR_score"] / df["defense_snaps_total"] * 100,np.nan
)
        
        df["RunD_per100"] = np.where(df["defense_snaps_total"] > 200,df["RunD_score"] / df["defense_snaps_total"] * 100,np.nan
)

        


##Situational scoring calc
##Pulling from Play by play datasets
#Identifying who is making big time stops on 3rd and 4th down 
#Also counting who is making sacks on 3rd and long (obvious passing downs) and what percentage of their sack 
# totals do they make up as its not really a good thing if you only get sacks on 3rd and long

    third_long = clean_pbp[
    (clean_pbp["down"] == 3) &
    (clean_pbp["ydstogo"] >= 7) &
    (clean_pbp["sack"] == 1)]

    # full sacks
    full = (
        third_long["sack_player_id"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    full.columns = ["player_id", "sacks"]
    full["sacks"] = 1.0 * full["sacks"]

    # half sacks
    half1 = third_long["half_sack_1_player_id"].dropna()
    half2 = third_long["half_sack_2_player_id"].dropna()

    half = (
        pd.concat([half1, half2])
        .value_counts()
        .reset_index()
    )
    half.columns = ["player_id", "sacks"]
    half["sacks"] = 0.5 * half["sacks"]

    third_long_sacks = (
        pd.concat([full, half])
        .groupby("player_id")["sacks"]
        .sum()
        .reset_index()
    )
    third_long_sacks.columns = ["player_id", "third_and_long_sacks"]
        
    
    
    
    
    
    ##third and long sack

    df = df.merge(third_long_sacks, on="player_id", how="left")
    df["third_and_long_sacks"] = df["third_and_long_sacks"].fillna(0)

    # calculate ratio 
    df["third_long_sack_ratio"] = df["third_and_long_sacks"] / df["def_sacks"].replace(0, np.nan)
    df["third_long_sack_ratio"] = df["third_long_sack_ratio"].fillna(0)
 
    third_fail = clean_pbp[
    (clean_pbp["down"] == 3) &
    (clean_pbp["third_down_failed"] == 1)
] 
    sacks = third_fail[third_fail["sack"] == 1]

    sack_stops = (
        pd.concat([
            sacks["sack_player_id"],
            sacks["half_sack_1_player_id"],
            sacks["half_sack_2_player_id"]
        ])
        .dropna()
        .value_counts()
        .reset_index()
    )

    sack_stops.columns = ["player_id", "third_stop_sacks"]

    tfl = third_fail[third_fail["tackled_for_loss"] == 1]

    tfl_stops = (
        pd.concat([
            tfl["tackle_for_loss_1_player_id"],
            tfl["tackle_for_loss_2_player_id"]
        ])
        .dropna()
        .value_counts()
        .reset_index()
    )

    tfl_stops.columns = ["player_id", "third_stop_tfl"]

    ints = third_fail[third_fail["interception"] == 1]

    int_stops = (
        ints["interception_player_id"]
        .dropna()
        .value_counts()
        .reset_index()
    )

    int_stops.columns = ["player_id", "third_stop_int"]

    ff = third_fail[third_fail["fumble_forced"] == 1]

    ff_stops = (
        pd.concat([
            ff["forced_fumble_player_1_player_id"],
            ff["forced_fumble_player_2_player_id"]
        ])
        .dropna()
        .value_counts()
        .reset_index()
    )
    ff_stops.columns = ["player_id", "third_stop_ff"]

    third_stops = sack_stops \
        .merge(tfl_stops, on="player_id", how="outer") \
        .merge(int_stops, on="player_id", how="outer") \
        .merge(ff_stops, on="player_id", how="outer") \
        .fillna(0)

    third_stops["crucial_thirdStops"] = (
        third_stops["third_stop_sacks"] +
        third_stops["third_stop_tfl"] +
        third_stops["third_stop_int"] +
        third_stops["third_stop_ff"]
    )



    fourth_fail = clean_pbp[
    (clean_pbp["down"] == 4) &
    (clean_pbp["fourth_down_failed"] == 1)]
    
    sacks_4 = fourth_fail[fourth_fail["sack"] == 1]
    sack_stops_4 = (
        pd.concat([
            sacks_4["sack_player_id"],
            sacks_4["half_sack_1_player_id"],
            sacks_4["half_sack_2_player_id"]
        ])
        .dropna()
        .value_counts()
        .reset_index()
    )
    sack_stops_4.columns = ["player_id", "fourth_stop_sacks"]
    
    tackle_4 = fourth_fail[
    (fourth_fail["solo_tackle"] == 1) |
    (fourth_fail["assist_tackle"] == 1) |
    (fourth_fail["tackle_with_assist"] == 1)
]

    tackle_stops_4 = (
        pd.concat([
            tackle_4["solo_tackle_1_player_id"],
            tackle_4["solo_tackle_2_player_id"],
            tackle_4["assist_tackle_1_player_id"],
            tackle_4["assist_tackle_2_player_id"],
            tackle_4["assist_tackle_3_player_id"],
            tackle_4["assist_tackle_4_player_id"],
            tackle_4["tackle_with_assist_1_player_id"],
            tackle_4["tackle_with_assist_2_player_id"]
        ])
        .dropna()
        .value_counts()
        .reset_index()
    )
    tackle_stops_4.columns = ["player_id", "fourth_stop_tackle"]
    
    ints_4 = fourth_fail[fourth_fail["interception"] == 1]
    int_stops_4 = (
        ints_4["interception_player_id"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    int_stops_4.columns = ["player_id", "fourth_stop_int"]

    ff_4 = fourth_fail[fourth_fail["fumble_forced"] == 1]
    ff_stops_4 = (
        pd.concat([
            ff_4["forced_fumble_player_1_player_id"],
            ff_4["forced_fumble_player_2_player_id"]
        ])
        .dropna()
        .value_counts()
        .reset_index()
    )
    ff_stops_4.columns = ["player_id", "fourth_stop_ff"]

    fourth_stops = sack_stops_4 \
    .merge(tackle_stops_4, on="player_id", how="outer") \
    .merge(int_stops_4, on="player_id", how="outer") \
    .merge(ff_stops_4, on="player_id", how="outer") \
    .fillna(0)
    fourth_stops["crucial_fourthStops"] = (
        fourth_stops["fourth_stop_sacks"] +
        fourth_stops["fourth_stop_tackle"] +
        fourth_stops["fourth_stop_int"] +
        fourth_stops["fourth_stop_ff"]
    )


    third_final = third_stops[["player_id", "crucial_thirdStops"]]
    fourth_final = fourth_stops[["player_id", "crucial_fourthStops"]]
    # Merge into player df
    df = df.merge(third_final, on="player_id", how="left")
    df = df.merge(fourth_final, on="player_id", how="left")

    # Fill missing values with 0
    df[["crucial_thirdStops", "crucial_fourthStops"]] = (
        df[["crucial_thirdStops", "crucial_fourthStops"]]
        .fillna(0)
    )
    
    df["Adjusted_sack_score"] = df["def_sacks"] * (1 - .1 * df["third_long_sack_ratio"])
    ##Situational scoring
    df["Situational_score"] = (4*df["Adjusted_sack_score"] + 3*df["crucial_thirdStops"] + 4*df["crucial_fourthStops"]) 



    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Only fill stats that truly mean zero
    zero_cols = ["Turnover_score","Efficency_score","penalty_score", "Situational_score"
    ]
    df[zero_cols] = df[zero_cols].fillna(0)
    
    ##TOTAL Season SCORE
    if position_type == "EDGE":
        df["Season_score"] = (6*df["PR_per100"] + 3*df["RunD_per100"]+ 3*df["Turnover_score"] + 
        2*df["Efficency_score"] -2*df["penalty_score"]+ 4*df["Situational_score"])  #apply personal weights ie how valuable i view passrush score or efficiency or turnovers etc
        
    
    elif position_type == "INTERIOR":
        df["Season_score"] = (3*df["PR_per100"] + 7*df["RunD_per100"]+ 2*df["Turnover_score"] + 
        2*df["Efficency_score"]-2*df["penalty_score"]+ 4*df["Situational_score"]) #for interiors run D matter more
    


    season_scores = (df.groupby(["player_id", "player_name", "season"], as_index=False)[
        [
            "PR_per100",
            "RunD_per100",
            "Turnover_score",
            "Efficency_score",
            "Situational_score",
            "penalty_score",
            "Season_score",
        ]
        ].mean())

    return season_scores

    

    

    