# -*- coding: utf-8 -*-
# Author: Konstantinos

from collections import OrderedDict

import numpy as np
import scipy as sp
import itertools as it
import scipy.sparse as sps
import matplotlib.pyplot as plt
import multiprocessing
import abc
import time


class Node:

    dictionary = {'x':0, 'y':1, 'z':2, 'rx':3, 'ry':4, 'rz':5}

    def __init__(self, coordinates):
        self.label = np.nan

        self.links = []
        self.coords = np.array(coordinates)
        self.dsp = np.zeros((6, 1))
        self.vlc = np.zeros((6, 1))
        self.acl = np.zeros((6, 1))

        self.strain = np.zeros(3)

        self.adof = np.ones(6)*False
        self.cdof = np.ones(6)*False
        self.ndof = np.ones(6)*np.nan


    def __str__(self):
        string = 'model.Node({})'
        return string.format(self.coords)


    def __repr__(self):
        string = 'Node {} - <{}.{} object at {}>\n'+\
                 '    Coordinates:        {}\n'+\
                 '    Active DoF:         {}\n'+\
                 '    Constrained DoF:    {}\n'+\
                 '    Numeration:         {}\n'+\
                 '    Links:              {}\n'
        return string.format(self.label,
                             self.__module__,
                             type(self).__name__,
                             hex(id(self)),
                             self.coords,
                             self.adof.T,
                             self.cdof.T,
                             self.ndof.T,
                             self.links)


    def addLink(self, elementLabel):
        self.links.append(elementLabel)


    def setRestraint(self, dof):
        for dof in dofs:
            self.rdof[dictionary[dof]] = True

    def SetValue(self, Name, String, Value=6*[True]):
        if String == 'A':
            String = self.dictionary.keys()
        for i, j in enumerate(String):
            self.__dict__[Name][self.dictionary[j]] = Value[i]


    def AddValue(self, Name, String, Value):
        if String == 'A':
            String = self.dictionary.keys()
        for i, j in enumerate(String):
            self.__dict__[Name][self.dictionary[j]] += Value[i]



class Element:

    def __init__(self, nodes, element, material, thickness, irule):
        self.label = None
        self.nodes = nodes
        self.type = element
        self.material = material
        self.thickness = thickness
        self.irule = irule


    def getNodeCoordinates(self):

        ncoords = np.array([node.coords[:2] for node in self.nodes])
        return ncoords


    def getNodeLabels(self):

        labels = [node.label for node in self.nodes]
        return labels


    def getNodeDegreesOfFreedom(self):

        degreesOfFreedom = np.hstack([node.ndof[:2] for node in self.nodes])
        degreesOfFreedom = degreesOfFreedom.astype(int)

        return degreesOfFreedom


    def getIntegrationPoints(self):

        ipoints = self.irule[:, :2]
        return ipoints


    def getType(self):

        return self.type


    def getStiffness(self):
        
        ncoords = np.array([node.coords[:2] for node in self.nodes])
        cmatrix = np.array([material.C for material in self.material])
        thickness, irule = self.thickness, self.irule

        stiffness = self.type.getStiffness(ncoords, cmatrix, thickness, irule)

        return stiffness


    def getMass(self):

        ncoords = np.array([node.coords[:2] for node in self.nodes])
        densities = np.array([material.rho for material in self.material])
        thickness, irule = self.thickness, self.irule

        mass = self.type.getMass(ncoords, densities, thickness, irule)

        return mass


    def assemble(self, glob, data, row, col, loc):

        globalIndex = np.array([node.ndof[[0, 1]] for node in self.nodes])
        globalIndex = globalIndex.reshape(globalIndex.size)

        dimension = len(globalIndex)
        length = dimension**2

        loc += length
        data[loc: loc+length] = glob.reshape(length)
        row[loc: loc+length] = np.repeat(globalIndex, dimension)
        col[loc: loc+length] = np.tile(globalIndex, dimension)

        return data, row, col, loc


    def deformed(self, scale=1, color='r', lnwidth=0.5):

        enodes = self.nodes+[self.nodes[0]]
        x = [node.coords[0]+node.dsp[0]*scale for node in enodes]
        y = [node.coords[1]+node.dsp[1]*scale for node in enodes]

        plt.plot(x, y, color, linewidth=lnwidth)

    # def plotLabel(self):

    #     x = np.sum([node.coords[0]+node.dsp[0]*0 for node in self.nodes])/4
    #     y = np.sum([node.coords[1]+node.dsp[1]*0 for node in self.nodes])/4

    #     plt.text(x, y, self.label)




