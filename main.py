import argparse
import sys
from typing import List, Dict, Set

class ProgramPoint:
    def __init__(self):
        self.live_values: List[str] = []
    
    def add_live_value(self, value: str) -> None:
        self.live_values.append(value)
    
    def __str__(self) -> str:
        if not self.live_values:
            return "- []"
        string = "- ["
        for v in self.live_values[:-1]:
            string += f"{v} " 
        string += self.live_values[-1]
        string += "]"
        return string

class Register:
    def __init__(self, name: str):
        self.name: str = name
        self.value: int = 0
        self.is_live: bool = False
    
    def get_is_live(self) -> bool:
        return self.is_live
        
    def __str__(self) -> str:
        return f"[{self.name}:{self.value}]"

class RegisterSet:
    def __init__(self, cap: int):
        self.cap: int = cap
        self.registers: List[Register] = [Register("r"+str(i)) for i in range(0, self.cap)]
        
    def get_capacity(self) -> int:
        return self.cap
    
    def __str__(self) -> str:
        string = "" 
        for r in self.registers:
            string += f"- {str(r)}\n"
        return string

class InterferenceGraph:
    def __init__(self, universe_size: int):
        self.adj_matrix: List[List[int]] = []
        for i in range(universe_size):
            row = [0 for _ in range(universe_size)]
            self.adj_matrix.append(row)
    
    def add_edge(self, i: int, j: int) -> None:
        self.adj_matrix[i][j] = 1
        self.adj_matrix[j][i] = 1
    
    def __str__(self) -> str:
        string = ""
        for row in self.adj_matrix:
            string += str(row)
            string += "\n"
        return string

class Solver:
    def __init__(self, reg_set: RegisterSet, points: List[ProgramPoint]):
        self.reg_set: RegisterSet = reg_set 
        self.points: List[ProgramPoint] = points
        
        # Get unique variables
        self.variables: List[str] = []
        var_set: Set[str] = set()
        for point in self.points:
            for var in point.live_values:
                var_set.add(var)
        self.variables = list(var_set)
        
        # Create interference graph
        self.graph: InterferenceGraph = InterferenceGraph(len(self.variables))
    
    def build_interference_graph(self) -> None:
        # For each program point
        for point in self.points:
            # All variables at this point interfere with each other
            for i, var1 in enumerate(point.live_values):
                for j, var2 in enumerate(point.live_values):
                    if i != j:
                        idx1 = self.variables.index(var1)
                        idx2 = self.variables.index(var2)
                        self.graph.add_edge(idx1, idx2)
    
    def register_coloring(self) -> Dict[str, int]:
        self.build_interference_graph()
        # Assign colors (registers) to variables
        colors: Dict[str, int] = {}
        for var in self.variables:
            colors[var] = 0
        print(self.graph)
        return colors
    
def parse_input(path: str) -> tuple[RegisterSet, List[ProgramPoint]]:
    with open(path, "r") as input_file:
        n_reg = input_file.readline()
        r = RegisterSet(int(n_reg))
        program_points: List[ProgramPoint] = [] 
        for line in input_file.readlines():
            p = ProgramPoint() 
            for lv in line.strip('\r\n').split(' '):
                p.add_live_value(lv)
            
            program_points.append(p)
        return (r, program_points)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <PATH_TO_INPUT>")
        sys.exit(1)
    path = sys.argv[1]
    register_set, program_points = parse_input(path)
    
    solver = Solver(register_set, program_points)
    coloring = solver.register_coloring()
    
    print(register_set)
    for point in program_points:
        print(point)
