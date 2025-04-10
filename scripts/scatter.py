import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

df = pd.read_csv('./bench.csv')

df['ProblemID'] = df.apply(
    lambda x: f"{x['NumVariables']}_{x['NumSpilled']}_{x['NumEdges']}", 
    axis=1
)

greedy_times = []
backtrack_times = []

for problem_id in df['ProblemID'].unique():
    problem_data = df[df['ProblemID'] == problem_id]
    
    if len(problem_data) != 2:
        continue
        
    greedy_row = problem_data[problem_data['Method'] == 'greedy']
    backtrack_row = problem_data[problem_data['Method'] == 'backtracking']
    
    if len(greedy_row) == 0 or len(backtrack_row) == 0:
        continue
        
    greedy_times.append(greedy_row['TimeToSolve'].values[0])
    backtrack_times.append(backtrack_row['TimeToSolve'].values[0])

plt.figure(figsize=(10, 8))
plt.scatter(greedy_times, backtrack_times, color='green', alpha=0.7)
plt.xlabel('Greedy Time (s)')
plt.ylabel('Backtracking Time (s)')
plt.title('Running Time Comparison')
plt.xscale('log')
plt.yscale('log')

min_time = min(min(greedy_times), min(backtrack_times))
max_time = max(max(greedy_times), max(backtrack_times))
plt.loglog([min_time, max_time], [min_time, max_time], 'k-')
plt.grid(True)

plt.tight_layout()
plt.savefig("./time_comparison.png")
