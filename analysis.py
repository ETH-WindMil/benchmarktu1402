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
        The sigma value for shift-invert mode.
    numberOfEigenvalues
        The number of eigenvalues to be extracted.
    normalizationMethod
        The mode shapes normalization method.
    returnShapes
        Flag for returning the mode shapes.

    Methods
    -------
    setSigmaValue(sigma)
        Specify the sigma value, near which the eigenvalues are calculated.
    setTolerance(tolerance)
        Specify the relative accuracy for eigenvalues.
    setNumberOfEigenvalues(number)
        Specify the number of eigenvalues to be extracted.
    setNormalizationMethod(method)
        Specify the mode shape normalization method.
    setReturnModeShapes(value)
        Specify if mode shapes are returned in addition to eigenvalues.
    submit()
        Submit analysis.
    """

    def __init__(self, model):

        self.model = model
        self.tolerance = 0
        self.sigma = 0
        self.numberOfEigenvalues = 1
        self.normalizationMethod = 'Mass'
        self.returnModeShapes = True


    def setSigmaValue(self, sigma):

        """
        Specify the sigma value, near which the eigenvalues are calculated
        using shift-invert mode of the "scipy.sparse.linalg.eigsh" algorithm.

        Parameters
        ----------
        sigma: real
            The sigma value.
        """

        if sigma <= 0:
            error = 'Sigma must be positive and non-zero'
            raise TypeError(error)

        self.sigma = sigma


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

        if method.lower() not in ['displacement', 'mass']:
            error = 'Normalization method must be either "{}" or "{}".'
            raise TypeError(error.format('Displacement', 'Mass'))

        self.normalizationMethod = method


    def setReturnModeShapes(self, value):

        """
        Specify if mode shapes are returned in addition to eigenvalues.

        Parameters
        ----------
        value: bool
            The flag determining whether mode shapes are extracted or not.

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
        Submit the analysis.
        """

        stiffness = model.Stiffness(self.model).getPartitionFF()
        mass = model.Mass(self.model).getPartitionFF()

        values = linalg.eigsh(stiffness, k=self.numberOfEigenvalues,
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
            self.modes = np.zeros((len(self.model.ndof2), vectors.shape[1]))
            self.modes[list(self.model.fdof2.values()), :] = vectors
            self.modes[list(self.model.rdof2.values()), :] = 0
        else:
            self.modes = None
            if np.any(values<0):
                index = np.where(values>=0)
                values = values[index[0]]

                warning = '{} negative values found.\n'
                syst.stdout.write(warning.format(str(len(index[0]))))

        self.frequencies = np.sqrt(values)/(2*np.pi)



class TransientDynamics(object):

    """
    Methods
    -------
    setTimePeriod(period)
        Specify the simulation time period.
    setIncrementSize(size)
        Specify the solution time increment.
    submit()
        Submit analysis.
    """


    def __init__(self, model): # duration, step, method='linear'):
        self.model = model
        # self.duration = duration
        # self.step = step
        # if method != 'constant' and method != 'linear':
        #     raise TypeError('Invalid Newmark method')
        # else:
        #     self.method = method

        self.timePeriod = 1
        self.incrementSize = 0.1


    def setTimePeriod(self, period):

        """
        Specify the simulation time period.

        Parameters
        ----------
        period: float, positive
            The simulation time period.

        Raises
        ------
        TypeError
            If period is not positive.
        """

        if period <= 0:
            raise TypeError('Time period must be positive.')

        self.timePeriod = period


    def setIncrementSize(self, size):

        """
        Specify the solution increment size.

        Parameters
        ----------
        size: float, positive
            The increment size.

        Raises
        ------
        TypeError
            If the increment size is not positive.
        """

        if size <= 0:
            raise TypeError('Increment size must be positive.')

        self.incrementSize = size




    def submit(self):

        modal = Modal(self.model)
        modal.setNumberOfEigenvalues(10)
        modal.submit()

        frequencies = modal.frequencies
        modes = modal.modes

        beta, gamma = 1/6, 1/2
        period, step = self.timePeriod, self.incrementSize

        if step > 0.1*(1/frequencies[-1]):
            step = 0.1*(1/frequencies[-1])

        time = np.arange(0, period+step, step)


        alpha, beta = self.model.alpha, self.model.beta
        damping = alpha*1/(4*np.pi*frequencies)+beta*np.pi*frequencies

        dsp = np.zeros((len(frequencies), len(time)))
        vlc = np.zeros((len(frequencies), len(time)))
        acc = np.zeros((len(frequencies), len(time)))

        K = (np.diag(frequencies)*2*np.pi)**2
        C = np.diag(frequencies)*2*np.pi*2*damping
        M = np.eye(len(frequencies))

        # { Construct modal force vector

        loads = np.zeros((len(self.model.loads), len(time)))

        for j, load in enumerate(self.model.loads):
            loads[i] = np.interp(time, load[0], load[1])

        frc = model.T.dot(self.model.Sp).dot(loads)

        # }

        efrc = -C.dot(vlc[:, 0])-K.dot(dsp[:, 0])
        acc[:, 0] = np.linalg.solve(M, frc[:, 0]+efrc)

        a1 = 1/(beta*step**2)*M+gamma/(beta*step)*C
        a2 = 1/(beta*step)*M+(gamma/beta-1)*C
        a3 = (1/(2*beta)-1)*M+step*(gamma/(2*beta)-1)*C
        Ki = np.linalg.inv(K+a1)

        c1 = gamma/(beta*step)
        c2 = 1-gamma/beta
        c3 = step*(1-gamma/(2*beta))
        c4 = 1/(beta*step**2)
        c5 = -1/(beta*step)
        c6 = -(1/(2*beta)-1)

        for j in range(len(time)-1):

            efrc = a1.dot(dsp[:, j])+a2.dot(vlc[:, j])+a3.dot(acc[:, j])
            dsp[:, j+1] = Ki.dot(frc[:, j+1]+efrc)

            vlc[:, j+1] = c1*(dsp[:, j+1]-dsp[:, j])+c2*vlc[:, j]+c3*acc[:, j]
            acc[:, j+1] = c4*(dsp[:, j+1]-dsp[:, j])+c5*vlc[:, j]+c6*acc[:, j]

        self.displacement = dsp
        self.velocity = vlc
        self.acceleration = acc



    # def analyze(self):

    #     modalAnalysis = Modal(self.mesh, 4)
    #     modalAnalysis.analyze()
    #     frequencies = modalAnalysis.frequencies
    #     modes = modalAnalysis.modes[list(self.mesh.fdof2.values()), :]

    #     step = self.step
    #     dmp = 0.01

    #     if self.method is 'constant':
    #         beta, gamma = 1/4, 1/2
    #     elif self.method is 'linear':
    #         beta, gamma = 1/6, 1/2

    #     Tup = 1/frequencies[-1]

    #     if step > 0.1*Tup:
    #         step = 0.1*Tup

    #     time_ = np.arange(0, self.duration+step, step)
    #     m = len(frequencies)
    #     t = len(time_)
        
    #     mdsp_k = np.zeros(m)
    #     mvlc_k = np.zeros(m)

    #     mdsp = np.zeros((m, t))
    #     mvlc = np.zeros((m, t))
    #     macl = np.zeros((m, t))

    #     K = (np.diag(frequencies)*2*np.pi)**2
    #     C = np.diag(frequencies)*2*np.pi*2*dmp
    #     M = np.eye(m)

    #     dsp = model._Displacement(self.mesh).ff()
    #     vlc = model._Velocity(self.mesh).ff()

    #     # for i, mode in enumerate(modes.T):
    #     #     nom = mode.dot(modalAnalysis.mass.ff())
    #     #     den = nom.dot(mode.T)
    #     #     mdsp_k[i] = nom.dot(dsp)/den.toarray()
    #     #     mvlc_k[i] = nom.dot(vlc)/den.toarray()


    #     p = len(self.mesh.loads)
    #     Sp = self.mesh.Sp
    #     loads = np.zeros((p, t))

    #     for i, load in enumerate(self.mesh.loads):
    #         loads[i] = np.interp(time_, load[0], load[1])

    #     mfrc = modes.T.dot(Sp).dot(loads)


    #     macl_k = np.linalg.solve(M, mfrc[:, 0]-C.dot(mvlc_k)-K.dot(mdsp_k))
    #     mdsp[:, 0], mvlc[:, 0], macl[:, 0] = mdsp_k, mvlc_k, macl_k

    #     a1 = 1/(beta*step**2)*M+gamma/(beta*step)*C
    #     a2 = 1/(beta*step)*M+(gamma/beta-1)*C
    #     a3 = (1/(2*beta)-1)*M+step*(gamma/(2*beta)-1)*C

    #     K += a1
    #     Kinv = np.linalg.inv(K)

    #     c1 = gamma/(beta*step)
    #     c2 = 1-gamma/beta
    #     c3 = step*(1-gamma/(2*beta))
    #     c4 = 1/(beta*step**2)
    #     c5 = -1/(beta*step)
    #     c6 = -(1/(2*beta)-1)

    #     for j in range(t-1):

    #         efrc_l = mfrc[:, j+1]+a1.dot(mdsp_k)+a2.dot(mvlc_k)+a3.dot(macl_k)

    #         mdsp_l = Kinv.dot(efrc_l)
    #         mvlc_l = c1*(mdsp_l-mdsp_k)+c2*mvlc_k+c3*macl_k
    #         macl_l = c4*(mdsp_l-mdsp_k)+c5*mvlc_k+c6*macl_k

    #         mdsp[:, j+1] = mdsp_k = mdsp_l
    #         mvlc[:, j+1] = mvlc_k = mvlc_l
    #         macl[:, j+1] = macl_k = macl_l

    #     return mdsp, mvlc, macl, time_
