# -*- coding: utf-8 -*-
#!/usr/bin/env python

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


import random
import warnings
from geometricbasics import turn

# TODO: cambiar bridge a miembro o sacarla de la clase (actualmente es
# miembro de clase)

LEFT = 0
RIGHT = 1
UPPER = 3
LOWER = 4

"""Module implementing various data structures"""

# I feel the class slow. It is not clear
# whether the complexity is wrong or is just
# the overhead of constructing the Node objects.
# Or I am just a bad programmer.
# This could be a source for big improvement in the future.
# Seems to be working ok though.
class Treap(object):

    """An implementation of a treap. Note that
       lower priority elements are at the top.
       Loosely based on the description in "Randomized Algorithms"
       by Motwani and Raghavan. All mistakes are mine"""

    def __str__(self):
        if self.empty:
            return "Empty Treap"
        return str(self.root)

    def __init__(self, compare=lambda x, y: x - y, max_size=1000):

        self.compare = compare
        self.root = None
        self.empty = True

    # def clear(self):
     #   self.root=None
     #   self.empty=True
     #   self.free_nodes=self.nodes[:]

    def find(self, key):
        if self.empty:
            return None
        else:
            node = self.root
            while(node is not None):
                # if its smaller
                if self.compare(key, node.key) < 0:
                    node = node.left
                elif self.compare(key, node.key) > 0:
                    node = node.right
                else:
                    return node
            return node

    def delete(self, key):
        node = self.find(key)
        self.delete_node(node)
        return node

    def delete_node(self, node):
        if node is None:
            return None
        while node.left is not None or node.right is not None:
            if node.left is None or node.right is None:
                if node.left is None:
                    self.rotate_left(node)
                else:
                    self.rotate_right(node)
            else:
                if self.compare_priorities(node.left, node.right) > 0:
                    self.rotate_left(node)
                else:
                    self.rotate_right(node)

        if node.parent is not None:
            if node.parent.left == node:
                node.parent.left = None
            else:
                node.parent.right = None
        else:
            self.root = None
            self.empty = True

        return node

    def insert(self, key, obj=None):
        node = self.Node(key=key, obj=obj)
        self.insert_node(node)

    def insert_node(self, node):
        if self.empty:
            self.root = node
            self.empty = False
        else:
            leaf = self.root
            parent = self.root
            while(leaf is not None):
                # if its smaller
                parent = leaf
                if self.compare(node.key, leaf.key) < 0:
                    leaf = leaf.left
                else:
                    leaf = leaf.right
            node.parent = parent
            if self.compare(node.key, parent.key) < 0:
                parent.left = node
            else:
                parent.right = node
            self.restore_heap(node)

    def restore_heap(self, node):
        """Restores the heap property by
           rotating the node upwards if necessary"""
        if node.parent is None:
            return False

        while self.compare_priorities(node.parent, node) > 0:
            if node == node.parent.left:
                self.rotate_right(node.parent)
            else:
                self.rotate_left(node.parent)
            if node.parent is None:
                break

    def restore_heap_downwards(self, node):
        """Restores the heap property by rotating
           the node downwards if necessary."""
        while(self.compare_priorities(node, node.left)) >= 1 or (self.compare_priorities(node, node.right)) >= 1:
            if self.compare_priorities(
                    node.left,
                    node.right) >= 1 or node.left is None:
                # right must go above
                self.rotate_left(node)
            else:
                # left must go above
                self.rotate_right(node)

    def show(self):
        print self.root.__str__()

    def compare_priorities(self, x, y):
        if x == y or x is None or y is None:
            return 0
        while x.priority == y.priority:
            x.priority.append(random.random())
            y.priority.append(random.random())

        if x.priority < y.priority:
            return -1
        else:
            return 1

    def min(self):
        return self.min_tree(self.root)

    def min_tree(self, node):
        """Returns the minimum value
           at the tree hanging from node
           as a root"""
        if node is None:
            return None
        return_node = node
        while return_node.left is not None:
            return_node = return_node.left
        return return_node

    def max(self):
        return self.max_tree(self.root)

    def max_tree(self, node):
        """Returns the maximum value
           at the tree hanging from node
           as a root"""
        if node is None:
            return None
        return_node = node
        while return_node.right is not None:
            return_node = return_node.right
        return return_node

    def rotate_left(self, node):
        if node.right is not None:
            grandpa = node.parent
            nnode = node.right
            nnode.parent = grandpa
            node.parent = nnode

            if grandpa is not None:
                if grandpa.left == node:
                    grandpa.left = nnode
                else:
                    grandpa.right = nnode
            else:
                self.root = nnode

            node.right = nnode.left
            nnode.left = node

            if node.right is not None:
                node.right.parent = node

    def rotate_right(self, node):
        if node.left is not None:
            grandpa = node.parent
            nnode = node.left
            nnode.parent = grandpa
            node.parent = nnode

            if grandpa is not None:
                if grandpa.left == node:
                    grandpa.left = nnode
                else:
                    grandpa.right = nnode
            else:
                self.root = nnode

            node.left = nnode.right
            nnode.right = node

            if node.left is not None:
                node.left.parent = node

    def check_priority(self, node):
        if node is None:
            return True
        if (not self.check_priority(node.left)) or (
                not self.check_priority(node.right)):
            return False
        if node.left is not None or node.right is not None:
            if node.left is not None:
                if self.compare_priorities(node, node.left) > 0:
                    return False
            if node.right is not None:
                if self.compare_priorities(node, node.right) > 0:
                    return False
        return True

    def count_elements(self, node=0):
        if node == 0:
            node = self.root

        if node is None:
            return 0
        else:
            num = self.count_elements(
                node.left) + self.count_elements(node.right) + 1
            return num

    def move_node_to_root(self, node):
        """Moves the node to the root, but
           breaks the heap property in the proccess.
           Afterwards a splitting a this vertex is trivial"""
        parent = node.parent
        while parent is not None:
            if parent.left == node:
                self.rotate_right(parent)
            else:
                self.rotate_left(parent)
            parent = node.parent

    def split_at_node(self, node):
        """Splits the treap a the given node."""
        self.move_node_to_root(node)
        left_treap = Treap(compare=self.compare)
        right_treap = Treap(compare=self.compare)
        root = self.root
        if root.left is not None:
            left_treap.empty = False
            left_treap.root = root.left
            left_treap.root.parent = None
        if root.right is not None:
            right_treap.empty = False
            right_treap.root = root.right
            right_treap.root.parent = None
        root.left = None
        root.right = None
        return (left_treap, root, right_treap)

    def split(self, key):
        """Splits the treap at the given key
           value. Note that the old treap no longer
           satisfies the heap property; should
           be destroyed but it is difficult and
           undesirable to do so in Python."""
        node = self.find(key)
        if node is not None:
            return self.split_at_node(node)
        print "\n", key, "not found", "in", self
        print "Split returns NONE"
        return (self, None, None)

    def paste(self, node, T2):
        """Returns a new treap conaining self, the node and the
           treap T2. The original treaps, self and T2 no longer
           satisfy the heap property."""
