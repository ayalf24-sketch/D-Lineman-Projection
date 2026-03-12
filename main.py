from dataPull import load_data
from dataCleaning import clean_dl_stats, clean_edge_data
from dataCleaning import clean_pbp
from featureEngineering import build_player_features
import pandas as pd
from agg_scoring import agg_scores
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from money import assign_roles
from money import compare_pay
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import MaxNLocator





def main():
    pbp, player_stats, snaps, rosters, contracts, injuries = load_data()
    contracts.rename(columns={"player": "player_id"}, inplace=True)
    contracts = contracts.sort_values("year_signed", ascending=False).drop_duplicates(subset="gsis_id", keep="first")

    edge_stats, interior_stats = clean_dl_stats(player_stats) 
    interior_ids = [                                                            
        ("00-0032762", "C.Jones"),            # Chris Jones
        ("00-0035248", "Z.Allen"),            # Zach Allen
        ("00-0031933", "L.Williams"),         # Leonard Williams
        ("00-0026190", "C.Campbell"),         # Calais Campbell
        ("00-0034800", "B.Hill"),             # B.J. Hill
        ("00-0036916", "M.Williams"),         # Milton Williams
        ("00-0033523", "J.Allen"),            # Jonathan Allen
        ("00-0032416", "Q.Jefferson"),        # Quinton Jefferson
        ("00-0035890", "T.Wharton"),          # Tershawn Wharton
        ("00-0039734", "B.Fiske"),            # Braden Fiske
        ("00-0032424", "D.Reader"),           # D.J. Reader
        ("00-0033546", "D.Tomlinson"),        # Dalvin Tomlinson
        ("00-0032667", "R.Robertson-Harris"), # Roy Robertson-Harris
        ("00-0036220", "D.Brown"),            # Derrick Brown
        ("00-0032889", "A.Robinson"),         # A'Shawn Robinson
        ("00-0034773", "D.Jones"),            # D.J. Jones
        ("00-0029657", "A.Hicks"),            # Akiem Hicks
        ("00-0037759", "D.Leal"),             # DeMarvin Leal
        ("00-0034755", "M.Adams"),             # Montravius Adams
        ("00-0034805", "J.Franklin-Myers")  #J.F.M
    ]
    interior_ids_only = [x[0] for x in interior_ids]
    interior_from_edge = edge_stats[edge_stats["player_id"].isin(interior_ids_only)]
    edge_stats = edge_stats[~edge_stats["player_id"].isin(interior_ids_only)]

    interior_stats = pd.concat([interior_stats, interior_from_edge])                            ##MOVE Actual Interior players into their correct position class

    edge_stats = clean_edge_data(edge_stats)    ##takes out LBS who are faslefully in edge class
    ##Moves falsely labelled interior players from my edge class into their right interior class
    

    pbpClean = clean_pbp(pbp)   ##cleans our data, drops useless info or Nans

    edge_features = build_player_features(edge_stats, "EDGE", pbpClean,snaps)
    interior_features = build_player_features(interior_stats, "INTERIOR", pbpClean,snaps)
    
    
    
    finals_edge = agg_scores(edge_features)         ##calc aggregated scores 
    finals_int = agg_scores(interior_features)

    cluster_edge_features = finals_edge[['Final_agg_score']].dropna()     ##clustering features based on Aggscore
    cluster_int_features = finals_int[['Final_agg_score']].dropna()

    ##Scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(cluster_edge_features) ##Edges
    X_scaled1 = scaler.fit_transform(cluster_int_features)  ##Interiors

    kmeans_edge = KMeans(n_clusters=6, random_state=42)
    kmeans_int = KMeans(n_clusters=6, random_state=42)
    
    finals_edge['Cluster'] = kmeans_edge.fit_predict(X_scaled)
    finals_int['Cluster'] = kmeans_int.fit_predict(X_scaled1)       
    
    ##sorts clusters 0-elite 1-very good, 2etc ...
    edge_order = {old:new for new, old in enumerate(finals_edge.groupby('Cluster')['Final_agg_score'].mean().sort_values(ascending=False).index)}
    int_order = {old:new for new, old in enumerate(finals_int.groupby('Cluster')['Final_agg_score'].mean().sort_values(ascending=False).index)}

    finals_edge['Tier'] = finals_edge['Cluster'].map(edge_order)
    finals_int['Tier'] = finals_int['Cluster'].map(int_order)

    
    ##Pay Tiers and Apy
    edge_roles = assign_roles(finals_edge, "EDGE")      ##Assign each player a role based on their passrush vs runD metrics
    int_roles = assign_roles(finals_int, "INTERIOR")    ##Roles will affect future valuations
    
    
    

    edge_tiers = compare_pay(edge_roles, contracts, "EDGE") ##Assigns OUR VALUATION of apy for each player based on their performance, tiers, roles, and positionmarket
    int_tiers = compare_pay(int_roles, contracts, "INTERIOR")

    #prints
    print(edge_tiers.to_string()) ##PRINTS EVERYTHING, TIERS, THE PLAYERS FINAL SCORES , MONEY ESTIMATIONS AND PAY FLAG
    #print(int_tiers.to_string())


    plt.figure(figsize=(14,12))   # bigger graph
    
    # scatter plot PASS D VS RUND PERFORMANCE FOR EDGES
    sns.scatterplot(
        data=edge_tiers,
        x="agg_RunD_score",
        y="agg_PR_score",
        hue="Tier",
        palette="viridis",
        s=50,
        alpha = 0.4
    )

    # quadrant lines 
    x_avg = edge_tiers["agg_RunD_score"].mean()
    y_avg = edge_tiers["agg_PR_score"].mean()

    plt.axvline(x=x_avg, color="black", linestyle="--")
    plt.axhline(y=y_avg, color="black", linestyle="--")

    # add player labels
    for i, row in edge_tiers.iterrows():
        plt.text(
            row["agg_RunD_score"] + 0.01,
            row["agg_PR_score"] + 0.01,
            row["player_name"],
            fontsize=8
        )

    plt.title("Edges Run Defense vs Pass Rush Impact")
    plt.xlabel("Run Defense Score")
    plt.ylabel("Pass Rush Score")

    plt.grid(True)
    plt.show()

