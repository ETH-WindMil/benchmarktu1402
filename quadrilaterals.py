"""
Provides the implementation of isoparametric quadrilateral plane-stress and 
plane-strain elements.
"""

import abc
import numpy as np

__author__ = 'Konstantinos Tatsis'
__email__ = 'konnos.tatsis@gmail.com'

class Quadrilateral(abc.ABC):

    """
    Class for interfacing the methods of quadrilateral elements for 
    plane-stress and plane strain problems.

    Methods
    -------
    getStiffness(ncoords, cmatrix, thickness, irule)
        Get the global stiffness matrix.
    getMass(ncoords, mdensity, thickness, irule)
        Get the global mass matrix.
    getJacobian(ncoords, r1, r2)
        Get the Jacobian.
    getDeformationMatrix(ncoords, r1, r2)
        Get the deformation matrix.
    """

    def getStiffness(self, ncoords, cmatrix, thickness, irule):

        """
        Get the global stiffness matrix.

        Parameters
        ----------
        ncoords: ndarray
            The nodal coordinates (n x 2), where n is he number of nodes.
        cmatrix: ndarray
            The material constitutive matrix at the integration points.
        thickness: ndarray
            The element thickness at the integration points.
        irule: ndarray
            The integration rule (p x 4), where p is the number of integration
            points. The first two columns contain the sample points while the
            last one contains the corresponding weights.

        Returns
        -------
        stiffness: ndarray
            The global stiffness matrix.
        """

        stiffness = np.zeros((self.degrees, self.degrees))

        for C, t, (r1, r2, w1, w2) in zip(cmatrix, thickness, irule):
            B, jacobian = self.getDeformationMatrix(ncoords, r1, r2)
            stiffness += w1*w2*B.T.dot(C).dot(B)*np.linalg.det(jacobian)*t

        return stiffness


    def getMass(self, ncoords, mdensity, thickness, irule):

        """
        Get the global mass matrix.

        Parameters
        ----------
        ncoords: ndarray
            The nodal coordinates (n x 2), where n is the number of nodes.
        mdensity: ndarray
            The material density at integration points.
        thickness: ndarray
            The element thickness at integration points.
        irule: ndarray
            The integration rule (p x 4), where p is the number of integration
            points. The first two columns contain the sample points while the
            last one contains the corresponding weights.

        Returns
        -------
        mass: ndarray
            The global mass matrix.
        """

        mass = np.zeros((self.degrees, self.degrees))

        for density, t, (r1, r2, w1, w2) in zip(mdensity, thickness, irule):
            N = self.getShapeFunctions(r1, r2)
            jacobian = self.getJacobian(ncoords, r1, r2)
            mass += w1*w2*N.T.dot(N)*density*np.linalg.det(jacobian)*t

        return mass


    def getStiffnessMass(self, ncoords, cmatrix, thickness, mdensity, irule):

        """
        Get the global stiffness and mass matrix.

        Parameters
        ----------
        ncoords: ndarray
            The nodal coordinates (n x 2), where n is the number of nodes.
        cmatrix: ndarray
            The material constitutive matrix at the integration points.
        thickness: ndarray
            The element thickness at integration points.
        mdensity: ndarray
            The material density at integration points.
        irule: ndarray
            The integration rule (p x 4), where p is the number of integration
            points. The first two columns contain the sample points while the
            last one contains the corresponding weights.

        Returns
        -------
        stiffness: ndarray
            The global stiffness matrix.
        mass: ndarray
            The global mass matrix.
        """

        stiffness = np.zeros((self.degrees, self.degrees))
        mass = np.zeros((self.degrees, self.degrees))

        for C, r, t, (r1, r2, w1, w2) in zip(cmatrix, mdensity, thickness, irule):
            B, jacobian = self.getDeformationMatrix(ncoords, r1, r2)
            N = self.getShapeFunctions(r1, r2)

            stiffness += w1*w2*B.T.dot(C).dot(B)*np.linalg.det(jacobian)*t
            mass += w1*w2*N.T.dot(N)*r*np.linalg.det(jacobian)*t

        return stiffness, mass


    def getDeformationMatrix(self, ncoords, r1, r2):

        """
        Get the deformation matrix, relating displacements to strains.

        Parameters
        ----------
        ncoords: ndarray
            The nodal coordinates (n x 2), where n is the number of nodes.
        r1, r2: float
            The quadrilateral natural coordinates, ranging form -1 to 1.

        Returns
        -------
        deformation: ndarray
            The deformation matrix.
        jacobian: ndaray
            The jacobian matrix.
        """

        jacobian = self.getJacobian(ncoords, r1, r2)
        derivatives = self.getShapeFunctionsDerivatives(r1, r2)
        data = np.linalg.inv(jacobian).dot(derivatives).T
        deformation = np.zeros((3, self.degrees))

        cols = np.arange(0, self.degrees, 2)
        rows = [0, 1, 2, 2]
        shifts = [0, 1, 0, 1]
        entries = [0, 1, 1, 0]

        for row, shift, entry in zip(rows, shifts, entries):
            deformation[row, cols+shift] = data[:, entry]

        return deformation, jacobian



    def getJacobian(self, ncoords, r1, r2):

        """
        Get the Jacobian matrix.

        Parameters
        ----------
        ncoords
            The nodal coordinates (n x 2), where n is the number of nodes.
        r1, r2: float
            The quadrilateral natural coordinates, ragning from -1 to 1.

        Returns
        -------
        jacobian: ndarray
            The jacobian matrix.
        """

        jacobian = self.getShapeFunctionsDerivatives(r1, r2).dot(ncoords)

        return jacobian



