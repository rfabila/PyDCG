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

from geometricbasics import turn, sort_around_point, general_position
import warnings
import copy
import datastructures
import random
import sys
import traceback
import decimal
import bisect
from line import Line
from collections import deque
from math import ceil, floor
import ordertypes
import crossing

LEFT = -1
RIGHT = 1
COLLINEAR = 0

UP = 1
DOWN = -1

FARTHER = 1
CLOSER = -1

class Polygon(object):
    def __init__(self, vertices = [], fill = "", outline = "black", bounded = True):
        self.bounded = bounded
        self.vertices = [[float(p[0]), float(p[1])] for p in vertices]
        self.fill = fill
        self.outline = outline


class CollinearPoints(Exception):

    def __init__(self, p, q, r):
        self.p = p
        self.q = q
        self.r = r

    def __str__(self):
        return repr(self.p) + ", " + repr(self.q) + ", " + repr(self.r)


def gcdb(u, v):
    """Taken from wikipedia"""
    if u < 0:
        u *= -1
    if v < 0:
        v *= -1
#    // simple cases (termination)
    if u == v:
        return u

    if u == 0:
        return v

    if v == 0:
        return u

#    // look for factors of 2
    if ~u & 1:  # // u is even
        if v & 1:  # // v is odd
            return gcd(u >> 1, v)
        else:  # // both u and v are even
            return gcd(u >> 1, v >> 1) << 1

    if (~v & 1):  # // u is odd, v is even
        return gcd(u, v >> 1)

#    // reduce larger argument
    if (u > v):
        return gcd((u - v) >> 1, v)

    return gcd((v - u) >> 1, u)


def gcd(a, b):
    while b != 0:
        t = b
        b = a % b
        a = t
    return a


class rational(object):

    def __init__(self, a, b, simp=False):
        self.a = a
        self.b = b

        if b == 0:
            raise ZeroDivisionError("punto %d, %d" % (a, b))

        if self.b < 0:
            self.a *= -1
            self.b *= -1

        n = random.randint(0, 19)
        if simp or n == 10:
            self.simplify()

    def simplify(self):
        aux = gcd(self.a, self.b)
        self.a /= aux
        self.b /= aux

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, long):
            return self.a < other * self.b
        return self.a * other.b < other.a * self.b

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        if isinstance(other, int) or isinstance(other, long):
            return self.a <= other * self.b
        return self.a * other.b <= other.a * self.b

    def __gt__(self, other):
        return not self <= other

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, long):
            return self.a == other * self.b
        return self.a * other.b == other.a * self.b

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, long):
            return rational(self.a + other * self.b, self.b)
        den = self.b * other.b
        num = self.a * other.b + other.a * self.b
        return rational(num, den)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, long):
            return rational(self.a - other * self.b, self.b)
        den = self.b * other.b
        num = self.a * other.b - other.a * self.b
        return rational(num, den)

    def __rsub__(self, other):
        return self - other

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, long):
            return rational(self.a * other, self.b)
        den = self.b * other.b
        num = self.a * other.a
        return rational(num, den)

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        if isinstance(other, int) or isinstance(other, long):
            return rational(self.a * other, self.b)
        den = self.b * other.a
        num = self.a * other.b
        return rational(num, den)

    def __str__(self):
        return "%d/%d" % (self.a, self.b)

    def __repr__(self):
        return "rational(%d,%d)" % (self.a, self.b)

    def __float__(self): #TODO: Check if it's worth it to use decimal
        try:
            self.simplify()
            return float(self.a) / float(self.b)
        except Exception as e:
            print self.a
            print self.b
            raise e

    #TODO: Check if this is necessary (I think so, since somehere I use rationals as keys but Iḿ not sure anymore)
    def __hash__(self): 
        auxa = 2 * self.a if self.a > 0 else -2 * self.a - 1
        auxb = 2 * self.b if self.b > 0 else -2 * self.b - 1
        return ((auxa + auxb) * (auxa + auxb + 1) / 2) + auxb
        
    def copy(self):
        return copy.deepcopy(self)


class line(object):

    """A line defined by two points (p and q) in the plane.
       The slope and y-intersection are available at m and b, respectively"""

    # TODO: Si se quitan las propiedades, se debería protejer p, q, m, b?

    def __init__(self, p, q):
        if not (isinstance(p, list) or isinstance(p, tuple)) or not (isinstance(q, list) or isinstance(q, tuple)):
            raise Exception
        self.p = list(p)
        self.q = list(q)
        if self.p > self.q:
            self.p, self.q = self.q, self.p
        self.m = rational(self.p[1] - self.q[1], self.p[0] - self.q[0], True)
        self.b = self.m * (-self.p[0]) + self.p[1]
        self.b.simplify()

    def intersection_y_coord(self, l):
        """Returns the y coordinate of the point where self and l
           intersect. If self and l are paralell returns None"""
        if self.m == l.m:
            return None
        res = (l.m * self.b - self.m * l.b) / (l.m - self.m)
        res.simplify()
        return res

    def intersection_x_coord(self, l):
        """Returns the x coordinate of the point where self and l
           intersect. If self and l are paralell returns None"""
        if self.m == l.m:
            return None
        res = (self.b - l.b) / (l.m - self.m)
        res.simplify()
        return res

    def intersection(self, l):
        res = [self.intersection_x_coord(l), self.intersection_y_coord(l)]
        res[0].simplify()
        res[1].simplify()
        return res

    def __str__(self):
        return "y = %d/%d x %d/%d" % (self.m.a, self.m.b, self.b.a, self.b.b)

    def __repr__(self):
        return "y = %d/%d x %d/%d" % (self.m.a, self.m.b, self.b.a, self.b.b)

    def getPoints(self):
        if self.p > self.q:#Check this, it shouldn't be necessary to do this
            self.p, self.q = self.q, self.p
        return [self.p, self.q]

    def evalx(self, x):
        return self.m * x + self.b
        
    def __eq__(self, other):
        if isinstance(other, line) and other.m == self.m and other.b == self.b:
            return True
        return False


def dualize(obj):
    if isinstance(obj, line):
        return [obj.m, obj.b * -1]
#    elif isinstance(obj, list):
    print "Got", obj, type(obj), isinstance(obj, line)
    raise Exception("Not implemented yet!")
    
#        return #TODO: write this!


def getPointRegion(q, sortedpoints, indices):
    """ Assumes len(sortedpoints) > 3, each entry of sorted points should contain
        a point `p` and the other points sorted around it.
        Returns upper, lower and counters: the upper hull, lower hull, and a dictionary
        mapping the dual of each line inserted to the number of times it has been inserted
       """
    upper = []
    lower = []
    counters = {}

    for (p, pts) in sortedpoints.iteritems():
        pred, succ = indices[tuple(p)][0]
        predline = line(list(p), pts[pred])
        succline = line(list(p), pts[succ])

        intersection = predline.evalx(q[0])

        if intersection > q[1]:
            upper.append(predline)
        elif intersection < q[1]:
            lower.append(predline)
        else:
            raise CollinearPoints(q, p, pts[pred])

        intersection = succline.evalx(q[0])
        if intersection > q[1]:
            upper.append(succline)
        elif intersection < q[1]:
            lower.append(succline)
        else:
            raise CollinearPoints(q, p, pts[succ])

    # Now upper and lower contain the lines that bound q's region
    # We dualize the lines and find the lower and upper hull, respectively

    upperHull = datastructures.dynamic_half_hull(datastructures.UPPER)
    lowerHull = datastructures.dynamic_half_hull(datastructures.LOWER)

    for l in upper:
        point = dualize(l)
        counters[tuple(point)] = counters.setdefault(tuple(point), 0) + 1
        upperHull.insert(point, l)

    for l in lower:
        point = dualize(l)
        counters[tuple(point)] = counters.setdefault(tuple(point), 0) + 1
        lowerHull.insert(point, l)

    return upperHull, lowerHull, counters


def getRegionR(upper, lower, toList = True):
    # TODO: erase extra calls to popColiinear, rewrite repeated code
    # TODO: Make dynamic_haf_hull.toList() return a deque, since many
    # functions pop from the front
    if toList:
        U = upper.toList()
        L = lower.toList()
    else:
        U = upper
        L = lower
        
    L.reverse()
            
    def popCollinear(env):
#        print "ENV", env
        if len(env) == 0:
            return []
        aux = [env[0]]
        for i in xrange(1, len(env)):
            if i < len(env)-1:
                int1 = aux[-1][1].intersection(env[i][1])
                int2 = env[i][1].intersection(env[i + 1][1])
                if int1 == int2:
                    continue
            aux.append(env[i])
        return aux
        
    U = popCollinear(U)
    L = popCollinear(L)

    if len(U) == 0 or len(L) == 0:
        L.reverse()
        return U, L

    # First bitangent
    idxL, idxU = 0, len(U) - 1
    l = sorted([L[idxL][0], U[idxU][0]])

    doneL, doneU = False, False
    while not (doneL and doneU):
        doneL, doneU = False, False
        if idxL == len(L) - 1 or turn(l[0], l[1], L[idxL + 1][0]) < 0:
            doneL = True
        elif turn(l[0], l[1], L[idxL + 1][0]) == 0:
            if (L[idxL + 1][0][0] < L[idxL][0][0] < U[idxU][0][0]
                ) or (L[idxL + 1][0][0] > L[idxL][0][0] > U[idxU][0][0]):
                doneL = True
            else:
                doneL = False
        else:
            doneL = False

        if idxU == 0 or turn(l[0], l[1], U[idxU - 1][0]) > 0:
            doneU = True
        elif turn(l[0], l[1], U[idxU - 1][0]) == 0:
            if (U[idxU - 1][0][0] < U[idxU][0][0] < L[idxL][0][0]
                ) or (U[idxU - 1][0][0] > U[idxU][0][0] > L[idxL][0][0]):
                doneU = True
            else:
                doneU = False
        else:
            doneU = False

        if not doneL:
            idxL += 1

        if not doneU:
            idxU -= 1

        l = sorted([L[idxL][0], U[idxU][0]])

    if L[idxL][0][0] < U[idxU][0][0]:
        #        print "Borro principio de L y final de U"
        L = L[idxL:]
        U = U[:idxU + 1]
    else:
        #        print "Borro principio de U y final de L"
        L = L[:idxL + 1]
        U = U[idxU:]
        
    # Second bitangent
    idxL, idxU = len(L) - 1, 0
    l = sorted([L[idxL][0], U[idxU][0]])
    doneL, doneU = False, False
    while not (doneU and doneL):
        doneL, doneU = False, False
        if idxL == 0 or turn(l[0], l[1], L[idxL - 1][0]) < 0:
            doneL = True
        elif turn(l[0], l[1], L[idxL - 1][0]) == 0:
            if (L[idxL - 1][0][0] < L[idxL][0][0] < U[idxU][0][0]
                ) or (L[idxL - 1][0][0] > L[idxL][0][0] > U[idxU][0][0]):
                doneL = True
            else:
                doneL = False
        else:
            doneL = False

        if idxU == len(U) - 1 or turn(l[0], l[1], U[idxU + 1][0]) > 0:
            doneU = True
        elif turn(l[0], l[1], U[idxU + 1][0]) == 0:
            if (U[idxU + 1][0][0] < U[idxU][0][0] < L[idxL][0][0]
                ) or (U[idxU + 1][0][0] > U[idxU][0][0] > L[idxL][0][0]):
                doneU = True
            else:
                doneU = False
        else:
            doneU = False

        if not doneL:
            idxL -= 1

        if not doneU:
            idxU += 1

        l = sorted([L[idxL][0], U[idxU][0]])

    if L[idxL][0][0] < U[idxU][0][0]:
        #        print "Borro principio de L y final de U"
        L = L[idxL:]
        U = U[:idxU + 1]
    else:
        #        print "Borro principio de U1 y final de L"
        L = L[:idxL + 1]
        U = U[idxU:]

    L.reverse()

    return U, L
    
def crossEdge(n, p1, p2, side, upper, lower, indices, ordered):
#    p1, p2 = edge.getPoints()
    oldline = line(p1, p2)
    ant1, suc1 = indices[tuple(p1)][0]
    ant2, suc2 = indices[tuple(p2)][0]
    

    def update(p, q, ant, suc):
        antipodal = False
        if ordered[tuple(p)][ant] == q:
            indices[tuple(p)][0] = [(ant - 1) % n, ant]
            newpoint = ordered[tuple(p)][(ant - 1) % n]
            if ant in indices[tuple(p)][1]:
                antipodal = True
        else:
            indices[tuple(p)][0] = [suc, (suc + 1) % n]
            newpoint = ordered[tuple(p)][(suc + 1) % n]
            if suc in indices[tuple(p)][1]:
                antipodal = True

        newline = line(p, newpoint)
        aux = [p[0], p[1] + 1]
        
        # TODO: Explain why this works
        sameTurn = turn(p, q, newpoint) == turn(p, aux, newpoint)
        if sameTurn == antipodal:
            upper.insert(dualize(newline), newline)
            return dualize(newline), UP
        else:
            lower.insert(dualize(newline), newline)
            return dualize(newline), DOWN
        
#            if turn(p, q, newpoint) == turn(p, aux, newpoint):  
#                if antipodal:
#                    upper.insert(dualize(newline), newline)
#                    return dualize(newline), UP
#                else:
#                    lower.insert(dualize(newline), newline)
#                    return dualize(newline), DOWN
#            else:
#                if antipodal:
#                    lower.insert(dualize(newline), newline)
#                    return dualize(newline), DOWN
#                else:
#                    upper.insert(dualize(newline), newline)
#                    return dualize(newline), UP

    if side == UP:
        upper.delete(dualize(oldline))
        lower.insert(dualize(oldline), oldline)

    elif side == DOWN:
        lower.delete(dualize(oldline))
        upper.insert(dualize(oldline), oldline)
        
    # We update ant and suc for p1 and insert the new line in 
    # the appropiate envelope
    line1 = update(p1, p2, ant1, suc1)
    # We do the same for p2       
    line2 = update(p2, p1, ant2, suc2)

    U, L = getRegionR(upper, lower)
#        print U, L
    return line1, line2, U, L
#    poly = getPolygon(U,L)
    
def getPolygonKey(pol):
    key = []
    for i in xrange(3):
        x, y = pol[i][0].copy(), pol[i][1].copy()
        x.simplify()
        y.simplify()
        key.append(x)
        key.append(y)
    return tuple(key)


