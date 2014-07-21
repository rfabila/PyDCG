# -*- coding: utf-8 -*-
from geometricbasics import turn, sort_around_point
import copy
import datastructures
import random
from line import Line

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
    if ~u & 1: #// u is even
        if v & 1:# // v is odd
            return gcd(u >> 1, v)
        else:# // both u and v are even
            return gcd(u >> 1, v >> 1) << 1
 
    if (~v & 1): #// u is odd, v is even
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
    def __init__(self, a, b, simp = False):
        self.a = a
        self.b = b
        
        if b == 0:
            raise ZeroDivisionError("punto %d, %d"%(a,b))
        
        if self.b < 0:
            self.a *= -1
            self.b *= -1
        
        n = random.randint(0,19)
        if simp or n == 10:
            self.simplify()
            
    def simplify(self):
        aux = gcd(self.a, self.b)
        self.a /= aux
        self.b /= aux
        
    def __lt__(self, other):
        if isinstance(other, int):
            return self.a < other*self.b
        return self.a*other.b < other.a*self.b
        
    def __ge__(self, other):
        return not self < other
        
    def __le__(self, other):
        if isinstance(other, int):
            return self.a <= other*self.b
        return self.a*other.b <= other.a*self.b
        
    def __gt__(self, other):
        return not self <= other
    
        
    def __eq__(self, other):
        if isinstance(other, int):
            return self.a == other*self.b
        return self.a*other.b == other.a*self.b
        
    def __ne__(self, other):
        return not self == other
        
    def __add__(self, other):
        if isinstance(other, int):
            return rational(self.a + other*self.b, self.b)
        den = self.b * other.b
        num = self.a*other.b + other.a*self.b
        return rational(num, den)
        
    def __radd__(self, other):
        return self + other
        
    def __sub__(self, other):
        if isinstance(other, int):
            return rational(self.a - other*self.b, self.b)
        den = self.b * other.b
        num = self.a*other.b - other.a*self.b
        return rational(num, den)
        
    def __rsub__(self, other):
        return self - other
        
    def __mul__(self, other):
        if isinstance(other, int):
            return rational(self.a * other, self.b)
        den = self.b * other.b
        num = self.a*other.a
        return rational(num, den)
        
    def __rmul__(self, other):
        return self * other
        
    def __div__(self, other):
        if isinstance(other, int):
            return rational(self.a*other, self.b)
        den = self.b * other.a
        num = self.a*other.b
        return rational(num, den)
        
    def __str__(self):
        return "%d/%d"%(self.a, self.b)
        
    def __repr__(self):
#        return "rational(%f)"%(float(self.a) / float(self.b)) #TODO: Remove this, it's only here for debugging purposes
        return "rational(%d,%d)"%(self.a, self.b)
        
    def __float__(self):
        return float(self.a)/float(self.b)
        
    def __hash__(self):
        auxa = 2*self.a if self.a > 0 else -2*self.a-1
        auxb = 2*self.b if self.b > 0 else -2*self.b-1
        return ((auxa+auxb)*(auxa+auxb+1)/2)+auxb

class line(object):
    """A line defined by two points (p and q) in the plane.
       The slope and y-intersection are available at m and b, respectively"""
    def __init__(self, p, q): #TODO: Si se quitan las propiedades, se debería protejer p, q, m, b?
        if type(p) is not list or type(q) is not list:
            raise StandardError
        self.__p = p
        self.q = q
        self.m = rational(self.p[1] - self.q[1], self.p[0] - self.q[0], True)
        self.b = self.m*(-self.p[0]) + self.p[1]
        self.b.simplify()
        
    @property
    def p(self):
        return self.__p
        
#    @property
#    def m(self):
#        """Value of the slope"""
##        return float(self.p[1] - self.q[1]) / float(self.p[0] - self.q[0])
#        return rational(self.p[1] - self.q[1], self.p[0] - self.q[0])
#    @property
#    def b(self):
#        """y-intersection"""
##        return float(self.p[1] - self.m * self.p[0])
##        return rational(self.m.b*self.p[1] - self.m.a * self.p[0], self.m.b)
#        return self.m*(-self.p[0]) + self.p[1]
        
    def intersection_y_coord(self, l):
        """Returns the y coordinate of the point where self and l 
           intersect. If self and l are paralell returns None"""
        if self.m == l.m:
            return None
        return (l.m * self.b - self.m * l.b)/(l.m - self.m)
    def intersection_x_coord(self, l):
        """Returns the x coordinate of the point where self and l 
           intersect. If self and l are paralell returns None"""
        if self.m == l.m:
            print "Warning, same slopes"
            print self, l
            print "endpoints", self.getPoints, l.getPoints
            return None
        return (self.b-l.b) / (l.m - self.m)
    def intersection(self, l):
        return [self.intersection_x_coord(l), self.intersection_y_coord(l)]
    def __str__(self):
