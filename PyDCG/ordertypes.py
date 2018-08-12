from . import geometricbasics
import hashlib
from . import convexhull


def points_index(pts):
    """Returns a dictionary with the indices of the points in pts"""
    D = {}
    for i in range(len(pts)):
        q = (pts[i][0], pts[i][1])
        D[q] = i
    return D


def lambda_matrix(pts):
    """M[i,j] is the number of points of pts that lie to the LEFT
    of the edge (pts[i],pts[j])."""
    M = [[0 for i in range(len(pts))] for j in range(len(pts))]
    D = points_index(pts)
    n = len(pts)
    for i in range(n):
        tpts = pts[:i]
        tpts.extend(pts[i+1:])
        p = pts[i]
        # Check whether we have the C++ version running correctly
        pts_sorted = geometricbasics.sort_around_point(p, tpts)
        k = 0
        for j in range(n-1):
            while (geometricbasics.turn(p, pts_sorted[j], pts_sorted[(k+1) % (n-1)]) <= 0 and
                   (k+1) % (n-1) != j):
                k = k+1
            ni = (k-j) % (n-1)
            M[D[tuple(p)]][D[tuple(pts_sorted[j])]] = ni
    return M


def signature(pts):
    """Obtains a hash from the lambda matrix. Useful for checking for repetitions.
       Runs in O(n^2 \log n) time."""
    # print("lambda Matrix started")
    M = lambda_matrix(pts)
    # print("lambda Matrix Done")
    # s = ""
    s = []
    n = len(pts)
    counter = 0
    for i in range(n):
        for j in range(i+1, n):
            # print(counter)
            counter += 1
            s.append(str(M[i][j]))
            # s = s + str(M[i][j])+"|"
    s = "|".join(s)
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def unique_signature(pts):
    """Similar to signature, it produces a string associated to the point set,
       but it is independent of the labelling of the point set.
       It runs in O(n^3 \logn) time"""
    pts = [x[:] for x in pts]
    D = points_index(pts)
    ch = convexhull.CH(pts)
    S = []
    for p in ch:
        idx = D[tuple(p)]
        pts2 = pts[:idx]
        pts2.extend(pts[idx+1:])
        pts2 = geometricbasics.sort_around_point(p, pts2)
        pts2.append(p)
        S.append(signature(pts2))
    print(S)
    return min(S)


def remove_duplicates(P):
    """Given a set of pointsets, removes any duplicates"""
    D = {}
    for pts in P:
        D[signature(pts)] = pts
    return list(D.values())
