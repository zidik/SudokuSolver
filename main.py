__author__ = 'Mark'

from sudoku_solver import SudokuSolver, NoSolutionFound


def main():
    #List of puzzles to solve
    puzzle_files = ["puzzle.txt", "puzzle2.txt", "puzzle3.txt", "puzzle4.txt"]
    print("Loading puzzles.")
    puzzles = []
    puzzles.append(SudokuSolver.empty_puzzle())
    for path in puzzle_files:
        try:
            puzzle = SudokuSolver.fromfile(path)
        except (NoSolutionFound, FileNotFoundError) as e:
            print(e)
        else:
            puzzles.append(puzzle)
    print("Puzzles loaded.\n")

    print("Starting to solve puzzles:")
    solver = SudokuSolver()
    for puzzle in puzzles:
        solver.puzzle = puzzle
        print("Trying to solve this sudoku puzzle:")
        print(solver.puzzle)
        try:
            solver.solve()
        except NoSolutionFound:
            print("There is no solution for this puzzle!")
        else:
            print("Solution found!")
            print(solver.solution)

if __name__ == '__main__':
    main()