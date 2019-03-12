import os
import sys

import quadrature
import quadrilaterals
import analysis
import model
import material

import numpy as np
import itertools as it


import matplotlib.pyplot as plt


def main(job):

    #  Read job object

    jmodel = 'Damaged state 6'
    jthickness = 0.1
    jdamage = 0     # Percentage of stiffness reduction in the damaged area

    jmaterial = np.array([
            [1.8e11, 0.3, 10]]) # E, n, temperature

    jboundary1 = np.array([
            [1e15, 1e11, 20]]) # kx, ky, temperature

    jboundary2 = np.array([
            [1e15, 1e11, 20]]) # kx, ky, temperature

    jboundary3 = np.array([
            [1e15, 1e11, 20]]) # kx, ky, temperature

    jwastage = np.array([
            [0.0, 0.5]]) # Wastage, x / length

    jtemperature = np.array([
            [10, 0.5]]) # temperature, x / length

    # janalysis = 'Time history'
    janalysis = 'Modal'
    jsettings = {'modes': 5, 'normalization': 'Mass'}

    loadCase = '1'              # 1, 2, 3
    alpha, beta = 1e-1, 1e-1    # Rayleigh damping coefficients
    period = 10                 # Simulation period
    increment = 0.1             # Time increment
    jname = 'Job-1'             # job name


    #  Define element labels of damaged areas

    if jmodel == 'Healthy state':
        damagedElements = []
    elif jmodel == 'Damaged state 1':
        damagedElements = [49*6]
    elif jmodel == 'Damaged state 2':
        damagedElements = [49*6, 49*6+1]
    elif jmodel == 'Damaged state 3':
        damagedElements = [49*6, 49*6+1, 49*6+2]
    elif jmodel == 'Damaged state 4':
        damagedElements = [100*6+5]
    elif jmodel == 'Damaged state 5':
        damagedElements = [100*6+5, 100*6+4]
    elif jmodel == 'Damaged state 6':
        damagedElements = [100*6+5, 100*6+4, 100*6+3]


    #  Define Geometry

    length = 20                 # Dimension in x-axis
    density = 2000              # Material density

    height_start = 0.60         # Dimension in y-axis
    height_end = height_start

    width_start = 0.1           # Dimension in z-axis
    width_end = width_start

    nel_x = 200                 # Number of elements in x-axis
    nel_y = 6                   # Number of elements in y-axis

    el_size_x = length/nel_x    # Element size in x-direction
    el_size_y = height_start/nel_y    # Element size in y-direction

    points_x = np.arange(0, length*(1+1/nel_x)-1e-10, length/nel_x)
    counter = it.count(0)

    points_y = []
    nodes = []
    indices = []


    #  Define model nodes

    for i, x in enumerate(points_x):

        h = height_start-x/length*(height_start-height_end)
        points_y.append(np.arange(-h/2, h*(1/2+1/nel_y)-1e-10, h/nel_y))
        
        for y in points_y[i]:
            nodes.append(model.Node([x, y, 0]))
            nodes[-1].SetValue('adof', ['x', 'y'])
            label = next(counter)
            
            if x < length-1e-10 and y < h/2-1e-10:
                indices.append(label)    


    #  Define model elements

    elements = []
    etype = quadrilaterals.Quad4()
    irule = quadrature.Gauss.inQuadrilateral(rule=3).info

    for i, j in enumerate(indices):

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

        #  Calculate stiffnes reduction

        reduction = jdamage if i in damagedElements else 1

        #  Define material properties for each integration point

        E = np.interp(xi, jmaterial[:, 2], jmaterial[:, 0])*reduction
        n = np.interp(xi, jmaterial[:, 2], jmaterial[:, 1])
        materials = []

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

    # Interpolate temperature at boundary locations

    temp1 = np.interp(0, jtemperature[:, 1]*length, jtemperature[:, 0])
    temp2 = np.interp(length/2, jtemperature[:, 1]*length, jtemperature[:, 0])
    temp3 = np.interp(length, jtemperature[:, 1]*length, jtemperature[:, 0])

    # Interpolate boundary values at temperature value

    kx1 = np.interp(temp1, jboundary1[:, 2], jboundary1[:, 0])
    ky1 = np.interp(temp1, jboundary1[:, 2], jboundary1[:, 1])

    kx2 = np.interp(temp2, jboundary2[:, 2], jboundary2[:, 0])
    ky2 = np.interp(temp2, jboundary2[:, 2], jboundary2[:, 1])

    kx3 = np.interp(temp3, jboundary3[:, 2], jboundary3[:, 0])
    ky3 = np.interp(temp3, jboundary3[:, 2], jboundary3[:, 1])

    #  Apply boundary conditions

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
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx2, ky2])
        elif x == length/2-el_size_x and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx2, ky2])
        elif x == length/2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx2, ky2])
        elif x == length/2+el_size_x and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx2, ky2])
        elif x == length/2+el_size_x*2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx2, ky2])

        #  Right-hand side constraints

        elif x == length-el_size_x*3 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx3, ky3])
        elif x == length-el_size_x*2 and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx3, ky3])
        elif x == length-el_size_x and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx3, ky3])
        elif x == length and y == -height_start/2:
            model1.constraints.addSpring(node.label, ['x', 'y'], [kx3, ky3])


    #  Extract degrees of freedom for output locations

    columns = np.arange(5, nel_x+5, 10)[np.newaxis].T*(nel_y+1)
    rows = np.tile(np.array([1, 3, 5]), len(columns)).reshape((len(columns), 3))
    rows = (columns+rows).reshape((rows.size,))
    odofs = np.sort(np.hstack((rows*2, rows*2+1)))
    ocoords = np.array([(nodes[j].coords[0], nodes[j].coords[1]) for j in rows])

    # Save labels and coordinates of measurement nodes

    output = np.vstack((rows, ocoords.T)).T
    labels, frmt = 'label  x  y', ['%d', '%10.5f', '%10.5f']
    np.savetxt('Output_nodes.dat', output, fmt=frmt, header=labels)

    # Save labels of measurement degrees of freedom

    xlabels = np.array([str(item)+'x' for item in rows])
    ylabels = np.array([str(item)+'y' for item in rows])
    labels = np.vstack((xlabels, ylabels)).T.flatten()
    labels = '   '.join(label for label in labels)

    #  Run analysis

    if janalysis == 'Modal':

        # Submit modal analysis

        modal = analysis.Modal(model1)
        modal.setNumberOfEigenvalues(jsettings['modes'])
        modal.setNormalizationMethod(jsettings['normalization'])
        modal.submit()

        # Extract mode shapes at output locations

        frequencies = modal.frequencies
        modes = modal.modes[odofs, :]

        #  Save results

        sys.stdout.write('Writting output files ...\n')
        np.savetxt(jname+'_frequencies.dat', frequencies)
        np.savetxt(jname+'_modes.dat', modes, header=labels)

    elif janalysis == 'Time history':

        model1.setDampingCoefficients(alpha, beta)

        # Select load case

        if loadCase == '1':
            nlabels = np.arange(nel_y+1, (nel_x+1)*(nel_y+1) ,nel_y+1)
            loadCase = np.loadtxt('Load_case_1.dat', skiprows=1)
            velocity, load = loadCase[0], loadCase[1]

            for j, nlabel in enumerate(nlabels):

                t1 = nodes[nlabels[j-1]].coords[0]/velocity
                t2 = nodes[nlabels[j]].coords[0]/velocity

                if j == 0:
                    t1 = t2-1e-5

                if j == nlabels.shape[0]-1:
                    t3 = t2+1e-5
                else:
                    t3 = nodes[nlabels[j+1]].coords[0]/velocity

                time = np.array([t1, t2, t3])
                force = np.array([0, 1e3*load, 0])
                amplitude = [np.array([time, force])]

                model.Load(model1).addForce(nodes[nlabel].label, 'y', amplitude)

        elif loadCase == '2':
            nlabel = 63*(nel_y+1)-1

            loadCase = np.loadtxt('Load_case_2.dat', skiprows=1)
            time, force = loadCase[:, 0], loadCase[:, 1]
            amplitude = [np.array([time, force])]

            model.Load(model1).addForce(nodes[nlabel].label, 'y', amplitude)

        elif loadCase == '3':
            nlabel = 139*(nel_y+1)-1

            loadCase = np.loadtxt('Load_case_3.dat', skiprows=1)
            time, force = loadCase[:, 0], loadCase[:, 1]
            amplitude = [np.array([time, force])]

            model.Load(model1).addForce(nodes[nlabel].label, 'y', amplitude)

        # Define dynamic analysis

        dynamics = analysis.Dynamics(model1)
        dynamics.setTimePeriod(period)
        dynamics.setIncrementSize(period)
        dynamics.submit()

        # Extract time response at output degrees of freedom

        displacements = dynamics.modes[odofs, :].dot(dynamics.displacement).T
        accelerations = dynamics.modes[odofs, :].dot(dynamics.acceleration).T

        # Save results

        sys.stdout.write('Writting output files ...\n')

        np.savetxt(jname+'_displacements.dat', displacements, header=labels)
        np.savetxt(jname+'_accelerations.dat', accelerations, header=labels)

    elif janalysis == 'Static':

        nlabel = 63*(nel_y+1)-1

        loadCase = np.loadtxt('Load_case_2.dat', skiprows=1)
        time, force = loadCase[0, 0], loadCase[1, 1]
        amplitude = [np.array([time, force])]
        model.Load(model1).addForce(nodes[nlabel].label, 'y', amplitude)

        # Define static analysis

        static = analysis.Static(model1)
        static.submit()

        # Extract displacements at output degrees of freedom

        displacements = static.displacement[odofs][np.newaxis]

        # Save results

        sys.stdout.write('Writting output files ...\n')
        np.savetxt(jname+'_displacements.dat', displacements, header=labels)


    nlabel = np.arange(nel_y, (nel_x+1)*(nel_y+1) ,nel_y+1)



    #  Plot mode shapes

    # plt.figure(4)

    # for mode_no in range(1):
    #     # for item, mode in zip(list(model1.ndof.keys()), modal.modes[:, mode_no]):
    #     #     nodes[item[0]].dsp[item[1]] = mode

    #     for item, mode in zip(list(model1.ndof.keys()), static.displacement):
    #         nodes[item[0]].dsp[item[1]] = mode

    #     n = str(mode_no+1)
        
    #     # plt.subplot('41'+n)
    #     # plt.title('Mode '+n+' - '+str(modal.frequencies[mode_no])[:5]+' Hz', fontsize=11)
    #     plt.title('Mode '+n+' - '+'sjdfnsfdns Hz', fontsize=11)
    #     plt.axis('equal')

    #     plt.xlim(0, length)

    #     plt.xticks([], [])
    #     plt.yticks([], [])

    #     for i in range(len(elements)):

    #         if elements[i].label in damagedElements:
    #             clr = 'k'
    #             width = 1
    #         else:
    #             clr = 'r'
    #             width = 0.5

    #         elements[i].deformed(scale=1e6, color=clr, lnwidth=width)

    #         # elements[i].plotLabel()

    #     for lab in rows:
    #         plt.plot(nodes[lab].coords[0], nodes[lab].coords[1], 'o')

    #     for lab in [63*7-1, 139*7-1]:
    #         plt.plot(nodes[lab].coords[0], nodes[lab].coords[1], 'o')

    #     for lab in nlabel:
    #         plt.plot(nodes[lab].coords[0], nodes[lab].coords[1], 'o')


    # plt.tight_layout()
    # plt.show()



    # # Plot modal response

    # plt.figure()
    # plt.plot(dynamics.displacement[0, :])

    # plt.tight_layout()
    # plt.show()



if __name__ == '__main__':
    main(None)