class Quad4(Quadrilateral):

    """
    Class implementing the four-node quadrilateral element for plane-stress 
    and plane-strain problems.

    Attributes
    ----------
    degrees: int
        The number of degrees of freedom.

    Methods
    -------
    getShapeFunctions(r1, r2)
        Get the shape function matrix in natural coordinates.
    getShapeFunctionsDerivatives(r1, r2)
        Get the shape functions derivatives with respect to the natural
        coordinates.

    Notes
    -----

    Examples
    --------
    >>> mdensity = 500*np.ones(4)
    >>> thickness = 0.2*np.ones(4)
    >>> ncoords = np.array([[2, 1], [0, 1], [0, 0], [2, 0]])
    >>> irule = np.array([
            [-0.57735027, -0.57735027,  1.,  1.],
            [ 0.57735027, -0.57735027,  1.,  1.],
            [ 0.57735027,  0.57735027,  1.,  1.],
            [-0.57735027,  0.57735027,  1.,  1.]])
    >>> cmatrix = np.array([
            [108,  36,  0],
            [ 36, 108,  0],
            [  0,   0, 36]])
    >>> cmatrix = np.repeat(np.array([cmatrix]), 4, axis=0)
    >>> quad4 = quadrilaterals.Quad4()
    >>> stiffness = quad4.getStiffness(ncoords, cmatrix, thickness, irule)
    >>> mass = quad4.getMass(ncoords, mdensity, thickness, irule)
    """

    degrees = 8

    @staticmethod
    def getShapeFunctions(r1, r2):

        """
        Get the shape functions matrix, that relates nodal displacements to 
        element field displacements, in natural coordinates.

        Parameters
        ----------
        r1, r2
            The quadrilateral natural coordinates, ranging from -1 to 1, at
            which the shape functions are evaluated.

        Returns
        -------
        out: ndarray
            The shape functions matrix of size (2 x 8), where 8 is the number
            of degrees of freedom.
        """

        shapeFunctions = 0.25*np.array([
                (1+r1)*(1+r2), (1-r1)*(1+r2), (1-r1)*(1-r2), (1+r1)*(1-r2)])
        out = np.zeros((2, 8))
        cols = np.arange(0, 8, 2)

        for row in range(2):
            out[row, cols+row] = shapeFunctions

        return out


    @staticmethod
    def getShapeFunctionsDerivatives(r1, r2):

        """
        Get the shape functions derivatives with respect to the natural
        coordinates r1 and r2.

        Parameters
        ----------
        r1, r2
            The quadrilateral natural coordinates, ranging from -1 to 1, at
            which the shape functions derivatives are evaluated.

        Returns
        -------
        out: ndarray
            The shape functions derivatives of size (2 x 4), where 4 is the
            number of nodes.
        """

        out = np.zeros((2, 4))
        out[0, :] = np.array([(1+r2), -(1+r2), -(1-r2), (1-r2)])/4
        out[1, :] = np.array([(1+r1), (1-r1), -(1-r1), -(1+r1)])/4

        return out


