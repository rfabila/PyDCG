import geometricbasics
import hashlib

def points_index(pts):
    """Returns a dictionary with the indices of the points in pts"""
    D={}
    for i in xrange(len(pts)):
        q=(pts[i][0],pts[i][1])
        D[q]=i
    return D

def lambda_matrix(pts):
    """M[i,j] is the number of points of pts that lie to the LEFT
    of the edge (pts[i],pts[j])."""
    M=[[0 for i in xrange(len(pts))] for j in xrange(len(pts))]
    D=points_index(pts)
    n=len(pts)
    for i in xrange(n):
        tpts=pts[:i]
        tpts.extend(pts[i+1:])
        p=pts[i]
        #check whether we have the C++ version running correctly
        pts_sorted=geometricbasics.sort_around_point(p,tpts)
        k=0 
        for j in xrange(n-1):
            while (geometricbasics.turn(p,pts_sorted[j],pts_sorted[(k+1)%(n-1)])<=0 and
                    (k+1)%(n-1)!=j):
                k=k+1
            ni=(k-j)%(n-1)
            M[D[tuple(p)]][D[tuple(pts_sorted[j])]]=ni
    return M

def signature(pts):
    """Obtains a hash from the lambda matrix. Useful for checking for repetitions"""
    M=lambda_matrix(pts)
    s=""
    n=len(pts)
    for i in xrange(n):
        for j in xrange(i+1,n):
            s=s+str(M[i][j])+"|"
    return hashlib.md5(s).hexdigest()
        