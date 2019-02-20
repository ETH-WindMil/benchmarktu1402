"""

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
        rule: {1, 2, 3, 4, 5}
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

        if rule == 1:
            points = np.array([[0, 0]])
            weights = np.array([[2, 2]])

        elif rule == 2:
            p = np.sqrt(3)/3
            points = np.array([
                    [-p, -p],           # 1
                    [+p, -p],           # 2
                    [+p, +p],           # 3
                    [-p, +p]])          # 4
            weights = np.ones((4, 2))

        elif rule == 3.:
            p = np.sqrt(3/5)
            points = np.array([
                    [ 0,  0],           # 1
                    [-p, -p],           # 2
                    [ 0, -p],           # 3
                    [+p, -p],           # 4
                    [+p,  0],           # 5
                    [+p, +p],           # 6
                    [ 0, +p],           # 7
                    [-p, +p],           # 8
                    [-p,  0]])          # 9
            w0 = 8/9
            w1 = 5/9
            weights = np.array([
                    [w0, w0],           # 1
                    [w1, w1],           # 2
                    [w0, w1],           # 3
                    [w1, w1],           # 4
                    [w1, w0],           # 5
                    [w1, w1],           # 6
                    [w0, w1],           # 7
                    [w1, w1],           # 8
                    [w1, w0]])          # 9

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
