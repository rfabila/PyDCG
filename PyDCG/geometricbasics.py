# -*- coding: utf-8 -*-
"""Implementation of the basic geometric primitives"""

import random
import utilities
from utilities import cppWrapper

LEFT = -1
COLLINEAR = 0
RIGHT = 1

if not utilities.__config['PURE_PYTHON']:
    import geometricbasicsCpp as gbCpp


def turn(p0, p1, p2):
    """Consider the walk form p0 to p1 to p2. Returns
        -1 if it is a turn to the left, 1 if it is to the right
        and 0 otherwise"""
    t = ((p2[0] - p0[0]) * (p1[1] - p0[1])) - \
        ((p1[0] - p0[0]) * (p2[1] - p0[1]))
    if t > 0:
        return RIGHT
    elif t < 0:
        return LEFT
    return COLLINEAR


def sorted(p, pts):
    """Checks whether the point set is sorted around p"""
    for i in xrange(len(pts) - 1):
        if turn(p, pts[i], pts[i + 1]) > 0:
            return False
    return True


def sort_around_point_py(p, points, join=True, checkConcave=True):
    """Python version of sort_around_point"""
    l = 0
    r = 0
    p1 = [p[0], p[1] + 1]

    for q in points:
        if turn(p, p1, q) == RIGHT:
            r += 1
        else:
            if turn(p, p1, q) == LEFT:
                l += 1
            else:
                if p[1] >= q[1]:
                    l += 1
                else:
                    r += 1

    r = [[0, 0] for i in range(r)]
    l = [[0, 0] for i in range(l)]
    ir = 0
    il = 0

    for q in points:
        if turn(p, p1, q) == RIGHT:
            r[ir] = q[:]
            ir += 1
        else:
            if turn(p, p1, q) == LEFT:
                l[il] = q[:]
                il += 1
            else:
                if p[1] >= 1[1]:
                    l[il] = q[:]
                    il += 1
                else:
                    r[ir] = q[:]
                    ir += 1

    l.sort(lambda v1, v2: turn(p, v1, v2))
    r.sort(lambda v1, v2: turn(p, v1, v2))

    if join:
        tpts = [[0, 0] for i in range(len(points))]
        for i in range(len(r)):
            tpts[i] = r[i][:]
        for j in range(len(l)):
            tpts[len(r) + j] = l[j][:]

        if not checkConcave:
            return tpts

        concave = False
        for i in range(len(tpts)):
            if turn(tpts[i], p, tpts[(i + 1) % len(tpts)]) < 0:
                concave = True
                break
        if concave:
            start = (i + 1) % len(tpts)
            tpts = [tpts[(start + i) % len(tpts)][:] for i in range(len(tpts))]

        return tpts
    else:
        return (r, l)


def sort_around_point(p, points, join=True, speedup=False):
    """Sorts `points` around `p` in CCW order."""
    name = 'sort_around_point'
    pyf = sort_around_point_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = gbCpp.sort_around_point
        
    return cppWrapper(name, pyf, cppf, speedup, p=p, points=points, join=join)


def __test_sort_around_point_versions(n=100, k=10000000):
    """Tests whether the two sort_around_point functions match"""
    pts = [[random.randint(-k, k), random.randint(-k, k)] for i in range(n)]
    p = [random.randint(-k, k), random.randint(-k, k)]
    # p=[0,0]
#    pts_1=sort_around_point_python(p,pts)
    pts_1 = sort_around_point(p, pts)
    pts_2 = sort_around_point(p, pts, speedup=True)
    j = 1
    print(j)
    while(pts_1 == pts_2):
        pts = [[random.randint(-k, k), random.randint(-k, k)]
               for i in range(n)]
        # p=[0,0]
        p = [random.randint(-k, k), random.randint(-k, k)]
#        pts_1=sort_around_point_python(p,pts)
        pts_1 = sort_around_point(p, pts)
        pts_2 = sort_around_point(p, pts, speedup=True)
        j = j + 1
        print j
    return (p, pts)


def iterate_over_points(pts, f):
    """Takes a function and a point set as a parameter.
       It applies f(p,pts-p) for every point p in pts"""
    res = []
    tmp = [x[:] for x in pts[1:]]
    for i in xrange(len(pts)):
        for j in xrange(i):
            tmp[j] = pts[j][:]
        for j in xrange(i + 1, len(pts)):
            tmp[j - 1] = pts[j][:]
        res.append(f(pts[i], tmp))
    return res


def general_position(pts, report=False):  # XXX: Isn't this O(n^3 logn) ?
    """Tests whether the point set is in general position or not.
       If report is set to True it return all triples of points not in general position"""
    def f(p, pts):
        triples = []
        tmp_pts = sort_around_point(p, pts)
        for i in xrange(len(tmp_pts) - 1):
            if turn(p, tmp_pts[i], tmp_pts[i + 1]) == 0:
                if report:
                    triples.append((p, tmp_pts[i], tmp_pts[i + 1]))
                else:
                    return False
        if report:
            return triples
        else:
            return True

    res = iterate_over_points(pts, f)
    if report:
        return res
    else:
        for x in res:
            if not x:
                return False
        return True