#        print "pasting",self, node, T2
        treap = Treap(compare=self.compare)
        treap.empty = False
        treap.root = node
        treap.root.left = self.root
        treap.root.right = T2.root
        if treap.root.left is not None:
            treap.root.left.parent = treap.root
        if treap.root.right is not None:
            treap.root.right.parent = treap.root
        treap.root.parent = None
        treap.restore_heap_downwards(treap.root)
        return treap

    def join(self, T2):
        """Returns the join of self and T2, destroys
           the heap property of both in the proccess. It
           assumes T1<=T2"""
        if self.empty:
            return T2
        elif T2.empty:
            return self
        else:
            max_node = self.max()
            self.delete_node(max_node)
            return self.paste(max_node, T2)

    def compute_height(self, node):
        if node is None:
            return 0
        left = self.compute_height(node.left)
        right = self.compute_height(node.right)
        h = max(left, right)
        return h + 1

    def successor(self, node):
        """Returns the succesor of node"""
        if node.right is not None:
            return self.min_tree(node.right)
        elif node.parent is not None:
            parent_node = node.parent
            son_node = node
            while parent_node.parent is not None and parent_node.left != son_node:
                son_node = parent_node
                parent_node = parent_node.parent
            if parent_node.left != son_node:
                return None
            else:
                return parent_node
        else:
            return None

    def predecessor(self, node):
        """Returns the predecessor of a node"""
        if node.left is not None:
            return self.max_tree(node.left)
        elif node.parent is not None:
            parent_node = node.parent
            son_node = node
            while parent_node.parent is not None and parent_node.right != son_node:
                son_node = parent_node
                parent_node = parent_node.parent
            if parent_node.right != son_node:
                return None
            else:
                return parent_node
        else:
            return None

    class Node(object):

        def __init__(self, key=0, obj=None):
            self.key = key
            self.obj = obj
            self.priority = []
            self.parent = None
            self.right = None
            self.left = None

        # for debugging purposes
        def __str__(self):

            if self.left is None:
                sleft = "()"
            else:
                sleft = self.left.__str__()

            if self.right is None:
                sright = "()"
            else:
                sright = self.right.__str__()
            # ",pr="+self.priority.__str__()+","+self.obj.__str__()+")"
            snode = "(key=" + self.key.__str__() + ")"
            s = "(" + snode + "(" + sleft + "," + sright + ")" + ")"
            return s

        def isLeaf(self):
            return self.right is None and self.left is None


