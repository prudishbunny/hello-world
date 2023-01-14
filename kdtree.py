import time
from collections import namedtuple
from typing import List

import matplotlib.pyplot as plt


class Point(namedtuple("Point", "x y")):
    def __repr__(self) -> str:
        return f'Point{tuple(self)!r}'


class Rectangle(namedtuple("Rectangle", "lower upper")):
    def __repr__(self) -> str:
        return f'Rectangle{tuple(self)!r}'

    def is_contains(self, p: Point) -> bool:
        return self.lower.x <= p.x <= self.upper.x and self.lower.y <= p.y <= self.upper.y


class Node(namedtuple("Node", "location left right")):
    """
    location: Point
    left: Node
    right: Node
    """

    def __repr__(self):
        return f'{tuple(self)!r}'


class KDTree:
    """k-d tree"""

    # initialize the data structure
    def __init__(self):
        self._root = None
        self._n = 0

    def insert(self, p: List[Point]):
        """insert a list of points"""
        if p == []: return None
        k = len(p[0])  # dimension  k
        currentd = 0  # current dimension

        # recursion
        def buildtree(points, currentd):
            if points == []: return None
            points.sort(key=lambda x: x[currentd])  # sort the points by current dimension
            median = len(points) // 2
            currentd = (currentd + 1) % k  # next dimension
            root = Node(points[median], buildtree(points[:median], currentd),
                        buildtree(points[median + 1:], currentd))  # create a new tree node
            self._n += 1
            return root  # return root of the built tree

        self._root = buildtree(p, currentd)

    def range(self, rectangle: Rectangle) -> List[Point]:
        """range query"""
        if not self._root: return []

        # recursion function
        def findwithin(root, currentd):

            if not root: return []
            # a leaf
            if not root.left and not root.right:
                if rectangle.is_contains(root.location):
                    return [root.location]
                else:
                    return []
            # not a leaf
            result = []
            if rectangle.is_contains(root.location):
                result.append(root.location)

            if root.location[currentd] < rectangle.lower[currentd]:
                result += findwithin(root.right, (currentd + 1) % 2)
            elif root.location[currentd] > rectangle.upper[currentd]:
                result += findwithin(root.left, (currentd + 1) % 2)
            else:
                result += findwithin(root.left, (currentd + 1) % 2)
                result += findwithin(root.right, (currentd + 1) % 2)
            return result

        return findwithin(self._root, 0)

    def nearest(self, point: Point) -> Point:
        k = len(point)  # k: dimension

        if not self._root: return None
        self.radius = 99999999999  # the shortest distance
        self.nearestneighbor = None  # the nearest neighbor

        def distance(p1, p2):
            return ((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2) ** 0.5

        # recursion
        def nearest_neighbor(root, currentd):
            if not root: return

            # find the leaf
            if root.left or root.right:
                nextd = (currentd + 1) % k
                if root.left and point[currentd] < root.location[currentd]:
                    nearest_neighbor(root.left, nextd)
                else:
                    nearest_neighbor(root.right, nextd)

            # move back
            tmpdis = distance(root.location, point)
            if tmpdis < self.radius:
                self.radius = tmpdis
                self.nearestneighbor = root.location

            # the circle intersects with the other subtree
            if abs(point[currentd] - root.location[currentd]) < self.radius:
                nextd = (currentd + 1) % k
                # search in the other side
                if root.left and point[currentd] >= root.location[currentd]:
                    nearest_neighbor(root.left, nextd)
                elif root.right and point[currentd] < root.location[currentd]:
                    nearest_neighbor(root.right, nextd)

        nearest_neighbor(self._root, 0)  # starting dimension 0
        return self.nearestneighbor


def nearest_test():
    points = [Point(7, 2), Point(5, 4), Point(9, 6), Point(4, 7), Point(8, 1), Point(2, 3)]
    kd = KDTree()
    kd.insert(points)
    result1 = kd.nearest(Point(11, 10))
    assert result1 == Point(9, 6)
    result2 = kd.nearest(Point(4, 4))
    assert result2 == Point(5, 4)


def range_test():
    points = [Point(7, 2), Point(5, 4), Point(9, 6), Point(4, 7), Point(8, 1), Point(2, 3)]  # a point set
    kd = KDTree()
    kd.insert(points)
    result = kd.range(Rectangle(Point(0, 0), Point(6, 6)))
    assert sorted(result) == sorted([Point(2, 3), Point(5, 4)])

def performance_test():
    points = [Point(x, y) for x in range(1000) for y in range(1000)]

    lower = Point(500, 500)
    upper = Point(504, 504)
    rectangle = Rectangle(lower, upper)

    start = int(round(time.time() * 1000))
    result1 = [p for p in points if rectangle.is_contains(p)]
    end = int(round(time.time() * 1000))
    print(f'Naive method: {end - start}ms')
    time1 = end - start

    kd = KDTree()
    kd.insert(points)
    start = int(round(time.time() * 1000))
    result2 = kd.range(rectangle)
    end = int(round(time.time() * 1000))
    print(f'K-D tree: {end - start}ms')
    time2 = end - start

    assert sorted(result1) == sorted(result2)

    plt.figure()
    plt.title("Time performance")
    plt.bar(["Naive", "KD-Tree"], [time1, time2])
    plt.show()


if __name__ == '__main__':
    nearest_test()
    range_test()
    performance_test()
