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


import geometricbasics, itertools, convexhull

def max_cup(pts):
    pts=[x[:] for x in pts]
    n=len(pts)
    pts.sort()
    M={}
    for i in xrange(n):
        for j in xrange(i+1,n):
            M[(i,j)]=2
    for j in xrange(n):
        for i in xrange(j):
            for k in xrange(j+1,n):
                if geometricbasics.turn(pts[i],pts[j],pts[k])<=0:
                    if M[j,k]<M[i,j]+1:
                        M[j,k]=M[i,j]+1
    m=0
    for e in M:
        if M[e]>m:
            m=M[e]
    return m
    
def max_cap(pts):
    pts=[x[:] for x in pts]
    n=len(pts)
    pts.sort()
    M={}
    for i in xrange(n):
        for j in xrange(i+1,n):
            M[(i,j)]=2
    for j in xrange(n):
        for i in xrange(j):
            for k in xrange(j+1,n):
                if geometricbasics.turn(pts[i],pts[j],pts[k])>=0:
                    if M[j,k]<M[i,j]+1:
                        M[j,k]=M[i,j]+1
    m=0
    for e in M:
        if M[e]>m:
            m=M[e]
    return m
    

LEFT = -1
COLLINEAR = 0
RIGHT = 1

def sortAroundPoint(p, ptsIdx, pts):
    p1 = [p[0], p[1] + 1]
    r=[]
    l=[]
    
    for i in ptsIdx:    
        q = pts[i]
        if geometricbasics.turn(p, p1, q) == RIGHT:
            r.append(i)
        elif geometricbasics.turn(p, p1, q) == LEFT:
            l.append(i)
        else:
            if p[1] >= q[1]:
                l.append(i)
            else:
                r.append(i)

    l.sort(lambda v1, v2: geometricbasics.turn(p, pts[v1], pts[v2]))
    r.sort(lambda v1, v2: geometricbasics.turn(p, pts[v1], pts[v2]))

    r.extend(l)

    concave = False
    i = 0
    for i in xrange(len(r)):
        if geometricbasics.turn(pts[r[i]], p, pts[r[(i + 1) % len(r)]]) < 0:
            concave = True
            break
    if concave:
        start = (i + 1) % len(r)
        r = [r[(start + i) % len(r)] for i in xrange(len(r))]

    return r
    

def maxKgon(pts): #Finds the largest rgon in pts in time O(n^3))
    allSorted = []
    tmp = range(1, len(pts))
        
    p = 0
    allSorted = [[] for i in xrange(len(pts))]
    allSorted[0].extend(sortAroundPoint(pts[p], tmp, pts))
    
    for i in xrange(len(tmp)):
        p, tmp[i] = tmp[i], p
        allSorted[i+1].extend(sortAroundPoint(pts[p], tmp, pts))
    
    lkp = {(i,j):-1 for i in xrange(len(pts)) for j in xrange(len(pts))}
    
    for p in xrange(len(allSorted)):
        srtd = allSorted[p]
        for i in xrange(len(srtd)):
            q = srtd[i]
            lkp[p, q] = i
    
    maxRgon = 0
    
    def findNext(i, j): #Finds the point that makes the smallest ccw angle with line pts[i]pts[j], measured around pts[j]
        if i == j:
            return -1
        p = pts[i] #points are sorted around p
        q = pts[j]
        k = 0
        lim = len(allSorted[i])
        r = pts[allSorted[i][k]]

        while(k < lim and geometricbasics.turn(q, p, r) < 0):
            k +=1
            r = pts[allSorted[i][k]]
        lim2 = lim*2
        
        while(k < lim2 and geometricbasics.turn(q, p, r) >= 0):
            k += 1
            r = pts[allSorted[i][k%lim]]
        if k == lim2:
            k = -1
        
        return allSorted[i][k%lim]
    
    nextpt = [[findNext(i, j) for j in xrange(len(pts))] for i in xrange(len(pts))]
        
    tab = [[-1 for j in xrange(len(pts))] for i in xrange(len(pts))]
    
    def step(p, q, r):
        if q < 0 or r < 0:
            return
        if pts[r] == pts[p]:
            return 2
        if tab[q][r] != -1:
            return tab[q][r]
        
        tab[q][r] = max(1+step(p, r, nextpt[r][q]) if pts[r] >= pts[p] else 0, 
                        step(p, q, allSorted[q][lkp[q,r]+1]) if lkp[q,r] < len(allSorted[q])-1 else 0)
        return tab[q][r]
        
    for i in xrange(len(pts)):
        tab = [[-1 for m in xrange(len(pts))] for n in xrange(len(pts))] 
        for j in xrange(len(pts)):
            if i == j:
                continue
            if pts[i] <= pts[j] and nextpt[j][i] != -1:
                maxRgon = max(maxRgon, step(i, j, nextpt[j][i]))
    
    return maxRgon

def maxKgonN4(pts): #Finds the largest rgon in pts in time O(n^4))
    maxH = 0
    tab = [[-1 for j in xrange(len(pts))] for i in xrange(len(pts))]
    
    def step(q, i, j): #Finds the largest rgon with q as left-most point and pts[i], pts[j] as last vertices, when sorted ccw beginning at q
        if tab[i][j] != -1: #already know the max
            return tab[i][j]
        for k in xrange(len(pts)): #try to extend it with every point in pts
            if pts[k] < q or geometricbasics.turn(q, pts[j], pts[k]) >= 0 or geometricbasics.turn(pts[i], pts[j], pts[k]) >= 0:
                continue
            if tab[j][k] == -1:
               tab[j][k] = step(q, j, k)
            tab[i][j] = max(tab[i][j], tab[j][k] + 1)
        if tab[i][j] == -1:
            tab[i][j] = 3
        return tab[i][j]
        
    for i in xrange(len(pts)):
        q = pts[i] #left-most point of the rgon
        for m in xrange(len(pts)): #reset table
            for n in xrange(len(pts)):
                tab[m][n] = -1
        for j in xrange(len(pts)):
            r = pts[j]
            if r < q:
                continue
            for k in xrange(len(pts)):
                s = pts[k]
                if s < q or geometricbasics.turn(q, r, s) >= 0:
                    continue #both r and s are to the right of q and (q, r, s) form a left turn
                maxH = max(step(q, j, k), maxH)
    return maxH
    
def naiveMaxKgon(pts): #Super naive function. Tries every combination of n points (starting with n=3) and checks if they are in convex position.
    maxH = 0
    s = []
    for n in xrange(3, len(pts)):
        found = False
        for pol in itertools.combinations(pts, n):
            ch = convexhull.CH(list(pol))
            if len(ch) == n:
                maxH = n
                s = list(pol)
                found = True
                break
        if not found:
            break
    return maxH, s
