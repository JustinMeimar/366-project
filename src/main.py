import sys
import os
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: main.py <PATH_TO_INPUT> <COLORING_METHOD>")
        print("COLORING_METHOD can be 'greedy' or 'backtracking'")
        sys.exit(1)
    
    input_path = sys.argv[1]
    method = sys.argv[2].lower()

    if method not in ["greedy", "backtracking"]:
        print("COLORING_METHOD must be 'greedy' or 'backtracking'")
        sys.exit(1)
    
    register_set, program_points = parse_input(input_path)
    
    solver = Solver(register_set, program_points)
    coloring = solver.register_coloring(method)
    
    if "--viz" in sys.argv:
        num_files = len(os.listdir("./plots")) / 2
        visualize_interference_graph(solver.graph, coloring,
                                     f"plots/coloring-{method}-{num_files}.png")
    
    if "--benchmark" in sys.argv:
        pass

    print(f"\nInterference Graph:")
    print(solver.graph)
    
    print(f"\nRegister Set:")
    print(register_set)
    
    print(f"\nProgram Points:")
    for point in program_points:
        print(point)
    
    print_coloring(coloring)

