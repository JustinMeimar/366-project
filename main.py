import sys
from typing import List, Dict, Set

class ProgramPoint:
    """
    Represents the live variables, or live virutal registers, at a given point
    in the program.
    """
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
    """
    Represents the physical, finite resource of a hardware register.
    """
    def __init__(self, name: str):
        self.name: str = name
        self.value: int = 0
        self.is_live: bool = False
    
    def get_is_live(self) -> bool:
        return self.is_live
        
    def __str__(self) -> str:
        return f"[{self.name}:{self.value}]"

class RegisterSet:
    """
    A set of registers. The goal is to allocate as many live variables, or virtual
    registers into the register set at once.
    """
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
    """
    Represents, in an adjacency matrix format, the liveness dependencies between
    all virtual registers. An edge means that two virtual registers must be in 
    different physical registers, at some point in time.
    """
    def __init__(self, variables: List[str]):
        self.variables = variables
        self.size = len(variables)
        self.var_to_index = {var: i for i, var in enumerate(variables)}
        self.adj_matrix: List[List[int]] = []
        for _ in range(self.size):
            row = [0 for _ in range(self.size)]
            self.adj_matrix.append(row)
    
    def add_edge(self, var1: str, var2: str) -> None:
        if var1 == var2:
            return 
        i = self.var_to_index[var1]
        j = self.var_to_index[var2]
        self.adj_matrix[i][j] = 1
        self.adj_matrix[j][i] = 1
    
    def get_neighbors(self, var: str) -> List[str]:
        idx = self.var_to_index[var]
        neighbors = []
        for i, conflicts in enumerate(self.adj_matrix[idx]):
            if conflicts == 1:
                neighbors.append(self.variables[i])
        return neighbors
    
    def get_degree(self, var: str) -> int:
        idx = self.var_to_index[var]
        return sum(self.adj_matrix[idx])
    
    def __str__(self) -> str:
        return "\n".join(str(row) for row in self.adj_matrix)

class Solver:
    """
    Class that can either implement greedy or backtracking solution to 
    the register coloring problem.
    """
    def __init__(self, reg_set: RegisterSet, points: List[ProgramPoint]):
        self.reg_set: RegisterSet = reg_set 
        self.points: List[ProgramPoint] = points
        self.variables: List[str] = []
        var_set: Set[str] = set()
        for point in self.points:
            for var in point.live_values:
                var_set.add(var)
        self.variables = list(var_set)
        self.graph = InterferenceGraph(self.variables)
    
    def build_interference_graph(self) -> None:
        for point in self.points:
            for i in range(len(point.live_values)):
                for j in range(i+1, len(point.live_values)):
                    var1 = point.live_values[i]
                    var2 = point.live_values[j]
                    if var1 != var2:
                        self.graph.add_edge(var1, var2)
    
    def greedy_coloring(self) -> Dict[str, int]:
        """
        The greedy algorithm will find the virtual register with the highest
        in degree and allocate it first. This is a heuristic for allocating
        the most constrained variables first. It does not always produce the
        optimal coloring because two highly-constrained variables may in-fact
        be disjoint in liveness, and therefore can use the same register.
        """
        self.build_interference_graph()
        k = self.reg_set.get_capacity()
        sorted_vars = sorted(
            self.variables, 
            key=lambda var: self.graph.get_degree(var), 
            reverse=True
        )
        colors: Dict[str, int] = {}
        for var in self.variables:
            colors[var] = -1
        for var in sorted_vars:
            neighbor_colors = set()
            for neighbor in self.graph.get_neighbors(var):
                if colors[neighbor] != -1:
                    neighbor_colors.add(colors[neighbor])
            color = 0
            while color < k and color in neighbor_colors:
                color += 1
     
            if color >= k:
                print(f"Warning: Not enough registers, need to spill {var}")
            else:
                colors[var] = color
        
        return colors

    def kempe_backtracking(self) -> Dict[str, int]:
        """
        Kempe backtracking is a variant of register coloring which goes as follows.
        First we count the indegree of each node in our interference graph. We take
        the node with the smallest in degree, remove it from the graph, decrement
        the in-degree of it's neighbours, and push it onto a stack. We do so continu
        """
 
        self.build_interference_graph()
        k = self.reg_set.get_capacity()
        
        sorted_vars = sorted(self.variables, 
            key=lambda var: self.graph.get_degree(var), 
            reverse=True
        )
         
        print(f"Vars sorted by degree: {sorted_vars}")
        colors = {}
        for var in self.variables:
            colors[var] = -1
            
        best_solution = {"colored_count": 0, "colors": colors.copy()}
        
        max_degree = max(self.graph.get_degree(var) for var in self.variables) if self.variables else 0
        min_colors_needed = min(max_degree + 1, len(self.variables))
        
        max_colorable = min(k, len(self.variables))
        
        def backtrack(index: int, current_colors: Dict[str, int], colored_count: int):
            if colored_count > best_solution["colored_count"]:
                best_solution["colored_count"] = colored_count
                best_solution["colors"] = current_colors.copy()
                if colored_count == max_colorable:
                    return True
                    
            if index == len(sorted_vars):
                return False
            
            current_var = sorted_vars[index]
            remaining_vars = len(sorted_vars) - index
            if colored_count + remaining_vars <= best_solution["colored_count"]:
                return False
                
            neighbor_colors = set()
            for neighbor in self.graph.get_neighbors(current_var):
                if current_colors[neighbor] != -1:
                    neighbor_colors.add(current_colors[neighbor])
            
            for color in range(k):
                if color not in neighbor_colors:
                    next_colors = current_colors.copy()
                    next_colors[current_var] = color
                    if backtrack(index + 1, next_colors, colored_count + 1):
                        return True
            if backtrack(index + 1, current_colors.copy(), colored_count):
                return True 
            return False
        backtrack(0, colors.copy(), 0)
        
        result_colors = best_solution["colors"]
        
        colored_count = sum(1 for color in result_colors.values() if color != -1)
        if colored_count == 0:
            print("Backtracking could not color any variables.")
        elif colored_count < len(self.variables):
            print(f"Backtracking found a partial solution with {len(self.variables) - colored_count} spilled variables.")
            print(f"Using {colored_count} of {k} available registers.")
        else:
            print("Backtracking found a complete solution!")
            
        return result_colors
 
    def register_coloring(self, method: str = "greedy") -> Dict[str, int]:
        if method == "greedy":
            return self.greedy_coloring()
        elif method == "backtracking":
            return self.kempe_backtracking()
        else:
            raise ValueError(f"Unknown coloring method: {method}")

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
    
    path = sys.argv[1]
    method = sys.argv[2].lower()
    
    if method not in ["greedy", "backtracking"]:
        print("COLORING_METHOD must be 'greedy' or 'backtracking'")
        sys.exit(1)
    
    register_set, program_points = parse_input(path)
    
    solver = Solver(register_set, program_points)
    coloring = solver.register_coloring(method)
    
    print(f"\nInterference Graph:")
    print(solver.graph)
    
    print(f"\nRegister Set:")
    print(register_set)
    
    print(f"\nProgram Points:")
    for point in program_points:
        print(point)
    
    print_coloring(coloring)

