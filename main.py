import argparse
import sys

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
    
    with open(path, "r") as input_file:
        n_reg = input_file.readline()
        print("n: ", n_reg)
        r = RegisterSet(int(n_reg))
        for line in input_file.readlines():
            print(line)
    
if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: main.py <PATH_TO_INPUT>")
        sys.exit(1)

    path = sys.argv[1]
    parse_input(path)
        

    
