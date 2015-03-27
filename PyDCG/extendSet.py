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

"""
Created on Sun Oct 19 20:43:41 2014

@author: Carlos
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 21:43:38 2014

@author: carlos
"""

import holes, datastructures, pointExplorer
import random, time, pickle, sys, argparse
#import holes, pointExplorer, datastructures, random, time, pickle

def extend(pts, speedup='try'):
    if holes.count_convex_rholes(pts, 6) != 0:
        print "Initial set has empty hexagons"
    p = datastructures.randPoint(10000000000)
    bestp = p[:]
    pts.append(p)
    emptyRegions = []
    minH = holes.count_convex_rholes(pts, 6, speedup=speedup)
    print "starting with", minH
    pts.pop()
    Ap, Bp = holes.count_convex_rholes_p(p, pts, 6, speedup=speedup)
    regionsChecked = 0
    for pol in pointExplorer.getRandomWalkDFS(p, pts, float('inf')):
        regionsChecked += 1
        print "checking region", regionsChecked
        q = pointExplorer.getCenter(pol)
        if q is None:
            emptyRegions.append(pol)
        else:
            print "trying with", q
            Aq, Bq = holes.count_convex_rholes_p(q, pts, 6, speedup=speedup)
            newH = minH + Aq - Ap + Bp - Bq
            
            if newH <= minH:
                if newH < minH:
                    print "%d points, %d 6 holes"%(len(pts)+1, newH)
                minH = newH
                Ap, Bp = Aq, Bq
                bestp = q[:]
                
                if minH == 0:
                    print "yay!"
                    name = "%d_pts%d_holes%d.pts"%(len(pts)+1, minH, int(time.time()) )
                    pts.append(bestp)
                    f = open(name, "wb")
                    pickle.dump(pts, f)
                    f.close()
                    return pts
    print "Checked", regionsChecked, "best result:", minH, "with", bestp
    return emptyRegions

def hill_climbing(pts = None, tries = 1000, start=10, t=1000000000, run_time=300, days=0, save_interval = 300, speedup='try'):
    
    if days>0:
        run_time=24*3600*days
        
    start_time = time.time()
    last_save = time.time()
    
    if pts is None:
        pts = [datastructures.randPoint(t) for i in xrange(start)]
    else:
        for i in xrange(start - len(pts)):
            pts.append(datastructures.randPoint(t))
        
#    p = random.choice(pts)
            
#    for i in range(n-len(pts)):
#            if colored: 
#               pts.append([random.randint(-k,k),random.randint(-k,k),random.randint(0,1)])
#            else:
#               pts.append([random.randint(-k,k),random.randint(-k,k)]) 
    minH = holes.count_convex_rholes(pts, 6, speedup=speedup)
    
    while minH == 0:
        pts.append(datastructures.randPoint(t))
        minH = holes.count_convex_rholes(pts, 6, speedup=speedup)    
    
    while time.time()-start_time<run_time:
        minH = holes.count_convex_rholes(pts, 6)
        print "Starting with %d points, %d holes"%(len(pts), minH)
        
        if time.time()-last_save > save_interval:
            Id = str(int(time.time()))+"_%d_pts_%d_h"%(len(pts), minH)
            f = open(Id, "w")
            pickle.dump(pts, f)
            f.close()        
            last_save = time.time()
       
        idx = random.randint(0,len(pts)-1)
        p = pts.pop(idx)
        Ap, Bp = holes.count_convex_rholes_p(p, pts, 6, speedup=speedup)
        
        for pol in pointExplorer.getRandomWalkDFS(p, pts, tries):
            q = pointExplorer.getCenter(pol)
            if q is None:
                continue
            q = [int(q[0]), int(q[1])]
#            pts[idxp] = q
            Aq, Bq = holes.count_convex_rholes_p(q, pts, 6, speedup=speedup)
            newH = minH + Aq - Ap + Bp - Bq
            
            if newH <= minH:
                if newH < minH:
                    print "%d points, %d 6 holes"%(len(pts)+1, newH)
                minH = newH
                Ap, Bp = Aq, Bq
                p = q[:]
                
                if minH == 0:
                    print "yay!"
                    break
        pts.append(p)
        if minH == 0:
           # return pts
            Id = str(int(time.time()))+"_%d_pts_%d_h"%(len(pts), minH)
            f = open(Id, "w")
            pickle.dump(pts, f)
            f.close()
            print pts
            
            pts.append(datastructures.randPoint(t))
                
    print "Done!"
    Id = str(int(time.time()))+"_%d_pts_%d_h"%(len(pts), minH)
    f = open(Id, "w")
    pickle.dump(pts, f)
    f.close()
    return pts

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-filename', default = None, type = str, help = "Name of a file containing a set of points")
#    parser.add_argument('-start', default = 10, type = int, help = "Nummber of points to start the search")
#    parser.add_argument('-tries', default = 300, type = int, help = "Number of tries to move a point")
#    parser.add_argument('-t', default = 1000000, type = int, help = "Maximum absolute value of the coordinate for a random point")
#    parser.add_argument('-run_time', default = 300, type = int, help = "Run time in seconds")
#    parser.add_argument('-save_interval', default = 300, type = int, help = "Interval to dave the current set of points in seconds")
#    parser.add_argument('-days', default = 0, type = int, help = "Number of days to run the program")
    args = parser.parse_args()
    if args.filename is not None:
        f = open(args.filename, 'r')
	pts = pickle.load(f)
	f.close()
 
	hill_climbing(pts = pts, tries = args.tries, start = args.start, run_time = args.run_time, save_interval = args.save_interval, days = args.days)
    else:
        hill_climbing(tries = args.tries, start = args.start, run_time = args.run_time, save_interval = args.save_interval, days = args.days)
#    hill_climbing(tries=300, start = 29, run_time = 43200, save_interval = 3600)
