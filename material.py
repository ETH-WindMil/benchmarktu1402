import numpy as np


class LinearElastic:
    
    def __init__(self, E, n, rho=0):
        self.E = E
        self.n = n
        self.rho = rho
        self.G = self.E/(2*(1+self.n))
        
        ct = self.E/(1-self.n**2)
        self.C = np.zeros((3, 3))
        self.C[-1, -1] = ct*0.5*(1-self.n)
        self.C[:2, :2] = ct*(np.eye(2)+self.n*(np.ones((2, 2))-np.eye(2)))
