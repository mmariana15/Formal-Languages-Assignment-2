**Formal-Lenguages-Assigment 2**

**Members**
Sofia Velasquez
Luciana Pineda
Mariana Montoya Deza

**Class Number** 
S2666-0509

**Description**
Implementation of the Subset Construction algorithm in Python. The program converts a Non-Deterministic Finite Automaton (NFA) into an equivalent Deterministic Finite Automaton (DFA), following Kozen (1997), Lecture 6.
The program reads the automaton information from standard input and generates the corresponding DFA transition table.

**Programming Language:** 
Python 3

**Libraries:**
Python standard libraries (re, sys, collections, itertools). No external libraries are required.

**Execution**
To run the program, open a terminal in the project directory and execute:

python3 subset_construction.py < input.txt

Where input.txt contains the input cases with the NFA information.

The program also supports an optional --all argument to display all possible subsets of the original states, including unreachable states:

python3 subset_construction.py --all < input.txt

**Algorithm**
The Subset Construction algorithm converts an NFA into a DFA by representing each DFA state as a subset of the original NFA states.

The implementation starts with the initial states of the NFA and calculates new states by combining all possible transitions for each alphabet symbol.

A Breadth-First Search (BFS) using a queue is used to find all reachable subsets. Each subset becomes a state in the resulting DFA.

A DFA state is considered final if its subset contains at least one final state from the original NFA. The program then generates the transition table, indicating the initial and final states.
The empty set is represented by 0, as specified in the assignment.

**Reference**
Kozen, Dexter C. (1997). Automata and Computability. Springer-Verlag, Lecture 6.