def randMove(upper, lower, indices, ordered, regionU, regionL, visitedPolygons, lastLine=None):
    total = len(regionU) + len(regionL) - 1
    avoidLines = set()

    side = None
    n = (len(indices) - 1) * 2
    polygonFound = False
#    U, L = None, None
#    p1, p2 = None, None

    while not polygonFound:
        
        lineChosen = False
        edge = -1
    
        while not lineChosen:
            edge = random.randint(0, total)
            while edge in avoidLines:
                edge = random.randint(0, total)
            if edge < len(regionU):
                edge = regionU[edge][1]
                side = UP
            else:
                edge = regionL[total - edge][1]
                side = DOWN
            p1, p2 = edge.getPoints()
            if lastLine is None or sorted([p1, p2]) != lastLine:
                lineChosen = True
                
        oldline = line(p1, p2)
        ant1, suc1 = indices[tuple(p1)][0]
        ant2, suc2 = indices[tuple(p2)][0]
                
        line1, line2, U, L = crossEdge(n, p1, p2, side, upper, lower, indices, ordered)
        poly = getPolygon(U, L)
    
        
        triang = getPolygonKey(poly)
        
        if triang in visitedPolygons:
            #print "dup"
            avoidLines.add(edge)
            indices[tuple(p1)][0] = [ant1, suc1]
            indices[tuple(p2)][0] = [ant2, suc2]
            
            if line1[1] == UP:
                upper.delete(line1[0])
            else:
                lower.delete(line1[0])                
            if line2[1] == UP:
                upper.delete(line2[0])
            else:
                lower.delete(line2[0])
                
            if side == UP:
                lower.delete(dualize(oldline))
                upper.insert(dualize(oldline), oldline)
            else:
                upper.delete(dualize(oldline))
                lower.insert(dualize(oldline), oldline)
        else:
            visitedPolygons.add(triang)
            polygonFound = True
        
    regionU[:] = U
    regionL[:] = L
    return sorted([p1, p2]), poly
    

def getSegments(upper, lower):
    if isinstance(upper, list):
        U = upper
    else:
        U = upper.toList()

    if isinstance(lower, list):
        L = lower
    else:
        L = lower.toList()

    s = []
    for item in U:
        seg = item[1].getPoints()
        seg.append("red")
        s.append(seg)
    for item in L:
        seg = item[1].getPoints()
        seg.append("blue")
        s.append(seg)
    return s


def getLines(upper, lower=None, mode=1):
    if isinstance(upper, list):
        U = upper
    else:
        U = upper.toList()

    if lower is not None:
        if isinstance(upper, list):
            L = lower
        else:
            L = lower.toList()

    uplines = []
    lowlines = []
    if mode == 0:
        for item in U:
            seg = item.getPoints()
            l = Line(seg[0], seg[1], "red")
            uplines.append(l)
    else:
        for item in U:
            seg = item[1].getPoints()
            l = Line(seg[0], seg[1], "red")
            uplines.append(l)

    if lower is not None:
        if mode == 0:
            for item in L:
                seg = item.getPoints()
                l = Line(seg[0], seg[1], "blue")
                lowlines.append(l)
        else:
            for item in L:
                seg = item[1].getPoints()
                l = Line(seg[0], seg[1], "blue")
                lowlines.append(l)

    if lower is not None:
        return uplines, lowlines
    return uplines


def orderAllPoints(q, points):
    """ Returns a pair of dictionaries: orderedpoints and indices.
        - orderedpoints maps every point p in points to a list with the points in {pts \ {p}} \cup antipodals {pts \ {p}} sorted ccw around p.
        - indices maps every point to a pair of lists:
            indices[p][0] is a list with the indices of the points that would appear before and after q in orderedpoints[p]
            indices[p][1] is a list with the indices of the points in orderedpoints[p] that are antipodal
    """
    orderedpoints = {}
    indices = {}
    reinsert = False
    try:
        index = points.index(q)
        reinsert = True
    except ValueError:
        index = None

    if index is not None:
        points.pop(index)

    for p in points:
        indices[tuple(p)] = [[], []]

    for i in xrange(len(points)):
        revert = {}
        p = points[i]
        pts = points[:i] + points[i + 1:]
        antipodals = []

        for pt in pts:
            anti = [2 * p[0] - pt[0], 2 * p[1] - pt[1]]
            antipodals.append(anti)
            revert[tuple(anti)] = pt

        pts.extend(antipodals)
        ordered = sort_around_point(p, pts)

        for i in xrange(len(ordered)):  # TODO: Another binary search
            if turn(
                p, ordered[i], q) == LEFT and turn(
                p, ordered[
                    (i + 1) %
                    len(ordered)], q) == RIGHT:
                indices[tuple(p)][0] = [i, (i + 1) % len(ordered)] #TODO: Rewrite this, there's no point in having an antipodal list. Just mark the points directly
                break

        for i in xrange(len(ordered)):
            key = tuple(ordered[i])
            if key in revert:
                ordered[i] = revert[key]
                indices[tuple(p)][1].append(i)

        orderedpoints[tuple(p)] = ordered

    if reinsert:
        points.insert(index, q)

    return orderedpoints, indices


class pointAndLines(object):

    def __init__(self, p, l1, l2, polygon):
        self.l1 = l1
        self.l2 = l2
        self.p = p
        self.pol = polygon


def tester(pts):
    res = []
    cont = 0
    for p in pts:
        print "\nPOINT", cont
        cont += 1
        ordered, indices = orderAllPoints(p, pts)
        upper, lower, counters = getPointRegion(p, ordered, indices)
        lines1 = getLines(upper, lower)
        cosa = getRegionR(upper, lower)
        lines2 = getLines(cosa[0], cosa[1])
        pol = getPolygon(cosa[0], cosa[1])
        aux = pointAndLines(
            p,
            lines1[0] +
            lines1[1],
            lines2[0] +
            lines2[1],
            getPolSegs(pol))
        res.append(aux)
    return res


def restorePts(pts):
    for p in pts:
        if len(p) > 2:
            p.pop()


def updateVis(vis, pts, res, indexp, indexLines, pol=False):
    restorePts(pts)
    pts[pts.index(res[indexp].p)].append(0)
    vis.lines = res[indexp].l1 if indexLines == 0 else res[indexp].l2
    if pol:
        vis.segments = res[indexp].pol
    else:
        vis.segments = []


def getPolygon(U, L, k=10000):
    if len(U) == 0 and len(L) == 0:
        raise Exception("Can't form a polygon from empty chains")
        return

    upts, lpts = [], []
    for i in xrange(len(U) - 1):
        upts.append(U[i][1].intersection(U[i + 1][1]))
    for i in xrange(len(L) - 1):
        lpts.append(L[i][1].intersection(L[i + 1][1]))
    lpts.reverse()

    if len(L) == 0:
        p1 = upts[0][:]
        p1[0] += k
        p1[1] = U[0][1].evalx(p1[0])

        p2 = upts[-1][:]
        p2[0] -= k
        p2[1] = U[-1][1].evalx(p2[0])

        upts.insert(0, p1)
        upts.append(p2)
#        print "just up"
        return upts

    if len(U) == 0:
        #        print "lpts", lpts
        p1 = lpts[0][:]
        p1[0] -= k
        p1[1] = L[-1][1].evalx(p1[0])

        p2 = lpts[-1][:]
        p2[0] += k
        p2[1] = L[0][1].evalx(p2[0])

        lpts.insert(0, p1)
        lpts.append(p2)
#        print "just down"
        return lpts

    # This one should be the left-most point of the polygon
    lm = U[-1][1].intersection(L[-1][1])
    # and this one should be the right-most one
    rm = U[0][1].intersection(L[0][1])

    if len(U) == 1 and len(L) == 1:  # This means the region is just a wedge
        
        # Let's see if we need the right or the left wedge
        p = lm
        p1 = [p[0] + k, U[0][1].evalx(p[0] + k)]
        p2 = [p[0] + k, L[0][1].evalx(p[0] + k)]
        if turn(p1, p, p2) > 0:
            p1 = [p[0] - k, L[0][1].evalx(p[0] - k)]
            p2 = [p[0] - k, U[0][1].evalx(p[0] - k)]
#        print "unbounded"
        return [p1, p, p2]

    else:
        aux = upts[-1] if len(upts) > 0 else lpts[0]
        if lm[0] > aux[0]:
            lpts.append(rm)
            lpts += upts
            p1 = lpts[0][:]
            p1[0] -= k
            p1[1] = L[-1][1].evalx(p1[0])

            p2 = lpts[-1][:]
            p2[0] -= k
            p2[1] = U[-1][1].evalx(p2[0])

            lpts.insert(0, p1)
            lpts.append(p2)
#            print "unbounded"
            return lpts

        aux = upts[0] if len(upts) > 0 else lpts[-1]
        if rm[0] < aux[0]:

            upts.append(lm)
            upts += lpts

            p1 = upts[0][:]
            p1[0] += k
            p1[1] = U[0][1].evalx(p1[0])

            p2 = upts[-1][:]
            p2[0] += k
            p2[1] = L[0][1].evalx(p2[0])
            upts.insert(0, p1)
            upts.append(p2)
#            print "unbounded"
            return upts

    # If we get to this point, the region is a bounded polygon
    upts.append(lm)
    upts += lpts
    upts.append(rm)

    return upts

def pointInPolygon(p, pol):
    t = turn(pol[0],pol[1],p)
    for i in xrange(len(pol)):
        aux = turn(pol[i],pol[(i+1)%len(pol)],p)
        if t != aux:
            return False
    return True
        
def sameXCoord(p, pts):
    for q in pts:
        if p[0] == q[0]:
            return True
    return False
        
def getCenter(polygon):
    n = float(len(polygon))
    res = [0, 0]
    for pt in polygon:
        res[0] += pt[0]
        res[1] += pt[1]
        
    res[0].simplify()
    res[1].simplify()
    res[0]=float(res[0])
    res[1]=float(res[1])
            
    funcs = [lambda n: int(ceil(n)), lambda n: int(floor(n))]
        
    for f in funcs:
        for g in funcs:
            candidate = [f(res[0]/n), g(res[1]/n)]
            deltas = [0,-1,2]
            for d in deltas:
                candidate[0]+=d
                if pointInPolygon(candidate, polygon) and not sameXCoord(candidate, polygon):
                    return candidate
                    
#    print "Warning, no center found", polygon
    return None

def getPolSegs(polygon, w=3):
    colors = ["green", "red", "blue", "black", "orange", "brown", "cyan"]
    color = random.choice(colors)
    pol = []
    n = len(polygon)
    for i in range(len(polygon)):
        p1 = [float(polygon[i % n][0]), float(polygon[i % n][1])]
        p2 = [float(polygon[(i + 1) % n][0]), float(polygon[(i + 1) % n][1])]
        seg = [p1, p2, color, w]
        pol.append(seg)
    return pol


def getRandomWalk(p, pts, steps=10):
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counter = getPointRegion(
        p, ordered, indices)  # TODO: USE COUNTER!!!
    U, L = getRegionR(upper, lower)
    regions = [getPolygon(U, L)]
    last = None
    visitedPolygons = set()
    for i in range(steps):
        last, polygon = randMove(upper, lower, indices, ordered, U, L, visitedPolygons, last)
        regions.append(polygon)
    return regions, visitedPolygons


def generateRandomWalk(p, pts, steps=10):
    k=0
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counter = getPointRegion(
        p, ordered, indices)  # TODO: USE COUNTER!!!
    U, L = getRegionR(upper, lower)
    last = None
    visitedPolygons = set()
    for i in range(steps):
        print k
        k+=1
        last = randMove(upper, lower, indices, ordered, U, L, set(), last)
        yield getPolygon(U, L)


def getLineArray(p, pts):
    lines = []
    for i in xrange(len(pts) - 1):
        for j in xrange(i + 1, len(pts)):
            if pts[i] != p and pts[j] != p:
                lines.append(line(pts[i], pts[j]))
    return getLines(lines, mode=0)
    
def getPolygonArray(pts):
    lines = []
    for i in xrange(len(pts)):
        lines.append(line(pts[i], pts[(i+1)%len(pts)]))
    return getLines(lines, mode=0)


def segmentsInOrder(visualizer, segs):
    index = 0
    visualizer.segments = segs[0]
    visualizer.draw()
    previous = ""
    inst = raw_input("Instruction: ")
    while inst != 'q':
        ask = True
        if inst == "":
            inst = previous
        if inst == 'c':
            if index == len(segs) - 1:
                print "Index out of range"
            else:
                index += 1
        elif inst == 'p':
            if index == 0:
                print "Index out of range"
            else:
                index -= 1
        elif inst == 'q':
            ask = False
        else:
            try:
                index = int(inst)
            except ValueError:
                print "Wrong instruction"
        visualizer.segments = segs[index]
        visualizer.draw()
        previous = inst
        if ask:
            inst = raw_input("Instruction: ")


def checkConvex(pol):
    n = len(pol)
    for i in range(len(pol)):
        if turn(pol[i % n], pol[(i + 1) % n], pol[(i + 2) % n]) > 0:
            return False
    return True


def rationalPointToFloat(pt):
    return [float(pt[0]), float(pt[1])]


def profile(n=50, w=1000, functions=None, fileName="profiler_res"):
    import line_profiler
    prof = line_profiler.LineProfiler()
    if functions is not None:
        for f in functions:
            prof.add_function(f)
    else:
        prof.add_function(getRandomWalk)
        prof.add_function(orderAllPoints)
        prof.add_function(getPointRegion)
        prof.add_function(getRegionR)
        prof.add_function(getPolygon)
        prof.add_function(randMove)

    pts = [datastructures.randPoint(1000000) for i in xrange(n)]
    p = random.choice(pts)

    prof.runctx(
        "getRandomWalk(p, pts, w)", {
            'p': p, 'pts': pts, 'w': w, 'getRandomWalk': getRandomWalk}, None)
    f = open(fileName, "w")
    prof.print_stats(f)
    f.close()
    print "Done. Stats saved in '%s'" % fileName