class Load:

    def __init__(self, model):
        self.model = model
    
    def addForce(self, labels, dofs, functions):

        model = self.model
        dic = Node.dictionary

        labels = [labels] if not isinstance(labels, list) else labels
        dofs = [dofs] if not isinstance(dofs, list) else dofs

        for label in labels:
            node = model.nodes[label]
            for dof, function in zip(dofs, functions):
                if node.ndof[dic[dof]] in model.rdof.values():
                    continue
                else:
                    model.loads.append(function)
                    model.ldof[(label, dic[dof])] = int(node.ndof[dic[dof]])

        model.Sp = np.zeros((len(model.ndof), len(model.ldof)))
        model.Sp[list(model.ldof.values()), range(len(model.ldof))] = 1
        model.Sp = model.Sp[list(model.fdof.values())]


    def addDisplacement(self, labels, dofs, value):

        mesh = self.mesh
        dic = Node.dictionary

        if not isinstance(labels, list): labels = [labels]

        if not isinstance(dofs, list): dofs = [dofs]

        for label in labels:
            node = mesh.nodes[label]
            for dof in dofs:
                if node.ndof[dic[dof]] in mesh.rdof.values():
                    break
                else:
                    mesh.ldof[(label, dic[dof])] = int(node.ndof[dic[dof]])



class Constraint:
    
    def __init__(self, model):
        self.model = model
    
    def addFixation(self, labels, dofs):
        model = self.model
        dic = Node.dictionary

        labels = [labels] if not isinstance(labels, list) else labels
        dofs = [dofs] if not isinstance(dofs, list) else dofs

        for label in labels:
            node = model.nodes[label]

            for dof in dofs:
                if node.ndof[dic[dof]] in model.rdof.values():
                    continue
                else:
                    node.cdof[dic[dof]] = True
                    model.rdof[(label, dic[dof])] = int(node.ndof[dic[dof]])
                    model.fdof.pop((label, dic[dof]))

        model.Sp = model.Sp[list(model.fdof.values())]


    def addSpring(self, labels, dofs, values):

        labels = [labels] if not isinstance(labels, list) else labels
        dofs = [dofs] if not isinstance(dofs, list) else dofs

        dic = Node.dictionary

        for label in labels:
            node = self.model.nodes[label]

            for dof, value in zip(dofs, values):
                self.model.springs[0].append(label)
                self.model.springs[1].append(dic[dof])
                self.model.springs[2].append(int(node.ndof[dic[dof]]))
                self.model.springs[3].append(value)


    def addMass(self, labels, dofs, value):

        labels = [labels] if not isinstance(labels, list) else labels
        dofs = [dofs] if not isinstance(dofs, list) else dofs

        dic = Node.dictionary

        for label in labels:
            node = self.model.nodes[label]

            for dof in dofs:
                self.model.masses[0].append(label)
                self.model.masses[1].append(dic[dof])
                self.model.masses[2].append(int(node.ndof[dic[dof]]))
                self.model.masses[3].append(value)




class Model:
    
    def __init__(self, nodes=[], elements=[]):
        self.nodes = nodes
        self.elements = elements
        
        self.ndof = OrderedDict()
        self.rdof = OrderedDict()
        self.fdof = OrderedDict()
        self.ldof = OrderedDict()
        
        self.loads = []

        self.springs = [[], [], [], []]
        self.masses = [[], [], [], []]
    
        elementCounter = it.count(0)
        nodeCounter = it.count(0)
        dofCounter = it.count(0)
        
        for element in self.elements:
            element.label = next(elementCounter)

            for node in element.nodes:
                node.addLink(element.label)

        for node in self.nodes:
            node.label = next(nodeCounter)

            for dof in np.flatnonzero(node.adof):
                num = next(dofCounter)
                node.ndof[dof] = num
                self.ndof[(node.label, dof)] = num
                self.fdof[(node.label, dof)] = num

        self.Sp = np.zeros((len(self.fdof), len(self.ldof)))

        self.constraints = Constraint(self)


    def setDampingCoefficients(self, alpha, beta):

        """ Specify the proportional damping coefficients. """

        self.alpha = alpha
        self.beta = beta


    
