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


import geometricbasics

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