#INTERIOR PASS V RUN
    sns.scatterplot(
        data=int_tiers,
        x="agg_RunD_score",
        y="agg_PR_score",
        hue="Tier",
        palette="viridis",
        s=50,
        alpha = 0.4
    )

    # quadrant lines 
    x_avg = int_tiers["agg_RunD_score"].mean()
    y_avg = int_tiers["agg_PR_score"].mean()

    plt.axvline(x=x_avg, color="black", linestyle="--")
    plt.axhline(y=y_avg, color="black", linestyle="--")

    # add player labels
    for i, row in int_tiers.iterrows():
        plt.text(
            row["agg_RunD_score"] + 0.01,
            row["agg_PR_score"] + 0.01,
            row["player_name"],
            fontsize=7
        )

    plt.title("Interior-Lineman Run Defense vs Pass Rush Impact")
    plt.xlabel("Run Defense Score")
    plt.ylabel("Pass Rush Score")

    plt.grid(True)
    plt.show()

    plotdy = edge_tiers[edge_tiers["Situational_score"] > 10]
    #SITUATIONAL SCORE METRICS EDGES:
    plt.figure(figsize=(14,12))
    sns.scatterplot(
    data=plotdy, ###rids of the useless practice squad and bottom guys clogging up the graph
    x="Situational_score",
    y="Final_agg_score",
    hue="Tier",
    palette="viridis",
    s=50,
    alpha=0.4
)
    x_avg = plotdy["Situational_score"].mean()
    y_avg = plotdy["Final_agg_score"].mean()

    plt.axvline(x=x_avg, color="black", linestyle="--")
    plt.axhline(y=y_avg, color="black", linestyle="--")

    # add player labels
    for i, row in plotdy.iterrows():
        plt.text(
            row["Situational_score"] + 0.01,
            row["Final_agg_score"] + 0.01,
            row["player_name"],
            fontsize=7,
            alpha=0.6
        )
    plt.xlim(left=0)

    plt.xlabel("Situational Impact (3rd/4th Down)")
    plt.ylabel("Overall Performance Score")
    plt.title("Edges Clutch Defensive Impact (> 10 points)")

    plt.grid(True)
    plt.show()


    #
    # 
    # 
    # #

    #INTERIOR SITUATIONAL IMPACT
    plt.figure(figsize=(14,12))
    plotdy = int_tiers[(int_tiers["Situational_score"] > 5) & (int_tiers["Final_agg_score"] > 40)]
    sns.scatterplot(
    data=plotdy, ###rids of the useless practice squad and bottom guys clogging up the graph
    x="Situational_score",
    y="Final_agg_score",
    hue="Tier",
    palette="viridis",
    s=50,
    alpha=0.4
)
    x_avg = plotdy["Situational_score"].mean()
    y_avg = plotdy["Final_agg_score"].mean()

    plt.axvline(x=x_avg, color="black", linestyle="--")
    plt.axhline(y=y_avg, color="black", linestyle="--")

    # add player labels
    for i, row in plotdy.iterrows():
        plt.text(
            row["Situational_score"] + 0.01,
            row["Final_agg_score"] + 0.01,
            row["player_name"],
            fontsize=7,
            alpha=0.6
        )
    plt.xlim(left=0)

    plt.xlabel("Situational Impact (3rd/4th Down)")
    plt.ylabel("Overall Performance Score")
    plt.title("Interiors Clutch Defensive Impact (> 5 points)")

    plt.grid(True)
    plt.show()


    ##Hard to plot perfomance vs apy as its noisy
    #
    #
    #Est Apy vs Apy EDGES:
    plt.figure(figsize=(18,10))
    
    plotdy = edge_tiers[(edge_tiers["Final_agg_score"] > 140) | (edge_tiers["apy"] > 2.5)] ##rids of the useless practice squad and bottom guys clogging up the graph
    sns.scatterplot(    
    data=plotdy,
    x="apy",
    y="Est_APY",
    hue="Tier",
    palette="viridis",
    s=50,
    alpha=0.4
)

