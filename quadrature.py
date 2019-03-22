# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 22:44:18 2015
"""

__author__ = 'Konstantinos Tatsis'
__email__ = 'konnos.tatsis@gmail.com'

import numpy as np
import abc


class Quadrature:

    def __init__(self, points, weights):
        self.info = np.hstack((points, weights))


class Gauss(Quadrature):

    @classmethod
    def inLine(cls, rule):

        """
        Gauss quadrature rule in a one-dimensional linear domain.

        Parameters
        ----------
        rule: {1, 2, 3, 4, 5}
            The integration rule, as described in the table below.
            ----------------------
             Rule  Points  Degree 
            ----------------------
               1      1      1     
               2      2      3
               3      3      5
               4      4      7
               5      5      9
            ----------------------

        Returns
        -------
        quadrature: Gauss
            The quadrature points and weights.

        Raises
        ------
        TypeError
            If an invalid rule is specified.
        """

        if rule == 1:
            points = np.array([0])
            weights = np.array([2])

        elif rule == 2:
            p = np.sqrt(3)/3
            points = np.array([[+p], [-p]])
            weights = np.array([[1], [1]])

        elif rule == 3:
            p = np.sqrt(3/5)
            points = np.array([[-p], [0], [+p]])
            weights = np.array([[5/9], [8/9], [5/9]])

        elif rule == 4:
            p1 = np.sqrt(525+70*np.sqrt(30))/35
            p2 = np.sqrt(525-70*np.sqrt(30))/35
            points = np.array([[-p1], [-p2], [+p2], [+p1]])
            w1 = (18-np.sqrt(30))/36
            w2 = (18+np.sqrt(30))/36
            weights = np.array([[w1], [w2], [w2], [w1]])

        elif rule == 5:
            p1 = np.sqrt(5+2*np.sqrt(10/7))/3
            p2 = np.sqrt(5-2*np.sqrt(10/7))/3
            points = np.array([[-p1], [-p2], [0], [+p1], [+p2]])
            w1 = (322-13*np.sqrt(70))/900
            w2 = (322+13*np.sqrt(70))/900
            weights = np.array([[w1], [w2], [128/225], [w1], [w2]])

        else:
            raise TypeError('Invalid integration rule.')

        return cls(points, weights)


    @classmethod
    def inTriangle(cls, rule):

        """
        Parameters
        ----------
        rule: {1, 3, -3, 6, -6, 7, 12}
        The integration rule, as described in the table below.
            ------------------------------------------------------------------
             Rule  Points  Degree  Comments
            ------------------------------------------------------------------
               1      1      1     Centroid rule, useful for Tri3 stiffness.
               3      3      2     Useful for Tri6 stiffness and Tri3 mass.
              -3      3      2     Midpoint rule, less accurate than 3.
               6      6      4     Useful for Tri10 stiffness and Tri6 mass.
              -6      6      3     A linear combination of 3 and -3 rules.
               7      7      5     Radon's formula, useful for Tri10 stiffness.
              12     12      6     Useful for Tri10 mass.
            ------------------------------------------------------------------

        Returns
        -------
        quadrature: Gauss
            The quadrature points and weights.

        Raises
        ------
        TypeError
            If an invalid rule is specified.
        """

        if rule == 1:
            points = np.array([[1/3, 1/3, 1/3]])
            weights = np.array([[1]])

        elif rule == 3:
            p1, p2 = 1/6, 2/3
            points = np.array([[p2, p1, p1], [p1, p2, p1], [p1, p1, p2]])
            weights = np.array([[1/3], [1/3], [1/3]])

        elif rule == -3:
            points = np.array([[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]])
            weights = np.array([[1/3], [1/3], [1/3]])

        elif rule == 6:
            p1 = 0
            p2 = 0

        elif rule == -6:
            pass

        elif rule == 7:
            p0 = 1/3
            p1, p2 = (6+np.sqrt(15))/21, (6-np.sqrt(15))/21
            p3, p4 = (9+2*np.sqrt(15))/21, (9-2*np.sqrt(15))/21
            points = np.array([
                    [p0, p0],           # 1
                    [p1, p4],           # 2
                    [p1, p1],           # 3
                    [p4, p1],           # 4
                    [p3, p2],           # 5
                    [p2, p3],           # 6
                    [p2, p2]])          # 7
            w0, w1, w2 = 9/40, (155+np.sqrt(15))/1200, (155-np.sqrt(15))/1200
            weights = np.array([[w0, w1, w1, w1, w2, w2, w2]]).T
        elif rule == 12:
            pass

        else:
            raise TypeError('Invalid integration rule.')

        return cls(points, weights)



    @classmethod
    def inQuadrilateral(cls, rule):

        """
        Parameters
        ----------
        rule: {1, 3, -3, 6, -6, 7, 12}
        The integration rule, as described in the table below.
            ------------------------------------------------------------------
             Rule  Points  Degree  Comments
            ------------------------------------------------------------------
               1      1      1     Used in reduced and selective integration.
               2      4      3     Used for Quad4 stiffness and mass.
               3      9      5     Used for Quad8 and Quad9 stiffness and mass.
               4     16      7     Used for Quad16 stiffness and mass.
               5     25      9     -
            ------------------------------------------------------------------
        """

        # The order of Gauss points follows the definition of Shape functions:
        # Order 1:  V
        # Order 2:  V
        # Order 3:  V
        # Order 4:  X
        # Order 5:  X

        if rule == 1:
            points = np.array([[0, 0]])
            weights = np.array([[2, 2]])

        elif rule == 2:
            p = np.sqrt(3)/3
            points = np.array([
                    [+p, +p],           # 1
                    [-p, +p],           # 2
                    [-p, -p],           # 3
                    [+p, -p]])          # 4          

            weights = np.ones((4, 2))

        elif rule == 3.:
            p = np.sqrt(3/5)
            points = np.array([
                    [+p, +p],           # 1
                    [-p, -p],           # 2
                    [-p, +p],           # 3
                    [+p, -p],           # 4
                    [ 0, +p],           # 5
                    [-p,  0],           # 6
                    [ 0, -p],           # 7
                    [+p,  0],           # 8
                    [ 0,  0]])          # 9

            w0 = 8/9
            w1 = 5/9
            weights = np.array([
                    [w1, w1],           # 1
                    [w1, w1],           # 2
                    [w1, w1],           # 3
                    [w1, w1],           # 4
                    [w0, w1],           # 5
                    [w1, w0],           # 6
                    [w0, w1],           # 7
                    [w1, w0],           # 8
                    [w0, w0]])          # 9

        elif rule == 4:
            p1 = np.sqrt((3+2*np.sqrt(6/5))/7)
            p2 = np.sqrt((3-2*np.sqrt(6/5))/7)
            points = np.array([
                    [-p1, -p1],         # 1
                    [-p2, -p1],         # 2
                    [+p2, -p1],         # 3
                    [+p1, -p1],         # 4
                    [+p1, -p2],         # 5
                    [+p1, +p2],         # 6
                    [+p1, +p1],         # 7
                    [+p2, +p1],         # 8
                    [-p2, +p1],         # 9
                    [-p1, +p1],         # 10
                    [-p1, +p2],         # 11
                    [-p1, -p2],         # 12
                    [-p2, -p2],         # 13
                    [+p2, -p2],         # 14
                    [+p2, +p2],         # 15
                    [-p2, +p2]])        # 16
            w1 = (18-np.sqrt(30))/36
            w2 = (18+np.sqrt(30))/36
            weights = np.array([
                    [w1, w1],           # 1
                    [w2, w1],           # 2
                    [w2, w1],           # 3
                    [w1, w1],           # 4
                    [w1, w2],           # 5
                    [w1, w2],           # 6
                    [w1, w1],           # 7
                    [w2, w1],           # 8
                    [w2, w1],           # 9
                    [w1, w1],           # 10
                    [w1, w2],           # 11
                    [w1, w2],           # 12
                    [w2, w2],           # 13
                    [w2, w2],           # 14
                    [w2, w2],           # 15
                    [w2, w2]])          # 16

        elif rule==5:
            p1 = np.sqrt(5+2*np.sqrt(10/7))/3
            p2 = np.sqrt(5-2*np.sqrt(10/7))/3
            points = np.array([
                    [-p1, -p1],         # 1
                    [-p2, -p1],         # 2
                    [  0, -p1],         # 3
                    [+p2, -p1],         # 4
                    [+p1, -p1],         # 5
                    [-p1, -p2],         # 6
                    [-p2, -p2],         # 7
                    [  0, -p2],         # 8
                    [+p2, -p2],         # 9
                    [+p1, -p2],         # 10
                    [-p1,   0],         # 11
                    [-p2,   0],         # 12
                    [  0,   0],         # 13
                    [+p2,   0],         # 14
                    [+p1,   0],         # 15
                    [-p1, +p2],         # 16
                    [-p2, +p2],         # 17
                    [  0, +p2],         # 18
                    [+p2, +p2],         # 19
                    [+p1, +p2],         # 20
                    [-p1, +p1],         # 21
                    [-p2, +p1],         # 22
                    [  0, +p1],         # 23 
                    [+p2, +p1],         # 24
                    [+p1, +p1]])        # 25
            w0 = 128/225
            w1 = (322-13*np.sqrt(70))/900
            w2 = (322+13*np.sqrt(70))/900
            weights = np.array([
                    [w1, w1],           # 1
                    [w2, w1],           # 2
                    [w0, w1],           # 3
                    [w2, w1],           # 4
                    [w1, w1],           # 5
                    [w1, w2],           # 6
                    [w2, w2],           # 7 
                    [w0, w2],           # 8
                    [w2, w2],           # 9
                    [w1, w2],           # 10
                    [w1, w0],           # 11
                    [w2, w0],           # 12
                    [w0, w0],           # 13
                    [w2, w0],           # 14
                    [w1, w0],           # 15
                    [w1, w2],           # 16
                    [w2, w2],           # 17
                    [w0, w2],           # 18
                    [w2, w2],           # 19
                    [w1, w2],           # 20
                    [w1 ,w1],           # 21
                    [w2, w1],           # 22
                    [w0, w1],           # 23
                    [w2, w1],           # 24
                    [w1, w1]])          # 25

        else:
            raise TypeError('Invalid integration rule.')

        return cls(points, weights)


    @classmethod
    def inTetrahedron(cls, rule):

        """
        Parameters
        ----------
        rule: {1, 4, 8, -8, 14, -14, 15, -15, 24}
            The integration rule, as described in the table below.
            -----------------------------------------------------------------
             Rule  Points  Degree  Comments
            -----------------------------------------------------------------
               1      1      1     Centroid rule, useful for Tet4 stiffness.
               4      4      2     Useful for Tet4 mass and Tet10 stiffness.
               8      8      3     
              -8      8      3     Has corners and face centers as points.
              14     14      4     Useful for Tet10 mass.
             -14     14      3     Has edge midpoints as sample points.
              15     15      5     Useful for Tet21 stiffness.
             -15     15      4     Less accurate than above.
              24     24      6     Useful for Tet21 stiffness.
            -----------------------------------------------------------------
        """

        if rule == 1:
            p, w = 1/4, 1
            points = np.array([[p, p, p, p]])
            weights = np.array([[w]])

        elif rule == 4:
            p1 = (5-np.sqrt(5))/20
            p2 = (5+3*np.sqrt(5))/20
            points = np.array([
                    [p2, p1, p1, p1],
                    [p1, p2, p1, p1],
                    [p1, p1, p2, p1],
                    [p1, p1, p1, p2]])
            weights = np.array([[1/4], [1/4], [1/4], [1/4]])

        elif rule == 8:
            p1 = (55-3*np.sqrt(17)+np.sqrt(1022-134*np.sqrt(17)))/196
            p2 = (55-3*np.sqrt(17)-np.sqrt(1022-134*np.sqrt(17)))/196
            w1 = 1/8+np.sqrt((1715161837-406006699*np.sqrt(17))/23101)/3120
            w2 = 1/8-np.sqrt((1715161837-406006699*np.sqrt(17))/23101)/3120
            points = np.array([
                    [1-3*p1, p1, p1, p1],   # 1
                    [p1, 1-3*p1, p1, p1],   # 2
                    [p1, p1, 1-3*p1, p1],   # 3
                    [p1, p1, p1, 1-3*p1],   # 4
                    [1-3*p2, p2, p2, p2],   # 5
                    [p2, 1-3*p2, p2, p2],   # 6
                    [p2, p2, 1-3*p2, p2],   # 7
                    [p2, p2, p2, 1-3*p2]])  # 8
            weights = np.array([
                    [w1], [w1], [w1], [w1], [w2], [w2], [w2], [w2]])

        elif rule == -8:
            w1, w2 = 1/40, 9/40
            points = np.array([
                    [1, 0, 0, 0],   # 1
                    [0, 1, 0, 0],   # 2
                    [0, 0, 1, 0],   # 3
                    [0, 0, 0, 1],   # 4
                    [0, 1, 1, 1],   # 5
                    [1, 0, 1, 1],   # 6
                    [1, 1, 0, 1],   # 7
                    [1, 1, 1, 0]])  # 8
            weights = np.array([
                    [w1], [w1], [w1], [w1], [w2], [w2], [w2], [w2]])

        elif rule == 14:
            p1 = 0
            p2 = 0
            p3 = 0
            w1 = 1
            w2 = 1
            w3 = 1
            points = np.array([
                    [1-3*p1, p1, p1, p1],       # 1
                    [p1, 1-3*p1, p1, p1],       # 2
                    [p1, p1, 1-3*p1, p1],       # 3
                    [p1, p1, p1, 1-3*p1],       # 4
                    [1-3*p2, p2, p2, p2],       # 5
                    [p2, 1-3*p2, p2, p2],       # 6
                    [p2, p2, 1-3*p2, p2],       # 7
                    [p2, p2, p2, 1-3*p2],       # 8
                    [0.5-p3, 0.5-p3, p3, p3],   # 9
                    [0.5-p3, p3, 0.5-p3, p3],   # 10
                    [0.5-p3, p3, p3, 0.5-p3],   # 11
                    [p3, 0.5-p3, 0.5-p3, p3],   # 12
                    [p3, 0.5-p3, p3, 0.5-p3],   # 13
                    [p3, p3, 0.5-p3, 0.5-p3]])  # 14
            weights = np.array([
                [w1], [w1], [w1], [w1], 
                [w2], [w2], [w2], [w2], 
                [w3], [w3], [w3], [w3], [w3], [w3]])

        elif rule == -14:
            p1 = (243-51*np.sqrt(11)+2*np.sqrt(16486-9723*np.sqrt(11)/2))/356
            p2 = (243-51*np.sqrt(11)-2*np.sqrt(16486-9723*np.sqrt(11)/2))/356
            w1 = 31/280+np.sqrt((13686301-3809646*np.sqrt(11))/5965)/600
            w2 = 31/280-np.sqrt((13686301-3809646*np.sqrt(11))/5965)/600
            points = np.array([
                    [1-3*p1, p1, p1, p1],       # 1
                    [p1, 1-3*p1, p1, p1],       # 2
                    [p1, p1, 1-3*p1, p1],       # 3
                    [p1, p1, p1, 1-3*p1],       # 4
                    [1-3*p2, p2, p2, p2],       # 5
                    [p2, 1-3*p2, p2, p2],       # 6
                    [p2, p2, 1-3*p2, p2],       # 7
                    [p2, p2, p2, 1-3*p2],       # 8
                    [0.5, 0.5, 0, 0],           # 9
                    [0.5, 0, 0.5, 0],           # 10
                    [0.5, 0, 0, 0.5],           # 11
                    [0, 0.5, 0.5, 0],           # 12
                    [0, 0.5, 0, 0.5],           # 13
                    [0, 0, 0.5, 0.5]])          # 14
            weights = np.array([
                [w1], [w1], [w1], [w1],
                [w2], [w2], [w2], [w2],
                [w3], [w3], [w3], [w3], [w3], [w3]])

        elif rule == 15:
            p1 = (7-np.sqrt(15))/34
            p2 = 7/17-p1
            p3 = (10-2*np.sqrt(15))/40
            w1 = (2665+14*np.sqrt(15))/37800
            w2 = (2665-14*np.sqrt(15))/37800
            points = np.array([
                    [1-3*p1, p1, p1, p1],       # 1
                    [p1, 1-3*p1, p1, p1],       # 2
                    [p1, p1, 1-3*p1, p1],       # 3
                    [p1, p1, p1, 1-3*p1],       # 4
                    [1-3*p2, p2, p2, p2],       # 5
                    [p2, 1-3*p2, p2, p2],       # 6
                    [p2, p2, 1-3*p2, p2],       # 7
                    [p2, p2, p2, 1-3*p2],       # 8
                    [0.5-p3, 0.5-p3, p3, p3],   # 9
                    [0.5-p3, p3, 0.5-p3, p3],   # 10
                    [0.5-p3, p3, p3, 0.5-p3],   # 11
                    [p3, 0.5-p3, 0.5-p3, p3],   # 12
                    [p3, 0.5-p3, p3, 0.5-p3],   # 13
                    [p3, p3, 0.5-p3, 0.5-p3],   # 14
                    [0.25, 0.25, 0.25, 0.25]])  # 15
            weights = np.array([
                    [w1], [w1], [w1], [w1],
                    [w2], [w2], [w2], [w2],
                    [w3], [w3], [w3], [w3], [w3], [w3], 16/135])

        elif rule == -15:
            p1 = (13-np.sqrt(91))/52
            p2, p3 = 1/3, 1/11
            w1 = 81/2240
            w2 = 161051/2304960
            w3 = 338/5145
            points = np.array([
                    [0, p2, p2, p2],            # 1
                    [p2, 0, p2, p2],            # 2
                    [p2, p2, 0, p2],            # 3
                    [p2, p2, p2, 0],            # 4
                    [8/11, p3, p3, p3],         # 5
                    [p3, 8/11, p3, p3],         # 6
                    [p3, p3, 8/11, p3],         # 7
                    [p3, p3, p3, 8/11],         # 8
                    [0.5-p1, 0.5-p1, p1, p1],   # 9
                    [0.5-p1, p1, 0.5-p1, p1],   # 10
                    [0.5-p1, p1, p1, 0.5-p1],   # 11
                    [p1, 0.5-p1, 0.5-p1, p1],   # 12
                    [p1, 0.5-p1, p1, 0.5-p1],   # 13
                    [p1, p1, 0.5-p1, 0.5-p1],   # 14
                    [0.25, 0.25, 0.25, 0.25]])  # 15
            weights = np.array([
                    [w1], [w1], [w1], [w1],
                    [w2], [w2], [w2], [w2],
                    [w3], [w3], [w3], [w3], [w3], [w3], 6544/36015])

        elif rule == 24:
            p1 = 0
            p2 = 0
            p3 = 0
            p4=(3-np.sqrt(5))/12
            p4j=(5+np.sqrt(5))/12
            p4k=(1+np.sqrt(5))/12
            w1 = 1
            w2 = 1
            w3 = 1
            w4 = 27/560
            points = np.array([
                    [1-3*p1, p1, p1, p1],   # 1
                    [p1, 1-3*p1, p1, p1],   # 2
                    [p1, p1, 1-3*p1, p1],   # 3
                    [p1, p1, p1, 1-3*p1],   # 4
                    [1-3*p2, p2, p2, p2],   # 5
                    [p2, 1-3*p2, p2, p2],   # 6
                    [p2, p2, 1-3*p2, p2],   # 7
                    [p2, p2, p2, 1-3*p2],   # 8
                    [1-3*p3, p3, p3, p3],   # 9
                    [p3, 1-3*p3, p3, p3],   # 10
                    [p3, p3, 1-3*p3, p3],   # 11
                    [p3, p3, p3, 1-3*p3],   # 12
                    [p4j, p4k, p4, p4],     # 13
                    [p4j, p4, p4k, p4],     # 14
                    [p4j, p4, p4, p4k],     # 15
                    [p4, p4j, p4k, p4],     # 16
                    [p4, p4j, p4, p4k],     # 17
                    [p4, p4, p4j, p4k],     # 18
                    [p4k, p4j, p4, p4],     # 19
                    [p4k, p4, p4j, p4],     # 20
                    [p4k, p4, p4, p4j],     # 21
                    [p4, p4k, p4j, p4],     # 22
                    [p4, p4k, p4, p4j],     # 23
                    [p4, p4, p4k, p4j]])    # 24
            weights = np.array([
                    [w1], [w1], [w1], [w1], 
                    [w2], [w2], [w2], [w2],
                    [w3], [w3], [w3], [w3],
                    [w4], [w4], [w4], [w4],
                    [w4], [w4], [w4], [w4],
                    [w4], [w4], [w4], [w4]])

        else:
            raise TypeError('Invalid integration rule.')

        return cls(points, weights)


    @classmethod
    def inWedge(cls, rule):
        pass


    @classmethod
    def inPyramid(cls, rule):
        pass


    @classmethod
    def inHexahedron(cls, rule):

        """
        Parameters
        ----------
        rule: {1, 2, 3, 4, 5}
            The integration rule, as described in the table below.
            -----------------------------------------------------------------
             Rule  Points  Degree  Comments
            -----------------------------------------------------------------
               1      1      1     Used in reduced and selective integration.
               2      8      3     Useful for Hex8 stiffness and mass.
               3     27      5     Useful for Hex20 & 27 stiffness and mass.
               4     64      7     Rarely used.
               5    125      9     rarely used.
            -----------------------------------------------------------------
        """

        if rule == 1:
            points = np.array([[0, 0, 0]])
            weights = np.array([[2, 2, 2]])

        elif rule == 2:
            p = np.sqrt(3)/3
            points = np.array([
                    [-p, -p, -p],       # 1
                    [+p, -p, -p],       # 2
                    [+p, +p, -p],       # 3
                    [-p, +p, -p],       # 4
                    [-p, -p, +p],       # 5
                    [+p, -p, +p],       # 6
                    [+p, +p, +p],       # 7
                    [-p, +p, +p]])      # 8
            weights = np.ones((8, 3))

        elif rule == 3:
            p = np.sqrt(3/5)
            points = np.array([
                    [ 0,  0, -p],       # 1
                    [-p, -p, -p],       # 2
                    [ 0, -p, -p],       # 3
                    [+p, -p, -p],       # 4
                    [+p,  0, -p],       # 5
                    [+p, +p, -p],       # 6
                    [ 0, +p, -p],       # 7
                    [-p, +p, -p],       # 8
                    [-p,  0, -p],       # 9
                    [ 0,  0,  0],       # 10
                    [-p, -p,  0],       # 11
                    [ 0, -p,  0],       # 12
                    [+p, -p,  0],       # 13
                    [+p,  0,  0],       # 14
                    [+p, +p,  0],       # 15
                    [ 0, +p,  0],       # 16
                    [-p, +p,  0],       # 17
                    [-p,  0,  0],       # 18
                    [ 0,  0, +p],       # 19
                    [-p, -p, +p],       # 20
                    [ 0, -p, +p],       # 21
                    [+p, -p, +p],       # 22
                    [+p,  0, +p],       # 23
                    [+p, +p, +p],       # 24
                    [ 0, +p, +p],       # 25
                    [-p, +p, +p],       # 26
                    [-p,  0, +p]])      # 27
            w0 = 8/9
            w1 = 5/9
            weights = np.array([
                    [w0, w0, w1],       # 1
                    [w1, w1, w1],       # 2
                    [w0, w1, w1],       # 3
                    [w1, w1, w1],       # 4
                    [w1, w0, w1],       # 5
                    [w1, w1, w1],       # 6
                    [w0, w1, w1],       # 7
                    [w1, w1, w1],       # 8
                    [w1, w0, w1],       # 9
                    [w0, w0, w0],       # 10
                    [w1, w1, w0],       # 11
                    [w0, w1, w0],       # 12
                    [w1, w1, w0],       # 13
                    [w1, w0, w0],       # 14
                    [w1, w1, w0],       # 15
                    [w0, w1, w0],       # 16
                    [w1, w1, w0],       # 17
                    [w1, w0, w0],       # 18
                    [w0, w0, w1],       # 19
                    [w1, w1, w1],       # 20
                    [w0, w1, w1],       # 21
                    [w1, w1, w1],       # 22
                    [w1, w0, w1],       # 23
                    [w1, w1, w1],       # 24
                    [w0, w1, w1],       # 25
                    [w1, w1, w1],       # 26
                    [w1, w0, w1]])      # 27

        elif rule == 4:
            p1 = np.sqrt((3+2*np.sqrt(6/5))/7)
            p2 = np.sqrt((3-2*np.sqrt(6/5))/7)
            points = np.array([
                    [-p1, -p1, -p1],    # 1
                    [-p2, -p1, -p1],    # 2
                    [+p2, -p1, -p1],    # 3
                    [+p1, -p1, -p1],    # 4
                    [+p1, -p2, -p1],    # 5
                    [+p1, +p2, -p1],    # 6
                    [+p1, +p1, -p1],    # 7
                    [+p2, +p1, -p1],    # 8
                    [-p2, +p1, -p1],    # 9
                    [-p1, +p1, -p1],    # 10
                    [-p1, +p2, -p1],    # 11
                    [-p1, -p2, -p1],    # 12
                    [-p2, -p2, -p1],    # 13
                    [+p2, -p2, -p1],    # 14
                    [+p2, +p2, -p1],    # 15
                    [-p2, +p2, -p1],    # 16
                    [-p1, -p1, -p2],    # 17
                    [-p2, -p1, -p2],    # 18
                    [+p2, -p1, -p2],    # 19
                    [+p1, -p1, -p2],    # 20
                    [+p1, -p2, -p2],    # 21
                    [+p1, +p2, -p2],    # 22
                    [+p1, +p1, -p2],    # 23
                    [+p2, +p1, -p2],    # 24
                    [-p2, +p1, -p2],    # 25
                    [-p1, +p1, -p2],    # 26
                    [-p1, +p2, -p2],    # 27
                    [-p1, -p2, -p2],    # 28
                    [-p2, -p2, -p2],    # 29
                    [+p2, -p2, -p2],    # 30
                    [+p2, +p2, -p2],    # 31
                    [-p2, +p2, -p2],    # 32
                    [-p1, -p1, +p2],    # 33
                    [-p2, -p1, +p2],    # 34
                    [+p2, -p1, +p2],    # 35
                    [+p1, -p1, +p2],    # 36
                    [+p1, -p2, +p2],    # 37
                    [+p1, +p2, +p2],    # 38
                    [+p1, +p1, +p2],    # 39
                    [+p2, +p1, +p2],    # 40
                    [-p2, +p1, +p2],    # 41
                    [-p1, +p1, +p2],    # 42
                    [-p1, +p2, +p2],    # 43
                    [-p1, -p2, +p2],    # 44
                    [-p2, -p2, +p2],    # 45
                    [+p2, -p2, +p2],    # 46
                    [+p2, +p2, +p2],    # 47
                    [-p2, +p2, +p2],    # 48
                    [-p1, -p1, +p1],    # 49
                    [-p2, -p1, +p1],    # 50
                    [+p2, -p1, +p1],    # 51
                    [+p1, -p1, +p1],    # 52
                    [+p1, -p2, +p1],    # 53
                    [+p1, +p2, +p1],    # 54
                    [+p1, +p1, +p1],    # 55
                    [+p2, +p1, +p1],    # 56
                    [-p2, +p1, +p1],    # 57
                    [-p1, +p1, +p1],    # 58
                    [-p1, +p2, +p1],    # 59
                    [-p1, -p2, +p1],    # 60
                    [-p2, -p2, +p1],    # 61
                    [+p2, -p2, +p1],    # 62
                    [+p2, +p2, +p1],    # 63
                    [-p2, +p2, +p1]])   # 64
            w1 = (18-np.sqrt(30))/36
            w2 = (18+np.sqrt(30))/36
            weights = np.array([
                    [w1, w1, w1],       # 1
                    [w2, w1, w1],       # 2
                    [w2, w1, w1],       # 3
                    [w1, w1, w1],       # 4
                    [w1, w2, w1],       # 5
                    [w1, w2, w1],       # 6
                    [w1, w1, w1],       # 7
                    [w2, w1, w1],       # 8
                    [w2, w1, w1],       # 9
                    [w1, w1, w1],       # 10
                    [w1, w2, w1],       # 11
                    [w1, w2, w1],       # 12
                    [w2, w2, w1],       # 13
                    [w2, w2, w1],       # 14
                    [w2, w2, w1],       # 15
                    [w2, w2, w1],       # 16
                    [w1, w1, w2],       # 17
                    [w2, w1, w2],       # 18
                    [w2, w1, w2],       # 19
                    [w1, w1, w2],       # 20
                    [w1, w2, w2],       # 21
                    [w1, w2, w2],       # 22
                    [w1, w1, w2],       # 23
                    [w2, w1, w2],       # 24
                    [w2, w1, w2],       # 25
                    [w1, w1, w2],       # 26
                    [w1, w2, w2],       # 27
                    [w1, w2, w2],       # 28
                    [w2, w2, w2],       # 29
                    [w2, w2, w2],       # 30
                    [w2, w2, w2],       # 31
                    [w2, w2, w2],       # 32
                    [w1, w1, w2],       # 33
                    [w2, w1, w2],       # 34
                    [w2, w1, w2],       # 35
                    [w1, w1, w2],       # 36
                    [w1, w2, w2],       # 37
                    [w1, w2, w2],       # 38
                    [w1, w1, w2],       # 39
                    [w2, w1, w2],       # 40
                    [w2, w1, w2],       # 41
                    [w1, w1, w2],       # 42
                    [w1, w2, w2],       # 43
                    [w1, w2, w2],       # 44
                    [w2, w2, w2],       # 45
                    [w2, w2, w2],       # 46
                    [w2, w2, w2],       # 47
                    [w2, w2, w2],       # 48
                    [w1, w1, w1],       # 49
                    [w2, w1, w1],       # 50
                    [w2, w1, w1],       # 51
                    [w1, w1, w1],       # 52
                    [w1, w2, w1],       # 53
                    [w1, w2, w1],       # 54
                    [w1, w1, w1],       # 55
                    [w2, w1, w1],       # 56
                    [w2, w1, w1],       # 57
                    [w1, w1, w1],       # 58
                    [w1, w2, w1],       # 59
                    [w1, w2, w1],       # 60
                    [w2, w2, w1],       # 61
                    [w2, w2, w1],       # 62
                    [w2, w2, w1],       # 63
                    [w2, w2, w1]])      # 64

        elif rule == 5:
            p1 = np.sqrt(5+2*np.sqrt(10/7))/3
            p2 = np.sqrt(5-2*np.sqrt(10/7))/3
            points = np.array([
                    [-p1, -p1, -p1],    # 1
                    [-p2, -p1, -p1],    # 2
                    [  0, -p1, -p1],    # 3
                    [+p2, -p1, -p1],    # 4
                    [+p1, -p1, -p1],    # 5
                    [-p1, -p2, -p1],    # 6
                    [-p2, -p2, -p1],    # 7
                    [  0, -p2, -p1],    # 8
                    [+p2, -p2, -p1],    # 9
                    [+p1, -p2, -p1],    # 10
                    [-p1,   0, -p1],    # 11
                    [-p2,   0, -p1],    # 12
                    [  0,   0, -p1],    # 13
                    [+p2,   0, -p1],    # 14
                    [+p1,   0, -p1],    # 15
                    [-p1, +p2, -p1],    # 16
                    [-p2, +p2, -p1],    # 17
                    [  0, +p2, -p1],    # 18
                    [+p2, +p2, -p1],    # 19
                    [+p1, +p2, -p1],    # 20
                    [-p1, +p1, -p1],    # 21
                    [-p2, +p1, -p1],    # 22
                    [  0, +p1, -p1],    # 23
                    [+p2, +p1, -p1],    # 24
                    [+p1, +p1, -p1],    # 25
                    [-p1, -p1, -p2],    # 26
                    [-p2, -p1, -p2],    # 27
                    [  0, -p1, -p2],    # 28
                    [+p2, -p1, -p2],    # 29
                    [+p1, -p1, -p2],    # 30
                    [-p1, -p2, -p2],    # 31
                    [-p2, -p2, -p2],    # 32 
                    [  0, -p2, -p2],    # 33
                    [+p2, -p2, -p2],    # 34
                    [+p1, -p2, -p2],    # 35
                    [-p1,   0, -p2],    # 36
                    [-p2,   0, -p2],    # 37
                    [  0,   0, -p2],    # 38
                    [+p2,   0, -p2],    # 39
                    [+p1,   0, -p2],    # 40
                    [-p1,  p2, -p2],    # 41
                    [-p2,  p2, -p2],    # 42
                    [  0,  p2, -p2],    # 43
                    [+p2,  p2, -p2],    # 44
                    [+p1,  p2, -p2],    # 45
                    [-p1,  p1, -p2],    # 46
                    [-p2,  p1, -p2],    # 47
                    [  0,  p1, -p2],    # 48
                    [+p2,  p1, -p2],    # 49
                    [+p1,  p1, -p2],    # 50
                    [-p1, -p1,   0],    # 51
                    [-p2, -p1,   0],    # 52
                    [  0, -p1,   0],    # 53
                    [+p2, -p1,   0],    # 54
                    [+p1, -p1,   0],    # 55
                    [-p1, -p2,   0],    # 56
                    [-p2, -p2,   0],    # 57
                    [  0, -p2,   0],    # 58
                    [+p2, -p2,   0],    # 59
                    [+p1, -p2,   0],    # 60
                    [-p1,   0,   0],    # 61
                    [-p2,   0,   0],    # 62
                    [  0,   0,   0],    # 63
                    [+p2,   0,   0],    # 64
                    [+p1,   0,   0],    # 65
                    [-p1, +p2,   0],    # 66
                    [-p2, +p2,   0],    # 67
                    [  0, +p2,   0],    # 68
                    [+p2, +p2,   0],    # 69
                    [+p1, +p2,   0],    # 70
                    [-p1, +p1,   0],    # 71
                    [-p2, +p1,   0],    # 72
                    [  0, +p1,   0],    # 73
                    [+p2, +p1,   0],    # 74
                    [+p1, +p1,   0],    # 75                          
                    [-p1, -p1, +p2],    # 76
                    [-p2, -p1, +p2],    # 77
                    [  0, -p1, +p2],    # 78
                    [+p2, -p1, +p2],    # 79
                    [+p1, -p1, +p2],    # 80
                    [-p1, -p2, +p2],    # 81
                    [-p2, -p2, +p2],    # 82
                    [  0, -p2, +p2],    # 83
                    [+p2, -p2, +p2],    # 84
                    [+p1, -p2, +p2],    # 85
                    [-p1,   0, +p2],    # 86
                    [-p2,   0, +p2],    # 87
                    [  0,   0, +p2],    # 88
                    [+p2,   0, +p2],    # 89
                    [+p1,   0, +p2],    # 90
                    [-p1, +p2, +p2],    # 91
                    [-p2, +p2, +p2],    # 92
                    [  0, +p2, +p2],    # 93
                    [+p2, +p2, +p2],    # 94
                    [+p1, +p2, +p2],    # 95
                    [-p1, +p1, +p2],    # 96
                    [-p2, +p1, +p2],    # 97
                    [  0, +p1, +p2],    # 98
                    [+p2, +p1, +p2],    # 99
                    [+p1, +p1, +p2],    # 100
                    [-p1, -p1, +p1],    # 101
                    [-p2, -p1, +p1],    # 102
                    [  0, -p1, +p1],    # 103
                    [+p2, -p1, +p1],    # 104
                    [+p1, -p1, +p1],    # 105
                    [-p1, -p2, +p1],    # 106
                    [-p2, -p2, +p1],    # 107
                    [  0, -p2, +p1],    # 108
                    [+p2, -p2, +p1],    # 109
                    [+p1, -p2, +p1],    # 110
                    [-p1,   0, +p1],    # 111
                    [-p2,   0, +p1],    # 112
                    [  0,   0, +p1],    # 113
                    [+p2,   0, +p1],    # 114
                    [+p1,   0, +p1],    # 115
                    [-p1, +p2, +p1],    # 116
                    [-p2, +p2, +p1],    # 117
                    [  0, +p2, +p1],    # 118
                    [+p2, +p2, +p1],    # 119
                    [+p1, +p2, +p1],    # 120
                    [-p1, +p1, +p1],    # 121
                    [-p2, +p1, +p1],    # 122
                    [  0, +p1, +p1],    # 123
                    [+p2, +p1, +p1],    # 124
                    [+p1, +p1, +p1]])   # 125
            w0 = 128/225
            w1 = (322-13*np.sqrt(70))/900
            w2 = (322+13*np.sqrt(70))/900
            weights = np.array([
                    [w1, w1, w1],       # 1
                    [w2, w1, w1],       # 2
                    [w0, w1, w1],       # 3
                    [w2, w1, w1],       # 4
                    [w1, w1, w1],       # 5
                    [w1, w2, w1],       # 6
                    [w2, w2, w1],       # 7
                    [w0, w2, w1],       # 8
                    [w2, w2, w1],       # 9
                    [w1, w2, w1],       # 10
                    [w1, w0, w1],       # 11
                    [w2, w0, w1],       # 12
                    [w0, w0, w1],       # 13
                    [w2, w0, w1],       # 14
                    [w1, w0, w1],       # 15
                    [w1, w2, w1],       # 16
                    [w2, w2, w1],       # 17
                    [w0, w2, w1],       # 18
                    [w2, w2, w1],       # 19
                    [w1, w2, w1],       # 20
                    [w1, w1, w1],       # 21
                    [w2, w1, w1],       # 22
                    [w0, w1, w1],       # 23
                    [w2, w1, w1],       # 24
                    [w1, w1, w1],       # 25
                    [w1, w1, w2],       # 26
                    [w2, w1, w2],       # 27
                    [w0, w1, w2],       # 28
                    [w2, w1, w2],       # 29
                    [w1, w1, w2],       # 30
                    [w1, w2, w2],       # 31
                    [w2, w2, w2],       # 32
                    [w0, w2, w2],       # 33
                    [w2, w2, w2],       # 34
                    [w1, w2, w2],       # 35
                    [w1, w0, w2],       # 36
                    [w2, w0, w2],       # 37
                    [w0, w0, w2],       # 38
                    [w2, w0, w2],       # 39
                    [w1, w0, w2],       # 40
                    [w1, w2, w2],       # 41
                    [w2, w2, w2],       # 42
                    [w0, w2, w2],       # 43
                    [w2, w2, w2],       # 44
                    [w1, w2, w2],       # 45
                    [w1, w1, w2],       # 46
                    [w2, w1, w2],       # 47
                    [w0, w1, w2],       # 48
                    [w2, w1, w2],       # 49
                    [w1, w1, w2],       # 50
                    [w1, w1, w0],       # 51
                    [w2, w1, w0],       # 52
                    [w0, w1, w0],       # 53
                    [w2, w1, w0],       # 54
                    [w1, w1, w0],       # 55
                    [w1, w2, w0],       # 56
                    [w2, w2, w0],       # 57
                    [w0, w2, w0],       # 58
                    [w2, w2, w0],       # 59
                    [w1, w2, w0],       # 60
                    [w1, w0, w0],       # 61
                    [w2, w0, w0],       # 62
                    [w0, w0, w0],       # 63
                    [w2, w0, w0],       # 64
                    [w1, w0, w0],       # 65
                    [w1, w2, w0],       # 66
                    [w2, w2, w0],       # 67
                    [w0, w2, w0],       # 68
                    [w2, w2, w0],       # 69
                    [w1, w2, w0],       # 70
                    [w1, w1, w0],       # 71
                    [w2, w1, w0],       # 72
                    [w0, w1, w0],       # 73
                    [w2, w1, w0],       # 74
                    [w1, w1, w0],       # 75
                    [w1, w1, w2],       # 76
                    [w2, w1, w2],       # 77
                    [w0, w1, w2],       # 78
                    [w2, w1, w2],       # 79
                    [w1, w1, w2],       # 80
                    [w1, w2, w2],       # 81
                    [w2, w2, w2],       # 82
                    [w0, w2, w2],       # 83
                    [w2, w2, w2],       # 84
                    [w1, w2, w2],       # 85
                    [w1, w0, w2],       # 86
                    [w2, w0, w2],       # 87
                    [w0, w0, w2],       # 88
                    [w2, w0, w2],       # 89
                    [w1, w0, w2],       # 90
                    [w1, w2, w2],       # 91
                    [w2, w2, w2],       # 92
                    [w0, w2, w2],       # 93
                    [w2, w2, w2],       # 94
                    [w1, w2, w2],       # 95
                    [w1, w1, w2],       # 96
                    [w2, w1, w2],       # 97
                    [w0, w1, w2],       # 98
                    [w2, w1, w2],       # 99
                    [w1, w1, w2],       # 100
                    [w1, w1, w1],       # 101
                    [w2, w1, w1],       # 102
                    [w0, w1, w1],       # 103
                    [w2, w1, w1],       # 104
                    [w1, w1, w1],       # 105
                    [w1, w2, w1],       # 106
                    [w2, w2, w1],       # 107
                    [w0, w2, w1],       # 108
                    [w2, w2, w1],       # 109
                    [w1, w2, w1],       # 110
                    [w1, w0, w1],       # 111
                    [w2, w0, w1],       # 112
                    [w0, w0, w1],       # 113
                    [w2, w0, w1],       # 114
                    [w1, w0, w1],       # 115
                    [w1, w2, w1],       # 116
                    [w2, w2, w1],       # 117
                    [w0, w2, w1],       # 118
                    [w2, w2, w1],       # 119
                    [w1, w2, w1],       # 120
                    [w1, w1, w1],       # 121
                    [w2, w1, w1],       # 122
                    [w0, w1, w1],       # 123
                    [w2, w1, w1],       # 124
                    [w1, w1, w1]])      # 125
        else:
            raise TypeError('Invalid integration rule.')

        return cls(points, weights)



class NewtonCotes(Quadrature):

    def __init__(self):
        pass
    


# class Gauss2:

#     def __init__(self, domain='linear', order=1):
#         quadrature.Gauss.__dict__[domain](self, order)


#     def linear(self, order):
#         if order == 1:
#             points = np.array([0])
#             weights = np.array([2])

#         elif order == 2:
#             p = np.sqrt(3)/3
#             points = np.array([[+p, -p]])
#             weights = np.array([[1], [1]])

#         elif order == 3:
#             p = np.sqrt(3/5)
#             points = np.array([[-p], [0], [+p]])
#             weights = np.array([[5/9], [8/9], [5/9]])

#         elif order == 4:
#             p1 = np.sqrt(525+70*np.sqrt(30))/35
#             p2 = np.sqrt(525-70*np.sqrt(30))/35
#             points = np.array([[-p1], [-p2], [+p2], [+p1]])
#             w1 = (18-np.sqrt(30))/36
#             w2 = (18+np.sqrt(30))/36
#             weights = np.array([[w1], [w2], [w2], [w1]])

#         elif order == 5:
#             p1 = np.sqrt(5+2*np.sqrt(10/7))/3
#             p2 = np.sqrt(5-2*np.sqrt(10/7))/3
#             points = np.array([[-p1], [-p2], [0], [+p1], [+p2]])
#             w1 = (322-13*np.sqrt(70))/900
#             w2 = (322+13*np.sqrt(70))/900
#             weights = np.array([[w1], [w2], [128/225], [w1], [w2]])

#         self.info = np.hstack((points, weights))


#     def triangular(self, order):
#         if order == 1:
#             points = np.array([1/3, 1/3])
#             weights = np.array([1, 1])
#         elif order == 2:
#             p1 = 1/6
#             p2 = 2/3
#             points = np.array([
#                 [p1, p1],
#                 [p2, p1],
#                 [p1, p2]])
#             w = 1/3
#             weights = np.array([
#                 [w, w],
#                 [w, w],
#                 [w, w]])
#         elif order == 3:
#             pass
#         elif order == 4:
#             pass
#         elif order == 5:
#             pass


#     def quadrilateral(self, order):
#         if order == 1:
#             points = np.array([
#                 [0, 0]])
#             weights = np.array([
#                 [2, 2]])

#         elif order == 2:
#             p = np.sqrt(3)/3
#             points = np.array([
#                 [-p, -p],           # 1
#                 [+p, -p],           # 2
#                 [+p, +p],           # 3
#                 [-p, +p]])          # 4
#             weights = np.ones((4, 2))

#         elif order == 3.:
#             p = np.sqrt(3/5)
#             points = np.array([
#                 [ 0,  0],           # 1
#                 [-p, -p],           # 2
#                 [ 0, -p],           # 3
#                 [+p, -p],           # 4
#                 [+p,  0],           # 5
#                 [+p, +p],           # 6
#                 [ 0, +p],           # 7
#                 [-p, +p],           # 8
#                 [-p,  0]])          # 9
#             w0 = 8/9
#             w1 = 5/9
#             weights = np.array([
#                 [w0, w0],           # 1
#                 [w1, w1],           # 2
#                 [w0, w1],           # 3
#                 [w1, w1],           # 4
#                 [w1, w0],           # 5
#                 [w1, w1],           # 6
#                 [w0, w1],           # 7
#                 [w1, w1],           # 8
#                 [w1, w0]])          # 9

#         elif order == 4:
#             p1 = np.sqrt((3+2*np.sqrt(6/5))/7)
#             p2 = np.sqrt((3-2*np.sqrt(6/5))/7)
#             points = np.array([
#                 [-p1, -p1],         # 1
#                 [-p2, -p1],         # 2
#                 [+p2, -p1],         # 3
#                 [+p1, -p1],         # 4
#                 [+p1, -p2],         # 5
#                 [+p1, +p2],         # 6
#                 [+p1, +p1],         # 7
#                 [+p2, +p1],         # 8
#                 [-p2, +p1],         # 9
#                 [-p1, +p1],         # 10
#                 [-p1, +p2],         # 11
#                 [-p1, -p2],         # 12
#                 [-p2, -p2],         # 13
#                 [+p2, -p2],         # 14
#                 [+p2, +p2],         # 15
#                 [-p2, +p2]])        # 16
#             w1 = (18-np.sqrt(30))/36
#             w2 = (18+np.sqrt(30))/36
#             weights = np.array([
#                 [w1, w1],           # 1
#                 [w2, w1],           # 2
#                 [w2, w1],           # 3
#                 [w1, w1],           # 4
#                 [w1, w2],           # 5
#                 [w1, w2],           # 6
#                 [w1, w1],           # 7
#                 [w2, w1],           # 8
#                 [w2, w1],           # 9
#                 [w1, w1],           # 10
#                 [w1, w2],           # 11
#                 [w1, w2],           # 12
#                 [w2, w2],           # 13
#                 [w2, w2],           # 14
#                 [w2, w2],           # 15
#                 [w2, w2]])          # 16

#         elif order==5:
#             p1 = np.sqrt(5+2*np.sqrt(10/7))/3
#             p2 = np.sqrt(5-2*np.sqrt(10/7))/3
#             points = np.array([
#                 [-p1, -p1],         # 1
#                 [-p2, -p1],         # 2
#                 [  0, -p1],         # 3
#                 [+p2, -p1],         # 4
#                 [+p1, -p1],         # 5
#                 [-p1, -p2],         # 6
#                 [-p2, -p2],         # 7
#                 [  0, -p2],         # 8
#                 [+p2, -p2],         # 9
#                 [+p1, -p2],         # 10
#                 [-p1,   0],         # 11
#                 [-p2,   0],         # 12
#                 [  0,   0],         # 13
#                 [+p2,   0],         # 14
#                 [+p1,   0],         # 15
#                 [-p1, +p2],         # 16
#                 [-p2, +p2],         # 17
#                 [  0, +p2],         # 18
#                 [+p2, +p2],         # 19
#                 [+p1, +p2],         # 20
#                 [-p1, +p1],         # 21
#                 [-p2, +p1],         # 22
#                 [  0, +p1],         # 23 
#                 [+p2, +p1],         # 24
#                 [+p1, +p1]])        # 25
#             w0 = 128/225
#             w1 = (322-13*np.sqrt(70))/900
#             w2 = (322+13*np.sqrt(70))/900
#             weights = np.array([
#                 [w1, w1],           # 1
#                 [w2, w1],           # 2
#                 [w0, w1],           # 3
#                 [w2, w1],           # 4
#                 [w1, w1],           # 5
#                 [w1, w2],           # 6
#                 [w2, w2],           # 7 
#                 [w0, w2],           # 8
#                 [w2, w2],           # 9
#                 [w1, w2],           # 10
#                 [w1, w0],           # 11
#                 [w2, w0],           # 12
#                 [w0, w0],           # 13
#                 [w2, w0],           # 14
#                 [w1, w0],           # 15
#                 [w1, w2],           # 16
#                 [w2, w2],           # 17
#                 [w0, w2],           # 18
#                 [w2, w2],           # 19
#                 [w1, w2],           # 20
#                 [w1 ,w1],           # 21
#                 [w2, w1],           # 22
#                 [w0, w1],           # 23
#                 [w2, w1],           # 24
#                 [w1, w1]])          # 25

#         self.info = np.hstack((points, weights))
    
#     def tetrahedral(self, order):
#         if order == 1:
#             pass
#         elif order == 2:
#             pass
#         elif order == 3:
#             pass
#         elif order == 4:
#             pass
#         elif order == 5:
#             pass
                              
#     def hexahedral(self, order):
#         if order == 1:
#             points = np.array([[0, 0, 0]])
#             weights = np.array([[2, 2, 2]])

#         elif order == 2:
#             p = np.sqrt(3)/3
#             points = np.array([
#                 [-p, -p, -p],       # 1
#                 [+p, -p, -p],       # 2
#                 [+p, +p, -p],       # 3
#                 [-p, +p, -p],       # 4
#                 [-p, -p, +p],       # 5
#                 [+p, -p, +p],       # 6
#                 [+p, +p, +p],       # 7
#                 [-p, +p, +p]])      # 8
#             weights = np.ones((8, 3))

#         elif order == 3:
#             p = np.sqrt(3/5)
#             points = np.array([
#                 [ 0,  0, -p],       # 1
#                 [-p, -p, -p],       # 2
#                 [ 0, -p, -p],       # 3
#                 [+p, -p, -p],       # 4
#                 [+p,  0, -p],       # 5
#                 [+p, +p, -p],       # 6
#                 [ 0, +p, -p],       # 7
#                 [-p, +p, -p],       # 8
#                 [-p,  0, -p],       # 9
#                 [ 0,  0,  0],       # 10
#                 [-p, -p,  0],       # 11
#                 [ 0, -p,  0],       # 12
#                 [+p, -p,  0],       # 13
#                 [+p,  0,  0],       # 14
#                 [+p, +p,  0],       # 15
#                 [ 0, +p,  0],       # 16
#                 [-p, +p,  0],       # 17
#                 [-p,  0,  0],       # 18
#                 [ 0,  0, +p],       # 19
#                 [-p, -p, +p],       # 20
#                 [ 0, -p, +p],       # 21
#                 [+p, -p, +p],       # 22
#                 [+p,  0, +p],       # 23
#                 [+p, +p, +p],       # 24
#                 [ 0, +p, +p],       # 25
#                 [-p, +p, +p],       # 26
#                 [-p,  0, +p]])      # 27
#             w0 = 8/9
#             w1 = 5/9
#             weights = np.array([
#                 [w0, w0, w1],       # 1
#                 [w1, w1, w1],       # 2
#                 [w0, w1, w1],       # 3
#                 [w1, w1, w1],       # 4
#                 [w1, w0, w1],       # 5
#                 [w1, w1, w1],       # 6
#                 [w0, w1, w1],       # 7
#                 [w1, w1, w1],       # 8
#                 [w1, w0, w1],       # 9
#                 [w0, w0, w0],       # 10
#                 [w1, w1, w0],       # 11
#                 [w0, w1, w0],       # 12
#                 [w1, w1, w0],       # 13
#                 [w1, w0, w0],       # 14
#                 [w1, w1, w0],       # 15
#                 [w0, w1, w0],       # 16
#                 [w1, w1, w0],       # 17
#                 [w1, w0, w0],       # 18
#                 [w0, w0, w1],       # 19
#                 [w1, w1, w1],       # 20
#                 [w0, w1, w1],       # 21
#                 [w1, w1, w1],       # 22
#                 [w1, w0, w1],       # 23
#                 [w1, w1, w1],       # 24
#                 [w0, w1, w1],       # 25
#                 [w1, w1, w1],       # 26
#                 [w1, w0, w1]])      # 27

#         elif order == 4:
#             p1 = np.sqrt((3+2*np.sqrt(6/5))/7)
#             p2 = np.sqrt((3-2*np.sqrt(6/5))/7)
#             points = np.array([
#                 [-p1, -p1, -p1],    # 1
#                 [-p2, -p1, -p1],    # 2
#                 [+p2, -p1, -p1],    # 3
#                 [+p1, -p1, -p1],    # 4
#                 [+p1, -p2, -p1],    # 5
#                 [+p1, +p2, -p1],    # 6
#                 [+p1, +p1, -p1],    # 7
#                 [+p2, +p1, -p1],    # 8
#                 [-p2, +p1, -p1],    # 9
#                 [-p1, +p1, -p1],    # 10
#                 [-p1, +p2, -p1],    # 11
#                 [-p1, -p2, -p1],    # 12
#                 [-p2, -p2, -p1],    # 13
#                 [+p2, -p2, -p1],    # 14
#                 [+p2, +p2, -p1],    # 15
#                 [-p2, +p2, -p1],    # 16
#                 [-p1, -p1, -p2],    # 17
#                 [-p2, -p1, -p2],    # 18
#                 [+p2, -p1, -p2],    # 19
#                 [+p1, -p1, -p2],    # 20
#                 [+p1, -p2, -p2],    # 21
#                 [+p1, +p2, -p2],    # 22
#                 [+p1, +p1, -p2],    # 23
#                 [+p2, +p1, -p2],    # 24
#                 [-p2, +p1, -p2],    # 25
#                 [-p1, +p1, -p2],    # 26
#                 [-p1, +p2, -p2],    # 27
#                 [-p1, -p2, -p2],    # 28
#                 [-p2, -p2, -p2],    # 29
#                 [+p2, -p2, -p2],    # 30
#                 [+p2, +p2, -p2],    # 31
#                 [-p2, +p2, -p2],    # 32
#                 [-p1, -p1, +p2],    # 33
#                 [-p2, -p1, +p2],    # 34
#                 [+p2, -p1, +p2],    # 35
#                 [+p1, -p1, +p2],    # 36
#                 [+p1, -p2, +p2],    # 37
#                 [+p1, +p2, +p2],    # 38
#                 [+p1, +p1, +p2],    # 39
#                 [+p2, +p1, +p2],    # 40
#                 [-p2, +p1, +p2],    # 41
#                 [-p1, +p1, +p2],    # 42
#                 [-p1, +p2, +p2],    # 43
#                 [-p1, -p2, +p2],    # 44
#                 [-p2, -p2, +p2],    # 45
#                 [+p2, -p2, +p2],    # 46
#                 [+p2, +p2, +p2],    # 47
#                 [-p2, +p2, +p2],    # 48
#                 [-p1, -p1, +p1],    # 49
#                 [-p2, -p1, +p1],    # 50
#                 [+p2, -p1, +p1],    # 51
#                 [+p1, -p1, +p1],    # 52
#                 [+p1, -p2, +p1],    # 53
#                 [+p1, +p2, +p1],    # 54
#                 [+p1, +p1, +p1],    # 55
#                 [+p2, +p1, +p1],    # 56
#                 [-p2, +p1, +p1],    # 57
#                 [-p1, +p1, +p1],    # 58
#                 [-p1, +p2, +p1],    # 59
#                 [-p1, -p2, +p1],    # 60
#                 [-p2, -p2, +p1],    # 61
#                 [+p2, -p2, +p1],    # 62
#                 [+p2, +p2, +p1],    # 63
#                 [-p2, +p2, +p1]])   # 64
#             w1 = (18-np.sqrt(30))/36
#             w2 = (18+np.sqrt(30))/36
#             weights = np.array([
#                 [w1, w1, w1],       # 1
#                 [w2, w1, w1],       # 2
#                 [w2, w1, w1],       # 3
#                 [w1, w1, w1],       # 4
#                 [w1, w2, w1],       # 5
#                 [w1, w2, w1],       # 6
#                 [w1, w1, w1],       # 7
#                 [w2, w1, w1],       # 8
#                 [w2, w1, w1],       # 9
#                 [w1, w1, w1],       # 10
#                 [w1, w2, w1],       # 11
#                 [w1, w2, w1],       # 12
#                 [w2, w2, w1],       # 13
#                 [w2, w2, w1],       # 14
#                 [w2, w2, w1],       # 15
#                 [w2, w2, w1],       # 16
#                 [w1, w1, w2],       # 17
#                 [w2, w1, w2],       # 18
#                 [w2, w1, w2],       # 19
#                 [w1, w1, w2],       # 20
#                 [w1, w2, w2],       # 21
#                 [w1, w2, w2],       # 22
#                 [w1, w1, w2],       # 23
#                 [w2, w1, w2],       # 24
#                 [w2, w1, w2],       # 25
#                 [w1, w1, w2],       # 26
#                 [w1, w2, w2],       # 27
#                 [w1, w2, w2],       # 28
#                 [w2, w2, w2],       # 29
#                 [w2, w2, w2],       # 30
#                 [w2, w2, w2],       # 31
#                 [w2, w2, w2],       # 32
#                 [w1, w1, w2],       # 33
#                 [w2, w1, w2],       # 34
#                 [w2, w1, w2],       # 35
#                 [w1, w1, w2],       # 36
#                 [w1, w2, w2],       # 37
#                 [w1, w2, w2],       # 38
#                 [w1, w1, w2],       # 39
#                 [w2, w1, w2],       # 40
#                 [w2, w1, w2],       # 41
#                 [w1, w1, w2],       # 42
#                 [w1, w2, w2],       # 43
#                 [w1, w2, w2],       # 44
#                 [w2, w2, w2],       # 45
#                 [w2, w2, w2],       # 46
#                 [w2, w2, w2],       # 47
#                 [w2, w2, w2],       # 48
#                 [w1, w1, w1],       # 49
#                 [w2, w1, w1],       # 50
#                 [w2, w1, w1],       # 51
#                 [w1, w1, w1],       # 52
#                 [w1, w2, w1],       # 53
#                 [w1, w2, w1],       # 54
#                 [w1, w1, w1],       # 55
#                 [w2, w1, w1],       # 56
#                 [w2, w1, w1],       # 57
#                 [w1, w1, w1],       # 58
#                 [w1, w2, w1],       # 59
#                 [w1, w2, w1],       # 60
#                 [w2, w2, w1],       # 61
#                 [w2, w2, w1],       # 62
#                 [w2, w2, w1],       # 63
#                 [w2, w2, w1]])      # 64

#         elif order == 5:
#             p1 = np.sqrt(5+2*np.sqrt(10/7))/3
#             p2 = np.sqrt(5-2*np.sqrt(10/7))/3
#             points = np.array([
#                 [-p1, -p1, -p1],    # 1
#                 [-p2, -p1, -p1],    # 2
#                 [  0, -p1, -p1],    # 3
#                 [+p2, -p1, -p1],    # 4
#                 [+p1, -p1, -p1],    # 5
#                 [-p1, -p2, -p1],    # 6
#                 [-p2, -p2, -p1],    # 7
#                 [  0, -p2, -p1],    # 8
#                 [+p2, -p2, -p1],    # 9
#                 [+p1, -p2, -p1],    # 10
#                 [-p1,   0, -p1],    # 11
#                 [-p2,   0, -p1],    # 12
#                 [  0,   0, -p1],    # 13
#                 [+p2,   0, -p1],    # 14
#                 [+p1,   0, -p1],    # 15
#                 [-p1, +p2, -p1],    # 16
#                 [-p2, +p2, -p1],    # 17
#                 [  0, +p2, -p1],    # 18
#                 [+p2, +p2, -p1],    # 19
#                 [+p1, +p2, -p1],    # 20
#                 [-p1, +p1, -p1],    # 21
#                 [-p2, +p1, -p1],    # 22
#                 [  0, +p1, -p1],    # 23
#                 [+p2, +p1, -p1],    # 24
#                 [+p1, +p1, -p1],    # 25
#                 [-p1, -p1, -p2],    # 26
#                 [-p2, -p1, -p2],    # 27
#                 [  0, -p1, -p2],    # 28
#                 [+p2, -p1, -p2],    # 29
#                 [+p1, -p1, -p2],    # 30
#                 [-p1, -p2, -p2],    # 31
#                 [-p2, -p2, -p2],    # 32 
#                 [  0, -p2, -p2],    # 33
#                 [+p2, -p2, -p2],    # 34
#                 [+p1, -p2, -p2],    # 35
#                 [-p1,   0, -p2],    # 36
#                 [-p2,   0, -p2],    # 37
#                 [  0,   0, -p2],    # 38
#                 [+p2,   0, -p2],    # 39
#                 [+p1,   0, -p2],    # 40
#                 [-p1,  p2, -p2],    # 41
#                 [-p2,  p2, -p2],    # 42
#                 [  0,  p2, -p2],    # 43
#                 [+p2,  p2, -p2],    # 44
#                 [+p1,  p2, -p2],    # 45
#                 [-p1,  p1, -p2],    # 46
#                 [-p2,  p1, -p2],    # 47
#                 [  0,  p1, -p2],    # 48
#                 [+p2,  p1, -p2],    # 49
#                 [+p1,  p1, -p2],    # 50
#                 [-p1, -p1,   0],    # 51
#                 [-p2, -p1,   0],    # 52
#                 [  0, -p1,   0],    # 53
#                 [+p2, -p1,   0],    # 54
#                 [+p1, -p1,   0],    # 55
#                 [-p1, -p2,   0],    # 56
#                 [-p2, -p2,   0],    # 57
#                 [  0, -p2,   0],    # 58
#                 [+p2, -p2,   0],    # 59
#                 [+p1, -p2,   0],    # 60
#                 [-p1,   0,   0],    # 61
#                 [-p2,   0,   0],    # 62
#                 [  0,   0,   0],    # 63
#                 [+p2,   0,   0],    # 64
#                 [+p1,   0,   0],    # 65
#                 [-p1, +p2,   0],    # 66
#                 [-p2, +p2,   0],    # 67
#                 [  0, +p2,   0],    # 68
#                 [+p2, +p2,   0],    # 69
#                 [+p1, +p2,   0],    # 70
#                 [-p1, +p1,   0],    # 71
#                 [-p2, +p1,   0],    # 72
#                 [  0, +p1,   0],    # 73
#                 [+p2, +p1,   0],    # 74
#                 [+p1, +p1,   0],    # 75                          
#                 [-p1, -p1, +p2],    # 76
#                 [-p2, -p1, +p2],    # 77
#                 [  0, -p1, +p2],    # 78
#                 [+p2, -p1, +p2],    # 79
#                 [+p1, -p1, +p2],    # 80
#                 [-p1, -p2, +p2],    # 81
#                 [-p2, -p2, +p2],    # 82
#                 [  0, -p2, +p2],    # 83
#                 [+p2, -p2, +p2],    # 84
#                 [+p1, -p2, +p2],    # 85
#                 [-p1,   0, +p2],    # 86
#                 [-p2,   0, +p2],    # 87
#                 [  0,   0, +p2],    # 88
#                 [+p2,   0, +p2],    # 89
#                 [+p1,   0, +p2],    # 90
#                 [-p1, +p2, +p2],    # 91
#                 [-p2, +p2, +p2],    # 92
#                 [  0, +p2, +p2],    # 93
#                 [+p2, +p2, +p2],    # 94
#                 [+p1, +p2, +p2],    # 95
#                 [-p1, +p1, +p2],    # 96
#                 [-p2, +p1, +p2],    # 97
#                 [  0, +p1, +p2],    # 98
#                 [+p2, +p1, +p2],    # 99
#                 [+p1, +p1, +p2],    # 100
#                 [-p1, -p1, +p1],    # 101
#                 [-p2, -p1, +p1],    # 102
#                 [  0, -p1, +p1],    # 103
#                 [+p2, -p1, +p1],    # 104
#                 [+p1, -p1, +p1],    # 105
#                 [-p1, -p2, +p1],    # 106
#                 [-p2, -p2, +p1],    # 107
#                 [  0, -p2, +p1],    # 108
#                 [+p2, -p2, +p1],    # 109
#                 [+p1, -p2, +p1],    # 110
#                 [-p1,   0, +p1],    # 111
#                 [-p2,   0, +p1],    # 112
#                 [  0,   0, +p1],    # 113
#                 [+p2,   0, +p1],    # 114
#                 [+p1,   0, +p1],    # 115
#                 [-p1, +p2, +p1],    # 116
#                 [-p2, +p2, +p1],    # 117
#                 [  0, +p2, +p1],    # 118
#                 [+p2, +p2, +p1],    # 119
#                 [+p1, +p2, +p1],    # 120
#                 [-p1, +p1, +p1],    # 121
#                 [-p2, +p1, +p1],    # 122
#                 [  0, +p1, +p1],    # 123
#                 [+p2, +p1, +p1],    # 124
#                 [+p1, +p1, +p1]])   # 125
#             w0 = 128/225
#             w1 = (322-13*np.sqrt(70))/900
#             w2 = (322+13*np.sqrt(70))/900
#             weights = np.array([
#                 [w1, w1, w1],       # 1
#                 [w2, w1, w1],       # 2
#                 [w0, w1, w1],       # 3
#                 [w2, w1, w1],       # 4
#                 [w1, w1, w1],       # 5
#                 [w1, w2, w1],       # 6
#                 [w2, w2, w1],       # 7
#                 [w0, w2, w1],       # 8
#                 [w2, w2, w1],       # 9
#                 [w1, w2, w1],       # 10
#                 [w1, w0, w1],       # 11
#                 [w2, w0, w1],       # 12
#                 [w0, w0, w1],       # 13
#                 [w2, w0, w1],       # 14
#                 [w1, w0, w1],       # 15
#                 [w1, w2, w1],       # 16
#                 [w2, w2, w1],       # 17
#                 [w0, w2, w1],       # 18
#                 [w2, w2, w1],       # 19
#                 [w1, w2, w1],       # 20
#                 [w1, w1, w1],       # 21
#                 [w2, w1, w1],       # 22
#                 [w0, w1, w1],       # 23
#                 [w2, w1, w1],       # 24
#                 [w1, w1, w1],       # 25
#                 [w1, w1, w2],       # 26
#                 [w2, w1, w2],       # 27
#                 [w0, w1, w2],       # 28
#                 [w2, w1, w2],       # 29
#                 [w1, w1, w2],       # 30
#                 [w1, w2, w2],       # 31
#                 [w2, w2, w2],       # 32
#                 [w0, w2, w2],       # 33
#                 [w2, w2, w2],       # 34
#                 [w1, w2, w2],       # 35
#                 [w1, w0, w2],       # 36
#                 [w2, w0, w2],       # 37
#                 [w0, w0, w2],       # 38
#                 [w2, w0, w2],       # 39
#                 [w1, w0, w2],       # 40
#                 [w1, w2, w2],       # 41
#                 [w2, w2, w2],       # 42
#                 [w0, w2, w2],       # 43
#                 [w2, w2, w2],       # 44
#                 [w1, w2, w2],       # 45
#                 [w1, w1, w2],       # 46
#                 [w2, w1, w2],       # 47
#                 [w0, w1, w2],       # 48
#                 [w2, w1, w2],       # 49
#                 [w1, w1, w2],       # 50
#                 [w1, w1, w0],       # 51
#                 [w2, w1, w0],       # 52
#                 [w0, w1, w0],       # 53
#                 [w2, w1, w0],       # 54
#                 [w1, w1, w0],       # 55
#                 [w1, w2, w0],       # 56
#                 [w2, w2, w0],       # 57
#                 [w0, w2, w0],       # 58
#                 [w2, w2, w0],       # 59
#                 [w1, w2, w0],       # 60
#                 [w1, w0, w0],       # 61
#                 [w2, w0, w0],       # 62
#                 [w0, w0, w0],       # 63
#                 [w2, w0, w0],       # 64
#                 [w1, w0, w0],       # 65
#                 [w1, w2, w0],       # 66
#                 [w2, w2, w0],       # 67
#                 [w0, w2, w0],       # 68
#                 [w2, w2, w0],       # 69
#                 [w1, w2, w0],       # 70
#                 [w1, w1, w0],       # 71
#                 [w2, w1, w0],       # 72
#                 [w0, w1, w0],       # 73
#                 [w2, w1, w0],       # 74
#                 [w1, w1, w0],       # 75
#                 [w1, w1, w2],       # 76
#                 [w2, w1, w2],       # 77
#                 [w0, w1, w2],       # 78
#                 [w2, w1, w2],       # 79
#                 [w1, w1, w2],       # 80
#                 [w1, w2, w2],       # 81
#                 [w2, w2, w2],       # 82
#                 [w0, w2, w2],       # 83
#                 [w2, w2, w2],       # 84
#                 [w1, w2, w2],       # 85
#                 [w1, w0, w2],       # 86
#                 [w2, w0, w2],       # 87
#                 [w0, w0, w2],       # 88
#                 [w2, w0, w2],       # 89
#                 [w1, w0, w2],       # 90
#                 [w1, w2, w2],       # 91
#                 [w2, w2, w2],       # 92
#                 [w0, w2, w2],       # 93
#                 [w2, w2, w2],       # 94
#                 [w1, w2, w2],       # 95
#                 [w1, w1, w2],       # 96
#                 [w2, w1, w2],       # 97
#                 [w0, w1, w2],       # 98
#                 [w2, w1, w2],       # 99
#                 [w1, w1, w2],       # 100
#                 [w1, w1, w1],       # 101
#                 [w2, w1, w1],       # 102
#                 [w0, w1, w1],       # 103
#                 [w2, w1, w1],       # 104
#                 [w1, w1, w1],       # 105
#                 [w1, w2, w1],       # 106
#                 [w2, w2, w1],       # 107
#                 [w0, w2, w1],       # 108
#                 [w2, w2, w1],       # 109
#                 [w1, w2, w1],       # 110
#                 [w1, w0, w1],       # 111
#                 [w2, w0, w1],       # 112
#                 [w0, w0, w1],       # 113
#                 [w2, w0, w1],       # 114
#                 [w1, w0, w1],       # 115
#                 [w1, w2, w1],       # 116
#                 [w2, w2, w1],       # 117
#                 [w0, w2, w1],       # 118
#                 [w2, w2, w1],       # 119
#                 [w1, w2, w1],       # 120
#                 [w1, w1, w1],       # 121
#                 [w2, w1, w1],       # 122
#                 [w0, w1, w1],       # 123
#                 [w2, w1, w1],       # 124
#                 [w1, w1, w1]])      # 125
        
#         self.info = np.hstack((points, weights))