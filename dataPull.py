import pandas as pd
import numpy as np
import sklearn
import nflreadpy as nfl

def load_data():

    Years = [2022, 2023, 2024]
    pbp = nfl.load_pbp(Years).to_pandas()
    player_stats = nfl.load_player_stats(Years).to_pandas()
    snaps = nfl.load_snap_counts(seasons=Years).to_pandas()
    rosters = nfl.load_rosters(seasons=Years).to_pandas()
    contracts = nfl.load_contracts().to_pandas()
    injuries = nfl.load_injuries(seasons=Years).to_pandas()
    

    print("Data loaded successfully.")
    

    return pbp,player_stats, snaps, rosters, contracts, injuries


