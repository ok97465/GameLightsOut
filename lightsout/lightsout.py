"""Generate Lights Out puzzle.

Ref: https://github.com/pmneila/Lights-Out
"""
# Standard library imports
from operator import add
from itertools import chain, combinations
from functools import reduce

# Third party imports
import numpy as np
from numpy import eye, hstack, vectorize, vstack, int32
from numpy.core.numeric import array, ndarray, where, zeros
from numpy.random import randint


class GF2(object):
    """Galois field GF(2).

    Ref: https://github.com/pmneila/Lights-Out
    """

    def __init__(self, a=0):
        self.value = int(a) % 2

    def __add__(self, rhs):
        return GF2(self.value + GF2(rhs).value)

    def __mul__(self, rhs):
        return GF2(self.value * GF2(rhs).value)

    def __sub__(self, rhs):
        return GF2(self.value - GF2(rhs).value)

    def __truediv__(self, rhs):
        return GF2(self.value / GF2(rhs).value)

    def __repr__(self):
        return str(self.value)

    def __eq__(self, rhs):
        if isinstance(rhs, GF2):
            return self.value == rhs.value
        return self.value == rhs

    def __le__(self, rhs):
        if isinstance(rhs, GF2):
            return self.value <= rhs.value
        return self.value <= rhs

    def __lt__(self, rhs):
        if isinstance(rhs, GF2):
            return self.value < rhs.value
        return self.value < rhs

    def __int__(self):
        return self.value

    def __long__(self):
        return self.value


GF2array = vectorize(GF2)


def powerset(iterable):
    """Calculate power set.

    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    Ref: https://github.com/pmneila/Lights-Out
    """
    s = list(iterable)
    return chain.from_iterable(
        combinations(s, r) for r in range(len(s) + 1))


class ManageLightsOutPuzzle(object):
    """Manage Lights Out Puzzle."""

    def __init__(self):
        self.n_lights_1axis = 0
        self.mat_inv = array([])
        self.mat_null = array([])
        self.mat_puzzle = array([])
        self.mat_solution = array([])

    @staticmethod
    def state_transition_matrix_lightsout(n_lights_1axis):
        """Calculate state trasition matrix of light out."""
        matrix = zeros((n_lights_1axis * n_lights_1axis,
                        n_lights_1axis * n_lights_1axis))

        for idx_row in range(1, n_lights_1axis + 1):
            for idx_col in range(1, n_lights_1axis + 1):
                vector = zeros((n_lights_1axis + 2, n_lights_1axis + 2))
                vector[idx_row - 1, idx_col + 0] = 1
                vector[idx_row + 1, idx_col + 0] = 1
                vector[idx_row + 0, idx_col + 0] = 1
                vector[idx_row + 0, idx_col + 1] = 1
                vector[idx_row + 0, idx_col - 1] = 1
                vector = vector[1:n_lights_1axis + 1, 1:n_lights_1axis + 1]

                matrix[(idx_row - 1) * n_lights_1axis
                       + (idx_col - 1), :] = vector.ravel()

        return matrix

    @staticmethod
    def inv_by_gauss_elimination(mat):
        """Caculate inverse matrix by gauss elimination.

        Parameters
        ----------
        mat : ndarray
            matrix.

        Returns
        -------
        mat_inv : ndarray
            inverse matrix.
        mat_null : ndarray
            null space matrix.

        """
        n_row, n_col = mat.shape

        if n_row != n_col:
            raise ValueError("n_row and n_col are different.")

        data = GF2array(hstack([mat, eye(n_row)]))

        n_null_dim = 0
        mat_null = array([])

        # Row echelon form
        for idx_row_src in range(n_row - 1):
            idx_pivot_candidate = where(data[idx_row_src:, idx_row_src] == 1)[
                0]

            if len(idx_pivot_candidate) > 0:
                idx_pivot = idx_pivot_candidate[0] + idx_row_src
            else:
                n_null_dim += 1
                continue

            if idx_pivot != idx_row_src:
                tmp = data[idx_row_src, :].copy()
                data[idx_row_src, :] = data[idx_pivot, :]
                data[idx_pivot, :] = tmp

            for idx_row_dst in range(idx_row_src + 1, n_row):
                data[idx_row_dst, :] += (data[idx_row_src, :]
                                         * data[idx_row_dst, idx_row_src])

        if np.sum(data[-1, :n_col]) == 0:
            n_null_dim += 1

        # inverse matrix
        for idx_row_src in range(n_row - 1, 0, -1):
            for idx_row_dst in range(idx_row_src - 1, -1, -1):
                data[idx_row_dst, :] += (data[idx_row_src, :]
                                         * data[idx_row_dst, idx_row_src])

        # Find Null space
        if n_null_dim > 0:
            mat_diag = data[:, :n_col]
            mat_null = vstack(
                [mat_diag[:n_row - n_null_dim, -n_null_dim:],
                 GF2array(eye(n_null_dim))])

        mat_inv = data[-n_row:, -n_col:]

        return mat_inv, mat_null

    @staticmethod
    def check_solvable(lights_mat, mat_null):
        """Check if the problem is solved.

        Parameters
        ----------
        lights_mat : ndarray
            matrix of lightout problem.
        mat_null : ndarray
            null space matrix.

        Returns
        -------
        is_solvable: bool
            return True if lights_mat is solvable.

        """
        is_solvable = True

        if len(mat_null) > 0:
            ret = np.sum((int32(lights_mat.ravel()) @ int32(mat_null)) % 2)
            if ret != 0:
                is_solvable = False

        return is_solvable

    def new_puzzle(self, n_lights_1axis):
        """Generate New Puzzle."""
        if self.n_lights_1axis != n_lights_1axis:
            self.n_lights_1axis = n_lights_1axis
            state_mat = self.state_transition_matrix_lightsout(n_lights_1axis)
            (self.mat_inv,
             self.mat_null) = self.inv_by_gauss_elimination(state_mat)

        self.mat_puzzle = randint(0, 2, size=(n_lights_1axis, n_lights_1axis))
        while (not self.check_solvable(self.mat_puzzle, self.mat_null)
               or np.sum(self.mat_puzzle) == 0):
            self.mat_puzzle = randint(0, 2,
                                      size=(n_lights_1axis, n_lights_1axis))

        self.calculate_solution()

    def calculate_solution(self):
        """Calculate solution."""
        n_lights = self.n_lights_1axis
        solution_1st = (int32(self.mat_inv) @ int32(self.mat_puzzle.ravel()))
        solution_1st %= 2

        # Given a solution, we can find more valid solutions
        # adding any combination of the null vectors.
        # Find the solution with the minimum number of 1's.
        # Ref: https://github.com/pmneila/Lights-Out
        solutions = [(solution_1st + reduce(add, nvs, 0)) % 2 for nvs in
                     powerset(int32(self.mat_null.T))]
        solution_final = min(solutions, key=lambda x: x.sum())
        # print([x.sum() for x in solutions])

        self.mat_solution = solution_final.reshape(n_lights, n_lights)

    def count_1_of_solution(self):
        """Count 1 of solution."""
        return self.mat_solution.sum()
