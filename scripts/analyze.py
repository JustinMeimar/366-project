import pandas as pd
import numpy as np
import sys

def analyze_methods(csv_file, output_file):
    df = pd.read_csv(csv_file)
    
    methods = df['Method'].unique()
    
    results = []
    
    for method in methods:
        method_df = df[df['Method'] == method]
        
        avg_runtime = method_df['TimeToSolve'].mean()
        std_runtime = method_df['TimeToSolve'].std()
        avg_spilled = method_df['NumSpilled'].mean()
        avg_max_spilled = method_df['MaxColorsUsed'].mean()
        
        results.append({
            'Method': method,
            'AvgRuntime': avg_runtime,
            'StdDevRuntime': std_runtime,
            'AvgSpilled': avg_spilled,
            'AvgMaxSpilled': avg_max_spilled
        })
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    
    print(f"Results written to {output_file}")

if __name__ == "__main__":
    analyze_methods(sys.argv[1], "results.csv")