# Test functions
def treap_sort(s, t=100):
    treap = Treap(max_size=s)
    for i in xrange(t):
        #        print "sort",i
        for j in xrange(s):
            treap.insert(random.randint(0, 2 * s))
        while not treap.empty:
            node = treap.min()
#            print node.key
            treap.delete(node.key)


def treapToList(T):
    l = []

    def inOrder(node):
        if node.left is not None:
            inOrder(node.left)

        if node.obj is not None:
            l.append([node.key, node.obj])
        else:
            l.append(node.key)

        if node.right is not None:
            inOrder(node.right)

    if T.empty:
        return l
        
    inOrder(T.root)
    
    return l


class dynamic_half_hull(object):

    def __init__(self, side=UPPER):
        self.root = None
        self.empty = True
        self.side = side

    def right_rotation(self, node):
        if node.left is not None:
            parent = node.parent
            lson = node.left

            lson.parent = parent
            if parent is not None:
                if parent.right == node:
                    parent.right = lson
                else:
                    parent.left = lson
            else:
                self.root = lson

            node.left = lson.right
            if node.left is not None:
                node.left.parent = node

            node.parent = lson
            lson.right = node

    def left_rotation(self, node):
        if node.right is not None:
            parent = node.parent
            rson = node.right

            rson.parent = parent
            if parent is not None:
                if parent.right == node:
                    parent.right = rson
                else:
                    parent.left = rson
            else:
                self.root = rson

            node.right = rson.left
            if node.right is not None:
                node.right.parent = node

            node.parent = rson
            rson.left = node

    def insert(self, p, obj=None):
        # v is the new node
        v = self.Node(key=p, obj=obj)
        v.J = p
        v.Q.insert(key=p, obj=obj)

        if self.empty:
            self.root = v
            self.empty = False
            return
            
        u = self.DOWN(self.root, v)
                
        if u.key != v.key:
            aux = self.Node()
            aux.priority[0] = random.random()
            parent = u.parent
            
            if parent is None:                       # u is currently the root
                self.root = aux
            elif parent.right is u:     # u is a right son
                parent.right = aux
                aux.parent = parent
            else:
                parent.left = aux      # u is a left son
                aux.parent = parent
                
            u.parent = aux
            v.parent = aux
            if v.key[0] >= u.key[0]:
                if v.key[0] == u.key[0]:
                    print "Same Coordinate"
                    print "v:J", v.J, "v.data", v.obj, "v.points", v.obj.getPoints()
                    print "u:J", u.J, "u.data", u.obj, "u.points", u.obj.getPoints()
                    raise Exception("Trying to insert a point with the same x-coordinate as an existing one") #TODO: This means that there are points with the same x-coordinate. 
                                    #Make a descriptive exception or find a way to handle this case
                aux.key = [u.key[0], 0]
                aux.left = u
                aux.right = v
            else:
                aux.key = [v.key[0], 0]
                aux.left = v
                aux.right = u

        else:
            #            print "Point", p, "is already in the tree"
            self.UP(u)
            return
            
        self.UP(v)
