import os
import quadrature
# import membrane
import quadrilaterals
import analysis
import model
import material

import numpy as np
import itertools as it


import matplotlib.pyplot as plt


def main(job):

    # { Read job object

    # }

    ###   Define Geometry

    length = 20           # along x-axis

    height_start = 0.60   # along y-axis
    height_end = 0.60

    width_start = 0.1     # along z-axis
    width_end = 0.1

    nel_x = 200           # Number of elements in x-axis
    nel_y = 6             # Number of elements in y-axis


    E = 1.8e11
    n = 0.3
    density = 2000
    mat = material.LinearElastic(E, n, density)

    points_x = np.arange(0, length*(1+1/nel_x)-1e-10, length/nel_x)
    counter = it.count(0)

    points_y = []
    nodes = []
    indices = []


    for i, x in enumerate(points_x):

        h = height_start-x/length*(height_start-height_end)
        points_y.append(np.arange(-h/2, h*(1/2+1/nel_y)-1e-10, h/nel_y))
        
        for y in points_y[i]:
            nodes.append(model.Node([x, y, 0]))
            nodes[-1].SetValue('adof', ['x', 'y'])
            label = next(counter)
            
            if x < length-1e-10 and y < h/2-1e-10:
                indices.append(label)

            
    elements = []

    elm = quadrilaterals.Quad4()
    quadr = quadrature.Gauss.inQuadrilateral(rule=3).info

    for index in indices:
        nodesEl = [nodes[index],
                   nodes[index+nel_y+1],
                   nodes[index+nel_y+2],
                   nodes[index+1]]
        xc = (nodes[index].coords[0]+
              nodes[index+nel_y+1].coords[0]+
              nodes[index+nel_y+2].coords[0]+
              nodes[index+1].coords[0])/4
    #    th = np.interp(xc, points, widths)
    #    th = np.interp(xc, [0, 27], [width_start, width_end])

        thickness = np.ones(9)*0.1
        materials = [mat]*9

        # { Interpolate temperature at gauss points

        # }


        # { Interpolate thickness at gauss points

        # }

        elements.append(model.Element(nodesEl, elm, materials, thickness, quadr))



    # { Modify damaged elements

    # }


    mesh = model.Mesh(nodes, elements)

    for node in nodes:
        if node.coords[0] == 0:
            model.Constraint(mesh).Nodal(node.label, ['x', 'y'])
        elif node.coords[0] == length:
            model.Constraint(mesh).Nodal(node.label, ['x', 'y'])
        elif node.coords[0] == length/2 and node.coords[1] == -height_start/2:
            model.Constraint(mesh).Nodal(node.label, ['x', 'y'])


    modal = analysis.Modal(mesh)
    modal.setNumberOfEigenvalues(10)
    modal.submit()

    print(modal.frequencies)


    # { Plot mode shapes

    plt.figure(1)

    for mode_no in range(4):
        for item, mode in zip(list(mesh.ndof2.keys()), modal.modes[:, mode_no]):
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

    # }


    # { Run analysis

    # }


    # { Export results

    # }


if __name__ == '__main__':
    main(0)
