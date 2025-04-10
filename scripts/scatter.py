import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('./bench.csv')
df['ProblemID'] = df.apply(
    lambda x: f"{x['NumVariables']}_{x['NumSpilled']}_{x['NumEdges']}", 
    axis=1
)

greedy_times = []
backtrack_times = []
greedy_colors = []
backtrack_colors = []

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
    greedy_colors.append(greedy_row['MaxColorsUsed'].values[0])
    backtrack_colors.append(backtrack_row['MaxColorsUsed'].values[0])

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
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

plt.subplot(1, 2, 2)
plt.scatter(greedy_colors, backtrack_colors, color='green', alpha=0.7)
plt.xlabel('Greedy Max Colors')
plt.ylabel('Backtracking Max Colors')
plt.title('Max Colors Used Comparison')

max_colors = max(max(greedy_colors), max(backtrack_colors))
plt.plot([0, max_colors], [0, max_colors], 'k-')
plt.grid(True)

plt.tight_layout()
# plt.show()
plt.savefig("./color_scattern.pn")