#        print "DONE!"
#        print "Currently we have:"
#        aux = self.toList()
#        for cosa in aux:
#            print cosa[0], cosa[1].getPoints()

    def delete(self, p):
        #        print "deleting", p
        aux = self.Node(key=p)
        if self.root is None:#TODO: borrar
            print "FAIL! Empty treap"
            print self.toList()
            raise Exception()
        u = self.DOWN(self.root, aux)
#        print "DOWN gave", u

        if u.key != p:
#            warnings.warn("Point" + str(p) + "not found.", stacklevel=3)
            self.UP(u)
            raise Exception("Point" + str(p) + "not found.") #TODO: Check this exception
            return

        if u.parent is None:  # u is the only element in the tree
            self.empty = True
            self.root = None
            return

        sib = u.parent.right
        if sib is u:
            sib = u.parent.left

        grandpa = u.parent.parent

        if grandpa is not None:
            if grandpa.left is u.parent:
                grandpa.left = sib
            else:
                grandpa.right = sib

            sib.parent = grandpa

            self.UP(sib)
            return

        # This means that u's parent is the root, so we make sib the new root
        else:
            self.root = sib
            sib.parent = None
            return

    def DOWN(self, v, p):
        if not v.isLeaf():
            Q1, r, Q2 = v.Q.split(v.J)
            if Q1 is None or Q2 is None:
                raise Exception("Inside DOWN, split failed") #TODO: This shouldn't happen anymore, right?
            Q1.insert_node(r)
            if v.left is not None:
                v.left.Q = Q1.join(v.left.Q)
            if v.right is not None:
                v.right.Q = v.right.Q.join(Q2)
            if p.key[0] <= v.key[0]:
                v = v.left
            else:
                v = v.right
            return self.DOWN(v, p)
        else:
            return v

    def UP(self, v):
        if v != self.root:
            # First we check if a rotation is neccesary
            if v.parent != self.root:
                parent = v.parent
                grandpa = parent.parent
                
                while parent.priority == grandpa.priority:
                    parent.priority.append(random.random())
                    grandpa.priority.append(random.random())

                if parent.priority <= grandpa.priority:
                    sibling = parent.left if parent.right is v else parent.right
                # We will continue UP at v or its sibling new position
                # depending on who gets a lower position after rotating
                    if grandpa.right == parent:
                        self.left_rotation(grandpa)   #v's parent became v's rson
                    else:
                        self.right_rotation(grandpa)  #v's parent became v's lson
                    if sibling.parent == grandpa:
                        v = sibling

            Q1, Q2, Q3, Q4, J = dynamic_half_hull.bridge(
                v.parent.left.Q, v.parent.right.Q, self.side)

            v.parent.left.Q = Q2
            v.parent.right.Q = Q3
            v.parent.Q = Q1.join(Q4)
            v.parent.J = J
            v.parent.key = [max(v.parent.key[0], v.parent.left.key[0]), 0]
            self.UP(v.parent)
        return

    @classmethod
    # The points in Lower should have smaller y coordinates than the ones in
    # Upper
    def bridge(cls, Left, Right, side=UPPER):
        SUPPORT = 1
        CONCAVE = 2
        REFLEX = 3

        maxx = Left.max().key[0]

        def update_point(treap, t_aux):
            t = t_aux.key
            tm = treap.predecessor(t_aux)
            tm = t if tm is None else tm.key
            tM = treap.successor(t_aux)
            tM = t if tM is None else tM.key
            return t, tm, tM

        p_aux = Right.root
        p, pm, pM = update_point(Right, p_aux)

        q_aux = Left.root
        q, qm, qM = update_point(Left, q_aux)

        def find_case():
            p_case = 0
            q_case = 0

            if side == UPPER:
                if turn(q, p, pm) >= 0 and turn(q, p, pM) >= 0:
                    p_case = SUPPORT
                elif turn(q, p, pm) < 0 and turn(q, p, pM) >= 0:
                    p_case = CONCAVE
                else:
                    p_case = REFLEX

                if turn(q, p, qm) >= 0 and turn(q, p, qM) >= 0:
                    q_case = SUPPORT
                elif turn(q, p, qm) >= 0 and turn(q, p, qM) < 0:
                    q_case = CONCAVE
                else:
                    q_case = REFLEX

            elif side == LOWER:
                if turn(q, p, pm) <= 0 and turn(q, p, pM) <= 0:
                    p_case = SUPPORT
                elif turn(q, p, pm) > 0 and turn(q, p, pM) <= 0:
                    p_case = CONCAVE
                else:
                    p_case = REFLEX

                if turn(q, p, qm) <= 0 and turn(q, p, qM) <= 0:
                    q_case = SUPPORT
                elif turn(q, p, qm) <= 0 and turn(q, p, qM) > 0:
                    q_case = CONCAVE
                else:
                    q_case = REFLEX

            return p_case, q_case

        pcase, qcase = find_case()

        while pcase != SUPPORT or qcase != SUPPORT:
            # Caso 2
            if pcase == SUPPORT and qcase == REFLEX:
                pm = p
                q_aux = q_aux.left
                q, qm, qM = update_point(Left, q_aux)
            # Caso 3
            elif pcase == SUPPORT and qcase == CONCAVE:
                pm = p
                q_aux = q_aux.right
                q, qm, qM = update_point(Left, q_aux)
            # Caso 4
            elif pcase == REFLEX and qcase == SUPPORT:
                qM = q
                p_aux = p_aux.right
                p, pm, pM = update_point(Right, p_aux)
            # Caso 5
            elif pcase == CONCAVE and qcase == SUPPORT:
                qM = q
                p_aux = p_aux.left
                p, pm, pM = update_point(Right, p_aux)
            # Caso 6
            elif pcase == REFLEX and qcase == REFLEX:
                p_aux = p_aux.right
                p, pm, pM = update_point(Right, p_aux)
                q_aux = q_aux.left
                q, qm, qM = update_point(Left, q_aux)
            # caso 7
            elif pcase == CONCAVE and qcase == REFLEX:
                q_aux = q_aux.left
                q, qm, qM = update_point(Left, q_aux)
            # Caso 8
            elif pcase == REFLEX and qcase == CONCAVE:
                p_aux = p_aux.right
                p, pm, pM = update_point(Right, p_aux)
            # Caso 9
            elif pcase == CONCAVE and qcase == CONCAVE:
                # We need the y coordinate of the intersection of tangents ppm and qqM
                # Slope of line ppm
                ap = p[1] - pm[1]
                bp = p[0] - pm[0]
                # Slope of line qqM
                aq = q[1] - qM[1]
                bq = q[0] - qM[0]
                if bp == 0 or bq == 0:
                    print "Recta vertical"
                if (ap / bq) == (aq / bq):
                    warnings.warn("Misma pendiente")
                # Each line equation looks like ax - by = ax_0 - by_0, we store
                # the rhs of this equation on c
                cp = ap * p[0] - bp * p[1]
                cq = aq * q[0] - bq * q[1]