class Quad8(Quadrilateral):

    """
    Class implementing the eight-node quadrilateral element for plane-stress 
    and plain strain problems.

    Methods
    -------
    getShapeFunctions(r1, r2)
        Get the shape functions matrix.
    getShapeFunctionsDerivatives(r1, r2)
        Get the shape functions derivatives with respect to the natural
        coordinates.

    Examples
    --------
    >>> mdensity = 500*np.ones(9)
    >>> thickness = 0.2*np.ones(9)
    >>> ncoords = np.array([
            [2, 2], [0, 2], [0, 0], [2, 0],
            [1, 2], [0, 1], [1, 0], [2, 1]])
    >>> irule = array([
            [ 0.        ,  0.        ,  0.88888889,  0.88888889],
            [-0.77459667, -0.77459667,  0.55555556,  0.55555556],
            [ 0.        , -0.77459667,  0.88888889,  0.55555556],
            [ 0.77459667, -0.77459667,  0.55555556,  0.55555556],
            [ 0.77459667,  0.        ,  0.55555556,  0.88888889],
            [ 0.77459667,  0.77459667,  0.55555556,  0.55555556],
            [ 0.        ,  0.77459667,  0.88888889,  0.55555556],
            [-0.77459667,  0.77459667,  0.55555556,  0.55555556],
            [-0.77459667,  0.        ,  0.55555556,  0.88888889]])
    >>> cmatrix = np.array([
            [108,  36,  0],
            [ 36, 108,  0],
            [  0,   0, 36]])
    >>> cmatrix = np.repeat(np.array([cmatrix]), 9, axis=0)
    >>> quad8 = quadrilaterals.Quad8()
    >>> stiffness = quad8.getStiffness(ncoords, cmatrix, thickness, irule)
    >>> mass = quad8.getMass(ncoords, mdensity, thickness, irule)
    """

    degrees = 16

    @staticmethod
    def getShapeFunctions(r1, r2):

        """
        Get the shape fucntions matrix, that relates nodal displacements to
        element field displacements.

        Parameters
        ----------
        r1, r2: float
            The quadrilateral natural coordinates, ranging from -1 to 1, at 
            which the shape functions are evaluated.

        Returns
        -------
        out: ndarray
            The shape functions matrix of size (2 x 16), where 16 is the
            number of degrees of freedom.
        """

        shapeFunctions = 0.5*np.array([
                (1+r1)*(1+r2)*(r1+r2-1)/2, 
                (1-r1)*(1+r2)*(-r1+r2-1)/2,
                (1-r1)*(1-r2)*(-r1-r2-1)/2, 
                (1+r1)*(1-r2)*(r1-r2-1)/2,
                (1-r1**2)*(1+r2), 
                (1-r1)*(1-r2**2),
                (1-r1**2)*(1-r2), 
                (1+r1)*(1-r2**2)])
        out = np.zeros((2, 16))
        cols = np.arange(0, 16, 2)

        for row in range(2):
            out[row, cols+row] = shapeFunctions

        return out


    @staticmethod
    def getShapeFunctionsDerivatives(r1, r2):

        """
        Get the shape functions derivatives with respect to the natural 
        coordiantes r1 and r2.

        Parameters
        ----------
        r1, r2
            The quadrilateral natural coordinates, ranging from -1 to 1, at
            which the shape functions' derivatives are evaluted.

        Returns
        -------
        out: ndarray
            The shape functions derivatives of size (2 x 8), where 8 is the 
            number of nodes.
        """

        out = np.zeros((2, 8))
        out[0, :2] = np.array([(1+r1)*(-2*r1+r2), -(1+r2)*(-2*r1+r2)])/4
        out[0, 2:4] = np.array([(1-r2)*(2*r1+r2), (1-r2)*(2*r1-r2)])/4
        out[0, 4:6] = np.array([-2*r1*(1+r2), -(1-r2**2)])/2
        out[0, 6:] = np.array([-2*r1*(1-r2), (1-r2**2)])/2

        out[1, :2] = np.array([(1+r1)*(2*r2+r1), (1-r1)*(2*r2-r1)])/4
        out[1, 2:4] = np.array([(1-r1)*(2*r2+r1), (1+r1)*(2*r2-r1)])/4
        out[1, 4:6] = np.array([(1-r1**2), -2*r2*(1-r1)])/2
        out[1, 6:] = np.array([-(1-r1**2), -2*r2*(1+r1)])/2

        return out


