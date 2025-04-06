from typing import List, Set, Dict
import time

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
    
    def num_edges(self) -> int:
        edges = 0
        seen = set()
        m = len(self.adj_matrix)
        n = len(self.adj_matrix[0])
        for i in range(m):
            for j in range(n):
                if self.adj_matrix[i][j] != 0 and (i,j) not in seen:
                    edges += 1
                    seen.add((i, j))
        return edges

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
        self.last_solve_time = 0.0 # keep track of solve time for benchmarks

        # create a set of unique virtual registers / variables.
        var_set: Set[str] = set()
        for point in self.points:
            for var in point.live_values:
                var_set.add(var)
        
        self.variables = sorted(list(var_set))
        self.graph = InterferenceGraph(self.variables)
    
    def build_interference_graph(self) -> None:
        """
        Construct the graph where each node is a virtual regsiter/variable
        and the edges represent a time-dependency, meaning both must be 
        allocated to distinct virtual registers.
        """
        for point in self.points:
            for i in range(len(point.live_values)):
                for j in range(i+1, len(point.live_values)):
                    var1 = point.live_values[i]
                    var2 = point.live_values[j]
                    if var1 != var2:
                        self.graph.add_edge(var1, var2)
    
    def greedy_coloring(self) -> Dict[str, int]:
        """
        The linear scan algorithm is greedy. 
        """
        start = time.time()
        self.build_interference_graph()
        colors: Dict[str, int] = {}
        k = self.reg_set.get_capacity()
        for var in self.variables:
            colors[var] = -1 # initially all variables are spilled
        for var in self.variables:
            neighbour_colors = set()
            for n in self.graph.get_neighbors(var):
                if colors[n] != -1:
                    neighbour_colors.add(colors[n])
            # find miniumum unique color not in neighbour_colors
            min_color = 0
            while min_color < k and min_color in neighbour_colors:
                min_color += 1

            if min_color < k:
                colors[var] = min_color
            else:
                colors[var] = -1 
        end = time.time()
        self.last_solve_time = end - start
        return colors

    def register_coloring(self, method: str = "greedy") -> Dict[str, int]:
        if method == "greedy":
            return self.greedy_coloring()
        elif method == "backtracking":
            return self.kempe_backtracking()
        else:
            raise ValueError(f"Unknown coloring method: {method}")
    
    def kempe_backtracking(self) -> Dict[str, int]:
        """
        Kempe backtracking is a variant of register coloring which goes as follows.
        First we count the indegree of each node in our interference graph. We take
        the node with the smallest in degree, remove it from the graph, decrement
        the in-degree of it's neighbours, and push it onto a stack.
        """ 
        start = time.time()
        self.build_interference_graph()
        k = self.reg_set.get_capacity()
        
        sorted_vars = sorted(self.variables, 
                             key=lambda var: self.graph.get_degree(var),
                             reverse=False)
        
        colors = {var: -1 for var in self.variables}
        best_colors = colors.copy()
        max_colored = 0
        
        def is_valid_color(var: str, color: int, current_colors: Dict[str, int]):
            # Closure for checking if a node is colorable as color
            for neighbor in self.graph.get_neighbors(var):
                if current_colors[neighbor] == color:
                    return False
            return True
        
        def backtrack(index: int, current_colors: Dict[str, int], colored_count: int):
            # Closure for backtracing
            nonlocal max_colored, best_colors
            if index == len(sorted_vars):
                if colored_count > max_colored:
                    max_colored = colored_count
                    best_colors = current_colors.copy()
                return
            
            var = sorted_vars[index]
            backtrack(index + 1, current_colors, colored_count)
            
            for color in range(k):
                if is_valid_color(var, color, current_colors):
                    current_colors[var] = color
                    backtrack(index + 1, current_colors, colored_count + 1)
                    current_colors[var] = -1  # Backtrack to try other options
        
        working_colors = colors.copy()
        backtrack(0, working_colors, 0)
        
        # Update colors with the best solution found
        colors.update(best_colors)
        colored_count = sum(1 for color in colors.values() if color != -1)
        spilled_count = len(self.variables) - colored_count
        print(f"Backtracking found a partial solution with {spilled_count} spilled variables.")
        print(f"Using {colored_count} of {k} available registers.")
        
        end = time.time()
        self.last_solve_time = end - start
        return colors