# If we are calculating the right/left hulls we solve for y:
# y = (ap*cq - cp*aq)/(-ap*bq + bp*aq)
#                y_num = ap*cq - aq*cp
#                y_den = aq*bp - ap*bq
# If we are calculating the upper/lower hulls we solve for x
                #x = (-cp*bq + cq*bp)/(-ap*bq + bp*aq)
                x_num = cq * bp - cp * bq
                x_den = aq * bp - ap * bq

                # This is to avoid multiplying by a negative number in the next
                # if, thus changing the inequality
                if x_den < 0:
                    x_den *= -1
                    x_num *= -1

                # Subcase 1:
                if x_num <= (maxx * x_den):
                    # We can only eliminate the lower part of the hull
                    if qm != q:
                        qm = q
                    # q is the first point of the chain, so we can move on to
                    # the upper part
                    else:
                        q_aux = q_aux.right
                        q, qm, qM = update_point(Left, q_aux)
                # Subcase 2
                else:
                    # We can only eliminate the upper part of the hull
                    if pM != p:
                        pM = p
                    # q is the last point of the chain, so we can move on to
                    # the lower part
                    else:
                        p_aux = p_aux.left
                        p, pm, pM = update_point(Right, p_aux)

            pcase, qcase = find_case()

        # p and q are the points that determine the bridge
        # COLINEAR CASES################################### TODO: Are these neccesary?