# fairness line
    max_val = max(plotdy["apy"].max(), plotdy["Est_APY"].max())
    plt.plot([0,max_val],[0,max_val], linestyle="--")
    alpha=0.6
    for i, row in plotdy.iterrows():
        plt.text(
            row["apy"] + 0.01,
            row["Est_APY"] + 0.01,
            row["player_name"],
            fontsize=7
        )
    plt.xlim(left=0)

    plt.title("Edges Actual APY vs Model Estimated APY (Min Agg.Score-140 or APY >2.5M)")
    plt.xlabel("Actual APY ($M)")
    plt.ylabel("Estimated APY ($M)")

    plt.grid(True)

    plt.show()


    ##INTERIORS APYS


    plt.figure(figsize=(14,12))
    
    plotdy = int_tiers[(int_tiers["Final_agg_score"] > 180) | (int_tiers["apy"] > 5.0)] ##rids of the useless practice squad and bottom guys clogging up the graph
    sns.scatterplot(    
    data=plotdy,
    x="apy",
    y="Est_APY",
    hue="Tier",
    palette="viridis",
    s=50,
    alpha = 0.4
)

# fairness line
    max_val = max(plotdy["apy"].max(), plotdy["Est_APY"].max())
    plt.plot([0,max_val],[0,max_val], linestyle="--")
    alpha=0.6
    for i, row in plotdy.iterrows():
        plt.text(
            row["apy"] + 0.01,
            row["Est_APY"] + 0.01,
            row["player_name"],
            fontsize=7
        )
    
    plt.xlim(left=0)
    plt.title("Interiors Actual APY vs Model Estimated APY Min Agg.Score-180 or APY >5M)")
    plt.xlabel("Actual APY ($M)")
    plt.ylabel("Estimated APY ($M)")

    plt.grid(True)

    plt.show()





    ###MONEYBALL EDGES:
    

    plt.figure(figsize=(16,14))
    plotdy = edge_tiers[(edge_tiers["Final_agg_score"] > 50)]
    plotdy["paydiff"] = plotdy["Est_APY"] - plotdy["apy"]
    plotdy["paydiff_jitter"] = plotdy["paydiff"] + np.random.normal(0, 0.25, len(plotdy))

    sns.scatterplot(
        data=plotdy,
        x="paydiff_jitter",
        y="Final_agg_score",
        hue="Role",          # color by role instead of tier
        palette="Set2",
        s=50,
        alpha=0.35
    )

    # vertical divider (fair value)
    plt.axvline(0, linestyle="--", color="black")

    # optional horizontal divider (average performance)
    y_avg = plotdy["Final_agg_score"].mean()
    plt.axhline(y_avg, linestyle="--", color="gray", alpha=0.6)

    # quadrant labels
    plt.text(
        plotdy["paydiff"].max()*0.55,
        plotdy["Final_agg_score"].max()*0.9,
        "Underpaid Stars",
        fontsize=12,
        weight="bold"
    )

    plt.text(
        plotdy["paydiff"].min()*0.75,
        plotdy["Final_agg_score"].max()*0.9,
        "Overpaid Stars",
        fontsize=12,
        weight="bold"
    )

    plt.text(
        plotdy["paydiff"].max()*0.55,
        plotdy["Final_agg_score"].min()*1.3,
        "Value Depth",
        fontsize=12,
        weight="bold"
    )

    plt.text(
        plotdy["paydiff"].min()*0.75,
        plotdy["Final_agg_score"].min()*1.3,
        "Replaceable",
        fontsize=12,
        weight="bold"
    )

    for i, row in plotdy.iterrows():
        plt.text(
            row["paydiff"] + 0.01,
            row["Final_agg_score"] + 0.01,
            row["player_name"],
            fontsize=7
        )

    plt.xlabel("Value Difference (Est APY − Actual APY)")
    plt.ylabel("Aggregate Performance Score")
    plt.title("EDGE Moneyball Market Inefficiencies (Min Score: 50)")

    plt.grid(True)
    plt.show()


    ##MONEYBALL INTERIORS


    plt.figure(figsize=(16,14))
    plotdy = int_tiers[(int_tiers["Final_agg_score"] > 60)]
    plotdy["paydiff"] = plotdy["Est_APY"] - plotdy["apy"]
    plotdy["paydiff_jitter"] = plotdy["paydiff"] + np.random.normal(0, 0.25, len(plotdy))

    sns.scatterplot(
        data=plotdy,
        x="paydiff_jitter",
        y="Final_agg_score",
        hue="Role",          # color by role instead of tier
        palette="Set2",
        s=50,
        alpha=0.35
    )

    # vertical divider (fair value)
    plt.axvline(0, linestyle="--", color="black")

    # optional horizontal divider (average performance)
    y_avg = plotdy["Final_agg_score"].mean()
    plt.axhline(y_avg, linestyle="--", color="gray", alpha=0.6)

    # quadrant labels
    plt.text(
        plotdy["paydiff"].max()*0.55,
        plotdy["Final_agg_score"].max()*0.9,
        "Underpaid Stars",
        fontsize=12,
        weight="bold"
    )

    plt.text(
        plotdy["paydiff"].min()*0.75,
        plotdy["Final_agg_score"].max()*0.9,
        "Overpaid Stars",
        fontsize=12,
        weight="bold"
    )

    plt.text(
        plotdy["paydiff"].max()*0.55,
        plotdy["Final_agg_score"].min()*1.3,
        "Value Depth",
        fontsize=12,
        weight="bold"
    )

    plt.text(
        plotdy["paydiff"].min()*0.75,
        plotdy["Final_agg_score"].min()*1.3,
        "Replaceable",
        fontsize=12,
        weight="bold"
    )

    for i, row in plotdy.iterrows():
        plt.text(
            row["paydiff"] + 0.01,
            row["Final_agg_score"] + 0.01,
            row["player_name"],
            fontsize=7
        )

    plt.xlabel("Value Difference (Est APY − Actual APY)")
    plt.ylabel("Aggregate Performance Score")
    plt.title("Interior Moneyball Market Inefficiencies (Min Score: 60)")

    plt.grid(True)
    plt.show()
        


    

    ##BEST AND WORST CONTRACTS EDGES
    plotdy = edge_tiers[(edge_tiers["Final_agg_score"] > 80) & (edge_tiers["apy"] > 2.5)]           ##Excluding Rookie and Min Deals
    
    plotdy["value_ratio"] = plotdy["Est_APY"]/plotdy["apy"] ##USING VAL RATION BECAUSE DIFFERENCES IN LARGE CONTRACTS WILL ALWAYS SEEM WORSE

    best_contracts = plotdy.sort_values("value_ratio", ascending=False).head(10)
    worst_contracts = plotdy.sort_values("value_ratio").head(10)


    fig, axes = plt.subplots(1,2, figsize=(16,8))

    # BEST VALUE
    axes[0].barh(
        best_contracts["player_name"],
        best_contracts["value_ratio"],
        color="seagreen",
        alpha=0.8
    )

    axes[0].invert_yaxis()
    axes[0].set_title("Best Value Contracts (Ratio)")
    axes[0].set_xlabel("Estimated Ratio Surplus (Est_APY / APY)")
    axes[0].xaxis.set_major_locator(MultipleLocator(0.50))


    # WORST VALUE
    axes[1].barh(
        worst_contracts["player_name"],
        worst_contracts["value_ratio"],
        color="indianred",
        alpha=0.8
    )

    axes[1].invert_yaxis()
    axes[1].set_title("Worst Value Contracts (Ratio)")
    axes[1].set_xlabel("Estimated Ratio Deficit (Est_APY / APY)")
    axes[1].xaxis.set_major_locator(MultipleLocator(0.25))


    fig.suptitle("Excluding Edge Rookie Deals and Minimum Salary Contracts", fontsize=16)
    plt.tight_layout()
    plt.show()


    ##INTERIORS
    plotdy = int_tiers[(int_tiers["Final_agg_score"] > 80) & (int_tiers["apy"] > 2.5)]           ##Excluding Rookie and Min Deals
    
    plotdy["value_ratio"] = plotdy["Est_APY"]/plotdy["apy"] ##USING VAL RATION BECAUSE DIFFERENCES IN LARGE CONTRACTS WILL ALWAYS SEEM WORSE

    best_contracts = plotdy.sort_values("value_ratio", ascending=False).head(10)
    worst_contracts = plotdy.sort_values("value_ratio").head(10)


    fig, axes = plt.subplots(1,2, figsize=(16,8))

    # BEST VALUE
    axes[0].barh(
        best_contracts["player_name"],
        best_contracts["value_ratio"],
        color="seagreen",
        alpha=0.8
    )

    axes[0].invert_yaxis()
    axes[0].set_title("Best Value Contracts (Ratio)")
    axes[0].set_xlabel("Estimated Ratio Surplus (Est_APY / APY)")
    axes[0].xaxis.set_major_locator(MultipleLocator(0.50))


    # WORST VALUE
    axes[1].barh(
        worst_contracts["player_name"],
        worst_contracts["value_ratio"],
        color="indianred",
        alpha=0.8
    )

    axes[1].invert_yaxis()
    axes[1].set_title("Worst Value Contracts (Ratio)")
    axes[1].set_xlabel("Estimated Ratio Deficit (Est_APY / APY)")
    axes[1].xaxis.set_major_locator(MultipleLocator(0.10))
    axes[1].xaxis.set_major_locator(MaxNLocator(5))     



    fig.suptitle("Excluding Interior Rookie Deals and Minimum Salary Contracts", fontsize=16)
    plt.tight_layout()
    plt.show()





    #EDGES 2


    plotdy = edge_tiers[(edge_tiers["Final_agg_score"] > 80)]      ##Including Rookie and Min. Salary Deals (still filtering out bottom feeders)
    
    plotdy["value_ratio"] = plotdy["Est_APY"]/plotdy["apy"] ##USING VALue RATIO BECAUSE DIFFERENCES IN LARGE CONTRACTS WILL ALWAYS SEEM WORSE

    best_contracts = plotdy.sort_values("value_ratio", ascending=False).head(10)
    worst_contracts = plotdy.sort_values("value_ratio").head(10)


    fig, axes = plt.subplots(1,2, figsize=(16,8))

    # BEST VALUE
    axes[0].barh(
        best_contracts["player_name"],
        best_contracts["value_ratio"],
        color="seagreen",
        alpha=0.8
    )

    axes[0].invert_yaxis()
    axes[0].set_title("Best Value Contracts (Ratio)")
    axes[0].set_xlabel("Estimated Ratio Surplus (Est_APY / APY)")
    axes[0].xaxis.set_major_locator(MultipleLocator(1))        
    axes[0].xaxis.set_major_locator(MaxNLocator(10))     


    # WORST VALUE
    axes[1].barh(
        worst_contracts["player_name"],
        worst_contracts["value_ratio"],
        color="indianred",
        alpha=0.8
    )

    axes[1].invert_yaxis()
    axes[1].set_title("Worst Value Contracts (Ratio)")
    axes[1].set_xlabel("Estimated Ratio Deficit (Est_APY / APY)")
    axes[1].xaxis.set_major_locator(MultipleLocator(0.10))


    plt.tight_layout()
    fig.suptitle("Including Edges Rookie Deals and Minimum Salary Contracts", fontsize=10)

    plt.show()



    ##INTERIORS

    plotdy = int_tiers[(int_tiers["Final_agg_score"] > 80)]      ##Including Rookie and Min. Salary Deals (still filtering out bottom feeders)
    
    plotdy["value_ratio"] = plotdy["Est_APY"]/plotdy["apy"] ##USING VALue RATIO BECAUSE DIFFERENCES IN LARGE CONTRACTS WILL ALWAYS SEEM WORSE

    best_contracts = plotdy.sort_values("value_ratio", ascending=False).head(10)
    worst_contracts = plotdy.sort_values("value_ratio").head(10)


    fig, axes = plt.subplots(1,2, figsize=(16,8))

    # BEST VALUE
    axes[0].barh(
        best_contracts["player_name"],
        best_contracts["value_ratio"],
        color="seagreen",
        alpha=0.8
    )

    axes[0].invert_yaxis()
    axes[0].set_title("Best Value Contracts (Ratio)")
    axes[0].set_xlabel("Estimated Ratio Surplus (Est_APY / APY)")
    axes[0].xaxis.set_major_locator(MultipleLocator(1))       
    axes[0].xaxis.set_major_locator(MaxNLocator(10))     


    # WORST VALUE
    axes[1].barh(
        worst_contracts["player_name"],
        worst_contracts["value_ratio"],
        color="indianred",
        alpha=0.8
    )

    axes[1].invert_yaxis()
    axes[1].set_title("Worst Value Contracts (Ratio)")
    axes[1].set_xlabel("Estimated Ratio Deficit (Est_APY / APY)")
    axes[1].xaxis.set_major_locator(MultipleLocator(0.10))
    axes[1].xaxis.set_major_locator(MaxNLocator(5))     



    plt.tight_layout()
    fig.suptitle("Including Interiors Rookie Deals and Minimum Salary Contracts", fontsize=7)

    plt.show()


