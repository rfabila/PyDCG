"""Module used to count the number of crossings in the complete
geometric graph"""

from geometricbasics import *

def count_crossings(pts):
    """Returns the he number of crossings in the complete
    geometric graph with vertex set pts. Runs in O(n^2logn) time"""
    n=len(pts)
    tmp_pts=[[0,0] for i in range(n-1)]
    cr=0
    for i in range(n):
        #pivote
        p=pts[i]
        #We copy the points distinct from p to tmp_pts
        for j in range(0,i):
            tmp_pts[j]=pts[j][:]
        for j in range(i+1,n):
            tmp_pts[j-1]=pts[j][:]
        tmp_pts=sort_around_point(p,tmp_pts)
        j=0
        for i in range(len(tmp_pts)):
            while (turn(p,tmp_pts[i],tmp_pts[(j+1)%(n-1)])<=0 and
                    (j+1)%(n-1)!=i):
                j=j+1
                    
            ni=(j-i)%(n-1)
            cr=cr+ni*(ni-1)/2

    total=n*(n-1)*(n-2)*(n-3)/2    
        
    return cr-(total/4)

def count_crossings_candidate_list(point_index,candidate_list,pts):
    """Let k=len(candidate_list), n=len(pts). Returns the
       best candidate for pts[point_index] in time
       O(n^2logn)+O(k*nlogn)."""
    
    def gen_interval_list(q,pts_q):
        pts_q=sort_around_point(q,pts_q)
        intervals_q=[[-x[0]+2*q[0],-x[1]+2*q[1]] for x in pts_q]
        intervals_q.extend(pts_q)
        sort_around_point(q,intervals_q)
        j=0
        for x in pts_q:
            while intervals_q[j]!=x:
                intervals_q[j].append(False)
                j=j+1
            intervals_q[j]=True
        return intervals_q
        
        