#        while turn(q, qM, p) == 0 and q != qM:
# print "collinear!"
#            q_aux = Left.successor(q_aux)
#            q, qm, qM = update_point(Left, q_aux)
#
#        while turn(p, pm, q) == 0 and p != pm:
# print "collinear!"
#            p_aux = Right.predecessor(p_aux)
#            p, pm, pM = update_point(Right, p_aux)

        ###############################################################
        J = q

        Q1, q, Q2 = Left.split(q)
        Q3, p, Q4 = Right.split(p)

        if Q1 is None or Q2 is None or Q3 is None or Q4 is None: #TODO: This shouldn't happen anymore either
            raise Exception("Inside bridge, split failed")

        Q1.insert_node(q)
        Q4.insert_node(p)
        
        return Q1, Q2, Q3, Q4, J

    def toList(self):
        if self.root is None:
            return []
        res = treapToList(self.root.Q)
        if self.side == LOWER:
            res.reverse()
        return res

    class Node(object):

        def __init__(self, key=[0, 0], obj=None):

            # A point is the node is a leaf, otherwise [0, maxy] where maxy is
            # the biggest y coordinate in the left subtree
            self.key = key
            # Q is the part does not contribute to the lc-hull of parent
            self.Q = Treap(lambda p, q: p[0] - q[0])  
            # J is the position of the support point in parent's lc-hull
            self.J = key
            self.parent = None
            self.right = None
            self.left = None
            self.obj = obj
            self.priority = [2]

        def isLeaf(self):
            return self.right is None and self.left is None

        # for debugging purposes
        def __str__(self):

            if self.left is None:
                sleft = "()"
            else:
                sleft = str(self.left)

            if self.right is None:
                sright = "()"
            else:
                sright = str(self.right)

            snode = "(key = " + str(self.key) + ")"
            s = "(%s(%s,%s))" % (snode, sleft, sright)
            return s


def paint_hull(pts, hull, color_u=0, color_l=1, color_int=2):
    def paint(pts_prime, color):
        for p in pts_prime:
            if len(p) < 3:
                pts[pts.index(p)].append(color)
            else:
                pts[pts.index(p)][2] = color

    if isinstance(hull, dynamic_half_hull):
        if hull.side == UPPER:
            paint(hull.toList(), color_u)
        else:
            paint(hull.toList(), color_l)

    elif isinstance(hull, dynamic_convex_hull):
        u = hull.upper.toList()
        l = hull.lower.toList()
        intersection_points = [l.pop(), u.pop()]
        l.pop(0)
        u.pop(0)
        paint(u, color_u)
        paint(l, color_l)
        paint(intersection_points, color_int)