#        return "y = %f x %f"%(self.m, self.b)
        return "y = %d/%d x %d/%d"%(self.m.a, self.m.b, self.b.a, self.b.b)
    def __repr__(self):
#        return "y = %f x %f"%(self.m, self.b)
        return "y = %d/%d x %d/%d"%(self.m.a, self.m.b, self.b.a, self.b.b)
        
    def getPoints(self):
        return [self.p, self.q]
        
    def evalx(self, x):
        return self.m*x + self.b
        
def dualize(obj):
    if isinstance(obj, line):
        return [obj.m, obj.b*-1] # XXX: deben estar simplificados no?
    elif isinstance(obj, list) and len(obj) == 2 and isinstance(obj[0], rational) and isinstance(obj[1], rational):
        return 

def getPointRegion(q, sortedpoints, indices):
    """Assumes len(sortedpoints) > 3, each entry of sorted points should contain
       a point `p` and the other points sorted around it."""
    upper = []
    lower = []
#    indices = {}
    counters = {}
    
    for (p, pts) in sortedpoints.iteritems():
        pred, succ = indices[tuple(p)][0]
#        pred, succ = pts[pred], pts[succ]        
        predline = line(list(p), pts[pred])
        succline = line(list(p), pts[succ])
        
        intersection = predline.evalx(q[0])# .m * q[0] + predline.b
        
        if intersection > q[1]:
            upper.append(predline)
            
        elif intersection < q[1]:
            lower.append(predline)
        else:
            raise CollinearPoints(q, p, pts[pred])
            
        intersection = succline.evalx(q[0])#m * q[0] + succline.b
        if intersection > q[1]:
            upper.append(succline)
        elif intersection < q[1]:
            lower.append(succline)
        else:
            raise CollinearPoints(q, p, pts[succ])
        
        
    #Now upper and lower contain the lines that bound q's region
    #We dualize the lines and find the lower and upper hull, respectively

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
    
#TODO: It appears that both getRegion and getRegionR work... I don't remember why I wrote two, check which one should
#stay and erase the other one
def getRegion(upper, lower): #TODO: Use the bridge function here, this runs in linear time and bridge is log(n)
#TODO: erase extra calls for popCollinear, rewrite repeated code
    U = upper.toList() #TODO: Make dynamic_haf_hull.toList() return a deque, since many functions pop from the front
    L = lower.toList()
    
    def popCollinear(env): #TODO: eliminar los casos colineales de abajo, ya no son necesarios
        index = 0
        while index <= len(env) - 3:
#            print "   found one!"
            int1 = env[index][1].intersection(env[index+1][1])
            int2 = env[index+1][1].intersection(env[index+2][1])
            if int1 == int2:
                env.pop(index+1)
            else:
                index += 1
                
    if len(U) == 0 or len(L) == 0:
        popCollinear(U)
        popCollinear(L)
        return U, L
    
    #We start popping from the begining of U and L
    l = [L[0][0], U[0][0]]
    doneL, doneU = False, False
    while not (doneL and doneU):
        popU, popL = 0,0
        if len(L) > 1:
            if turn(l[0], l[1], L[1][0]) > 0:
                doneL = True
            elif turn(l[0], l[1], L[1][0]) == 0:
                if (l[0][0] < L[1][0][0] < l[1][0]) or (l[0][0] > L[1][0][0] > l[1][0]):
                    popL = 0
                else:
                    popL = 1
                doneL = False
            else:
                doneL = False
        else:
            doneL = True
            
        if len(U) > 1:
            if turn(l[0], l[1], U[1][0]) < 0:
                doneU = True
            elif turn(l[0], l[1], U[1][0]) == 0:
                if (l[0][0] < U[1][0][0] < l[1][0]) or (l[0][0] > U[1][0][0] > l[1][0]):
                    popU = 0
                else:
                    popU = 1
                doneU = False
            else:
                doneU = False
        else:
            doneU = True
            
        if not doneL:
            L.pop(popL)
            l[0] = L[0][0]
            
        if not doneU:
            U.pop(popU)
            l[1] = U[0][0]

    #And now we pop from the end of U and L
    l = [L[-1][0], U[-1][0]]
    doneL, doneU = False, False
    while not (doneU and doneL):
        popU, popL = -1, -1
        if len(L) > 1:
            if turn(l[0], l[1], L[-2][0]) < 0:
                doneL = True
            elif turn(l[0], l[1], L[-2][0]) == 0:
                if (l[0][0] < L[-2][0][0] < l[1][0]) or (l[0][0] > L[-2][0][0] > l[1][0]):
                    popL = -1
                else:
                    popL = -2
            else:
                doneL = False
        else:
            doneL = True
            
        if len(U) > 1:
            if turn(l[0], l[1], U[-2][0]) > 0:
                doneU = True
            elif turn(l[0], l[1], U[-2][0]) == 0:
                if (l[0][0] < U[-2][0][0] < l[1][0]) or (l[0][0] > U[-2][0][0] > l[1][0]):
                    popU = -1
                else:
                    popU = -2
            else:
                doneU = False
        else:
            doneU = True
            
        if not doneL:
            L.pop(popL)
            l[0] = L[-1][0]
            
        if not doneU:
            U.pop(popU)
            l[1] = U[-1][0]
            
    popCollinear(U)
    popCollinear(L)
                
    return U, L
    
def getRegionR(upper, lower): #TODO: Use the bridge function here, this runs in linear time and bridge is log(n)
#TODO: erase extra calls to popColiinear, rewrite repeated code
    U = upper.toList() #TODO: Make dynamic_haf_hull.toList() return a deque, since many functions pop from the front
    L = lower.toList()
    L.reverse()
    
    
    def popCollinear(env):
        index = 0
        while index <= len(env) - 3:
            int1 = env[index][1].intersection(env[index+1][1])
            int2 = env[index+1][1].intersection(env[index+2][1])
            if int1 == int2:
                env.pop(index+1)
            else:
                index += 1
                
    popCollinear(U)
    popCollinear(L)
                
    if len(U) == 0 or len(L) == 0:
#        popCollinear(U)
#        popCollinear(L)
        L.reverse()
        return U, L
    
    #First bitangent    
    idxL, idxU = 0, len(U)-1
    l = [L[idxL][0], U[idxU][0]]
    l.sort()
    
    doneL, doneU = False, False
    while not (doneL and doneU):
        doneL, doneU = False, False
        if idxL == len(L)-1 or turn(l[0], l[1], L[idxL+1][0]) < 0:
            doneL = True
        elif turn(l[0], l[1], L[idxL+1][0]) == 0:
            if (L[idxL+1][0][0] < L[idxL][0][0] < U[idxU][0][0]) or (L[idxL+1][0][0] > L[idxL][0][0] > U[idxU][0][0]):
                doneL = True
            else:
                doneL = False
        else:
            doneL = False
            
        if idxU == 0 or turn(l[0], l[1], U[idxU-1][0]) > 0:
            doneU = True
        elif turn(l[0], l[1], U[idxU-1][0]) == 0:
            if (U[idxU-1][0][0] < U[idxU][0][0] < L[idxL][0][0]) or (U[idxU-1][0][0] > U[idxU][0][0] > L[idxL][0][0]):
                doneU = True
            else:
                doneU = False
        else:
            doneU = False
            
        if not doneL:
            idxL += 1
            
        if not doneU:
            idxU -= 1
            
        l = [L[idxL][0], U[idxU][0]]
        
        l.sort()
    
    if L[idxL][0][0] < U[idxU][0][0]:
#        print "Borro principio de L y final de U"
        L = L[idxL:]
        U = U[:idxU+1]
    else:
#        print "Borro principio de U y final de L"
        L = L[:idxL+1]
        U = U[idxU:]
    
    idxL, idxU = len(L)-1, 0
    l = [L[idxL][0], U[idxU][0]]
    l.sort()
    doneL, doneU = False, False
    while not (doneU and doneL):
        doneL, doneU = False, False
        if idxL == 0 or turn(l[0], l[1], L[idxL-1][0]) < 0:
            doneL = True
        elif turn(l[0], l[1], L[idxL-1][0]) == 0:
            if (L[idxL-1][0][0] < L[idxL][0][0] < U[idxU][0][0]) or (L[idxL-1][0][0] > L[idxL][0][0] > U[idxU][0][0]):
                doneL = True
            else:
                doneL = False
        else:
            doneL = False
            
        if idxU == len(U)-1 or turn(l[0], l[1], U[idxU+1][0]) > 0:
            doneU = True
        elif turn(l[0], l[1], U[idxU+1][0]) == 0:
            if (U[idxU+1][0][0] < U[idxU][0][0] < L[idxL][0][0]) or (U[idxU+1][0][0] > U[idxU][0][0] > L[idxL][0][0]):
                doneU = True
            else:
                doneU = False
        else:
            doneU = False
            
        if not doneL:
            idxL -= 1
            
        if not doneU:
            idxU += 1
            
        l = [L[idxL][0], U[idxU][0]]
            
        l.sort()
        
    if L[idxL][0][0] < U[idxU][0][0]:
#        print "Borro principio de L y final de U"
        L = L[idxL:]
        U = U[:idxU+1]
    else:
#        print "Borro principio de U1 y final de L"
        L = L[:idxL+1]
        U = U[idxU:]
    
#    popCollinear(U)
#    popCollinear(L)
    L.reverse()
                
    return U, L
    
def randMove(upper, lower, indices, ordered, regionU, regionL, last = None): #TODO: A lot of repeated code here! rewrite
    total = len(regionU) + len(regionL) - 1
    
    side = None
    n = (len(indices)-1)*2
    
    ready = False
    
    while not ready:
        edge = random.randint(0, total)
        if edge < len(regionU):
            edge = regionU[edge][1]
            side = UP        
        else:
            edge = regionL[total - edge][1]
            side = DOWN
        p1, p2 = edge.getPoints()
        if last is None or sorted([p1,p2]) != last:
            ready = True
    
    oldline = line(p1, p2)
    
    if side == UP:
        
        upper.delete(dualize(oldline))
        lower.insert(dualize(oldline), oldline)
        antipodal = False
        ant, suc = indices[tuple(p1)][0]
        
        if ordered[tuple(p1)][ant] == p2:
            indices[tuple(p1)][0] = [(ant-1)%n, ant]
            newpoint = ordered[tuple(p1)][(ant-1)%n]
            if ant in indices[tuple(p1)][1]:
                antipodal = True
        else:
            indices[tuple(p1)][0] = [suc, (suc+1)%n]
            newpoint = ordered[tuple(p1)][(suc+1)%n]
            if suc in indices[tuple(p1)][1]:
                antipodal = True
            
        newline = line(p1, newpoint)
        aux = [p1[0], p1[1]+1]
        
        if turn(p1, p2, newpoint) == turn(p1, aux, newpoint): #TODO: Explain why this works
            if antipodal:
                upper.insert(dualize(newline), newline)
            else:
                lower.insert(dualize(newline), newline)
        else:
            if antipodal:
                lower.insert(dualize(newline), newline)
            else:
                upper.insert(dualize(newline), newline)
                
         ###############################################################################################################   
        #Now for p2
        antipodal = False
        ant, suc = indices[tuple(p2)][0]
        if ordered[tuple(p2)][ant] == p1:
            indices[tuple(p2)][0] = [(ant-1)%n, ant]
            newpoint = ordered[tuple(p2)][(ant-1)%n]
            if ant in indices[tuple(p2)][1]:
                antipodal = True
        else:
            indices[tuple(p2)][0] = [suc, (suc+1)%n]
            newpoint = ordered[tuple(p2)][(suc+1)%n]
            if suc in indices[tuple(p2)][1]:
                antipodal = True
            
        newline = line(p2, newpoint)
        aux = [p2[0], p2[1]+1]
        
        if turn(p2, p1, newpoint) == turn(p2, aux, newpoint):
            if antipodal:
                upper.insert(dualize(newline), newline)
            else:
                lower.insert(dualize(newline), newline)
        else:
            if antipodal:
                lower.insert(dualize(newline), newline)
            else:
                upper.insert(dualize(newline), newline)

            ################################################################################################
    elif side == DOWN:
        antipodal = False
        lower.delete(dualize(oldline))
        upper.insert(dualize(oldline), oldline)

        #First for p1
        ant, suc = indices[tuple(p1)][0]
        if ordered[tuple(p1)][ant] == p2:
            indices[tuple(p1)][0] = [(ant-1)%n, ant]
            newpoint = ordered[tuple(p1)][(ant-1)%n]
            if ant in indices[tuple(p1)][1]:
                antipodal = True
            
        else:
            indices[tuple(p1)][0] = [suc, (suc+1)%n]
            newpoint = ordered[tuple(p1)][(suc+1)%n]
            if suc in indices[tuple(p1)][1]:
                antipodal = True
        
        newline = line(p1, newpoint)
        aux = [p1[0], p1[1]+1]
        
        if turn(p1, p2, newpoint) == turn(p1, aux, newpoint):
            if antipodal:
                upper.insert(dualize(newline), newline)
            else:
                lower.insert(dualize(newline), newline)
        else:
            if antipodal:
                lower.insert(dualize(newline), newline)
            else:
                upper.insert(dualize(newline), newline)
            
        antipodal = False
            
        #Now for p2
        ant, suc = indices[tuple(p2)][0]
        if ordered[tuple(p2)][ant] == p1:
            indices[tuple(p2)][0] = [(ant-1)%n, ant]
            newpoint = ordered[tuple(p2)][(ant-1)%n]
            if ant in indices[tuple(p2)][1]:
                antipodal = True
        else:
            indices[tuple(p2)][0] = [suc, (suc+1)%n]
            newpoint = ordered[tuple(p2)][(suc+1)%n]
            if suc in indices[tuple(p2)][1]:
                antipodal = True
            
        newline = line(p2, newpoint)    
        aux = [p2[0], p2[1]+1]
        
        if turn(p2, p1, newpoint) == turn(p2, aux, newpoint):
            if antipodal:
                upper.insert(dualize(newline), newline)
            else:
                lower.insert(dualize(newline), newline)
        else:
            if antipodal:
                lower.insert(dualize(newline), newline)
            else:
                upper.insert(dualize(newline), newline)
            
    
    U, L = getRegionR(upper, lower)
    regionU[:] = U
    regionL[:] = L
    return sorted([p1, p2])
    
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
    
