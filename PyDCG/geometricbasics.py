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

import utilities

LEFT = -1
COLLINEAR = 0
RIGHT = 1

if utilities.__load_extensions:
    import geometricbasicsCpp as gbCpp


def turn_py(p0, p1, p2):
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
    
def turn(p, q, r, speedup=False):
    """Sorts `points` around `p` in CCW order."""
    if utilities.__config['PURE_PYTHON'] or not speedup:
        return turn_py(p, q, r)
    try:
        return gbCpp.turn(p, q, r)
    except OverflowError:
        return turn_py(p, q, r)


def isSorted(p, pts):
    """Checks whether the point set is sorted around p"""
    for i in xrange(len(pts) - 1):
        if turn(p, pts[i], pts[i + 1]) > 0:
            return False
    return True
    
def sap(p, pts, join=True, checkConcave=True):
    def comp(q, r):
        if q == p and r != p:
            return -1
        if r == p and q != p:
            return 1
        qxcoord = q[0]-p[0]
        rxcoord = r[0]-p[0]
        xprod = qxcoord*rxcoord
        #Special cases:
        if xprod < 0: # xprod < 0: #One point to the left and one to the right of p, the one to the right goes first
            return 1 if q[0] < p[0] else -1
        elif xprod == 0: #At least one point with same x-coordinate than p
            qycoord = q[1]-p[1]
            rycoord = r[1]-p[1]
            if q[0] != r[0]: #Exactly one point with same x-coordinate than p, and that point is below p. The one below p goes last
                if q[0] == p[0] and q[1] < p[1]:
                    return 1
                if r[0] == p[0] and r[1] < p[1]:
                    return -1
            elif qycoord*rycoord == 0:#Two with same x-coordinate than p, one above and one below. The one below p goes last
                return 1 if q[1] < p[1] else -1
        return turn(p, q, r)

    tpts = sorted(pts, comp)

    if checkConcave:
        start = None
        for i in xrange(len(tpts)-1):
            if turn(tpts[i], p, tpts[i+1]) < 0:
                start = i
                break
        if start is not None:
            same = 0
            while tpts[same] == p:
                same+=1
            start += 1
            tpts = tpts[:same] + tpts[start:len(tpts)] + tpts[same:start]
        return tpts
    else:
        return tpts
        
def sort_around_point_py(p, points, join=True):
    """Python version of sort_around_point"""
    #print "recieved ", p
    p1 = [p[0], p[1] + 1]
    r, l = [], []
    same = 0
    
    for q in points:
        if q == p:
            same += 1
        elif turn(p, p1, q) == RIGHT:
            r.append(q[:])
        elif turn(p, p1, q) == LEFT:
            l.append(q[:])
        elif p[1] >= q[1]:
            l.append(q[:])
        else:
            r.append(q[:])

    l.sort(lambda v1, v2: turn(p, v1, v2))
    r.sort(lambda v1, v2: turn(p, v1, v2))
    r = [p[:] for i in xrange(same)] + r
    
    if not join:
        return r, l

    r.extend(l)

    concave = False
    i = 0
    for i in xrange(len(r)-1):
        if turn(r[i], p, r[i + 1]) < 0:
            concave = True
            break
    if concave:
        start = i + 1
        r = r[:same] + r[start:len(r)] + r[same:start]

    return r

def sort_around_point(p, points, join=True, speedup=True):
    """Sorts `points` around `p` in CCW order."""
    if not join or utilities.__config['PURE_PYTHON'] or not speedup:
        return sort_around_point_py(p, points, join)
    try:
        return gbCpp.sort_around_point(p, points)
    except OverflowError:
        return sort_around_point_py(p, points, join)


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