def getRandomWalkDFS2(p, pts, length=10, maxDepth=2000, getPolygon = True):
    """Recursive version. It's a generator"""
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counters = getPointRegion(p, ordered, indices)
    U, L = getRegionR(upper, lower)
    n = (len(indices) - 1) * 2
    
    start = getPolygon(U, L)
    regions = [start]
    visitedPolygons = set()
    visitedPolygons.add(getPolygonKey(start))
    depth = [0]
    
    def DFS(lastEdge=None):
        print "level",depth[0]
        if len(regions) >= length:
            return
        regionU, regionL = getRegionR(upper, lower)      
        total = len(regionU) + len(regionL)
    
        side = None
        
        edgeIndex = random.randint(0, total-1)
                
        for i in xrange(total):
            if len(regions) >= length:
                return
            edgeIndex += 1
            edgeIndex %= total
            if edgeIndex < len(regionU):
                crossingEdge = regionU[edgeIndex][1]
                side = UP
            else:                
                crossingEdge = regionL[edgeIndex - len(regionU)][1]
                side = DOWN
            p1, p2 = crossingEdge.getPoints()
            if sorted([p1, p2]) == lastEdge:
                continue
        
            ant1, suc1 = indices[tuple(p1)][0]            
            ant2, suc2 = indices[tuple(p2)][0]
        
            def update(p, q, ant, suc):
                antipodal = False
                if ordered[tuple(p)][ant] == q:
                    oldline = line(p, ordered[tuple(p)][suc])
                    indices[tuple(p)][0] = [(ant - 1) % n, ant]
                    newpoint = ordered[tuple(p)][(ant - 1) % n]
                    if ant in indices[tuple(p)][1]:
                        antipodal = True
                else:
                    oldline = line(p, ordered[tuple(p)][ant])
                    indices[tuple(p)][0] = [suc, (suc + 1) % n]
                    newpoint = ordered[tuple(p)][(suc + 1) % n]
                    if suc in indices[tuple(p)][1]:
                        antipodal = True
        
                newline = line(p, newpoint)
                aux = [p[0], p[1] + 1]
                
                # TODO: Explain why this works
                sameTurn = turn(p, q, newpoint) == turn(p, aux, newpoint)
                
                keyold = tuple(dualize(oldline))
                counters[keyold] -= 1
                oldSide = None
                
                if counters[keyold] == 0:
                    try:
                        upper.delete(dualize(oldline))
                        oldSide = UP
                    except:
                        lower.delete(dualize(oldline)) #TODO: Should know whether it's inside upper or lower
                        oldSide = DOWN
                
                keynew = tuple(dualize(newline))
                counters.setdefault(keynew, 0)
                counters[keynew] += 1
                
                if sameTurn == antipodal:#TODO: check this part
                    if counters[keynew] == 1:
                        upper.insert(dualize(newline), newline)
                    return newline, UP, oldline, oldSide #new goes to up, old was in oldside
                else:
                    if counters[keynew] == 1:
                        lower.insert(dualize(newline), newline)
                    return newline, DOWN, oldline, oldSide
    
            if side == UP:
                upper.delete(dualize(crossingEdge))
                lower.insert(dualize(crossingEdge), crossingEdge)
        
            elif side == DOWN:
                lower.delete(dualize(crossingEdge))
                upper.insert(dualize(crossingEdge), crossingEdge)
            
            # We update ant and suc for p1 and insert the new line in 
            # the appropiate envelope
            lines1 = update(p1, p2, ant1, suc1)
            # We do the same for p2       
            lines2 = update(p2, p1, ant2, suc2)
        
            U, L = getRegionR(upper, lower) #TODO: write a composing function
            poly = getPolygon(U,L)
            
            triang = getPolygonKey(poly)
            
            if triang not in visitedPolygons:
                visitedPolygons.add(triang)
                regions.append(poly)
                print "                       van", len(regions)
                if depth[0] < maxDepth:
                    depth[0] += 1
                    DFS(sorted([p1,p2]))
                    depth[0]-=1
                    
            indices[tuple(p1)][0] = [ant1, suc1]
            indices[tuple(p2)][0] = [ant2, suc2]
            
            def restore(lines):
                newkey = tuple(dualize(lines[0])) 
                counters[newkey] -= 1
                if counters[newkey] == 0:
                    if lines[1] == UP:
                        upper.delete(dualize(lines[0]))
                    else:
                        lower.delete(dualize(lines[0]))
                        
                oldkey = tuple(dualize(lines[2]))
                counters[oldkey] += 1
                if counters[oldkey] == 1:
                    if lines[3] == UP:
                        upper.insert(dualize(lines[2]),lines[2])
                    else:
                        lower.insert(dualize(lines[2]),lines[2])
                        
            restore(lines1)
            restore(lines2)
                
            if side == UP:
                lower.delete(dualize(crossingEdge))
                upper.insert(dualize(crossingEdge), crossingEdge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
            else:
                upper.delete(dualize(crossingEdge))
                lower.insert(dualize(crossingEdge), crossingEdge)
    try:
        DFS()
    except Exception as e:
        print str(e)
        print traceback.format_exc()
        print "fail!"
        return regions, visitedPolygons
        
    return regions, visitedPolygons
    
def getRandomWalkDFS(p, pts, length=10, getPolygons=True):
    """The non-recursive version, it's a generator"""
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counters = getPointRegion(p, ordered, indices)
    U, L = getRegionR(upper, lower)
    n = (len(indices) - 1) * 2
    
    start = getPolygon(U, L)
    regions = 1
    if getPolygons:
        yield start
    else:
        res = []
        for l in U:
            res.append([l[1].p, l[1].q])
        for l in L:
            res.append([l[1].p, l[1].q])
        yield res
    visitedPolygons = set()
    visitedPolygons.add(getPolygonKey(start))
    
    class region(object):
        def __init__(self, regionU, regionL, lastEdge = None, side = None, neighbors1=None, neighbors2=None, lines1=None, lines2=None):
            self.regionU = regionU
            self.regionL = regionL
            self.total = len(regionU) + len(regionL)
            self.edgeIndex = random.randint(0, self.total-1)
            self.i = 0
            self.lastEdge = lastEdge
            self.side = side
            self.neighbors1 = neighbors1
            self.neighbors2 = neighbors2
            self.lines1 = lines1
            self.lines2 = lines2
    
    def update(p, q, ant, suc):
        antipodal = False
        if ordered[tuple(p)][ant] == q:
            oldline = line(p, ordered[tuple(p)][suc])
            indices[tuple(p)][0] = [(ant - 1) % n, ant]
            newpoint = ordered[tuple(p)][(ant - 1) % n]
            if ant in indices[tuple(p)][1]:
                antipodal = True
        else:
            oldline = line(p, ordered[tuple(p)][ant])
            indices[tuple(p)][0] = [suc, (suc + 1) % n]
            newpoint = ordered[tuple(p)][(suc + 1) % n]
            if suc in indices[tuple(p)][1]:
                antipodal = True

        newline = line(p, newpoint)
        aux = [p[0], p[1] + 1]
        
        # TODO: Explain why this works
        sameTurn = turn(p, q, newpoint) == turn(p, aux, newpoint)
        
        keyold = tuple(dualize(oldline))
        counters[keyold] -= 1
        oldSide = None
        
        if counters[keyold] == 0:
            try:
                upper.delete(dualize(oldline))
                oldSide = UP
            except:
                lower.delete(dualize(oldline)) #TODO: Should know whether it's inside upper or lower
                oldSide = DOWN
        
        keynew = tuple(dualize(newline))
        counters.setdefault(keynew, 0)
        counters[keynew] += 1
        
        if sameTurn == antipodal:#TODO: check this part
            if counters[keynew] == 1:
                upper.insert(dualize(newline), newline)
            return newline, UP, oldline, oldSide #new goes to up, old was in oldside
        else:
            if counters[keynew] == 1:
                lower.insert(dualize(newline), newline)
            return newline, DOWN, oldline, oldSide
    
    def restore(lines):
        newkey = tuple(dualize(lines[0])) 
        counters[newkey] -= 1
        if counters[newkey] == 0:
            if lines[1] == UP:
                upper.delete(dualize(lines[0]))
            else:
                lower.delete(dualize(lines[0]))
                
        oldkey = tuple(dualize(lines[2]))
        counters[oldkey] += 1
        if counters[oldkey] == 1:
            if lines[3] == UP:
                upper.insert(dualize(lines[2]),lines[2])
            else:
                lower.insert(dualize(lines[2]),lines[2])
                
    S = deque()
    S.append(region(U, L))
    
    while len(S) > 0:
        
        current = S[-1]
        regionU, regionL = current.regionU, current.regionL
        
        if current.i < current.total:
            current.i += 1
            current.edgeIndex = (current.edgeIndex + 1) % current.total
#            print " "*len(S), "Will use", current.edgeIndex, " of" , current.total
            if current.edgeIndex < len(regionU):
                crossingEdge = regionU[current.edgeIndex][1]
                side = UP
            else:                
                crossingEdge = regionL[current.edgeIndex - len(regionU)][1]
                side = DOWN
            p1, p2 = crossingEdge.getPoints()
            if p1 > p2:
                p1, p2 = p2, p1
            if [p1, p2] == current.lastEdge:
#                print " "*len(S), "points", p1, p2, [p1, p2]
#                print " "*len(S), "lastedge!"
                continue
#            print "next line"
        
            ant1, suc1 = indices[tuple(p1)][0]            
            ant2, suc2 = indices[tuple(p2)][0]
    
            if side == UP:
                upper.delete(dualize(crossingEdge))
                lower.insert(dualize(crossingEdge), crossingEdge)
        
            elif side == DOWN:
                lower.delete(dualize(crossingEdge))
                upper.insert(dualize(crossingEdge), crossingEdge)
            
            # We update ant and suc for p1 and insert the new line in 
            # the appropiate envelope
            lines1 = update(p1, p2, ant1, suc1)
            # We do the same for p2       
            lines2 = update(p2, p1, ant2, suc2)
        
            U, L = getRegionR(upper, lower) #TODO: write a composing function
            poly = getPolygon(U,L)
            triang = getPolygonKey(poly)
            
            if triang not in visitedPolygons:
                visitedPolygons.add(triang)
                if getPolygons:
                    yield poly
                else:
                    res = []
                    for l in U:
                        res.append([l[1].p, l[1].q])
                    for l in L:
                        res.append([l[1].p, l[1].q])
                    yield res
                regions += 1
#                regions.append(poly)
#                print "                               van", len(regions)
#                print " "*len(S), "push!, I crossed", crossingEdge
                S.append( region( U, L, [p1,p2], side, (ant1, suc1), (ant2, suc2), lines1, lines2 ) )
#                print "level", len(S)
                if regions >= length and length>=0:
                   # print "found enough regions"
                    break
            else:
#                print " "*len(S), "already visited"
                indices[tuple(p1)][0] = [ant1, suc1]
                indices[tuple(p2)][0] = [ant2, suc2]
                            
                restore(lines1)
                restore(lines2)
                
                if side == UP:   
                    lower.delete(dualize(crossingEdge))
                    upper.insert(dualize(crossingEdge), crossingEdge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(crossingEdge))
                    lower.insert(dualize(crossingEdge), crossingEdge)
        else:
#            print " "*len(S), "done"
            if len(S) > 1:
                p1 = current.lastEdge[0]
                p2 = current.lastEdge[1]
                indices[tuple(p1)][0] = [current.neighbors1[0], current.neighbors1[1]]
                indices[tuple(p2)][0] = [current.neighbors2[0], current.neighbors2[1]]
                            
                restore(current.lines1)
                restore(current.lines2)
                    
                edge = line(p1, p2)   
#                print " "*len(S), "returning via", edge
                
                if current.side == UP:                    
                    lower.delete(dualize(edge))
                    upper.insert(dualize(edge), edge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(edge))
                    lower.insert(dualize(edge), edge)
#            print " "*len(S), "pop!"
            S.pop()
            
#    return regions, visitedPolygons
    

#pts = [[8172, -9003], [7480, -1467], [-9326, -111], [1880, 4958], [9628, 7411]]
#p = [-9326, -111]
#walk, visited = getRandomWalkDFS(p, pts, 17)

def getRandomWalkN2(p, pts, length=10):
#    p = [random.randint(-100000000, 100000000), random.randint(-100000000, 100000000)]
    
    upper = datastructures.dynamic_half_hull(datastructures.UPPER)
    lower = datastructures.dynamic_half_hull(datastructures.LOWER)
    
    for i in xrange(len(pts)):
        for j in xrange(i+1, len(pts)):
            l = line(pts[i], pts[j])
            intersection = l.evalx(p[0])
            if intersection > p[1]:
                upper.insert(dualize(l), l)
            elif intersection < p[1]:
                lower.insert(dualize(l), l)
                
    U, L = getRegionR(upper, lower)
    
    start = getPolygon(U, L)
    yield start
    visitedPolygons = set()
    visitedPolygons.add(getPolygonKey(start))
    
    class region(object):
        def __init__(self, regionU, regionL, lastEdge = None, side = None):
            self.regionU = regionU
            self.regionL = regionL
            self.total = len(regionU) + len(regionL)
            self.edgeIndex = random.randint(0, self.total-1)
            self.i = 0
            self.lastEdge = lastEdge
            self.side = side
                
    S = deque()
    S.append(region(U, L))
    
    while len(S) > 0:
        
        current = S[-1]
        regionU, regionL = current.regionU, current.regionL
        
        if current.i < current.total:
            current.i += 1
            current.edgeIndex = (current.edgeIndex + 1) % current.total
#            print " "*len(S), "Will use", current.edgeIndex, " of" , current.total
            if current.edgeIndex < len(regionU):
                crossingEdge = regionU[current.edgeIndex][1]
                side = UP
            else:                
                crossingEdge = regionL[current.edgeIndex - len(regionU)][1]
                side = DOWN
            p1, p2 = crossingEdge.getPoints()
            if p1 > p2:
                p1, p2 = p2, p1
            if [p1, p2] == current.lastEdge:
#                print " "*len(S), "points", p1, p2, [p1, p2]
#                print " "*len(S), "lastedge!"
                continue
#            print "next line"
    
            if side == UP:
                upper.delete(dualize(crossingEdge))
                lower.insert(dualize(crossingEdge), crossingEdge)
        
            elif side == DOWN:
                lower.delete(dualize(crossingEdge))
                upper.insert(dualize(crossingEdge), crossingEdge)
        
            U, L = getRegionR(upper, lower) #TODO: write a composing function
            poly = getPolygon(U,L)
            triang = getPolygonKey(poly)
            
            if triang not in visitedPolygons:
                visitedPolygons.add(triang)
                yield poly
                if len(visitedPolygons) > length:
                    break
                S.append( region( U, L, [p1,p2], side) )
#                print "level", len(S)
            else:
                if side == UP:   
                    lower.delete(dualize(crossingEdge))
                    upper.insert(dualize(crossingEdge), crossingEdge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(crossingEdge))
                    lower.insert(dualize(crossingEdge), crossingEdge)
        else:
#            print " "*len(S), "done"
            if len(S) > 1:
                p1, p2 = current.lastEdge
                edge = line(p1, p2)
                
                if current.side == UP:                    
                    lower.delete(dualize(edge))
                    upper.insert(dualize(edge), edge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(edge))
                    lower.insert(dualize(edge), edge)
#            print " "*len(S), "pop!"
            S.pop()
            
def getRandomWalkPent(pts):
    p = [random.randint(-100000000, 100000000), random.randint(-100000000, 100000000)]
    
    def search(p):
        for pt in pts:
            if p[0] == pt[0] and p[1] == pt[1]:
                return True
        return False
    
    upper = datastructures.dynamic_half_hull(datastructures.UPPER)
    lower = datastructures.dynamic_half_hull(datastructures.LOWER)
    
    for i in xrange(len(pts)):
        l = line(pts[i], pts[(i+1)%len(pts)])
        intersection = l.evalx(p[0])
        if intersection > p[1]:
            upper.insert(dualize(l), l)
        elif intersection < p[1]:
            lower.insert(dualize(l), l)
                
    U, L = getRegionR(upper, lower)
    start = getPolygon(U, L, 10000000000)
    
    originalPoints = 0
    for pt in start:
        if search(pt):
            originalPoints += 1
    if originalPoints != 2:
        yield start
        
    visitedPolygons = set()
    visitedPolygons.add(getPolygonKey(start))
    
    class region(object):
        def __init__(self, regionU, regionL, lastEdge = None, side = None):
            self.regionU = regionU
            self.regionL = regionL
            self.total = len(regionU) + len(regionL)
            self.edgeIndex = random.randint(0, self.total-1)
            self.i = 0
            self.lastEdge = lastEdge
            self.side = side
                
    S = deque()
    S.append(region(U, L))
    
    while len(S) > 0:
        
        current = S[-1]
        regionU, regionL = current.regionU, current.regionL
        
        if current.i < current.total:
            current.i += 1
            current.edgeIndex = (current.edgeIndex + 1) % current.total
#            print " "*len(S), "Will use", current.edgeIndex, " of" , current.total
            if current.edgeIndex < len(regionU):
                crossingEdge = regionU[current.edgeIndex][1]
                side = UP
            else:                
                crossingEdge = regionL[current.edgeIndex - len(regionU)][1]
                side = DOWN
            p1, p2 = crossingEdge.getPoints()
            if p1 > p2:
                p1, p2 = p2, p1
            if [p1, p2] == current.lastEdge:
#                print " "*len(S), "points", p1, p2, [p1, p2]
#                print " "*len(S), "lastedge!"
                continue
#            print "next line"
    
            if side == UP:
                upper.delete(dualize(crossingEdge))
                lower.insert(dualize(crossingEdge), crossingEdge)
        
            elif side == DOWN:
                lower.delete(dualize(crossingEdge))
                upper.insert(dualize(crossingEdge), crossingEdge)
        
            U, L = getRegionR(upper, lower) #TODO: write a composing function
            poly = getPolygon(U, L, 10000000000)
            triang = getPolygonKey(poly)
            
            if triang not in visitedPolygons:
                visitedPolygons.add(triang)
                originalPoints = 0
                for pt in poly:
                    if search(pt):
                        originalPoints += 1
                if originalPoints != 2:
                    yield poly
                S.append( region( U, L, [p1,p2], side) )
#                print "level", len(S)
            else:
                if side == UP:   
                    lower.delete(dualize(crossingEdge))
                    upper.insert(dualize(crossingEdge), crossingEdge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(crossingEdge))
                    lower.insert(dualize(crossingEdge), crossingEdge)
        else:
#            print " "*len(S), "done"
            if len(S) > 1:
                p1, p2 = current.lastEdge
                edge = line(p1, p2)
                
                if current.side == UP:                    
                    lower.delete(dualize(edge))
                    upper.insert(dualize(edge), edge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(edge))
                    lower.insert(dualize(edge), edge)
#            print " "*len(S), "pop!"
            S.pop()
            
def getRandomWalkN2Graham(p, pts, length=10):
#    p = [random.randint(-100000000, 100000000), random.randint(-100000000, 100000000)]
    
    upper = []
    lower = []
    
    for i in xrange(len(pts)):
        for j in xrange(i+1, len(pts)):
            l = line(pts[i], pts[j])
            intersection = l.evalx(p[0])
            if intersection > p[1]:
                upper.append([dualize(l), l])
            elif intersection < p[1]:
                lower.append([dualize(l), l])
                
    def hull(Points, side):
        '''Graham scan to find upper and lower convex hulls of a set of 2d points.'''
        H = []
        Points.sort()
        for p in Points:
            if side == datastructures.UPPER:
                while len(H) > 1 and turn(H[-2][0],H[-1][0],p[0]) <= 0: H.pop()
            if side == datastructures.LOWER:
                while len(H) > 1 and turn(H[-2][0],H[-1][0],p[0]) >= 0: H.pop()
            H.append(p)
        if side == datastructures.LOWER:
            H.reverse()
        return H
                
    U = hull(upper, datastructures.UPPER)
    L = hull(lower, datastructures.LOWER)
    U, L = getRegionR(U, L, False)
    
    start = getPolygon(U, L)
    yield start
    visitedPolygons = set()
    visitedPolygons.add(getPolygonKey(start))
    
    class region(object):
        def __init__(self, regionU, regionL, lastEdge = None, side = None):
            self.regionU = regionU
            self.regionL = regionL
            self.total = len(regionU) + len(regionL)
            self.edgeIndex = random.randint(0, self.total-1)
            self.i = 0
            self.lastEdge = lastEdge
            self.side = side
                
    S = deque()
    S.append(region(U, L))
    
    while len(S) > 0:
        current = S[-1]
        regionU, regionL = current.regionU, current.regionL
        
        if current.i < current.total:
            current.i += 1
            current.edgeIndex = (current.edgeIndex + 1) % current.total
#            print " "*len(S), "Will use", current.edgeIndex, " of" , current.total
            if current.edgeIndex < len(regionU):
                crossingEdge = regionU[current.edgeIndex][1]
                side = UP
            else:                
                crossingEdge = regionL[current.edgeIndex - len(regionU)][1]
                side = DOWN
            p1, p2 = crossingEdge.getPoints()
            if p1 > p2:
                p1, p2 = p2, p1
            if [p1, p2] == current.lastEdge:
#                print " "*len(S), "points", p1, p2, [p1, p2]
#                print " "*len(S), "lastedge!"
                continue
#            print "next line"
    
            if side == UP:
                upper.pop(upper.index([dualize(crossingEdge), crossingEdge]))
                lower.append([dualize(crossingEdge), crossingEdge])
        
            elif side == DOWN:
                lower.pop(lower.index([dualize(crossingEdge), crossingEdge]))
                upper.append([dualize(crossingEdge), crossingEdge])
        
            U = hull(upper, datastructures.UPPER)
            L = hull(lower, datastructures.LOWER)         
            U, L = getRegionR(U,L,False) #TODO: write a composing function
            poly = getPolygon(U,L)
            triang = getPolygonKey(poly)
            
            if triang not in visitedPolygons:
                visitedPolygons.add(triang)
                yield poly
                if len(visitedPolygons) > length:
                    break
                S.append( region( U, L, [p1,p2], side) )
#                print "level", len(S)
            else:
                if side == UP:   
                    lower.pop(lower.index([dualize(crossingEdge), crossingEdge]))
                    upper.append([dualize(crossingEdge), crossingEdge])
                else:
                    upper.pop(upper.index([dualize(crossingEdge), crossingEdge]))
                    lower.append([dualize(crossingEdge), crossingEdge])
        else:
#            print " "*len(S), "done"
            if len(S) > 1:
                p1, p2 = current.lastEdge
                edge = line(p1, p2)
                
                if current.side == UP:
                    lower.pop(lower.index([dualize(edge), edge]))
                    upper.append([dualize(edge), edge])
                else:
                    upper.pop(upper.index([dualize(edge), edge]))
                    lower.append([dualize(edge), edge])
#            print " "*len(S), "pop!"
            S.pop()
            
#def generateSpiralWalk(p, pts, length = 10):
#    ordered, indices = orderAllPoints(p, pts)
#    upper, lower, counter = getPointRegion(p, ordered, indices)  # TODO: USE COUNTER!!!
#    U, L = getRegionR(upper, lower)
#    forbiddenEdges = set()
#    current = getPolygon(U, L)
#    n = (len(indices) - 1) * 2
#    yield current
#    length -= 1
#    print "current", current
#    print
#    last = tuple(current[0])
#    print "crossing", last
#    print
#    jump = 0
#    
#    side = None
#    for edge in current:
#        forbiddenEdges.add(tuple(sorted(edge)))
#    
##    for edge in forbiddenEdges:
##        print edge
#        
#    while length > 0:
#        if jump < len(U)-1:
#            edge = U[jump][1]
#            side = UP
#        else:
#            edge = L[jump-len(U)][1]
#            side = DOWN
#        p1, p2 = edge.getPoints()
#                
#        line1, line2, U, L = crossEdge(n, p1, p2, side, upper, lower, indices, ordered)
#        print "lens", len(U), len(L)
#        current = getPolygon(U, L)
#        yield current
#        length -=1
#        jump = 0
#        print "current", current
#        print "jump", jump
#        print
#        jump = current.index(list(last))
#        jump += 1 
##        print current[jump], "vs", last
##        while tuple(current[jump]) != last:
##            jump = (jump+1)%len(current)
##            print tuple(current[jump]), "vs", last, tuple(current[jump]) != last
#        while tuple(current[jump]) in forbiddenEdges:
#            jump = (jump+1)%len(current)
#        last = tuple(current[jump])
#        print "crossing", last
#        print "jump", jump
#        print

def factorial(n):
    res = 1
    for i in xrange(1, n+1):
        res *= i
    return res
    
def choose(n, k):
    return factorial(n)/(factorial(n-k)*factorial(k))

def cellsNumber(n):
    if n == 2:
        return 2
    return cellsNumber(n-1) + (n-1)*(choose(n-1, 2)-n+5)-1
    
def randPointPolygon(poly, tries=100):
    triangs = [[poly[0], poly[i], poly[i+1]] for i in xrange(1, len(poly)-1)]
    
    weights = map(triangArea, triangs)
    
    totalArea = reduce(lambda a,b : a+b, weights)
    weights = map(lambda x : x/totalArea, weights)
    weights = [sum(weights[:i]) for i in xrange(1, len(weights)+1 )]
    
    while tries > 0:
        index = bisect.bisect(weights, random.random())
        p = randPointTriang(triangs[index])
        if p is not None:
            return p
        tries -= 1
#    print "Warning, no point found in", poly
    return None
    

def randPointTriang(triang, tries=100):
    v1 = [0,0]
    v1[0] = triang[1][0]-triang[0][0]
    v1[1] = triang[1][1]-triang[0][1]
    
    v2 = [0,0]
    v2[0] = triang[2][0]-triang[0][0]
    v2[1] = triang[2][1]-triang[0][1]
    
    funcs = [lambda n: int(ceil(n)), lambda n: int(floor(n))]
    while tries>0:
        a = random.random()
        b = random.random()
        while a+b > 1:
            a = random.random()
            b = random.random()
        p = [0,0]
        p[0] = a*float(v1[0])+b*float(v2[0])+float(triang[0][0])
        p[1] = a*float(v1[1])+b*float(v2[1])+float(triang[0][1])
        
        for f in funcs:
            for g in funcs:
                candidate = [f(p[0]), g(p[1])]
                if pointInPolygon(candidate, triang) and not sameXCoord(candidate, triang):
                    return candidate
        
        tries -= 1
    return None
        

def triangArea(triang):
    a, b, c = triang
    area = a[0]*(b[1] - c[1]) + b[0]*(c[1] - a[1]) + c[0]*(a[1] - b[1])
    if isinstance(area, rational):
        area /= 2
    else:
        area /= 2.0
    return abs(float(area))

#Added by Ruy

def get_all_extensions(pts,debug=False):
    """Returns (pts,C) where pts is a posibly scaled copy of pts
    and C is a list of all the posible extentions of pts. That is
    one point with integer coordinates per cell of the arrengement
    generated by pts"""
    min_x=min(pts,key=lambda x:x[0])[0]
    max_x=max(pts,key=lambda x:x[0])[0]
    min_y=min(pts,key=lambda x:x[1])[1]
    max_y=max(pts,key=lambda x:x[1])[1]
    if debug:
        print min_x,max_x,min_y,max_y
    p=[random.randint(min_x,max_x),random.randint(min_y,max_y)]
    pts.append(p)
    while not general_position(pts):
        pts.pop()
        p=[random.randint(min_x,max_x),random.randint(min_y,max_y)]
        pts.append(p)
    pts.pop()
    W=getRandomWalkDFS(p,pts,length=-1)
    C=[]
    r=1
    i=0
    for Q in W:
        i=i+1
        if debug:
            print i, r
        Qt=[[r*x[0],r*x[1]] for x in Q]
        p=randPointPolygon(Qt,tries=10)
        while p==None:
            r=r*2
            Qt=[[r*x[0],r*x[1]] for x in Q]
            p=randPointPolygon(Qt,tries=10)
        C.append([p,r])
    pts=[[r*x[0],r*x[1]] for x in pts]
    C=[[x[0][0]*(r/x[1]),x[0][1]*(r/x[1])] for x in C]
    return (pts,C)
    
# def _test_extentions(pts,C):
#     P=[(x[0],x[1]) for x in pts]
#     D={}
#     for x in P:
#         D[x]=pts.index([x[0],x[1]])
#     return D
    
def getAndPaintPolygons(p, pts, distance=float('inf'), strict = False, getPairs = False):
    """Returns all the cells in the line array at distance at most `distance`, as
    Polyons colored in the following way:
     -green if the distance is 0 mod 3
     -purple if the cell is at distance 1 mod 3
     -red if the distance is 2 mod 3     
    """
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counters = getPointRegion(p, ordered, indices)
    U, L = getRegionR(upper, lower)
    n = (len(indices) - 1) * 2
    
    start = getPolygon(U, L)
    colors = {0:"green", 1:"purple", 2:"red"}
    currDistance = 0
    if not strict or currDistance == distance:
#    if not strict or currDistance%3 == 0:
        if getPairs:
            res = []
            for l in U:
                endpoints = l[1].getPoints()
                endpoints = tuple(endpoints[0]), tuple(endpoints[1])
                res.append(endpoints)
            for l in L:
                endpoints = l[1].getPoints()
                endpoints = tuple(endpoints[0]), tuple(endpoints[1])
                res.append(endpoints)
            yield res
        else:
            yield Polygon(start, colors[0])
    
    visitedPolygons = set()
    visitedPolygons.add(getPolygonKey(start))
    
    
    class region(object):
        def __init__(self, regionU, regionL, lastEdge = None, side = None, neighbors1=None, neighbors2=None, lines1=None, lines2=None):
            self.regionU = regionU
            self.regionL = regionL
            self.total = len(regionU) + len(regionL)
            self.edgeIndex = random.randint(0, self.total-1)
            self.i = 0
            self.lastEdge = lastEdge
            self.side = side
            self.neighbors1 = neighbors1
            self.neighbors2 = neighbors2
            self.lines1 = lines1
            self.lines2 = lines2
    
    def update(p, q, ant, suc):
        antipodal = False
        if ordered[tuple(p)][ant] == q:
            oldline = line(p, ordered[tuple(p)][suc])
            indices[tuple(p)][0] = [(ant - 1) % n, ant]
            newpoint = ordered[tuple(p)][(ant - 1) % n]
            if ant in indices[tuple(p)][1]:
                antipodal = True
        else:
            oldline = line(p, ordered[tuple(p)][ant])
            indices[tuple(p)][0] = [suc, (suc + 1) % n]
            newpoint = ordered[tuple(p)][(suc + 1) % n]
            if suc in indices[tuple(p)][1]:
                antipodal = True

        newline = line(p, newpoint)
        aux = [p[0], p[1] + 1]
        
        # TODO: Explain why this works
        sameTurn = turn(p, q, newpoint) == turn(p, aux, newpoint)
        
        keyold = tuple(dualize(oldline))
        counters[keyold] -= 1
        oldSide = None
        
        if counters[keyold] == 0:
            try:
                upper.delete(dualize(oldline))
                oldSide = UP
            except:
                lower.delete(dualize(oldline)) #TODO: Should know whether it's inside upper or lower
                oldSide = DOWN
        
        keynew = tuple(dualize(newline))
        counters.setdefault(keynew, 0)
        counters[keynew] += 1
        
        if sameTurn == antipodal:#TODO: check this part
            if counters[keynew] == 1:
                upper.insert(dualize(newline), newline)
            return newline, UP, oldline, oldSide #new goes to up, old was in oldside
        else:
            if counters[keynew] == 1:
                lower.insert(dualize(newline), newline)
            return newline, DOWN, oldline, oldSide
    
    def restore(lines):
        newkey = tuple(dualize(lines[0])) 
        counters[newkey] -= 1
        if counters[newkey] == 0:
            if lines[1] == UP:
                upper.delete(dualize(lines[0]))
            else:
                lower.delete(dualize(lines[0]))
                
        oldkey = tuple(dualize(lines[2]))
        counters[oldkey] += 1
        if counters[oldkey] == 1:
            if lines[3] == UP:
                upper.insert(dualize(lines[2]),lines[2])
            else:
                lower.insert(dualize(lines[2]),lines[2])
                
    S = deque()
    S.append(region(U, L))
    
    while len(S) > 0:
        
        current = S[-1]
        regionU, regionL = current.regionU, current.regionL
        
        if current.i < current.total:
            current.i += 1
            current.edgeIndex = (current.edgeIndex + 1) % current.total
#            print " "*len(S), "Will use", current.edgeIndex, " of" , current.total
            if current.edgeIndex < len(regionU):
                crossingEdge = regionU[current.edgeIndex][1]
                side = UP
            else:                
                crossingEdge = regionL[current.edgeIndex - len(regionU)][1]
                side = DOWN
            p1, p2 = crossingEdge.getPoints()
#            if p1 > p2:
#                p1, p2 = p2, p1
            
            inc = turn(p1, p2, p)*side
            
            if [p1, p2] == current.lastEdge or currDistance+inc > distance:
#                print " "*len(S), "points", p1, p2, [p1, p2]
#                print " "*len(S), "lastedge!"
                continue
#            print "next line"
        
            ant1, suc1 = indices[tuple(p1)][0]            
            ant2, suc2 = indices[tuple(p2)][0]
    
            if side == UP:
                upper.delete(dualize(crossingEdge))
                lower.insert(dualize(crossingEdge), crossingEdge)
        
            elif side == DOWN:
                lower.delete(dualize(crossingEdge))
                upper.insert(dualize(crossingEdge), crossingEdge)
            
            # We update ant and suc for p1 and insert the new line in 
            # the appropiate envelope
            lines1 = update(p1, p2, ant1, suc1)
            # We do the same for p2       
            lines2 = update(p2, p1, ant2, suc2)
        
            U, L = getRegionR(upper, lower) #TODO: write a composing function
            poly = getPolygon(U,L)
            triang = getPolygonKey(poly)
            
            if triang not in visitedPolygons:
                visitedPolygons.add(triang)
                currDistance += inc
#                print "found one, distance", currDistance
                if not strict or currDistance == distance:
#                if not strict or currDistance%3 == 0:
                    if getPairs:
                        res = []
                        for l in U:
                            endpoints = l[1].getPoints()
                            endpoints = tuple(endpoints[0]), tuple(endpoints[1])
                            res.append(endpoints)
                        for l in L:
                            endpoints = l[1].getPoints()
                            endpoints = tuple(endpoints[0]), tuple(endpoints[1])
                            res.append(endpoints)
                        yield res
                    else:
                        yield Polygon(poly, colors[currDistance%3])

                #regions += 1
#                regions.append(poly)
#                print "                               van", len(regions)
#                print " "*len(S), "push!, I crossed", crossingEdge
                S.append( region( U, L, [p1,p2], side, (ant1, suc1), (ant2, suc2), lines1, lines2 ) )
#                print "level", len(S)
               # if regions >= length and length>=0:
                   # print "found enough regions"
                    #break
            else:
#                print " "*len(S), "already visited"
                indices[tuple(p1)][0] = [ant1, suc1]
                indices[tuple(p2)][0] = [ant2, suc2]
                            
                restore(lines1)
                restore(lines2)
                
                if side == UP:   
                    lower.delete(dualize(crossingEdge))
                    upper.insert(dualize(crossingEdge), crossingEdge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(crossingEdge))
                    lower.insert(dualize(crossingEdge), crossingEdge)
        else:
#            print " "*len(S), "done"
            if len(S) > 1:
                
                p1 = current.lastEdge[0]
                p2 = current.lastEdge[1]
                indices[tuple(p1)][0] = [current.neighbors1[0], current.neighbors1[1]]
                indices[tuple(p2)][0] = [current.neighbors2[0], current.neighbors2[1]]
                            
                restore(current.lines1)
                restore(current.lines2)
                    
                edge = line(p1, p2)
                inc = turn(p1, p2, p)*current.side
                currDistance -= inc
#                print "returning", currDistance
#                print " "*len(S), "returning via", edge
                
                if current.side == UP:                    
                    lower.delete(dualize(edge))
                    upper.insert(dualize(edge), edge) #TODO: should be able to dualize the point instead of adding the line as an object, right?
                else:
                    upper.delete(dualize(edge))
                    lower.insert(dualize(edge), edge)
#            print " "*len(S), "pop!"
            S.pop()
            
def jumpDistance(p, cell, edge):
    """Returns FARTHER or CLOSER, depending on the distance of the region adjacent to cell at edge"""
    #assert edge[0] < edge[1]
    return FARTHER if (cell.edgeIndices[edge][1] == UP and turn(edge[0], edge[1], p) == RIGHT) or \
                          (cell.edgeIndices[edge][1] == DOWN and turn (edge[0], edge[1], p) == LEFT) \
                       else CLOSER
    
            
def moveNCells(p, cell, jumps=3, forbiddenEdge = None, getCenters = False):#, reclevel=1):
    """
    Tries to jump `jumps` cells, relative to p. If succesfull, it returns a list
    where each element is a pair (edge, vertices), with the edge jumped and the vertices
    of the cell from where the jump is performed (i.e. the vertices of the first pair are the vertices
    of the orifinal cell).
    """
#    print "cell vertices", cell.vertices
#    print "jumps", jumps
#    """Jumps to a cell at distance `jumps` from this cell with respect to p"""
    inc = -1 if jumps > 0 else 1
    # i = 0
    for edge in cell.edges:
        # print "*"*reclevel, "checking edge", i, "of", cell.edges
        # i += 1
#        if edge == forbiddenEdge:
#            continue
#        print "side", cell.edgeIndices[edge]
#        print "turn", turn(edge[0], edge[1], p)
        # assert edge in cell.edges
        # assert edge in cell.edgeIndices
        move = jumpDistance(p, cell, edge)
#        print "edge", edge, "moves", "farther" if move == FARTHER else "closer"
        if (move == FARTHER and jumps > 0) or (move == CLOSER and jumps < 0):
#            print "One jump!", edge
#            center = randPointPolygon(cell.vertices)
#            assert center is not None
            current = [[edge, copy.deepcopy(cell.vertices)]]
            cell.jumpEdge(edge)
            if abs(jumps) == 1:
                if getCenters:
                    return current
                return [edge]
            res =  moveNCells(p, cell, jumps+inc, forbiddenEdge, getCenters)#, reclevel+1)
            if len(res) > 0:
                if getCenters:
                    return current + res
                return [edge] + res
            else:
                cell.jumpEdge(edge)
    return []
    
def xJump(p, cell, edge, jumpDir = 1, getAuxpt = False):
    """Tries to make an -+ x jump. Returns True and last jumped edge if succesful, else False and None"""
    dist = jumpDistance(p, cell, edge)
    if dist != CLOSER:
        if getAuxpt:
            return False, [None, None]
        return False, None
    cell.jumpEdge(edge)
    nextEdge = cell.edges.index(edge)
    nextEdge = cell.edges[(nextEdge+jumpDir)%len(cell.edges)]
    dist += jumpDistance(p, cell, nextEdge)
    auxvertices = cell.vertices
#    assert auxpt is not None
    if dist == 0:
        cell.jumpEdge(nextEdge)
        if getAuxpt:
            return True, [nextEdge, auxvertices]
        return True, nextEdge
    cell.jumpEdge(edge)
    if getAuxpt:
        return False, [None, None]
    return False, None
    
def semiCopy(cell):
    newCell = Cell([0,0], [[1,1],[2,3],[6,10]])
    newCell.points = cell.points
    newCell.p = cell.p
    newCell.ordered = cell.ordered
    
    newCell.upper = copy.deepcopy(cell.upper)
    newCell.lower = copy.deepcopy(cell.lower)
    newCell.indices = copy.deepcopy(cell.indices)
    newCell.counters = copy.deepcopy(cell.counters)
    
    newCell._updateEdges()
    return newCell
    
def testCr(startp, newp, pts, M, D, cr, edge):
    if  ordertypes.lambda_matrix(pts+[newp])!=M:
        return False, "Matrix"
    if crossing.count_crossings(pts+[newp])!=cr:
        return False, "CR"
    ch_cr=chg_cr(M,D,startp,edge,newp)
    cr=cr+ch_cr
    update_lambda_matrix(M,D,startp,edge,newp)
    return True, cr
    
def genSpiralWalk(p, pts, levels=float('inf'), getPols = False):
    """Returns all the cells in the line array of pts whose distance from p's cell satisfies:
    distance%3 = 0 and distance/3 <= levels.
    """
    
    start = Cell(p, pts)    
    level = 0
    
    if getPols:
        yield Polygon(start.vertices, "blue")
    else:
        yield start.edges
        
    
    
    
    ################################################33
#    auxpt = p
#    M=ordertypes.lambda_matrix(pts+[p])
#    D=ordertypes.points_index(pts+[p])   
#    cr=crossing.count_crossings(pts+[p])
    ################################################
    
    edge = moveNCells(p, start, 3)
    
    if len(edge) == 0:
        return
        
    ################################################3
#    for e in reversed(edge):
#        start.jumpEdge(e)
#    for e in edge:
#        res, mes = testCr(p, auxpt, pts, M, D, cr, e)
#        if not res:
#            raise Exception(mes)
#        else:
#            print "all good"
#            cr = mes
#        start.jumpEdge(e)
#        auxpt = getCenter(start.vertices)
        
    #################################################
    
    edge = edge[-1]    #edge is the edge which we jumped to land in the current cell
    
    
    while(level < levels and start is not None):
        print "                                           level", level+1
        print "starting with"
        print start.vertices
        firstEdge = edge
        
        if getPols:
            yield Polygon(start.vertices, "blue")
        else:
            yield start.edges
        
        nextStart = None
        nextFound = False
        nextEdge = None
        
        firstIndex = None
        finished = False
        starJump = False
        current = semiCopy(start)
        #################################################### TO THE LEFT ###############################################
        while not finished: #We go to the left
            lastVisited = current.edges
            print "To the left!                               "
#            print "current pre", current.edges
            if not nextFound:
                print "                                not found yet"
                nextStart = semiCopy(current)
                res = moveNCells(p, nextStart, 3)
                if len(res) > 0:
                    print "                                     FOUNDNEXT"
                    print nextStart.vertices
                    nextFound = True
                    nextEdge = res[-1]
                else:
                    nextStart = None
            
            edgeIndex = current.edges.index(edge)
                
            #Try an usual jump over every edge
            for i in xrange(len(current.edges)):
#                print "index", edgeIndex
                res, newEdge = xJump(p, current, current.edges[edgeIndex%len(current.edges)])
                
                if res:
                    if current.edges == lastVisited:
                        res = False
                        continue
                    if starJump:
                        starJump = False
                    edge = newEdge
                    if firstIndex == None:
                        firstIndex = edgeIndex
                    if current.edges != start.edges:
                        if getPols:
                            yield Polygon(current.vertices, "blue")
                        else:
                            yield current.edges
                    else:
#                        print "back to start"
                        finished = True
                    break
                edgeIndex -= 1
                
            if not res and not starJump: #We couldn't make an usual jump, try to starjump
#                print "No res"                
                star = False
                
                for i in xrange(-1,len(current.edges)-1):
                    e1 = current.edges[i]
                    e2 = current.edges[i+1]
                    if e1[0] in e2 and list(e1[0]) in current.vertices:
                        starPoint = e1[0]
                        star = True
                        break
                    if e1[1] in e2 and list(e1[1]) in current.vertices:
                        starPoint = e1[1]
                        star = True
                        break
                
#                print "star check:", star    
                if not star:
#                    print "Nothng else to do"
                    break
                
                starEdge = i
                
#                print "trying starjump"
                edge = current.edges[starEdge+1]
                dist = jumpDistance(p, current, edge)
                current.jumpEdge(edge)
                
                while dist != 0: #Jumping around starPoint
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        edge = current.edges[(index+1)%len(current.edges)]
                    else:
                        edge = current.edges[(index-1)%len(current.edges)]
                    dist += jumpDistance(p, current, edge)
                    current.jumpEdge(edge)
                    
                #We check than we landed in the right direction
                vertexCheck = 0
                while turn(edge[0], edge[1], current.vertices[vertexCheck]) == COLLINEAR:
                    vertexCheck += 1
#                print "giving to turn", p, starPoint, current.vertices[vertexCheck]
#                print
                if turn(p, starPoint, current.vertices[vertexCheck]) == LEFT:
#                    print "starjump"
                    starJump = True
                    res = True
                    if current.edges != start.edges:
    #                        print "back to start"
                        if getPols:
                            yield Polygon(current.vertices, "blue")
                        else:
                            yield current.edges
                        #We need to set the right edge
                        index = current.edges.index(edge)
                        if starPoint in current.edges[(index+1)%len(current.edges)]:
                            otherEdge = current.edges[(index+1)%len(current.edges)]
                        else:
                            otherEdge = current.edges[(index-1)%len(current.edges)]
                        vertexE = 0
                        while turn(edge[0], edge[1], current.vertices[vertexE]) != COLLINEAR:
                            vertexE += 1
                        vertexO = 0
                        while turn(edge[0], edge[1], current.vertices[vertexO]) != COLLINEAR:
                            vertexO += 1
                        if turn(starPoint, current.vertices[vertexE], current.vertices[vertexO]) == turn(starPoint, current.vertices[vertexE], p):
                            edge = otherEdge
                    else:
                        finished = True
                else: #The direction changed
#                    print "wall inside, inversion"
                    break
                
            if not res:
#                print "wall final, nothing else to do"
                break
        #################################################### END TO THE LEFT ###############################################            
#        print "finished?", finished
        edge = firstEdge
        current = start
        #################################################### TO THE RIGHT ###############################################
        while not finished: #We go to the right
            lastVisited = current.edges 
            print "To the right!                              "
#            print "current pre", current.edges
            if not nextFound:
                nextStart = semiCopy(current)
                print "                                        Not found yet!"
                res = moveNCells(p, nextStart, 3)
                if len(res) > 0:
                    print "                                     FOUNDNEXT"
                    print nextStart.vertices
#                    nextStart = semiCopy(current)
                    nextFound = True
                    nextEdge = res[-1]
                else:
#                    print "                                       Set to None"
                    nextStart = None
            
            edgeIndex = current.edges.index(edge)
                
            #Try an usual jump over every edge
#            print "trying usual"
            for i in xrange(len(current.edges)):
#                print "index", edgeIndex
                res, newEdge = xJump(p, current, current.edges[edgeIndex%len(current.edges)], -1)
                
                if res:
                    if current.edges == lastVisited:
#                        print "repeating"
                        res = False
                        continue
                    if starJump:
                        starJump = False
                    edge = newEdge
                    if firstIndex == None:
                        firstIndex = edgeIndex
                    if getPols:
                        yield Polygon(current.vertices, "blue")
                    else:
                        yield current.edges
                    break
                edgeIndex += 1
#            print "res, starJump is ", res, starJump
#            print 
            if not res and not starJump: #We couldn't make an usual jump, try to starjump
#                print "No res"                
                star = False
                
                for i in xrange(-1,len(current.edges)-1):
                    e1 = current.edges[i]
                    e2 = current.edges[i+1]
                    if e1[0] in e2 and list(e1[0]) in current.vertices:
                        starPoint = e1[0]
                        star = True
                        break
                    if e1[1] in e2 and list(e1[1]) in current.vertices:
                        starPoint = e1[1]
                        star = True
                        break
                
#                print "star check:", star    
                if not star:
#                    print "Nothng else to do"
                    break
                
                starEdge = i
                
#                print "trying starjump"
                edge = current.edges[starEdge+1]
                dist = jumpDistance(p, current, edge)
                current.jumpEdge(edge)
                
                while dist != 0: #Jumping around starPoint
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        edge = current.edges[(index+1)%len(current.edges)]
                    else:
                        edge = current.edges[(index-1)%len(current.edges)]
                    dist += jumpDistance(p, current, edge)
                    current.jumpEdge(edge)
                    
                #We check than we landed in the right direction
                vertexCheck = 0
                while turn(edge[0], edge[1], current.vertices[vertexCheck]) == COLLINEAR:
                    vertexCheck += 1
#                print "giving to turn", p, starPoint, current.vertices[vertexCheck]
#                print
                if turn(p, starPoint, current.vertices[vertexCheck]) == RIGHT:
#                    print "starjump"
                    starJump = True
                    res = True
#                    print "yielding"
#                        print "back to start"
                    if getPols:
                        yield Polygon(current.vertices, "blue")
                    else:
                        yield current.edges
                    #We need to set the right edge
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        otherEdge = current.edges[(index+1)%len(current.edges)]
                    else:
                        otherEdge = current.edges[(index-1)%len(current.edges)]
                    vertexE = 0
                    while turn(edge[0], edge[1], current.vertices[vertexE]) != COLLINEAR:
                        vertexE += 1
                    vertexO = 0
                    while turn(edge[0], edge[1], current.vertices[vertexO]) != COLLINEAR:
                        vertexO += 1
                    if turn(starPoint, current.vertices[vertexE], current.vertices[vertexO]) == turn(starPoint, current.vertices[vertexE], p):
                        edge = otherEdge
                    
                else: #The direction changed
#                    print "wall inside, inversion"
                    break
#            print 'AAAAAAAAAAAAAAA'    
            if not res:
#                print "wall final, nothing else to do"
                break
        #################################################### END TO THE RIGHT ###############################################
        print "END LEVEL", nextFound
        level += 1        
        start = nextStart
        edge = nextEdge
            
class Cell(object):
    def __init__(self, p, points):
        self.points = copy.deepcopy(points)
        self.p = copy.deepcopy(p)
        self.ordered, self.indices = orderAllPoints(p, points)
        self.upper, self.lower, self.counters = getPointRegion(self.p, self.ordered, self.indices)
        self.U, self.L = getRegionR(self.upper, self.lower)
        self.vertices = getPolygon(self.U, self.L)
        self.edges = []
        self.edgeIndices = {}
        self._updateEdges()
            
    def _updateEdges(self):
        self.U, self.L = getRegionR(self.upper, self.lower)
        self.edges = []
        self.edgeIndices = {}
        for l in self.U:
            endpoints = l[1].getPoints()
            endpoints = tuple(endpoints[0]), tuple(endpoints[1])
            self.edges.append(endpoints)
            self.edgeIndices[endpoints] = [l[1], UP]
        for l in reversed(self.L):
            endpoints = l[1].getPoints()
            endpoints = tuple(endpoints[0]), tuple(endpoints[1])
            self.edges.append(endpoints)
            self.edgeIndices[endpoints] = [l[1], DOWN]
        self.vertices = getPolygon(self.U, self.L)
            
    def jumpEdge(self, edge):
        p1, p2 = edge
        if list(p1) not in self.points or list(p2) not in self.points:
            raise ValueError("Both points must belong to the point set.")
        
        crossingEdge, side = self.edgeIndices[edge]
    
        ant1, suc1 = self.indices[p1][0]
        ant2, suc2 = self.indices[p2][0]

        if side == UP:
            self.upper.delete(dualize(crossingEdge))
            self.lower.insert(dualize(crossingEdge), crossingEdge)
    
        elif side == DOWN:
            self.lower.delete(dualize(crossingEdge))
            self.upper.insert(dualize(crossingEdge), crossingEdge)
        
        # We update ant and suc for p1 and insert the new line in 
        # the appropiate envelope
        self.update(p1, p2, ant1, suc1)
        # We do the same for p2       
        self.update(p2, p1, ant2, suc2)
        
    def update(self, p, q, ant, suc):
        n = (len(self.indices) - 1) * 2
        antipodal = False
        if self.ordered[tuple(p)][ant] == list(q):
            oldline = line(p, self.ordered[tuple(p)][suc])
            self.indices[tuple(p)][0] = [(ant - 1) % n, ant]
            newpoint = self.ordered[tuple(p)][(ant - 1) % n]
            if ant in self.indices[tuple(p)][1]:
                antipodal = True
        else:
            oldline = line(p, self.ordered[tuple(p)][ant])
            self.indices[tuple(p)][0] = [suc, (suc + 1) % n]
            newpoint = self.ordered[tuple(p)][(suc + 1) % n]
            if suc in self.indices[tuple(p)][1]:
                antipodal = True

        newline = line(p, newpoint)
        aux = [p[0], p[1] + 1]
        
        # TODO: Explain why this works
        sameTurn = turn(p, q, newpoint) == turn(p, aux, newpoint)
        
        oldDual = tuple(dualize(oldline))
        self.counters[oldDual] -= 1
        
        if self.counters[oldDual] == 0:
            try:
                self.upper.delete(dualize(oldline))
            except:
                self.lower.delete(dualize(oldline)) #TODO: Should know whether it's inside upper or lower
        
        newDual = tuple(dualize(newline))
        self.counters[newDual] = self.counters.setdefault(newDual, 0) + 1
        
        if sameTurn == antipodal:#TODO: check this part
            if self.counters[newDual] == 1:
                self.upper.insert(dualize(newline), newline) #new goes to up, old was in oldside
        else:
            if self.counters[newDual] == 1:
                self.lower.insert(dualize(newline), newline)
                
        self._updateEdges()
        self.vertices = getPolygon(self.U, self.L)
            
    ########################### END UPDATE ##################################
            
    def getVisPolygon(self):
        return getPolSegs(self.vertices)
        
def chg_cr(M,D,p,edge,vertices):
    assert len(vertices) > 2
    for point in vertices:
        if turn(edge[0], edge[1], point) != COLLINEAR:
            break
    edge2=([edge[0][0],edge[0][1]], [edge[1][0],edge[1][1]])
    if turn(edge2[0],edge2[1],point)>0:
        p0=D[edge[0]]
        p1=D[edge[1]]
    elif turn(edge2[0],edge2[1],point)<0:
        p0=D[edge[1]]
        p1=D[edge[0]]
    pi=D[(p[0],p[1])]
    #Esto es para calcular el cambio en cr al cruzar edge
    ch_cr=0
    ch_cr= ch_cr + M[p0][p1] 
    ch_cr= ch_cr - M[p1][p0] +1
    ch_cr= ch_cr - M[p0][pi] +1
    ch_cr= ch_cr + M[pi][p0]
    ch_cr= ch_cr + M[p1][pi]
    ch_cr= ch_cr - M[pi][p1] +1 
    return ch_cr
    #----------------------------------------------------------------        
def update_lambda_matrix(M,D,p,edge,vertices):
    assert len(vertices) > 2
    for point in vertices:
        if turn(edge[0], edge[1], point) != COLLINEAR:
            break
    edge2=([edge[0][0],edge[0][1]], [edge[1][0],edge[1][1]])
    if turn(edge2[0],edge2[1],point)>0:
        p0=D[edge[0]]
        p1=D[edge[1]]
    elif turn(edge2[0],edge2[1],point)<0:
        p0=D[edge[1]]
        p1=D[edge[0]]
    pi=D[(p[0],p[1])]        
    #Esto es para actualizar la lambda matriz
    M[p0][p1]=M[p0][p1]+1
    M[p1][p0]=M[p1][p0]-1
    M[p0][pi]=M[p0][pi]-1
    M[pi][p0]=M[pi][p0]+1
    M[p1][pi]=M[p1][pi]+1
    M[pi][p1]=M[pi][p1]-1
    #----------------------------------------------------------------- 
    
def genSpiralWalkCrModified(p, pts, levels=float('inf'), getPols = False):
    """Returns all the cells in the line array of pts whose distance from p's cell satisfies:
    distance%3 = 0 and distance/3 <= levels.
    """
    
    start = Cell(p, pts)    
    level = 0
    
#    if getPols:
#        yield Polygon(start.vertices, "blue")
#    else:
#        yield start.edges
    
    
    ################################################33
    auxpt = None
    M=ordertypes.lambda_matrix(pts+[p])
    D=ordertypes.points_index(pts+[p])   
    cr=crossing.count_crossings(pts+[p])
    initialCr = cr
    ################################################
    
    #yield auxpt, initialCr, initialCr, cr
    
    for e in start.edges:
        change = chg_cr(M, D, p, e, p)
        if cr+change < initialCr:
            initialCr = cr+change
            start.jumpEdge(e)
            yield getCenter(start.vertices), initialCr
            start.jumpEdge(e)
    
    edge = moveNCells(p, start, 3, getCenters=True)
    
#    auxpt = getCenter(start.vertices)
    
    if len(edge) == 0:
        return
        
    ################################################3
#    for e in reversed(edge):
#        start.jumpEdge(e)
    for i in xrange(len(edge)):
        e = edge[i][0]
        pt = edge[i][1]
        assert pt is not None
        cr+=chg_cr(M,D,p,e,pt)
        update_lambda_matrix(M,D,p,e,pt)
#        start.jumpEdge(e)
#        auxpt = getCenter(start.vertices)
        
    #################################################
    
    edge = edge[-1][0]    #edge is the edge which we jumped to land in the current cell
    
    
    while(level < levels and start is not None):
        print "                                           level", level+1
        print "starting with"
        print start.vertices
        firstEdge = edge
        auxpt = getCenter(start.vertices)
        
        nextStart = None
        nextFound = False
        nextEdge = None
        ################3
        nextM = None
        nextCr = None
        bakM = copy.deepcopy(M)
        bakCr = cr
        #################
        
        firstIndex = None
        finished = False
        starJump = False
        current = semiCopy(start)
        #################################################### TO THE LEFT ###############################################
        while not finished: #We go to the left
        
            for e in current.edges:
                change = chg_cr(M, D, p, e, auxpt)
                if cr+change < initialCr:
                    initialCr = cr+change
                    current.jumpEdge(e)
                    if crossing.count_crossings(pts+[getCenter(current.vertices)]) != initialCr:
                        raise Exception
                    yield getCenter(current.vertices), initialCr
                    
                    current.jumpEdge(e)
                    
            lastVisited = current.edges
            print "To the left!                               "
#            print "current pre", current.edges
            if not nextFound:
#                print "                                not found yet"
                nextStart = semiCopy(current)
                res = moveNCells(p, nextStart, 3, getCenters=True)
                if len(res) > 0:
                    nextM = copy.deepcopy(M)
                    nextCr = cr
                    for i in xrange(len(res)):
                        e = res[i][0]
                        pt = res[i][1]
                        
#                        yield nextCr, pt
                        assert pt is not None
                        nextCr += chg_cr(nextM,D,p,e,pt)
                        update_lambda_matrix(nextM,D,p,e,pt)
                        
#                    print "                                     FOUNDNEXT"
#                    print nextStart.vertices
                    nextFound = True
                    nextEdge = res[-1][0]
                else:
                    nextStart = None
            
            edgeIndex = current.edges.index(edge)
                
            #Try an usual jump over every edge
            for i in xrange(len(current.edges)):
#                print "index", edgeIndex
                edgeCandidadte = current.edges[edgeIndex%len(current.edges)]
                res, newEdge = xJump(p, current, current.edges[edgeIndex%len(current.edges)], getAuxpt=True)
                
                if res:
#                    print "found edge"
                    pt = newEdge[1]
                    newEdge = newEdge[0]
                    if current.edges == lastVisited:
                        res = False
                        continue
                    if starJump:
                        starJump = False
                        
                    ####################3
                    cr += chg_cr(M, D, p, edgeCandidadte, auxpt)
                    update_lambda_matrix(M, D, p, edgeCandidadte, auxpt)

#                    if  ordertypes.lambda_matrix(pts+[pt])!=M:
#                        print M
#                        print
#                        print ordertypes.lambda_matrix(pts+[pt])
#                        raise Exception("Matrix")
#                    if crossing.count_crossings(pts+[pt])!=cr:
#                        print cr
#                        print
#                        print crossing.count_crossings(pts+[pt])
#                        raise Exception("cr")
                        
                    auxpt = getCenter(current.vertices)
                    
#                    yield cr, pt
                    
                    change += chg_cr(M, D, p, newEdge, pt)
                    update_lambda_matrix(M, D, p, newEdge, pt)
                    
                    if cr+change < initialCr:
                        initialCr = cr+change
                        if crossing.count_crossings(pts+[auxpt]) != initialCr:
                            raise Exception
                        yield auxpt, initialCr
                    cr += change
                    
                    for e in current.edges:
                        change = chg_cr(M, D, p, e, auxpt)
                        if cr+change < initialCr:
                            initialCr = cr+change
                            current.jumpEdge(e)
                            if crossing.count_crossings(pts+[getCenter(current.vertices)]) != initialCr:
                                raise Exception
                            yield getCenter(current.vertices), initialCr
                            current.jumpEdge(e)
                    
#                    print "done two jumps"
#                    yield cr, auxpt
                    
                    
                    ##########################3
                    
                    edge = newEdge
                    if firstIndex == None:
                        firstIndex = edgeIndex
                        
#                    if current.edges != start.edges:
#                        if getPols:
#                            yield Polygon(current.vertices, "blue")
#                        else:
#                            yield current.edges
                    if current.edges == start.edges:
#                        print "back to start"
                        finished = True
                    break
                edgeIndex -= 1
                
            if not res and not starJump: #We couldn't make an usual jump, try to starjump
#                print "No res"                
                star = False
                
                for i in xrange(-1,len(current.edges)-1):
                    e1 = current.edges[i]
                    e2 = current.edges[i+1]
                    if e1[0] in e2 and list(e1[0]) in current.vertices:
                        starPoint = e1[0]
                        star = True
                        break
                    if e1[1] in e2 and list(e1[1]) in current.vertices:
                        starPoint = e1[1]
                        star = True
                        break
                
#                print "star check:", star    
                if not star:
#                    print "Nothng else to do"
                    break
                
                starEdge = i
                
#                print "trying starjump"
                edge = current.edges[starEdge+1]
                dist = jumpDistance(p, current, edge)
                current.jumpEdge(edge)
                
                ###########################33
                change = chg_cr(M, D, p, edge, auxpt)
                update_lambda_matrix(M, D, p, edge, auxpt)
                auxpt = getCenter(current.vertices)
                
                if cr+change < initialCr:
                    initialCr = cr+change
                    if crossing.count_crossings(pts+[auxpt]) != initialCr:
                        raise Exception
                    yield auxpt, initialCr
                    
                cr += change
                ###################################
                
                while dist != 0: #Jumping around starPoint
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        edge = current.edges[(index+1)%len(current.edges)]
                    else:
                        edge = current.edges[(index-1)%len(current.edges)]
                    dist += jumpDistance(p, current, edge)
                    current.jumpEdge(edge)
                    ###########################33
                    change = chg_cr(M, D, p, edge, auxpt)
                    update_lambda_matrix(M, D, p, edge, auxpt)
                    auxpt = getCenter(current.vertices)
                        
                    if cr+change < initialCr:
                        initialCr = cr+change
                        assert crossing.count_crossings(pts+[auxpt]) == initialCr
                        yield auxpt, initialCr
                        
                    cr += change
                    ###################################
                    
                #We check than we landed in the right direction
                vertexCheck = 0
                while turn(edge[0], edge[1], current.vertices[vertexCheck]) == COLLINEAR:
                    vertexCheck += 1
#                print "giving to turn", p, starPoint, current.vertices[vertexCheck]
#                print
                if turn(p, starPoint, current.vertices[vertexCheck]) == LEFT:
#                    print "starjump"
                    starJump = True
                    res = True
                    if current.edges != start.edges:
    #                        print "back to start"
#                        if getPols:
#                            yield Polygon(current.vertices, "blue")
#                        else:
#                            yield current.edges
                        #We need to set the right edge
                        index = current.edges.index(edge)
                        if starPoint in current.edges[(index+1)%len(current.edges)]:
                            otherEdge = current.edges[(index+1)%len(current.edges)]
                        else:
                            otherEdge = current.edges[(index-1)%len(current.edges)]
                        vertexE = 0
                        while turn(edge[0], edge[1], current.vertices[vertexE]) != COLLINEAR:
                            vertexE += 1
                        vertexO = 0
                        while turn(edge[0], edge[1], current.vertices[vertexO]) != COLLINEAR:
                            vertexO += 1
                        if turn(starPoint, current.vertices[vertexE], current.vertices[vertexO]) == turn(starPoint, current.vertices[vertexE], p):
                            edge = otherEdge
                    else:
                        finished = True
                else: #The direction changed
#                    print "wall inside, inversion"
                    break
                
            if not res:
#                print "wall final, nothing else to do"
                break
        #################################################### END TO THE LEFT ###############################################            
#        print "finished?", finished
        edge = firstEdge
        current = start
        
        M = bakM
        cr = bakCr
        auxpt = getCenter(current.vertices)
        #################################################### TO THE RIGHT ###############################################
        while not finished: #We go to the right
            lastVisited = current.edges 
            print "To the right!                              "
#            print "current pre", current.edges
            if not nextFound:
                nextStart = semiCopy(current)
                print "                                        Not found yet!"
                res = moveNCells(p, nextStart, 3, getCenters=True)
                if len(res) > 0:
                    nextM = copy.deepcopy(M)
                    nextCr = cr
                    for i in xrange(len(res)):
                        e = res[i][0]
                        pt = res[i][1]
                            
                        nextCr += chg_cr(nextM,D,p,e,pt)
                        update_lambda_matrix(nextM,D,p,e,pt)
                        
#                    print "                                     FOUNDNEXT ON RIGHT"
#                    print nextStart.vertices
#                    nextStart = semiCopy(current)
                    nextFound = True
                    nextEdge = res[-1][0]
                else:
#                    print "                                       Set to None"
                    nextStart = None
            
            edgeIndex = current.edges.index(edge)
                
            #Try an usual jump over every edge
#            print "trying usual"
            for i in xrange(len(current.edges)):
#                print "index", edgeIndex
                edgeCandidadte = current.edges[edgeIndex%len(current.edges)]
                res, newEdge = xJump(p, current, current.edges[edgeIndex%len(current.edges)], -1, getAuxpt=True)
                
                if res:
#                    print "found edge"
                    pt = newEdge[1]
                    newEdge = newEdge[0]
                    if current.edges == lastVisited:
#                        print "repeating"
                        res = False
                        continue
                    if starJump:
                        starJump = False
                        
                    ####################3
                    cr += chg_cr(M, D, p, edgeCandidadte, auxpt)
                    update_lambda_matrix(M, D, p, edgeCandidadte, auxpt)

#                    if  ordertypes.lambda_matrix(pts+[pt])!=M:
#                        print M
#                        print
#                        print ordertypes.lambda_matrix(pts+[pt])
#                        raise Exception("Matrix")
#                    if crossing.count_crossings(pts+[pt])!=cr:
#                        print cr
#                        print
#                        print crossing.count_crossings(pts+[pt])
#                        raise Exception("cr")
                        
                    auxpt = getCenter(current.vertices)
                    
#                    yield cr, pt
                    
                    change = chg_cr(M, D, p, newEdge, pt)
                    update_lambda_matrix(M, D, p, newEdge, pt)

                    if cr+change < initialCr:
                        initialCr = cr+change
                        assert crossing.count_crossings(pts+[auxpt]) == initialCr
                        yield auxpt, initialCr
                    cr += change
                    
                    for e in current.edges:
                        change = chg_cr(M, D, p, e, auxpt)
                        if cr+change < initialCr:
                            initialCr = cr+change
                            current.jumpEdge(e)
                            assert crossing.count_crossings(pts+[getCenter(current.vertices)]) == initialCr
                            yield getCenter(current.vertices), initialCr
                            current.jumpEdge(e)
                    
#                    print "done two jumps"
#                    yield cr, auxpt
                    
                    
                    ##########################3
                    edge = newEdge
                    if firstIndex == None:
                        firstIndex = edgeIndex
#                    if getPols:
#                        yield Polygon(current.vertices, "blue")
#                    else:
#                        yield current.edges
                    break
                edgeIndex += 1
#            print "res, starJump is ", res, starJump
#            print 
            if not res and not starJump: #We couldn't make an usual jump, try to starjump
#                print "No res"                
                star = False
                
                for i in xrange(-1,len(current.edges)-1):
                    e1 = current.edges[i]
                    e2 = current.edges[i+1]
                    if e1[0] in e2 and list(e1[0]) in current.vertices:
                        starPoint = e1[0]
                        star = True
                        break
                    if e1[1] in e2 and list(e1[1]) in current.vertices:
                        starPoint = e1[1]
                        star = True
                        break
                
#                print "star check:", star    
                if not star:
#                    print "Nothng else to do"
                    break
                
                starEdge = i
                
#                print "trying starjump"
                edge = current.edges[starEdge+1]
                dist = jumpDistance(p, current, edge)
                current.jumpEdge(edge)
                
                ###########################33
                change = chg_cr(M, D, p, edge, auxpt)
                update_lambda_matrix(M, D, p, edge, auxpt)
                
                auxpt = getCenter(current.vertices)
                    
                if cr+change < initialCr:
                    initialCr = cr+change
                    assert crossing.count_crossings(pts+[auxpt]) == initialCr
                    yield auxpt, initialCr
                    
                cr += change
                ###################################
                
                while dist != 0: #Jumping around starPoint
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        edge = current.edges[(index+1)%len(current.edges)]
                    else:
                        edge = current.edges[(index-1)%len(current.edges)]
                    dist += jumpDistance(p, current, edge)
                    current.jumpEdge(edge)
                    ###########################33
                    change = chg_cr(M, D, p, edge, auxpt)
                    update_lambda_matrix(M, D, p, edge, auxpt)
                    
                    auxpt = getCenter(current.vertices)
                    
                    if cr+change < initialCr:
                        initialCr = cr+change
                        assert crossing.count_crossings(pts+[auxpt]) == initialCr
                        yield auxpt, initialCr
                        
                    cr += change
                    ###################################
                    
                #We check than we landed in the right direction
                vertexCheck = 0
                while turn(edge[0], edge[1], current.vertices[vertexCheck]) == COLLINEAR:
                    vertexCheck += 1
#                print "giving to turn", p, starPoint, current.vertices[vertexCheck]
#                print
                if turn(p, starPoint, current.vertices[vertexCheck]) == RIGHT:
#                    print "starjump"
                    starJump = True
                    res = True
#                    print "yielding"
#                        print "back to start"
#                    if getPols:
#                        yield Polygon(current.vertices, "blue")
#                    else:
#                        yield current.edges
                    #We need to set the right edge
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        otherEdge = current.edges[(index+1)%len(current.edges)]
                    else:
                        otherEdge = current.edges[(index-1)%len(current.edges)]
                    vertexE = 0
                    while turn(edge[0], edge[1], current.vertices[vertexE]) != COLLINEAR:
                        vertexE += 1
                    vertexO = 0
                    while turn(edge[0], edge[1], current.vertices[vertexO]) != COLLINEAR:
                        vertexO += 1
                    if turn(starPoint, current.vertices[vertexE], current.vertices[vertexO]) == turn(starPoint, current.vertices[vertexE], p):
                        edge = otherEdge
                    
                else: #The direction changed
#                    print "wall inside, inversion"
                    break
#            print 'AAAAAAAAAAAAAAA'    
            if not res:
#                print "wall final, nothing else to do"
                break
        #################################################### END TO THE RIGHT ###############################################
        print "END LEVEL", nextFound
        level += 1        
        start = nextStart
        edge = nextEdge
        
        M = nextM
        cr = nextCr
        
def genSpiralWalkCr(p, pts, levels=float('inf'), initialJump=3, strict=True, debug=False, verbose=False):
    """Returns all the cells in the line array of pts whose distance from p's cell satisfies:
    distance%3 = 0 and distance/3 <= levels.
    """
    
    start = Cell(p, pts)    
    level = 0
    auxvertices = None
    M=ordertypes.lambda_matrix(pts+[p])
    D=ordertypes.points_index(pts+[p])
    cr=crossing.count_crossings(pts+[p])
    initialCr = [cr]
    # print "initial", initialCr
    # print "start", start.vertices
    # assert(initialCr[0] == crossing.count_crossings(pts+[p]))
    colors = ["blue", "red", "black", "green", "cyan", "brown", "yellow", "purple", "orange", "pink"]
    if debug:
        yield Polygon(start.vertices, fill = random.choice(colors))
    else:
        for x in checkNeighbors(start, initialCr, cr, M, D, p, pts, strict):
            yield x

    # print "post", initialCr
    # assert(cr == crossing.count_crossings(pts+[p]))
    edge = moveNCells(p, start, initialJump, getCenters=True)

    ###############3
    # print "start", start.vertices
    # for e in reversed(edge):
    #     start.jumpEdge(e[0])
    # assert(cr == crossing.count_crossings(pts+[p]))
    # print "start", start.vertices
    ############
    
    if len(edge) == 0:
        return
    for i in xrange(len(edge)):
        e = edge[i][0]
        vertices = edge[i][1]
        cr += chg_cr(M,D,p,e,vertices)
        update_lambda_matrix(M,D,p,e,vertices)
        ######################
        # start.jumpEdge(e)
        # z = randPointPolygon(start.vertices)
        # print cr, "     vs     ", crossing.count_crossings(pts+[z], speedup=False)        
        # assert(cr == crossing.count_crossings(pts+[z], speedup=False))
        ##########################

    # z = randPointPolygon(start.vertices)
    # print cr, "     vs     ", crossing.count_crossings(pts+[z], speedup=False)
    # assert(cr == crossing.count_crossings(pts+[z], speedup=False))
    
    edge = edge[-1][0]    #edge is the edge which we jumped to land in the current cell
    
    while(level < levels and start is not None):
        if verbose:
            print "level", level
        firstEdge = edge
        auxvertices = start.vertices
        # assert auxvertices is not None
        z = randPointPolygon(start.vertices)
        # assert(cr == crossing.count_crossings(pts+[z]))
        if debug:
            yield Polygon(start.vertices, fill = random.choice(colors))
        else:
            for x in checkNeighbors(start, initialCr, cr, M, D, p, pts, strict):
                yield x
        
        nextStart = None
        nextFound = False
        nextEdge = None
        nextM = None
        nextCr = None
        bakM = copy.deepcopy(M)
        bakCr = cr
        
        firstIndex = None
        finished = False
        starJump = False
        current = semiCopy(start)
        #################################################### TO THE LEFT ###############################################
        while not finished: #We go to the left
            if verbose:
                print "To the left"
            lastVisited = current.edges
            if not nextFound:
                nextStart = semiCopy(current)
                jumps = moveNCells(p, nextStart, 3, getCenters=True)
                if len(jumps) > 0:
                    nextM = copy.deepcopy(M)
                    nextCr = cr
                    for i in xrange(len(jumps)):
                        e = jumps[i][0]
                        vertices = jumps[i][1]
                        nextCr += chg_cr(nextM,D,p,e,vertices)
                        update_lambda_matrix(nextM,D,p,e,vertices)
                    nextFound = True
                    nextEdge = jumps[-1][0]
                else:
                    nextStart = None
            
            edgeIndex = current.edges.index(edge)
                
            #Try an usual jump over every edge
            for i in xrange(len(current.edges)):
                edgeCandidadte = current.edges[edgeIndex%len(current.edges)]
                jumps, midEdge = xJump(p, current, current.edges[edgeIndex%len(current.edges)], getAuxpt=True)
                
                if current.edges == lastVisited:
                    jumps = False
                    edgeIndex -= 1
                    continue

                if jumps:
                    midvertices, midEdge = midEdge[1], midEdge[0]
                    
                    if starJump:
                        starJump = False
                        
                    cr += chg_cr(M, D, p, edgeCandidadte, auxvertices)
                    update_lambda_matrix(M, D, p, edgeCandidadte, auxvertices)
                    auxvertices = current.vertices

                    current.jumpEdge(midEdge) #TODO: Is this neccesary?
                    
                    if debug:
                        yield Polygon(current.vertices, fill = random.choice(colors))
                    else:
                        for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                            yield x
                    current.jumpEdge(midEdge)
                    
                    cr += chg_cr(M, D, p, midEdge, midvertices)
                    update_lambda_matrix(M, D, p, midEdge, midvertices)

                    if debug:
                        yield Polygon(current.vertices, fill = random.choice(colors))
                    else:
                        for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                            yield x
                    
                    edge = midEdge
                    if firstIndex == None:
                        firstIndex = edgeIndex
                    if current.edges == start.edges:
                        finished = True
                    break
                edgeIndex -= 1
                
            if not jumps and not starJump: #We couldn't make an usual jump, try to starjump  
                star = False
                
                for i in xrange(-1,len(current.edges)-1):
                    e1 = current.edges[i]
                    e2 = current.edges[i+1]
                    if e1[0] in e2 and list(e1[0]) in current.vertices:
                        starPoint = e1[0]
                        star = True
                        break
                    if e1[1] in e2 and list(e1[1]) in current.vertices:
                        starPoint = e1[1]
                        star = True
                        break
                
                if not star:
                    break
                
                starEdge = i
                
                edge = current.edges[starEdge+1]
                dist = jumpDistance(p, current, edge)
                current.jumpEdge(edge)
                cr += chg_cr(M, D, p, edge, auxvertices)
                update_lambda_matrix(M, D, p, edge, auxvertices)
                auxvertices = current.vertices

                if debug:
                    yield Polygon(current.vertices, fill = random.choice(colors))
                else:
                    for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                        yield x
                
                while dist != 0: #Jumping around starPoint
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        edge = current.edges[(index+1)%len(current.edges)]
                    else:
                        edge = current.edges[(index-1)%len(current.edges)]
                    dist += jumpDistance(p, current, edge)
                    current.jumpEdge(edge)
                    cr += chg_cr(M, D, p, edge, auxvertices)
                    update_lambda_matrix(M, D, p, edge, auxvertices)
                    auxvertices = current.vertices

                    if debug:
                        yield Polygon(current.vertices, fill = random.choice(colors))
                    else:
                        for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                            yield x
                    
                #We check than we landed in the right direction
                auxVertex = 0
                while turn(edge[0], edge[1], current.vertices[auxVertex]) == COLLINEAR:
                    auxVertex += 1
                if turn(p, starPoint, current.vertices[auxVertex]) == LEFT:
#                    print "starjump"
                    starJump = True
                    jumps = True
                    if current.edges != start.edges:
                        index = current.edges.index(edge)
                        if starPoint in current.edges[(index+1)%len(current.edges)]:
                            otherEdge = current.edges[(index+1)%len(current.edges)]
                        else:
                            otherEdge = current.edges[(index-1)%len(current.edges)]
                        vertexE = 0
                        while turn(edge[0], edge[1], current.vertices[vertexE]) != COLLINEAR:
                            vertexE += 1
                        vertexO = 0
                        while turn(edge[0], edge[1], current.vertices[vertexO]) != COLLINEAR:
                            vertexO += 1
                        if turn(starPoint, current.vertices[vertexE], current.vertices[vertexO]) == turn(starPoint, current.vertices[vertexE], p):
                            edge = otherEdge
                    else:
                        finished = True
                else: #The direction changed
                    break
                
            if not jumps:
                break
        #################################################### END TO THE LEFT ###############################################
        edge = firstEdge
        current = start
        
        M = bakM
        cr = bakCr
        auxvertices = current.vertices
        #################################################### TO THE RIGHT ###############################################
        while not finished: #We go to the right
            if verbose:
                print "to the right"
            lastVisited = current.edges
            if not nextFound:
                nextStart = semiCopy(current)
                jumps = moveNCells(p, nextStart, 3, getCenters=True)
                if len(jumps) > 0:
                    nextM = copy.deepcopy(M)
                    nextCr = cr
                    for i in xrange(len(jumps)):
                        e = jumps[i][0]
                        vertices = jumps[i][1]
                        nextCr += chg_cr(nextM,D,p,e,vertices)
                        update_lambda_matrix(nextM,D,p,e,vertices)
                    nextFound = True
                    nextEdge = jumps[-1][0]
                else:
                    nextStart = None
            
            edgeIndex = current.edges.index(edge)
                
            #Try an usual jump over every edge
            for i in xrange(len(current.edges)):
                edgeCandidadte = current.edges[edgeIndex%len(current.edges)]
                jump, newEdge = xJump(p, current, current.edges[edgeIndex%len(current.edges)], -1, getAuxpt=True)

                if current.edges == lastVisited:
                    jump = False
                    edgeIndex += 1
                    continue

                if jump:
                    midvertices = newEdge[1]
                    newEdge = newEdge[0]

                    if starJump:
                        starJump = False

                    cr += chg_cr(M, D, p, edgeCandidadte, auxvertices)
                    update_lambda_matrix(M, D, p, edgeCandidadte, auxvertices)
                    auxvertices = current.vertices

                    current.jumpEdge(newEdge)

                    if debug:
                        yield Polygon(current.vertices, fill = random.choice(colors))
                    else:
                        for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                            yield x
                    current.jumpEdge(newEdge)
                    
                    cr += chg_cr(M, D, p, newEdge, midvertices)
                    update_lambda_matrix(M, D, p, newEdge, midvertices)

                    if debug:
                        yield Polygon(current.vertices, fill = random.choice(colors))
                    else:
                        for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                            yield x

                    edge = newEdge
                    if firstIndex == None:
                        firstIndex = edgeIndex

                    break
                edgeIndex += 1

            if not jump and not starJump: #We couldn't make an usual jump, try to starjump
                star = False
                
                for i in xrange(-1,len(current.edges)-1):
                    e1 = current.edges[i]
                    e2 = current.edges[i+1]
                    if e1[0] in e2 and list(e1[0]) in current.vertices:
                        starPoint = e1[0]
                        star = True
                        break
                    if e1[1] in e2 and list(e1[1]) in current.vertices:
                        starPoint = e1[1]
                        star = True
                        break
                
#                print "star check:", star    
                if not star:
                    break
                
                starEdge = i
                
                edge = current.edges[starEdge+1]
                dist = jumpDistance(p, current, edge)
                current.jumpEdge(edge)
                
                cr += chg_cr(M, D, p, edge, auxvertices)
                update_lambda_matrix(M, D, p, edge, auxvertices)
                auxvertices = current.vertices

                if debug:
                    yield Polygon(current.vertices, fill = random.choice(colors))
                else:
                    for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                        yield x
                
                while dist != 0: #Jumping around starPoint
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        edge = current.edges[(index+1)%len(current.edges)]
                    else:
                        edge = current.edges[(index-1)%len(current.edges)]
                    dist += jumpDistance(p, current, edge)
                    current.jumpEdge(edge)
                    cr += chg_cr(M, D, p, edge, auxvertices)
                    update_lambda_matrix(M, D, p, edge, auxvertices)
                    auxvertices = current.vertices

                    if debug:
                        yield Polygon(current.vertices, fill = random.choice(colors))
                    else:
                        for x in checkNeighbors(current, initialCr, cr, M, D, p, pts, strict):
                            yield x
                    
                #We check than we landed in the right direction
                vertexCheck = 0
                while turn(edge[0], edge[1], current.vertices[vertexCheck]) == COLLINEAR:
                    vertexCheck += 1
                if turn(p, starPoint, current.vertices[vertexCheck]) == RIGHT:
                    starJump = True
                    jump = True
                    #We need to set the right edge
                    index = current.edges.index(edge)
                    if starPoint in current.edges[(index+1)%len(current.edges)]:
                        otherEdge = current.edges[(index+1)%len(current.edges)]
                    else:
                        otherEdge = current.edges[(index-1)%len(current.edges)]
                    vertexE = 0
                    while turn(edge[0], edge[1], current.vertices[vertexE]) != COLLINEAR:
                        vertexE += 1
                    vertexO = 0
                    while turn(edge[0], edge[1], current.vertices[vertexO]) != COLLINEAR:
                        vertexO += 1
                    if turn(starPoint, current.vertices[vertexE], current.vertices[vertexO]) == turn(starPoint, current.vertices[vertexE], p):
                        edge = otherEdge
                    
                else: #The direction changed
                    break
            if not jump:
                break
        #################################################### END TO THE RIGHT ###############################################
#        print "END LEVEL", nextFound
        level += 1        
        start = nextStart
        edge = nextEdge
        
        M = nextM
        cr = nextCr
        
def checkNeighbors(cell, initialCr, cr, M, D, p, pts, strict=True):
    #assert auxpt is not None
    # yield Polygon(cell.vertices, fill="Blue")
    auxpt = randPointPolygon(cell.vertices)
    # if auxpt is not None:
    #     assert(cr == crossing.count_crossings(pts+[auxpt]))
    condition = (cr < initialCr[0]) if strict else (cr <= initialCr[0])
    if condition:
        # print "yup first"
        initialCr[0] = cr
        if auxpt is not None:
            # assert(cr == crossing.count_crossings(pts+[auxpt]))
            yield auxpt, cr
        else:
            yield cell.vertices, cr
        
    for e in cell.edges:
        change = chg_cr(M, D, p, e, cell.vertices)
        condition = ((cr+change) < initialCr[0]) if strict else ((cr+change) <= initialCr[0])
        if condition:
            # print "yup neighbors", cr+change
#            print initialCr[0]
            initialCr[0] = cr+change
            cell.jumpEdge(e)
            auxpt = randPointPolygon(cell.vertices)
            if auxpt is not None:
                # assert(cr+change == crossing.count_crossings(pts+[auxpt]))
                yield auxpt, initialCr[0]
            else:
                yield cell.vertices, initialCr[0]
            cell.jumpEdge(e)