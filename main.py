import argparse
import sys

class ProgramPoint:
    def __init__(self):
        self.live_values = []
    
    def add_live_value(self, value):
        self.live_values.append(value)
    
    def __str__(self):
        string = "- ["
        for v in self.live_values[0:-1]:
            string += f"{v} " 
        string += self.live_values[-1]
        string += "]"
        return string

class Register:
    def __init__(self, name):
        self.name = name
        self.value = 0

    def __str__(self):
        return f"[{self.name}:{self.value}]"

class RegisterSet():
    def __init__(self, cap):
        self.cap = cap  # default 4
        self.registers = [Register("r"+str(i)) for i in range(0, self.cap)]

    def get_capacity(self) -> int:
        return self.cap
    
    def __str__(self):
        string = "" 
        for r in self.registers:
            string += f"- {str(r)}\n"
        return string

def parse_input(path):
    """

    """
    with open(path, "r") as input_file:
        n_reg = input_file.readline()
        r = RegisterSet(int(n_reg))
        program_points = [] 
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
        
    print(register_set)
    for point in program_points:
        print(point)

