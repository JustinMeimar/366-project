import sys
import os
import csv
import argparse
from typing import List, Dict
from viz import visualize_interference_graph
from allocator import RegisterSet, ProgramPoint, Solver

def parse_input(path: str) -> tuple[RegisterSet, List[ProgramPoint]]:
    with open(path, "r") as input_file:
        n_reg = input_file.readline()
        r = RegisterSet(int(n_reg))
        program_points: List[ProgramPoint] = [] 
        for line in input_file.readlines():
            p = ProgramPoint() 
            for lv in line.strip('\r\n').strip().split(' '):
                p.add_live_value(lv)
            
            program_points.append(p)
        return (r, program_points)

def print_coloring(colors: Dict[str, int]) -> None:
    registers: Dict[int, List[str]] = {}
    spilled: List[str] = [] 
    for var, color in colors.items():
        if color == -1:
            spilled.append(var)
        else:
            if color not in registers:
                registers[color] = []
            registers[color].append(var)
    
    print("\nRegister Allocation Results:")
    for reg_num in sorted(registers.keys()):
        print(f"r{reg_num}: {', '.join(registers[reg_num])}") 
    if spilled:
        print(f"\nSpilled variables: {', '.join(spilled)}")
    else:
        print("\nNo variables needed to be spilled.")

def write_benchmark_stats(path: str,
                          method: str,
                          colors: Dict[str, int],
                          solver: Solver) -> None:
    """
    Write benchmark statistics to a CSV file
    """
    
    # Create header if file doesn't exist
    file_exists = os.path.isfile(path)
    
    # Calculate stats
    num_vars = len(colors)
    num_spilled = sum(1 for color in colors.values() if color == -1)
    spill_percentage = (num_spilled / num_vars) * 100 if num_vars > 0 else 0
    max_color = max([color for color in colors.values() if color != -1], default=-1) + 1
    num_edges = solver.graph.num_edges()
    
    with open(path, 'a', newline='') as csvfile:
        fieldnames = ['Method', 'NumVariables', 'NumSpilled', 'SpillPercentage', 
                     'MaxColorsUsed', 'NumEdges', 'TimeToSolve']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'Method': method,
            'NumVariables': num_vars,
            'NumSpilled': num_spilled,
            'SpillPercentage': f"{spill_percentage:.2f}",
            'MaxColorsUsed': max_color,
            'NumEdges': num_edges,
            'TimeToSolve': round(solver.last_solve_time, 5) if hasattr(solver, 'last_solve_time') else 'N/A'
        })
if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description='Register allocation solver')
    parser.add_argument('input_path', help='Path to the input file')
    parser.add_argument('method', choices=['greedy', 'backtracking'], 
                        help='Coloring method: greedy or backtracking')
    parser.add_argument('--viz', metavar='PATH', help='Path to save visualization')
    parser.add_argument('--benchmark', metavar='PATH', help='Path to save benchmark stats')
    
    args = parser.parse_args() 
    register_set, program_points = parse_input(args.input_path) 
    solver = Solver(register_set, program_points)
    coloring = solver.register_coloring(args.method)
    
    print("Running Test: ", args.input_path)
    if args.viz:
        # Create directory if it doesn't exist
        viz_dir = os.path.dirname(args.viz)
        if viz_dir and not os.path.exists(viz_dir):
            os.makedirs(viz_dir)
        visualize_interference_graph(solver.graph, coloring, args.viz)
    
    if args.benchmark:
        # Create directory if it doesn't exist
        benchmark_dir = os.path.dirname(args.benchmark)
        if benchmark_dir and not os.path.exists(benchmark_dir):
            os.makedirs(benchmark_dir)
        write_benchmark_stats(args.benchmark, args.method, coloring, solver)
    
    print(f"\nInterference Graph:")
    print(solver.graph)
    
    print(f"\nRegister Set:")
    print(register_set)
    
    print(f"\nProgram Points:")
    for point in program_points:
        print(point)
    
    print_coloring(coloring)
