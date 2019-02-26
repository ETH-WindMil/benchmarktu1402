# -*- coding: utf-8 -*-
# Author: Konstantinos

from scipy.sparse import linalg
import scipy.sparse as sps
import numpy as np
import scipy as sp
import model


class Modal:

    """
    Class for eigenvalue extraction, to calculte natural frequencies and the 
    corresponding mode shapes of an undamped system.

    Parameters
    ----------
    model: ...
        ...

    Attributes
    ----------
    tolerance
        The relative accuracy for eigenvalues.
    sigma
        ...
    numberOfEigenvalues
        The number of eigenvalues to be extracted.
    normalizationMethod
        The mode shapes normalization method.
    returnShapes
        Flag for returning the mode shapes.

    Methods
    -------
    setSigmaValue(sigma)
        ...
    setTolerance(tolerance)
        Specify the relative accuracy for eigenvalues.
    setNumberOfEigenvalues(number)
        Specify the number of eigenvalues to be extracted.
    setNormalizationMethod(method)
        Specify the mode shape normalization method.
    setReturnModeShapes(value)
        Specify if mode shapes are returned in addition to eigenvalues.
    submit()
        Submit for analysis.
    """

    def __init__(self, model):
        self.mesh = model # remove this when changed from all methods

        self._model = model

        self.tolerance = 0
        self.sigma = 0
        self.numberOfEigenvalues = 1
        self.normalizationMethod = 'Mass'
        self.returnModeShapes = True

        # Include flow information

    def Properties(self, m=5, sig=0, norm='mass'):

        self.stiffness = Model.Stiffness(self._model)
        self.mass = Model.Mass(self._model)

        Ma = self.mass.getFFMatrix() # self.mass.ff()
        K = self.stiffness.getFFMatrix() # self.stiffness.ff()
        values, vectors = spslinalg.eigsh(K, m, M=Ma, sigma=sig)#, tol=1e-10)

        # check if modes are already normalized

        # M = M.toarray()
        # for j in range(vecs.shape[1]):
        #     vecs[:, j] = vecs[:, j]/np.sqrt(vecs[:, j].dot(M).dot(vecs[:, j]))

        if np.any(values<0):
            index = np.where(values>=0)
            values, vectors = values[index[0]], vectors[:, index[0]]
            warnings.warn(str(len(index[0]))+' negative eigevalues found')

        # Fill-in with zeros for the constrained nodes and return the entire mode-shape vector
        # self.modes = np.zeros((len(self._model.ndof2), m))
        # self.modes[list(self._model.fdof2.values()), :] = vectors
        # self.modes[list(self._model.rdof2.values()), :] = 0

        self.frequencies = np.sqrt(values)/(2*np.pi)
        self.modes = vectors


    def setSigmaValue(self, value):

        """
        """

        if value <= 0:
            message = 'Sigma must be positive and non-zero'
            raise TypeError(message)
        self.sigma = value


    def setTolerance(self, tolerance):

        """
        Specify the relative accuracy (stopping criterion) for eigenvalues.
        If not specified, a zero value is used by default, which implies
        machine precision.

        Parameters
        ----------
        tolerance: float
            The relative accuracy.
        """

        self.tolerance = tolerance


    def setNumberOfEigenvalues(self, number):

        """
        Specify the number of eigenvalues to be extracted. If not specified, 
        only the first eigenvalue is extracted.

        Parameters
        ----------
        number: int, positive
            The number of eigenvalues.

        Raises
        ------
        TypeError
            If a non-positive number of eigenvalues is specified.
        """

        if number <= 0:
            error = 'Number of Eigenvalues must be positive.'
            raise TypeError(error)

        self.numberOfEigenvalues = number


    def setNormalizationMethod(self, method):

        """
        Specify the mode normalization method.

        Parameters
        ----------
        method: {'displacement', 'mass'}
            The method for mode shapes normalization. 

        Raises
        ------
        TypeError
            If an invalid normalization method is specified.
        """

        if method not in ['displacement', 'mass']:
            error = 'Normalization method must be either "{}" or "{}".'
            raise TypeError(error.format('Displacement', 'Mass'))

        self.normalizationMethod = method


    def setReturnModeShapes(self, value):

        """
        Specify if mode shapes are returned in addition to eigenvalues.

        Parameters
        ----------
        value: bool
            ...

        Raises
        ------
        TypeError
            If value is not a boolean.
        """

        if value not in [True, False]:
            error = 'value should be either "True" or "False".'
            raise TypeError(error)

        self.returnModeShapes = value


    # Modal time-history analysis works only with the free degrees of freedom
    # which should be accounted for in the solution
    def submit(self):

        """
        Submit the modal analysis
        """

        stiffness = Model.Stiffness(self._model).getFFMatrix()
        mass = Model.Mass(self._model).getFFMatrix()

        values = spslinalg.eigsh(stiffness, k=self.numberOfEigenvalues,
                M=mass, sigma=self.sigma, tol=self.tolerance,
                return_eigenvectors=self.returnModeShapes)

        if self.returnModeShapes:
            values, vectors = values[0], values[1]

            if np.any(values<0):
                index = np.where(values>=0)
                values, vectors = values[index[0]], vectors[:, index[0]]

                warning = '{} negative values found.\n'
                syst.stdout.write(warning.format(str(len(index[0]))))

            if self.normalizationMethod == 'Mass':
                for vector in vectors.T:
                    scaling = np.sqrt(vector.dot(mass.toarray().dot(vector)))
                    vector /= scaling
            else:
                scaling = np.max(np.abs(vectors), 0)
                vectors /= scaling

            # check if vectors has more than one columns.
            # If not, vectors.shape[1] will raise an error
            self.modes = np.zeros((len(self._model.ndof2), vectors.shape[1]))
            self.modes[list(self._model.fdof2.values()), :] = vectors
            self.modes[list(self._model.rdof2.values()), :] = 0
        else:
            self.modes = None
            if np.any(values<0):
                index = np.where(values>=0)
                values = values[index[0]]

                warning = '{} negative values found.\n'
                syst.stdout.write(warning.format(str(len(index[0]))))

        self.frequencies = np.sqrt(values)/(2*np.pi)


