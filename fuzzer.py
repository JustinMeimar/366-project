import random
import sys

def generate_test_case(output_path):
    # pick a random number for register capacity
    rc = random.randint(4, 16)
    
    # pick a random number of program points
    n_points = random.randint(6, 30)
    
    # create a pool of variable names (v1, v2, ..., vN)
    num_vars = rc + random.randint(1, 5)
    var_pool = [f"v{i+1}" for i in range(num_vars)]
    program_points = []
    
    # start with a single variable
    start_point = [random.choice(var_pool)]
    program_points.append(start_point)
    
    prev_point = start_point
    for _ in range(1, n_points):
        # copy previous live variables
        current_point = prev_point.copy()
        
        # add 0-2 new variables
        available_vars = [v for v in var_pool if v not in current_point]
        if available_vars and random.random() < 0.7:
            num_to_add = min(random.randint(1, 2), len(available_vars))
            current_point.extend(random.sample(available_vars, num_to_add))
        
        # remove 0-1 existing variables
        if current_point and random.random() < 0.4:
            current_point.remove(random.choice(current_point))
        
        # ensure at least one variable is live
        if not current_point:
            current_point = [random.choice(var_pool)]
        
        program_points.append(current_point)
        prev_point = current_point
    
    with open(output_path, "w") as output_file:
        output_file.write(f"{rc}\n")
        for point in program_points:
            output_file.write(" ".join(point) + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("script usage: python fuzzer.py <output_file>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_test_case(output_path)
    
    print(f"Test case generated and saved to {output_path}")

