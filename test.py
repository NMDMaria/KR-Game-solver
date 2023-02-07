from copy import deepcopy
from queue import Queue

def neighbours(index, dimensions):
    result = []
    r, c = index // dimensions[0], index % dimensions[0]

    if r + 1 < dimensions[0]:
        result.append((r + 1) * dimensions[0] + c)
    if r - 1 >= 0:
        result.append((r - 1) * dimensions[0] + c)
    if c + 1 < dimensions[1]:
        result.append(r * dimensions[0] + c + 1)
    if c - 1 >= 0:
        result.append(r * dimensions[0] + c - 1)
    return result


def minConn(mat):
    idxX = [i for i in range(len(mat)) if mat[i] == '#']

    return idxX


def rec(mat, start, rest, explored, path):
    min = []
    if not rest:
        return path

    for val in rest:
        p = BFS_SP((5,5), mat, start, val, deepcopy(explored))
        if not p:
            return []
        cp = deepcopy(rest)
        cp.remove(val)
        dr = rec(mat, val, cp, explored + [start], path[:-1] + p)
        if min == [] or len(dr) < len(min):
            min = dr

    return min


def path(mat, l):
    minPath = []

    for index in range(len(l)):
        p = rec(mat, l[index], l[:index] + l[(index + 1):], [], [])
        if minPath == [] or len(minPath) > len(p):
            minPath = p

    return minPath


def BFS_SP(dimensions, mat, start, goal, explored=[]):
    q = Queue()
    q.put([start])
    if start == goal:
        return []

    while not q.empty():
        path = q.get()
        node = path[-1]

        if node not in explored:
            n = neighbours(node, dimensions)

            for neighbour in n:
                if mat[neighbour] == '1' or mat[neighbour] == '2':
                    continue
                if neighbour in explored:
                    continue
                new_path = list(path)
                new_path.append(neighbour)
                q.put(new_path)

                if neighbour == goal:
                    return new_path

            explored.append(node)

    return []


if __name__ == '__main__':
    mat = ['.','.', '1','1','1','.','#','.','1','#','2','2','.','.','.','2','2','#','.','.','#','2','.','.','.']

    i = minConn(mat)
    print(path(mat, i))