class Quad9(Quadrilateral):

    """
    Class implementing the nine-node quadrilateral element for plane-stress 
    and plane strain problems.

    Methods
    -------
    getShapeFunctions(r1, r2)
        Get the shape functions matrix.
    getShapeFunctionsDerivatives(r1, r2)
        Get the shape functions derivatives with respect to the natural
        coordinates.

    Examples
    --------
    >>> mdensity = 500*np.ones(9)
    >>> thickness = 0.2*np.ones(9)
    >>> ncoords = np.array([
            [2, 2], [0, 2], [0, 0], [2, 0],
            [1, 2], [0, 1], [1, 0], [2, 1], [1, 1]])
    >>> irule = array([
            [ 0.        ,  0.        ,  0.88888889,  0.88888889],
            [-0.77459667, -0.77459667,  0.55555556,  0.55555556],
            [ 0.        , -0.77459667,  0.88888889,  0.55555556],
            [ 0.77459667, -0.77459667,  0.55555556,  0.55555556],
            [ 0.77459667,  0.        ,  0.55555556,  0.88888889],
            [ 0.77459667,  0.77459667,  0.55555556,  0.55555556],
            [ 0.        ,  0.77459667,  0.88888889,  0.55555556],
            [-0.77459667,  0.77459667,  0.55555556,  0.55555556],
            [-0.77459667,  0.        ,  0.55555556,  0.88888889]])
    >>> cmatrix = np.array([
            [108,  36,  0],
            [ 36, 108,  0],
            [  0,   0, 36]])
    >>> cmatrix = np.repeat(np.array([cmatrix]), 9, axis=0)
    >>> quad9 = quadrilaterals.Quad9()
    >>> stiffness = quad9.getStiffness(ncoords, cmatrix, thickness, irule)
    >>> mass = quad9.getMass(ncoords, mdensity, thickness, irule)
    """

    degrees = 18

    @staticmethod
    def getShapeFunctions(r1, r2):

        """
        Get the shape functions matrix, that relates nodal quantities to 
        element field quantities.

        Parameters
        ----------
        r1, r2
            The quadrilateral natural coordinates, ranging from -1 to 1, at
            which the shape functions are evaluated.

        Returns
        -------
        out: ndarray
            The shape functions matrix of size (3 x 18), where 18 is the
            number of degrees of freedom.
        """

        shapeFunctions = np.array([
                 (1+r1)*(1+r2)*r1*r2/4, 
                -(1-r1)*(1+r2)*r1*r2/4,
                 (1-r1)*(1-r2)*r1*r2/4, 
                -(1+r1)*(1-r2)*r1*r2/4,
                 (1-r1**2)*(1+r2)*r2/2,
                -(1-r1)*r1*(1-r2**2)/2,
                -(1-r1**2)*(1-r2)*r2/2,
                 (1+r1)*r1*(1-r2**2)/2,
                 (1-r1**2)*(1-r2**2)])
        out = np.zeros((2, 18))
        cols = np.arange(0, 18, 2)

        for row in range(2):
            out[row, cols+row] = shapeFunctions

        return out


    @staticmethod
    def getShapeFunctionsDerivatives(r1, r2):

        """
        Get the shape functions derivatives with respect to the natural 
        coordiantes r1 and r2.

        Parameters
        ----------
        r1, r2
            The quadrilateral natural coordinates, ranging from -1 to 1, at
            which the shape functions' derivatives are evaluated.

        Returns
        -------
        out: ndarray
            The shape functions derivatives of size (2 x 9), where 9 is the 
            number of nodes.
        """

        out = np.zeros((2, 9))

        out[0, :2] = np.array([(1+r2)*(2*r1*r2+r2), (1+r2)*(2*r1*r2-r2)])/4
        out[0, 2:4] = np.array([-(1-r2)*(2*r1*r2-r2), -(1-r2)*(2*r1*r2+r2)])/4
        out[0, 4:6] = np.array([-2*r1*r2*(1+r2), -(1-2*r1)*(1-r2**2)])/2
        out[0, 6:8] = np.array([2*r1*r2*(1-r2), (1+2*r1)*(1-r2**2)])/2
        out[0, 8:] = np.array([-2*r1*(1-r2**2)])

        out[1, :2] = np.array([(1+r1)*(2*r1*r2+r1), -(1-r1)*(2*r1*r2+r1)])/4
        out[1, 2:4] = np.array([-(1-r1)*(2*r1*r2-r1), (1+r1)*(2*r1*r2-r1)])/4
        out[1, 4:6] = np.array([(1-r1**2)*(1+2*r2), (1-r1)*2*r1*r2])/2
        out[1, 6:8] = np.array([-(1-r1**2)*(1-2*r2), -(1+r1)*2*r1*r2])/2
        out[1, 8:] = np.array([-2*r2*(1-r1**2)])

        return out