# class Modal(object):

#     def __init__(self, mesh, m=1, sigma=1, norm='mass'):
#         self.mesh = mesh
#         self.m = m
#         self.sigma = sigma
#         self.norm = norm


#     def analyze(self):
#         self.stiffness = model.Stiffness(self.mesh)
#         self.mass = model.Mass(self.mesh)

#         K = self.stiffness.ff()
#         M = self.mass.ff()

#         vals, vecs = linalg.eigsh(K, self.m, M, self.sigma)

#         self.modes = np.zeros((len(self.mesh.ndof2), self.m))
#         self.modes[list(self.mesh.fdof2.values()), :] = vecs
#         self.modes[list(self.mesh.rdof2.values()), :] = 0

#         self.frequencies = np.sqrt(vals)/(2*np.pi)



class TransientDynamic(object):

    def __init__(self, mesh, duration, step, method='linear'):
        self.mesh = mesh
        self.duration = duration
        self.step = step
        if method != 'constant' and method != 'linear':
            raise TypeError('Invalid Newmark method')
        else:
            self.method = method


    def analyze(self):

        modalAnalysis = Modal(self.mesh, 4)
        modalAnalysis.analyze()
        frequencies = modalAnalysis.frequencies
        modes = modalAnalysis.modes[list(self.mesh.fdof2.values()), :]

        step = self.step
        dmp = 0.01

        if self.method is 'constant':
            beta, gamma = 1/4, 1/2
        elif self.method is 'linear':
            beta, gamma = 1/6, 1/2

        Tup = 1/frequencies[-1]

        if step > 0.1*Tup:
            step = 0.1*Tup

        time_ = np.arange(0, self.duration+step, step)
        m = len(frequencies)
        t = len(time_)
        
        mdsp_k = np.zeros(m)
        mvlc_k = np.zeros(m)

        mdsp = np.zeros((m, t))
        mvlc = np.zeros((m, t))
        macl = np.zeros((m, t))

        K = (np.diag(frequencies)*2*np.pi)**2
        C = np.diag(frequencies)*2*np.pi*2*dmp
        M = np.eye(m)

        dsp = model._Displacement(self.mesh).ff()
        vlc = model._Velocity(self.mesh).ff()

        # for i, mode in enumerate(modes.T):
        #     nom = mode.dot(modalAnalysis.mass.ff())
        #     den = nom.dot(mode.T)
        #     mdsp_k[i] = nom.dot(dsp)/den.toarray()
        #     mvlc_k[i] = nom.dot(vlc)/den.toarray()


        p = len(self.mesh.loads)
        Sp = self.mesh.Sp
        loads = np.zeros((p, t))

        for i, load in enumerate(self.mesh.loads):
            loads[i] = np.interp(time_, load[0], load[1])

        mfrc = modes.T.dot(Sp).dot(loads)


        macl_k = np.linalg.solve(M, mfrc[:, 0]-C.dot(mvlc_k)-K.dot(mdsp_k))
        mdsp[:, 0], mvlc[:, 0], macl[:, 0] = mdsp_k, mvlc_k, macl_k

        a1 = 1/(beta*step**2)*M+gamma/(beta*step)*C
        a2 = 1/(beta*step)*M+(gamma/beta-1)*C
        a3 = (1/(2*beta)-1)*M+step*(gamma/(2*beta)-1)*C

        K += a1
        Kinv = np.linalg.inv(K)

        c1 = gamma/(beta*step)
        c2 = 1-gamma/beta
        c3 = step*(1-gamma/(2*beta))
        c4 = 1/(beta*step**2)
        c5 = -1/(beta*step)
        c6 = -(1/(2*beta)-1)

        for j in range(t-1):

            efrc_l = mfrc[:, j+1]+a1.dot(mdsp_k)+a2.dot(mvlc_k)+a3.dot(macl_k)

            mdsp_l = Kinv.dot(efrc_l)
            mvlc_l = c1*(mdsp_l-mdsp_k)+c2*mvlc_k+c3*macl_k
            macl_l = c4*(mdsp_l-mdsp_k)+c5*mvlc_k+c6*macl_k

            mdsp[:, j+1] = mdsp_k = mdsp_l
            mvlc[:, j+1] = mvlc_k = mvlc_l
            macl[:, j+1] = macl_k = macl_l

        return mdsp, mvlc, macl, time_
