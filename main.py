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

    # settings = job.getSettings()

    # material = settings['temperature']
    # boundaries = settigns['boundaries']
    # corrosion = settings['corrosion']
    # temperature = settings['temperature']

    # }

    ###   Define Geometry

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

    elm = quadrilaterals.Quad4()
    irule = quadrature.Gauss.inQuadrilateral(rule=3).info

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


        # { Define elements and modify damaged ones

        elements.append(model.Element(nodesEl, elm, materials, thickness, irule))

        # }

    # }

    mesh = model.Model(nodes, elements)

    for node in nodes:
        x, y = node.coords[0], node.coords[1]
        # Left-hand side constraints
        if x == 0 and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == el_size_x and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == el_size_x*2 and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        # Mid-point constraints
        elif x == length/2-el_size_x*2 and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == length/2-el_size_x and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == length/2 and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == length/2+el_size_x and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == length/2+el_size_x*2 and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        # Right-hand side constraints
        elif x == length-el_size_x*2 and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == length-el_size_x and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])
        elif x == length and y == -height_start/2:
            model.Constraint(mesh).addSpring(node.label, ['x', 'y'], [1e9, 1e9])


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
