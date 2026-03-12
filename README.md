# D-Lineman-Projection

**Overview:**

In this project, I analyze NFL defensive line contracts to identify market inefficiencies and evaluate whether players are overpaid or underpaid relative to their on-field performance. Using player production metrics, situational impact data, and contract values, I built a performance-based valuation model that estimates the annual value (APY) each defensive lineman is producing, regardless of age. This estimated value is then compared with the player’s actual contract to determine contract efficiency.
The analysis focuses on two primary defensive line positions: 1.) EDGE defenders 2.) Interior defensive linemen (IDL) 
  - Each postion has their own seperate graphing and scoring system 

**KEY GOALS:**
Create a tiering system 0-5 (0: Elite, 1: Very good, ...) where I cluster players together based on their performance scores.
Find which defensive linemen provide the most value relative to their contracts? And vice versa.
Designate roles for each player depending on their PassD score vs RunD score to separate those who are Designated Pass-Rushers, Run-Stoppers, or Every-Down players. 
Calculate the money market in each tier.

1.**Methodology:**
The project builds a performance-driven contract valuation model using a multi-step process.
Each player is assigned a Final Aggregate Score representing their overall impact in the past 3 years (2022,2023,2024). With recent years being valued more.
This score combines multiple performance metrics such as:
- Pass rush production
- Run defense production
- Situational performance (3rd/4th down impact)
- Play-by-play efficiency based on snap totals
- Turnover production
- Penalties


2.**Performance Aggregation:**
The goal of the aggregate score is to provide a single holistic measure of defensive line performance. Now the Final Agg score is affected by the weights of the performance metrics. For edge rushers, Pass Rush is more valuable, hence my weighting for an edge score is:
  6*["PR_per100"] + 3*["RunD_per100"]+ 3*["Turnover_score"] + 2*["Efficency_score"] -2*["penalty_score"]+ 4*["Situational_score"])
While for interior linemen, RunD is more valuable: 
  3*["PR_per100"] + 7*["RunD_per100"]+ 2*["Turnover_score"] + 2*["Efficency_score"]-2*["penalty_score"]+ 4*["Situational_score"]
Now the calculations for ex. of PR_per100 take into account the number of sacks, QB hits, and passes defended a player has with applied weighting for each stat.
These calculations are done accordingly for the other metrics using different stats and different weightings.
At the end of each season a player receives a season score, then finally scores from all 3 seasons are aggregated with recent years being valued more.

3.** Situational Impact**
Situational performance was analyzed to evaluate how players perform in high-leverage downs.
These situations often determine whether a defense gets off the field, making them particularly valuable for pass rushers.
Inside my Situation performance metric, not only do I calculate 3rd/4th down impact, but it also takes into account how many of a player's sacks are on 3rd and long. Getting sacks on 3rd and long is crucial; however, if most of your sacks come on obvious passing downs with time, then I don't find that to be a positive metric.

4. **Contract Estimation**
Players APY estimation was based on 4 important factors:
1. Your Tier class (based on final aggergate scoring)
2. Your Role designation
3. The approximate market midpoint APY of players in each tier
4. Then their Performance Z-Score relative to their tier
Based on those factors we are able to caluclate the estimated APY for each player then assign OverPaid,UnderPaid, and FairlyPaid tags for each player based on if their real contract was off by 5 Million.

5.) **Contract Analysis **
When graphing my finding I used different metrics to analyze the values of each players contract.
A.) Value Ratio = Estimated APY / Actual APY # Seperate Graphs Including and Excluding Rookie and Min. Salary Contracts
B.) Weighted Value Ratio = [(Estimated APY - Actual APY) / Sqrt(APY)] * (Final Agg Score / Avg Final Agg Score)

6. **Visual Analysis**
Taking into account the results I procceed to visualize my finding in different key graphics.
  A.) Pass Defense Score vs Run Defense Score
  B.) Situational Impact vs Overall Final Agg Score (Clutch Metric)
  C.) Scatter Plot of Estimated APY vs Actual APY : Indicating Market Efficiency 
  D.) MoneyBall metric of Overall Performance vs Estimated Pay Difference to find Overpaid Stars, Underpaid Stars, Replacement Players, and valuable depth pieces.
  E.) 3 Graphs indicating the best and worst contracts
        - Best and Worst Contracts according to Value Ratio (Including Rookie and Min. Salaries)
        - Best and Worst Contracts according to Value Ratio (Excluding Rookie and Min. Salaries)
        - Best and Worst Contracts according to Weighted Value Ratio



## Results & Visualizations

Below are the primary visualisations produced by the model.
Each chart highlights a different aspect of defensive line performance and contract efficiency.
### Pass Defense vs Run Defense Role Classification

This visualization helps classify defensive linemen into roles such as
designated pass rushers, run stoppers, and every-down defenders.

![Pass vs Run Defense](outputs/pass_vs_run.png)





Tools Used: Python, Pandas, NumPy, Matplotlib, Seaborn



**Limitations**
Several factors limit the precision of this contract valuation model:
Team scheme differences
Role-based responsibilities
Injury history and Age
Leadership and intangible contributions
Specific Contract timing and market inflation
The model should therefore be interpreted as a performance-based approximation of contract value, rather than an exact valuation.


**Conclusion**
This project demonstrates how data-driven analysis can uncover inefficiencies in NFL contract markets. By comparing player production with salary commitments, teams can better identify:
- undervalued contributors
- inefficient contracts
- opportunities for roster optimization
The methodology used here illustrates a simplified version of the performance valuation tools used in modern sports analytics and front-office decision making.



   