def getLines(upper, lower=None, mode = 1):
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
    
class pointExplorer(object):
    def __init__(self, points):
        self.points = points
    def randomWalk(self, q):
        if q not in self.points:
            return #TODO: Raise an appropiate exception
        sortedpoints = []
        aux = []
        index = self.points.index(q)
        for i in range(len(self.points)):
            if i == index:
                continue
            aux = self.points[0:i]
            aux.extend(self.points[i+1:])
            sortedpoints.append([self.points[i], sort_around_point(self.points[i], aux)])
        upper, lower, indices = getPointRegion(q, sortedpoints)
        print lower, upper
        
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
        indices[tuple(p)] = [[],[]]
    
    for i in xrange(len(points)):
        revert = {}
        p = points[i]
        pts = points[:i] + points[i+1:]
        antipodals = []
        
        for pt in pts:
            anti = [2*p[0]-pt[0], 2*p[1]-pt[1]]
            antipodals.append(anti)
            revert[tuple(anti)] = pt
            
        pts.extend(antipodals)
        ordered = sort_around_point(p, pts, checkConcave = True)
        
        for i in xrange(len(ordered)):#TODO: Another binary search
            if turn(p, ordered[i], q) == LEFT and turn(p, ordered[(i+1)%len(ordered)], q) == RIGHT:
                indices[tuple(p)][0] = [i, (i+1)%len(ordered)]
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
        cont+=1
        ordered, indices = orderAllPoints(p, pts)
        upper, lower, counters = getPointRegion(p, ordered, indices)
        lines1 = getLines(upper, lower)
        cosa = getRegionR(upper, lower)
        lines2 = getLines(cosa[0], cosa[1])
        pol = getPolygon(cosa[0], cosa[1])
        aux = pointAndLines(p, lines1[0]+lines1[1], lines2[0]+lines2[1], getPolSegs(pol))        
        res.append(aux)
    return res
    
def restorePts(pts):
    for p in pts:
        if len(p) > 2:
            p.pop()

def updateVis(vis, pts, res, indexp, indexLines, pol = False):
    restorePts(pts)
    pts[pts.index(res[indexp].p)].append(0)
    vis.lines = res[indexp].l1 if indexLines == 0 else res[indexp].l2
    if pol:
        vis.segments = res[indexp].pol
    else: vis.segments = []
    