class Plot(object):
    
    def __init__(self, mesh):
        self.mesh = mesh
        

    def undeformed2(self, split=False, elements=[]):

        elements = self.mesh.elements

        # x = np.zeros((len(self.mesh.ndof), 3))
        # y = np.zeros((len(self.mesh.ndof), 3))

        # create vector for plotting everything at once

        plt.figure()

        for element in elements:
            element.undeformed()

        plt.axis('equal')
        plt.show()



    def undeformed(self, split=False, elements=[]):
        if not elements:
            elements = self.mesh.elements
        if not split:
            fig = plt.figure('Undeformed View')
            axis = Axes3D(fig)
        else:
            axis = plt.gca()
        #axis.set_aspect('equal')
        #axis.auto_scale_xyz()

        # Do not iterate over elements but gather the data to be plotted in 
        # a single vector and plot them all together

        plt.ion()
        for element in elements:
            element.Undeformed(axis)

    def modes(self, modes):
        pass

                 
    def deformed(self, scale=1, overwrite=False):
        if not overwrite:
            fig = plt.figure('Deformed View')
            axis = Axes3D(fig)
        else:
            axis = plt.gca()
            
        for element in self.mesh.elements:
            element.Deformed(axis, scale)
            
    def animated(self, overwrite=False):
        if not(overwrite):
            fig = plt.figure('Animated View')
            axis = Axes3D(fig)
        else:
            axis = plt.gca()
        # To be extended
    
    def contours(self,overwrite=False):
        if not(overwrite):
            fig=plt.figure('Contour View')
            axis=Axes3D(fig)
        else:
            axis=plt.gca()
        # To be extended
        
    def elementLabels(self):
        axis = plt.gca()
        for element in self.mesh.elements:
            element.PlotId(axis)
        
    def nodeLabels(self):
        axis=plt.gca()
        for node in self.mesh.nodes:
            node.PlotId(axis)
                      
    def nodeMarks(self):
        fig=plt.figure('Contour View')
        axis=Axes3D(fig)
        #axis=plt.gca()
        for node in self.mesh.nodes:
            node.Mark(axis)




class Matrix(abc.ABC):

    @abc.abstractmethod
    def __init__(self, model):

        self.model = model
        m = len(self.model.ndof)
        self.full = sps.csr_matrix((int(m), int(m)), dtype=float)

        rng = int(5e3)
        length = (25**2)*(rng*3)
        end = len(self.model.elements)
        num = max(end//rng, 2)
        ind = np.linspace(0, end, num, dtype=int)

        for i in range(len(ind)-1):
            data = np.zeros(length, dtype=float)
            row = np.zeros(length, dtype=float)
            col = np.zeros(length, dtype=float)
            loc = 0

            for elm in self.model.elements[ind[i]:ind[i+1]]:
                glob = getattr(elm, self.method)()
                data, row, col, loc = elm.assemble(glob, data, row, col, loc)

            self.full += sps.csr_matrix((data, (row, col)), shape=(m, m))


        if isinstance(self, Stiffness):

            j, k = self.model.springs[2], self.model.springs[3]
            self.full += sps.csr_matrix((k, (j, j)), shape=(m, m))

        elif isinstance(self, Mass):

            j, k = self.model.masses[2], self.model.masses[3]
            self.full += sps.csr_matrix((k, (j, j)), shape=(m, m))


    def getPartitionFF(self):

        fdof = list(self.model.fdof.values())
        ff = self.full.tocsc()[:, fdof].tocsr()[fdof, :].tocsc()
        return ff


    def getPartitionFR(self):

        fdof = list(self.model.fdof.values())
        rdof = list(self.model.rdof.values())
        fr = self.full.tocsc()[:, rdof].tocsr()[fdof, :].tocsc()
        return fr


    def getPartitionRF(self):

        fdof = list(self.model.fdof.values())
        rdof = list(self.model.rdof.values())
        rf = self.full.tocsc()[:, fdof].tocsr()[rdof, :].tocsc()
        return rf


    def getPartitionRR(self):

        rdof = list(self.model.rdof.values())
        rr = self.full.tocsc()[:, rdof].tocsr()[rdof, :].tocsc()
        return rr
        
        
class Stiffness(Matrix):

    def __init__(self, model):
        self.method = 'getStiffness'
        super().__init__(model)


class Damping(Matrix):

    def __init__(self, model):
        self.method = 'getDamping'
        super().__init__(model)
        
        
class Mass(Matrix):
    
    def __init__(self, model):
        self.method = 'getMass'
        super().__init__(model)