class dynamic_convex_hull(object):

    def __init__(self):
        self.upper = dynamic_half_hull(UPPER)
        self.lower = dynamic_half_hull(LOWER)

    def insert(self, p):
        self.upper.insert(p)
        self.lower.insert(p)

    def delete(self, p):
        self.upper.delete(p)
        self.lower.delete(p)

    def toList(self):
        u = self.upper.toList()
        if len(u) > 0:
            u.pop()
        l = self.lower.toList()
        u.extend(l)
        if len(u) > 0:
            u.pop()
        return u

    def __str__(self):
        print self.toList()


def compute_height(node):
    if node is None:
        return 0
    left = compute_height(node.left)
    right = compute_height(node.right)
    h = max(left, right)
    return h + 1


def in_order_priorities(node):
    if node.right is None and node.left is None:
        print node.priority
        return
    if node.left is not None:
        in_order_priorities(node.left)
    print node.priority
    if node.right is not None:
        in_order_priorities(node.right)

######################### TESTS #####################################


def randPoint(k=1000000):
    return [random.randint(-k, k), random.randint(-k, k)]


def time_test(n=100, k=100000, skip=1, fileName="tests.txt"):
    from . import convexhull
    import time
    import copy
    f = open(fileName, "w")
    pts = []
    cont = 0
    ch = dynamic_convex_hull()
    for i in xrange(n):
        if not i % skip:
            print cont,
            f.write("%d," % (cont))
            cont += 1
        p = randPoint(k)
        pts.append(p)
        t0 = time.time()
        ch.insert(p)
        t1 = time.time()
        if not i % skip:
            print t1 - t0,
            f.write("%.10f," % (t1 - t0))

        s = copy.deepcopy(pts)
        t0 = time.time()
        U, L = convexhull.hulls(s)
        t1 = time.time()
        if not i % skip:
            print t1 - t0
            f.write("%.10f\n" % (t1 - t0))
    f.close()


def profile(n=1000, k=1000000, functions=None, fileName="profiler_res"):
    import line_profiler
    prof = line_profiler.LineProfiler()
    if functions is not None:
        for f in functions:
            prof.add_function(f)
    else:
        prof.add_function(dynamic_half_hull.insert)
        prof.add_function(dynamic_half_hull.UP)
        prof.add_function(dynamic_half_hull.bridge)
#        prof.add_function(dynamic_half_hull.DOWN)

    ch = dynamic_convex_hull()
    pts = [randPoint(k) for i in xrange(n)]

    for i in xrange(len(pts)):
        for j in xrange(i + 1, len(pts)):
            if pts[i][0] == pts[j][0]:
                print "Misma coordenada x:", pts[i], pts[j]

    def aux(ch, pts):
        for p in pts:
            ch.insert(p)

#    prof.runcall(aux, (ch,pts), {})
    prof.runctx("aux(ch, pts)", {'ch': ch, 'pts': pts, 'aux': aux}, None)
    f = open(fileName, "w")
    prof.print_stats(f)
    f.close()
    print "Done. Stats saved in '%s'" % fileName


def verifyBinaryTree(T):
    #    import inspect
    comp = T.compare
#    print inspect.getsource(comp)

    def check(node):
        if node is None:
            return True
        if node.left is not None:
            resL = comp(node.key, node.left.key) >= 0
        else:
            resL = True

        if node.right is not None:
            resR = comp(node.key, node.right.key) <= 0
        else:
            resR = True

        if resL and resR:
            return True and check(node.left) and check(node.right)
        print "fail at node", node
        return False
    res = check(T.root)
    if not res:
        print "FAIL!", T
        raise Exception
    else:
        print "ALL GOOD"
