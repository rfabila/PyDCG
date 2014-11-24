# -*- coding: utf-8 -*-
from geometricbasics import turn, sort_around_point
import warnings
import copy
import datastructures
#from . import datastructures
import random
import sys
import traceback
import decimal
import bisect
from line import Line
from collections import deque
from math import ceil, floor

LEFT = -1
RIGHT = 1
COLLINEAR = 0

UP = 1
DOWN = 2


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
        if not isinstance(p, list) or not isinstance(q, list):
            raise Exception
        self.p = p
        self.q = q
        self.m = rational(self.p[1] - self.q[1], self.p[0] - self.q[0], True)
        self.b = self.m * (-self.p[0]) + self.p[1]
        self.b.simplify()

    def intersection_y_coord(self, l):
        """Returns the y coordinate of the point where self and l
           intersect. If self and l are paralell returns None"""
        if self.m == l.m:
            return None
        return (l.m * self.b - self.m * l.b) / (l.m - self.m)

    def intersection_x_coord(self, l):
        """Returns the x coordinate of the point where self and l
           intersect. If self and l are paralell returns None"""
        if self.m == l.m:
            return None
        return (self.b - l.b) / (l.m - self.m)

    def intersection(self, l):
        return [self.intersection_x_coord(l), self.intersection_y_coord(l)]

    def __str__(self):
        return "y = %d/%d x %d/%d" % (self.m.a, self.m.b, self.b.a, self.b.b)

    def __repr__(self):
        return "y = %d/%d x %d/%d" % (self.m.a, self.m.b, self.b.a, self.b.b)

    def getPoints(self):
        return [self.p, self.q]

    def evalx(self, x):
        return self.m * x + self.b


def dualize(obj):
    if isinstance(obj, line):
        return [obj.m, obj.b * -1]
#    elif isinstance(obj, list):
    raise Exception("Not implemented yet!")
#        return #TODO: write this!


def getPointRegion(q, sortedpoints, indices):
    """Assumes len(sortedpoints) > 3, each entry of sorted points should contain
       a point `p` and the other points sorted around it."""
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
        counters.setdefault(tuple(point), 0)
        counters[tuple(point)] += 1
        upperHull.insert(point, l)

    for l in lower:
        point = dualize(l)
        counters.setdefault(tuple(point), 0)
        counters[tuple(point)] += 1
        lowerHull.insert(point, l)

    return upperHull, lowerHull, counters


def getRegionR(upper, lower):
    # TODO: erase extra calls to popColiinear, rewrite repeated code
    # TODO: Make dynamic_haf_hull.toList() return a deque, since many
    # functions pop from the front
    U = upper.toList()
    L = lower.toList()
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
            print "dup"
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


def getPolygon(U, L, tellUnbounded=False):
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
        p1[0] += 1000000
        p1[1] = U[0][1].evalx(p1[0])

        p2 = upts[-1][:]
        p2[0] -= 1000000
        p2[1] = U[-1][1].evalx(p2[0])

        upts.insert(0, p1)
        upts.append(p2)
        
        if tellUnbounded:
            return upts, True

        return upts

    if len(U) == 0:
        #        print "lpts", lpts
        p1 = lpts[0][:]
        p1[0] -= 1000000
        p1[1] = L[-1][1].evalx(p1[0])

        p2 = lpts[-1][:]
        p2[0] += 1000000
        p2[1] = L[0][1].evalx(p2[0])

        lpts.insert(0, p1)
        lpts.append(p2)
        
        if tellUnbounded:
            return lpts, True

        return lpts

    # This one should be the left-most point of the polygon
    lm = U[-1][1].intersection(L[-1][1])
    # and this one should be the right-most one
    rm = U[0][1].intersection(L[0][1])

    if len(U) == 1 and len(L) == 1:  # This means the region is just a wedge
        # Let's see if we need the right or the left wedge
        p = lm
        p1 = [p[0] + 1000000, U[0][1].evalx(p[0] + 1000000)]
        p2 = [p[0] + 1000000, L[0][1].evalx(p[0] + 1000000)]
        if turn(p1, p, p2) > 0:
            p1 = [p[0] - 1000000, L[0][1].evalx(p[0] - 1000000)]
            p2 = [p[0] - 1000000, U[0][1].evalx(p[0] - 1000000)]
            
        if tellUnbounded:
            return [p1, p, p2], True
#
        return [p1, p, p2]

    else:
        aux = upts[-1] if len(upts) > 0 else lpts[0]
        if lm[0] > aux[0]:
            lpts.append(rm)
            lpts += upts
            p1 = lpts[0][:]
            p1[0] -= 1000000
            p1[1] = L[-1][1].evalx(p1[0])

            p2 = lpts[-1][:]
            p2[0] -= 1000000
            p2[1] = U[-1][1].evalx(p2[0])

            lpts.insert(0, p1)
            lpts.append(p2)
            
            if tellUnbounded:
                return lpts, True

            return lpts

        aux = upts[0] if len(upts) > 0 else lpts[-1]
        if rm[0] < aux[0]:

            upts.append(lm)
            upts += lpts

            p1 = upts[0][:]
            p1[0] += 1000000
            p1[1] = U[0][1].evalx(p1[0])

            p2 = upts[-1][:]
            p2[0] += 1000000
            p2[1] = L[0][1].evalx(p2[0])
            upts.insert(0, p1)
            upts.append(p2)
            
            if tellUnbounded:
                return upts, True

            return upts

    # If we get to this point, the region is a bounded polygon
    upts.append(lm)
    upts += lpts
    upts.append(rm)
    
    if tellUnbounded:
        return upts, False

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
            if pointInPolygon(candidate, polygon) and not sameXCoord(candidate, polygon):
                return candidate
    return None

def getPolSegs(polygon):
    colors = ["green", "red", "blue", "black", "orange", "brown", "cyan"]
    color = random.choice(colors)
    pol = []
    n = len(polygon)
    for i in range(len(polygon)):
        p1 = [float(polygon[i % n][0]), float(polygon[i % n][1])]
        p2 = [float(polygon[(i + 1) % n][0]), float(polygon[(i + 1) % n][1])]
        seg = [p1, p2, color, 3]
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
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counter = getPointRegion(
        p, ordered, indices)  # TODO: USE COUNTER!!!
    U, L = getRegionR(upper, lower)
    last = None
    for i in range(steps):
        last = randMove(upper, lower, indices, ordered, U, L, last)
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


def getRandomWalkDFS2(p, pts, length=10, maxDepth=2000):
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
    
def getRandomWalkDFS(p, pts, length=10):
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counters = getPointRegion(p, ordered, indices)
    U, L = getRegionR(upper, lower)
    n = (len(indices) - 1) * 2
    
    start = getPolygon(U, L)
    regions = 1
    yield start
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
                yield poly
                regions += 1
#                regions.append(poly)
#                print "                               van", len(regions)
#                print " "*len(S), "push!, I crossed", crossingEdge
                S.append( region( U, L, [p1,p2], side, (ant1, suc1), (ant2, suc2), lines1, lines2 ) )
#                print "level", len(S)
                if regions >= length:
                    print "found enough regions"
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

def getRandomWalkN2(pts):
    p = [random.randint(-100000000, 100000000), random.randint(-100000000, 100000000)]
    
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
            if p[0] == pt[0] and p[1] == pt[2]:
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
    start = getPolygon(U, L)
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
            poly = getPolygon(U, L)
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
