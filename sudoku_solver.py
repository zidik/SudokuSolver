__author__ = 'Mark'
from copy import deepcopy

class SudokuSolver:
    def __init__(self, puzzle=None):
        self.puzzle = puzzle if (puzzle is not None) else SudokuPuzzle(SudokuPuzzle.empty())
        self.solution = None

    def solve(self):
        self.solution = self.solve_rec(self.puzzle)

    @classmethod
    def fromfile(cls, path):
        try:
            return SudokuPuzzle(SudokuPuzzle.fromfile(path))
        except SudokuException as e:
            print("caught SudokuException:", e)
            raise NoSolutionFound("This sudoku is invalid. ({})".format(path))


    @classmethod
    def empty_puzzle(cls):
        return SudokuPuzzle()

    @staticmethod
    def solve_rec(puzzle):
        """
        Depth-first search for solution
        :param puzzle: current puzzle state
        :return: solved puzzle
        :raise: NoSolutionFound when no solution was not found in this branch
        """
        if puzzle.is_solved:
            solution = puzzle
        else:
            chosen_cell = puzzle.cell_with_fewest_possibilities
            possible_values = puzzle.get_cell_value(*chosen_cell)
            for value in possible_values:
                new_puzzle = deepcopy(puzzle)
                assert (isinstance(new_puzzle, SudokuPuzzle)) #For Pycharm
                new_puzzle.set_cell_value(*chosen_cell, value=value)
                try:
                    new_puzzle.propagate_constraints()
                except SudokuException:
                    pass  # This puzzle does not have solution
                else:
                    try:
                        solution = SudokuSolver.solve_rec(new_puzzle)
                    except NoSolutionFound:
                        pass # No solution found, continue search
                    else:
                        break #We have found a solution -> break and return
            else:
                raise NoSolutionFound("Could not find solution")

        return solution


class NoSolutionFound(StopIteration):
    pass


class SudokuPuzzle:
    @classmethod
    def fromfile(cls, path):
        with open(path, "r") as f:
            lines = f.readlines()
        input_data = [line.strip().split() for line in lines]
        return input_data

    @classmethod
    def empty(cls, shape=(9, 9)):
        input_data = [['-' for _ in range(shape[0])] for _ in range(shape[1])]
        return input_data

    @property
    def is_solved(self):
        return all([isinstance(element, int) for row in self._contents for element in row])

    @property
    def cell_with_fewest_possibilities(self):
        min_len = None
        chosen_cell = None, None
        for row_no, row in enumerate(self._contents):
            for col_no, element in enumerate(row):
                try:
                    length = len(element)
                except TypeError:
                    #Cell does not contain a list -> This cell is fully defined
                    pass
                else:
                    if min_len is None or length < min_len:
                        min_len = length
                        chosen_cell = col_no, row_no
        if min_len is None:
            raise ValueError("No suitable cell found")
        return chosen_cell

    def __init__(self, input_data=None, autopropagate=False):
        if input_data is None:
            input_data = SudokuPuzzle.empty()
        self._contents = [[list(range(1, 9+1)) for elem in row] for row in input_data]
        for row_no, row in enumerate(input_data):
            for col_no, value in enumerate(row):
                if value != '-':
                    self.set_cell_value(col_no, row_no, int(value), autopropagate)

    def __str__(self):
        ret_string = ""
        for row_no, row in enumerate(self._contents):
            for cell_no, cell in enumerate(row):
                try:
                    len(cell)
                except TypeError:
                    ret_string += str(cell)
                else:
                    ret_string += "."
                ret_string += " "

                if cell_no % 3 == 2 and cell_no != 8:
                    ret_string += "|"

            ret_string += "\n"
            if row_no % 3 == 2 and row_no != 8:
                ret_string += "------+------+------\n"
        return ret_string

    def __repr__(self):
        output_string = ""
        for row in self._contents:
            output_string += str(row) + "\n"
        return output_string

    def get_cell_value(self, col, row):
        return self._contents[row][col]

    def set_cell_value(self, col, row, value, autopropagate=False):
        try:
            len(self._contents[row][col])
        except TypeError:
            #This does not contain a list => this cell already has a final value assigned.
            if self._contents[row][col] != value:
                raise SudokuException("Tried to assign a new value to already defined cell.\n "
                                 "row:{} col:{} current:{} new:{}".format(row, col, self._contents[row][col], value))
            return

        if value in self._contents[row][col]:
            self._contents[row][col] = value
        else:
            raise SudokuException("Unable to set cell {},{} to value {}.".format(col, row, value))
        for unit in self.get_units(col, row):
            for u_col, u_row in unit:
                try:
                    self._contents[u_row][u_col].remove(value)
                except (AttributeError, ValueError):
                    pass
                else:
                    #Check if there are any options left after removal.
                    if len(self.get_cell_value(u_col, u_row))==0:
                        raise SudokuException("Cell {},{} does not have any valid values left.".format(col, row))
                    if autopropagate:
                        u_value = self.get_cell_value(u_col, u_row)
                        if len(u_value) == 1:
                            self.set_cell_value(u_col, u_row, u_value[0], autopropagate)

    def propagate_constraints(self):
        changes_made = True
        while changes_made:
            changes_made = False
            for row_no, row in enumerate(self._contents):
                for col_no, element in enumerate(row):
                    try:
                        length = len(element)
                    except TypeError:
                        pass
                    else:
                        if length == 1:
                            self.set_cell_value(col_no, row_no, element[0], False)
                            changes_made = True

    def get_units(self, col, row):
        col_range = range(len(self._contents[row]))
        row_range = [row]
        row_unit = self.cross(col_range, row_range)

        col_range = [col]
        row_range = range(len(self._contents))
        col_unit = self.cross(col_range, row_range)

        start_col = (col//3)*3
        start_row = (row//3)*3
        col_range = range(start_col, start_col+3)
        row_range = range(start_row, start_row+3)
        box_unit = self.cross(col_range, row_range)
        return row_unit, col_unit, box_unit

    @staticmethod
    def cross(a, b):
        return [(e_a, e_b) for e_a in a for e_b in b]



class SudokuException(ValueError):
    pass