##WEIGHTED EDGES

    plotdy = edge_tiers[(edge_tiers["Final_agg_score"] > 80) & (edge_tiers["Role"] != "Replacement")].copy()    ##WEIGHTED CONTRACT VALUES

    plotdy["value_score"] = (plotdy["Est_APY"] - plotdy["apy"]) / np.sqrt(plotdy["apy"]) * (plotdy['Final_agg_score'] / plotdy['Final_agg_score'].mean())
    ##USING WEIGHTED APYS SO THAT Smaller contracts dont dominate and differences in large dont aswell
    ##Getting rid of replacement role players because they arent beneficial when deciding the best contracts and we need to weight performance along with the apys

    best_contracts = plotdy.sort_values("value_score", ascending=False).head(10)
    worst_contracts = plotdy.sort_values("value_score").head(10)

    fig, axes = plt.subplots(1,2, figsize=(16,8))

    # BEST VALUE
    axes[0].barh(
        best_contracts["player_name"],
        best_contracts["value_score"],
        color="seagreen",
        alpha=0.8
    )

    axes[0].invert_yaxis()
    axes[0].set_title("Best Value Contracts (Ratio)")
    axes[0].set_xlabel("Estimated Ratio Surplus (Est_APY - Apy / sqrt(APY) * (Final Agg.Score/ Avg Final Agg.Score) )")
    axes[0].xaxis.set_major_locator(MultipleLocator(1))


    # WORST VALUE
    axes[1].barh(
        worst_contracts["player_name"],
        worst_contracts["value_score"],
        color="indianred",
        alpha=0.8
    )

    axes[1].invert_yaxis()
    axes[1].set_title("Worst Value Contracts (Ratio)")
    axes[1].set_xlabel("Estimated Ratio Deficit (Est_APY - Apy / sqrt(APY) * (Final Agg.Score/ Avg Final Agg.Score) )")
    axes[1].xaxis.set_major_locator(MultipleLocator(0.50))

    plt.tight_layout()
    fig.suptitle("Edges Weighted Contracts Value Score", fontsize=12)
    plt.show()



    ###Interiors
    plotdy = int_tiers[(int_tiers["Final_agg_score"] > 80) & (int_tiers["Role"] != "Replacement")].copy()    ##WEIGHTED CONTRACT VALUES

    plotdy["value_score"] = (plotdy["Est_APY"] - plotdy["apy"]) / np.sqrt(plotdy["apy"]) * (plotdy['Final_agg_score'] / plotdy['Final_agg_score'].mean())
    ##USING WEIGHTED APYS SO THAT Smaller contracts dont dominate and differences in large dont aswell
    ##Getting rid of replacement role players because they arent beneficial when deciding the best contracts and we need to weight performance along with the apys

    best_contracts = plotdy.sort_values("value_score", ascending=False).head(10)
    worst_contracts = plotdy.sort_values("value_score").head(10)

    fig, axes = plt.subplots(1,2, figsize=(16,8))

    # BEST VALUE
    axes[0].barh(
        best_contracts["player_name"],
        best_contracts["value_score"],
        color="seagreen",
        alpha=0.8
    )

    axes[0].invert_yaxis()
    axes[0].set_title("Best Value Contracts (Ratio)")
    axes[0].set_xlabel("Estimated Ratio Surplus (Est_APY - Apy / sqrt(APY) * (Final Agg.Score/ Avg Final Agg.Score) )")
    axes[0].xaxis.set_major_locator(MultipleLocator(5))
    axes[0].xaxis.set_major_locator(MaxNLocator(10))     




    # WORST VALUE
    axes[1].barh(
        worst_contracts["player_name"],
        worst_contracts["value_score"],
        color="indianred",
        alpha=0.8
    )

    axes[1].invert_yaxis()
    axes[1].set_title("Worst Value Contracts (Ratio)")
    axes[1].set_xlabel("Estimated Ratio Deficit (Est_APY - Apy / sqrt(APY) * (Final Agg.Score/ Avg Final Agg.Score) )")
    axes[1].xaxis.set_major_locator(MultipleLocator(0.50))

    plt.tight_layout()
    fig.suptitle("Interiors Weighted Contracts Value Score", fontsize=12)
    plt.show()




    ##
    # where i left off
    #PLOTING OUR FINDINGS

    #Plots: 1: Pass D vs RunD    -->> Completed
    # 2: Situational CLUTCH score metrics -->>
    # 3: Est APY VS APY
    # 3.5 Scatter of Final agg score and apy just showing whose underpaid etc
    # 4: MOENY BALL METRICS TOTAL SCORE VS VALUE DIFF FROM OUR ESITMATIONS (ie. overpayed and underpayed metrics) ;
    # #Identifying best and worst contracts 

if __name__ == "__main__":
    main()