def getPolygon(U, L):
    if len(U) == 0 and len(L) == 0:
        print "Both U and L are empty!"
        return
        
#    print "TAMAÑOS", len(U), len(L)
        
    upts, lpts = [], []
    for i in xrange(len(U)-1):
        upts.append(U[i][1].intersection(U[i+1][1]))
    for i in xrange(len(L)-1):
        lpts.insert(0, L[i][1].intersection(L[i+1][1]))
    
        
    if len(L) == 0:
        p1 = upts[0][:]
        p1[0] += 1000000
        p1[1] = U[0][1].evalx(p1[0])
        
        p2 = upts[-1][:]
        p2[0] -= 1000000
        p2[1] = U[-1][1].evalx(p2[0])
        
        upts.insert(0, p1)
        upts.append(p2)
        
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
        
        return lpts
        
    #This one should be the left-most point of the polygon
    lm = U[-1][1].intersection(L[-1][1])
    #and this one should be the right-most one
    rm = U[0][1].intersection(L[0][1])
    
    if len(U) == 1 and len(L) == 1: #This means the region is just a wedge
#        print "WEDGE"
        #Let's see if we need the right or the left wedge
        p = lm   
        p1 = [p[0]+1000000, U[0][1].evalx(p[0]+1000000)]
        p2 = [p[0]+1000000, L[0][1].evalx(p[0]+1000000)]        
        if turn(p1, p, p2) > 0:            
            p1 = [p[0]-1000000, L[0][1].evalx(p[0]-1000000)]
            p2 = [p[0]-1000000, U[0][1].evalx(p[0]-1000000)]
#        else:
#        return [p1, p, p2]
#        auxU = U[0][1].evalx(p[0]+1)
#        auxL = L[0][1].evalx(p[0]+1)
#        if auxU > auxL: #Then we want the right wedge
#            p1 = [p[0]+1000000, U[0][1].evalx(p[0]+1000000)]
#            p2 = [p[0]+1000000, L[0][1].evalx(p[0]+1000000)]
#        else:
#            p1 = [p[0]-1000000, U[0][1].evalx(p[0]-1000000)]
#            p2 = [p[0]-1000000, L[0][1].evalx(p[0]-1000000)]
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
            
            return upts
            
    #If we get to this point, the region is a bounded polygon
    upts.append(lm)
    upts += lpts
    upts.append(rm)
    
    return upts
    
def getCenter(polygon):
    n = len(polygon)
    res = [0,0]
    for pt in polygon:
        res[0] += pt[0]
        res[1] += pt[1]
    res[0] = float(res[0]) / float(n)
    res[1] = float(res[1]) / float(n)
    return res
    
def getPolSegs(polygon):
    colors = ["green", "red", "blue", "black", "orange", "brown", "cyan"]
    color = random.choice(colors)
    pol = []
    n = len(polygon)
    for i in range(len(polygon)):
        p1 = [float(polygon[i%n][0]), float(polygon[i%n][1])]
        p2 = [float(polygon[(i+1)%n][0]), float(polygon[(i+1)%n][1])]
        seg = [p1, p2, color, 3]
        pol.append(seg)
    return pol
    
def getRandomWalk(p, pts, steps = 10):
    ordered, indices = orderAllPoints(p, pts)
    upper, lower, counter = getPointRegion(p, ordered, indices)#TODO: USE COUNTER!!!
    U, L = getRegionR(upper, lower)
    regions = [getPolygon(U, L)]
    last = None
    for i in range(steps):
        last = randMove(upper, lower, indices, ordered, U, L, last)
#        pol = getPolygon(U, L)
##        print "\ncheco pol", pol
#        if not checkConvex(pol):
#            print "Región  no convexa"
#            return upper, lower
        regions.append(getPolygon(U, L))
    return regions
    
def getLineArray(p, pts):
    lines = []
    for i in xrange(len(pts)-1):
        for j in xrange(i+1, len(pts)):
            if pts[i]!=p and pts[j]!=p:
                lines.append(line(pts[i], pts[j]))
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
            if index == len(segs)-1:
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
        if turn(pol[i%n], pol[(i+1)%n], pol[(i+2)%n]) > 0:
            return False
    return True
    
def rationalPointToFloat(pt):
    return [float(pt[0]), float(pt[1])]