# -*- coding: utf-8 -*-

#    PyDCG
#
#    A Python library for Discrete and Combinatorial Geometry.
#
#    Copyright (C) 2015 Ruy Fabila Monroy
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation version 2. 
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


"""Implementation of the basic geometric primitives"""

import random
import utilities
from utilities import cppWrapper

LEFT = -1
COLLINEAR = 0
RIGHT = 1

if utilities.__load_extensions:
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
    #print "recieved ", p
    p1 = [p[0], p[1] + 1]
    r=[]
    l=[]
    
    for q in points:
        if turn(p, p1, q) == RIGHT:
            r.append(q[:])
        elif turn(p, p1, q) == LEFT:
            l.append(q[:])
        else:
            if p[1] >= q[1]:
                l.append(q[:])
            else:
                r.append(q[:])

    l.sort(lambda v1, v2: turn(p, v1, v2))
    r.sort(lambda v1, v2: turn(p, v1, v2))

    if join:
        r.extend(l)

        if not checkConcave:
            return r

        concave = False
        i = 0
        for i in xrange(len(r)):
            if turn(r[i], p, r[(i + 1) % len(r)]) < 0:
                concave = True
                break
        if concave:
            start = (i + 1) % len(r)
            r = [r[(start + i) % len(r)][:] for i in xrange(len(r))]

        return r
    else:
        return (r, l)


def sort_around_point(p, points, join=True, speedup=False):
    """Sorts `points` around `p` in CCW order."""
    #TODO: This function does not exist in geometricbasicsCpp at the moment. It was moved to 
    #crossingCpp because of its dependence of 'pivote'. 
    return cppWrapper(sort_around_point_py,
                      None,
                      speedup,
                      [p],
                      [points],
                      p=p, points=points, join=join)


def __test_sort_around_point_versions(n=100, k=10000000): #TODO: check in ubuntu if the functions work, if so, delete this
    """Tests whether the two sort_around_point functions match"""
    pts = [[random.randint(-k, k), random.randint(-k, k)] for i in range(n)]
    p = [random.randint(-k, k), random.randint(-k, k)]
    # p=[0,0]
#    pts_1=sort_around_point_python(p,pts)
    pts_1 = sort_around_point(p, pts)
    pts_2 = sort_around_point(p, pts, speedup=True)
    j = 1
    print j
    while pts_1 == pts_2:
        pts = [[random.randint(-k, k), random.randint(-k, k)]
               for i in range(n)]
        # p=[0,0]
        p = [random.randint(-k, k), random.randint(-k, k)]
#        pts_1=sort_around_point_python(p,pts)
        pts_1 = sort_around_point(p, pts)
        pts_2 = sort_around_point(p, pts, speedup=True)
        j += 1
        print j
    return (p, pts)


def iterate_over_points(pts, f):
    """Takes a function and a point set as a parameter.
       It applies f(p,pts-p) for every point p in pts"""
    res = []
    tmp = [x[:] for x in pts[1:]]
    newVal = pts[0][:]
    for i in xrange(len(tmp)):
        res.append(f(newVal, tmp))
        newVal, tmp[i] = tmp[i][:], newVal[:]        
    res.append(f(newVal, tmp))
    return res


def general_position(pts, report=False):
    """Tests whether the point set is in general position or not.
       If report is set to True it return all triples of points not in general position"""
    def f(p, pts):
        triples = []
        tmp_pts = sort_around_point(p, pts)
        for i in xrange(len(tmp_pts) - 1):
            if turn(p, tmp_pts[i], tmp_pts[i + 1]) == COLLINEAR:
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