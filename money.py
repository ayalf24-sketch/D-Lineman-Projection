import pandas as pd
import numpy as np




def assign_roles(df, position):
    # Use quantiles to define high/medium/low 
    df = df.copy()
    if position == "EDGE":

        pr_high = df['agg_PR_score'].quantile(0.75)
        pr_mid  = df['agg_PR_score'].quantile(0.50)
        pr_low  = df['agg_PR_score'].quantile(0.35)
        rd_high = df['agg_RunD_score'].quantile(0.75)
        rd_mid  = df['agg_RunD_score'].quantile(0.50)
    else:
        pr_high = df['agg_PR_score'].quantile(0.90)
        pr_mid  = df['agg_PR_score'].quantile(0.55) #Interior players have lower RunD thresholds and higher PR thresholds
        pr_low  = df['agg_PR_score'].quantile(0.35)
        rd_high = df['agg_RunD_score'].quantile(0.63)
        rd_mid  = df['agg_RunD_score'].quantile(0.45)

    def role(row):
        pr = row['agg_PR_score']
        rd = row['agg_RunD_score']

        if pr > pr_high and rd > rd_high:
            return "Every-Down"     ##classifying specialist roles

        elif pr > pr_high and rd < rd_mid:
            return "Pass-Rush Specialist"

        elif rd > rd_high:
            return "Run Defender"

        elif pr > pr_mid and rd > rd_mid:
            return "Balanced"

        else:
            return "Replacement"

    df["Role"] = df.apply(role, axis=1)
    return df

def compare_pay(df, contracts, position_type):
    
    # Merge contract info
    df = df.merge(
        contracts[['gsis_id','apy','guaranteed']], 
        left_on='player_id', 
        right_on='gsis_id', 
        how='left'
    )
    # Compute "should be APY" using the mid-point of the tier range
    #tier_market = df.groupby("Tier")["apy"].mean()      ##EACH TIER MARKET AVERAGE APYS
    #print(tier_market)

    df["tier_score_z"] = df.groupby("Tier")["Final_agg_score"].transform(lambda x: (x - x.mean()) / x.std()) #find z score of final agg performance in each tier
    df["tier_Mrkt_Avg"] = df.groupby("Tier")["apy"].transform("mean") #tier apy averages
    
    if position_type == "EDGE":
    #ROLE MULTIPLYERS
        role_mult = {
            "Every-Down": 1.18,     #everydown players should recieve a boost
            "Balanced": 1.00,
            "Pass-Rush Specialist": 0.95,   #DPR isnt exactly a good thing because one is a liablity on 1st and 2nd down
            "Run Defender": 0.90,   #not a pass threat
            "Replacement": 0.75}    #poor
        tier_mid = {
        0: 36,      #current edge market points (Millions)
        1: 26.5,
        2: 16,
        3: 11,
        4: 7,
        5: 3
        }
    else: 
        role_mult = {
            "Every-Down": 1.18,
            "Balanced": 1.04,
            "Pass-Rush Specialist": 0.99,   
            "Run Defender": 0.98,   #interiors are expected to be run first
            "Replacement": 0.70}
        tier_mid = {
        0: 24,      #current interior market
        1: 17,
        2: 14,
        3: 7,
        4: 4,
        5: 2.5
        } 

    tier_spread = {
    0: 4,
    1: 4,       
    2: 4,
    3: 2.75,
    4: 2,
    5: 1
}
    df["tier_score_z"] = df["tier_score_z"].clip(-2.00, 2.00)   #capped so crazy outliers in tiers dont throw off apy estimates
    #estimating pay based on the tier mrkt average plus 
    df["Est_APY"] = (df["Tier"].map(tier_mid) + df["tier_score_z"] * df["Tier"].map(tier_spread)) #ur value is based on ur tier midpoints and then how u perform compared to players in ur tier
    df["Est_APY"] = df["Est_APY"]* df["Role"].map(role_mult)    #roles apply multipliers

    ##compare apy to z-score apy from players in their tier
    df['Tier_APY_Z'] = (df.groupby('Tier')['apy'].transform(lambda x: (x - x.mean()) / (x.std() if x.std() != 0 else 1)))
    ##assign over/under/fair based on z score
    df["Pay_Diff"] = df["apy"] - df["Est_APY"]

    df["Pay_flag"] = np.select([df["Pay_Diff"] > 5,df["Pay_Diff"] < -5],["OverPaid","UnderPaid"], default="FairlyPaid") #if ur est is >5 ur actual pay then ur underpaid
    
    return df[['player_id','player_name','Tier','Final_agg_score','agg_PR_score','agg_RunD_score','Situational_score','apy','Role',"Est_APY",'Pay_flag','Tier_APY_Z']]
    
   