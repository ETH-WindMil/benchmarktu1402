import os
import quadrature
import quadrilaterals
import analysis
import model
import material

import numpy as np
import itertools as it


import matplotlib.pyplot as plt


def main(job):

    # { Read job object

    # settings = job.getSettings()

    # material = settings['material']
    # boundaries = settings['boundaries']
    # corrosion = settings['corrosion']
    # temperature = settings['temperature']

    jmaterial = np.array([
            [1.8e11, 0.3, 10],
            [1.8e11, 0.3, 25]])

    jthickness = 0.1
    jwastage = np.array([
            [0.1, 0.0],
            [0.1, 0.5]])

    jtemperature = np.array([
            [10, 0.0],
            [15, 0.5]])

    # }


    # { Define damaged areas

    # }


    #  Define Geometry

    length = 20                 # Dimension in x-axis

    height_start = 0.60         # Dimension in y-axis
    height_end = 0.60

    width_start = 0.1           # Dimension in z-axis
    width_end = 0.1

    nel_x = 200                 # Number of elements in x-axis
    nel_y = 6                   # Number of elements in y-axis

    el_size_x = length/nel_x    # Element size in x-direction
    el_size_y = length/nel_y    # Element size in y-direction

    E = 1.8e11
    n = 0.3
    density = 2000
    mat = material.LinearElastic(E, n, density)

    points_x = np.arange(0, length*(1+1/nel_x)-1e-10, length/nel_x)
    counter = it.count(0)

    points_y = []
    nodes = []
    indices = []

    # { Define nodes

    for i, x in enumerate(points_x):

        h = height_start-x/length*(height_start-height_end)
        points_y.append(np.arange(-h/2, h*(1/2+1/nel_y)-1e-10, h/nel_y))
        
        for y in points_y[i]:
            nodes.append(model.Node([x, y, 0]))
            nodes[-1].SetValue('adof', ['x', 'y'])
            label = next(counter)
            
            if x < length-1e-10 and y < h/2-1e-10:
                indices.append(label)

    # }
    

    # {Define elements

    elements = []

    etype = quadrilaterals.Quad4()
    irule = quadrature.Gauss.inQuadrilateral(rule=3).info

    for j in indices:

        #  Define element nodes

        enodes = [nodes[j], nodes[j+nel_y+1], nodes[j+nel_y+2], nodes[j+1]]

        # Coordinates of element center-point

        xc = np.sum([node.coords[0] for node in enodes])/len(enodes)
        yc = np.sum([node.coords[1] for node in enodes])/len(enodes)

        # Coordinates of element integration points

        xi = xc+irule[:, 0]*el_size_x
        yi = yc+irule[:, 1]*el_size_y

        #  Interpolate temperature at gauss points

        temperature = np.interp(xi, jtemperature[:, 1]*length, jtemperature[:, 0])

        #  Define material properties for each integration point

        materials = []
        E = np.interp(xi, jmaterial[:, 2], jmaterial[:, 0])
        n = np.interp(xi, jmaterial[:, 2], jmaterial[:, 1])

        for k in range(len(xi)):
            materials.append(material.LinearElastic(E[k], n[k], density))

        #  Interpolate thickness at gauss points

        wastage = np.interp(xi, jwastage[:, 1]*length, jwastage[:, 0])
        thickness = jthickness*(np.ones(len(xi))-wastage)
        thickness = np.ones(9)*0.5

        #  Define elements and modify damaged ones

        elements.append(model.Element(enodes, etype, materials, thickness, irule))


    #  Initialize model

    model1 = model.Model(nodes, elements)

    #  Apply boundary conditions

    kx1, ky1 = 1e15, 1e11
    kx2, ky2 = 1e15, 1e11
    kx3, ky3 = 1e15, 1e11

    for node in nodes:
        x, y = node.coords[0], node.coords[1]

        #  Left-hand side constraints

        if x == 0 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == el_size_x and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == el_size_x*2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == el_size_x*3 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        
        #  Mid-point constraints

        elif x == length/2-el_size_x*2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == length/2-el_size_x and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == length/2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == length/2+el_size_x and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == length/2+el_size_x*2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        
        #  Right-hand side constraints

        elif x == length-el_size_x*3 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == length-el_size_x*2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == length-el_size_x and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])
        elif x == length and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx1, ky1])

    # }


    #  Run analysis

    if janalysis == 'Modal':

        modal = analysis.Modal(model1)
        modal.setNumberOfEigenvalues(10)
        modal.submit()

    else:

        pass

    print(modal.frequencies)


    #  Plot mode shapes

    plt.figure(1)

    for mode_no in range(4):
        for item, mode in zip(list(model1.ndof2.keys()), modal.modes[:, mode_no]):
            nodes[item[0]].dsp[item[1]] = mode

        n = str(mode_no+1)
        
        plt.subplot('41'+n)
        plt.title('Mode '+n+' - '+str(modal.frequencies[mode_no])[:5]+' Hz', fontsize=11)
        
        plt.xlim(0, length)
        
        plt.xticks([], [])
        plt.yticks([], [])

        for i in range(len(elements)):
            elements[i].deformed(scale=1e2)
            
    plt.tight_layout()
    plt.show()



    # { Export results

    # }


if __name__ == '__main__':
    main(0)
