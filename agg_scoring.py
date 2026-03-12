import pandas as pd
import numpy as np


##FINAL AGG TOTAL SCORE (3 SEASONS)

    ##Just pulls ur scores from each season and stores as a aggregated total
    #total PR score is ur PR per 100 snaps to account for efficiency and injury etc
def agg_scores(df):
    season_scores = (df.groupby(["player_id", "player_name", "season"], as_index=False)["Season_score"].sum())

    pivot = (season_scores.pivot(index=["player_id", "player_name"],
             columns="season",
             values="Season_score").fillna(0))
    
    pivot["Final_agg_score"] = (0.1*pivot.get(2022, 0) + 0.3*pivot.get(2023, 0) +0.6*pivot.get(2024, 0))
    pivot["Final_z"] = ((pivot["Final_agg_score"] - pivot["Final_agg_score"].mean()) /pivot["Final_agg_score"].std())
    
    #agg prscore per player
    avg_scores = df.groupby(["player_id","player_name"], as_index=False)[["PR_per100","RunD_per100","Situational_score"]].mean()    
    avg_scores = avg_scores.rename(columns={"PR_per100":"agg_PR_score", "RunD_per100":"agg_RunD_score"})
                
    pivot = pivot.reset_index().merge(avg_scores, on=["player_id","player_name"], how="left")
    pivot = pivot.sort_values("Final_agg_score", ascending=False)
    
    
    pivot = pivot.reset_index().sort_values("Final_agg_score", ascending=False)
    
    return pivot