## CMPUT 366 Course Project

#### Abstract

Register allocation is problem in code generation which involves finding a mapping from live values at the point of a program into a finite set of physical hardware registers. The constraint on this problem imposes that no two live variables can occupy the smae register simeltaneously. If there are more live variables than physical registers, the program must "splil" values to memory, to ensure the correctness of the program. The register allocation is NP hard and reduces to a graph coloring problem. We use a constraint satisfaction solver to implement register allocation at a high level in python and record the timings for different heuristic variations.

#### Introduction

##### Problem Representation
The first task is to find a suitable representation for the problem input and output. In Sudoku, we used a simple string of 81 characters for a nine by nine grid, with periods representing empty values, and digits representing constant values. To represent the input for the register allocation we use the following format. A text file includes `K` lines of input, the first includes a single number `N`, the number of registers in computer, and each subsequent line is sequence of space separated strings denoting the live values at a particualr program point. 


```
6
v1                              # v1 is the only value live at point 1
v1 v5
v1 v5 v8
v1 v5 v8 v9 10                  # five values are live at point 4 
v1 v3 v5 v8 v9 v10 v11           
v1 v3 v3 v5 v8 v9 v10 v11       # more than values are live at point 6 than registers.
v3 v9 v10
v9
```

##### Input Program Generation
We approached the problem of generating interesting, well defined inputs to out reigster allocation problem with a simple python script. We pass in the register capacity and generate, in a pseudo-random fashion, a plausible sequence of points that could represent a program. Typically, live variables will accumulate in the scope of a program as the programmer declares variables. Then, at a particular point, many variables will become dead at once, as the program pops a lexical scope. For example, consider the following `RISCV` program, translated from some high level source code.

```
{
    let i = 5;
    let j = 6;
    {
        let z = i;
        let y = 3;
        let x = y + z * 3;
    }
    #let k = i + j; 
}
```

Which may translate as follows to a `RISCV` assembly

```

addi sp -4
addi sp -4
li r0 5;
li r1 6;
str r0 sp(0)
str r1 sp(4)

##```

We can observe the live ranges for each register with the following graph.

```

```

    
#### Implementing Graph Coloring (CSP)


#### Evaluation

