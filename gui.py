import os
import sys
import copy
import webbrowser
import numpy as np
import itertools as it
import tkinter as tk
import matplotlib.pyplot as plt

from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from PIL import Image, ImageTk

import main


__author__ = 'Konstantinos Tatsis'
__email__ = 'konnos.tatsis@gmail.com'


class Main(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Benchmark problem - COST Action TU1402')
        self.root.protocol("WM_DELETE_WINDOW", self.callbackClose)
        self.root.resizable(False, False)
        # self.root.bind("<Destroy>", destroy)

        self.frame = tk.Frame(self.root)
        self.frame.grid()

        # instantiate other objects

        self.scenario = Scenario(self)
        self.model = Model(self, row=0, column=1)
        self.settings = Settings(self, row=1, column=1)
        self.analysis = Analysis(self, row=1, column=2)

        # self.root.mainloop()
        self.job = Job()


    def createScenario(self):
        
        self.scenario.createJobsList()
        self.scenario.createMessageBox()
        self.scenario.createButtons()


    def createModel(self):

        self.model.createModelPlot()


    def createSettings(self):
        
        self.settings.createModelConfiguration()


    def createAnalysis(self):

        """ Create "Analysis" widgets. """

        self.analysis.createAnalysisType()
        self.analysis.createModalSettings()
        self.analysis.createTimeHistorySettings()
        self.analysis.createJobWidgets()


    def switchWidgets(self, state):

        """ Switch state of widgets. """

        self.scenario.switchWidgets(state)
        self.settings.switchWidgets(state)
        self.analysis.switchWidgets(state)


    def run(self):
        self.root.mainloop()


    def saveJob(self):
        
        # Set job name
        self.job.setName(self.analysis.jobWidgets['job'].get())

        print('Name:', self.job.name, type(self.job.name))

        # Set job model
        selection = self.settings.modelConfiguration[0].curselection()[0]
        # self.job.setModel(self.settings.modelConfiguration[0].get(selection))
        self.job.setModel(selection)

        print('Model:', self.job.model, type(self.job.model))

        # Set job thickness
        thickness = float(self.settings.modelConfiguration[2].get())
        self.job.setThickness(thickness)

        print('Thickness:', self.job.thickness, type(self.job.thickness))

        # Set job damage
        damage = float(self.settings.modelConfiguration[4].get())
        self.job.setDamage(damage)

        print('Damage:', self.job.damage, type(self.job.damage))

        # Job material, boundary conditions, corrosion and temperature
        # are already set once the corresponding widgets are closed.

        # Set type of analysis
        analysis = self.analysis.analysisTypeVariables['Analysis'].get()
        self.job.setAnalysis(analysis)

        print(self.job.analysis, type(self.job.analysis))

        # Set settings for modal analysis
        modes = int(self.analysis.modalSettingsVariables['Modes'].get())
        index = self.analysis.modalSettingsVariables['Normalization'].get()
        normalization = 'Mass' if index == '1' else 'Displacement'
        self.job.setModalSettings(modes, normalization)

        print(self.job.modalSettings)

        # Set settings for dynamic analysis
        alpha = float(self.analysis.historySettings[2].get())
        beta = float(self.analysis.historySettings[4].get())
        period = float(self.analysis.historySettings[6].get())
        increment = float(self.analysis.historySettings[8].get())
        lcase = int(self.analysis.historySettings[10].get()[-1])-1
        self.job.setTimeHistorySettings(alpha, beta, period, increment, lcase)

        print(self.job.timeHistorySettings)


    def retrieveJob(self, job):

        self.job = job
        
        # Retrieve job name
        self.analysis.jobWidgets['job'].delete(0, tk.END)
        self.analysis.jobWidgets['job'].insert(tk.END, job.getName())

        # Retrieve job model
        self.settings.modelConfiguration[0].select_set(job.getModel())

        # Retrieve model figure
        self.model.updateModelPlot((job.getModel(), ))
        self.settings.modelConfiguration[0].select_clear(0, tk.END)
        self.settings.modelConfiguration[0].select_set(job.getModel())

        # Retrieve job thickness
        self.settings.modelConfiguration[2].delete(0, tk.END)
        self.settings.modelConfiguration[2].insert(tk.END, job.getThickness())

        # Retrieve job damage
        self.settings.modelConfiguration[4].delete(0, tk.END)
        self.settings.modelConfiguration[4].insert(tk.END, job.getDamage())

        # Job material, boundary conditions, corrosion and temperature values
        # are retrieved through the current job, as soon as the corresponding
        # widgets are created.

        # Retrieve type of analysis
        index = 0 if job.getAnalysis() == 'Modal' else 1
        self.analysis.analysisType[index].select()

        if index == 0:
            self.analysis.switchModalSettings('normal')
            self.analysis.switchTimeHistorySettings('disable')
        else:
            self.analysis.switchModalSettings('disable')
            self.analysis.switchTimeHistorySettings('normal')

        # Retrieve settings for modal analysis
        modalSettings = job.getModalSettings()
        self.analysis.modalSettings[1].delete(0, tk.END)
        self.analysis.modalSettings[1].insert(tk.END, modalSettings['Modes'])

        index = 0 if modalSettings['Normalization'] == 'Mass' else 1
        self.analysis.modalSettings[3+index].select()

        # Retrieve settings for dynamic analysis
        historySettings = job.getTimeHistorySettings()
        self.analysis.historySettings[2].delete(0, tk.END)
        self.analysis.historySettings[2].insert(tk.END, historySettings['Alpha'])

        self.analysis.historySettings[4].delete(0, tk.END)
        self.analysis.historySettings[4].insert(tk.END, historySettings['Beta'])

        self.analysis.historySettings[6].delete(0, tk.END)
        self.analysis.historySettings[6].insert(tk.END, historySettings['Period'])

        self.analysis.historySettings[8].delete(0, tk.END)
        self.analysis.historySettings[8].insert(tk.END, historySettings['Increment'])

        self.analysis.historySettings[-1].current(historySettings['Load case'])




    def callbackHelp(self):
        
        link = r"https://github.com/ETH-WindMil/benchmarktu1402/blob/master/IOMAC_2019.pdf"
        webbrowser.open_new(link)


    def callbackClose(self):

        # destroy model plot
        self.model.destroyModelPlot()

        try:
            self.root.destroy()
        except:
            pass



class Job:


    def __init__(self, name=None):

        self.name = name
        self.model = 0
        self.thickness = 0.1
        self.damage = 10

        values = {(0, 0): '210000000000', (0, 1):'0.3', (0, 2): '25'}
        self.material = {'values': values, 'temperature': False}

        values = {(0, 0): '200000000000', (0, 1): '200000000000', (0, 2): '25'}
        self.boundaries = {'values1': values, 'values2':values, 
                'values3': values, 'temperature': False, 'identical': False}

        values = {(0, 0): '10', (0, 1):'0.5'}
        self.corrosion = {'values': values, 'spatial': False}

        values = {(0, 0): '10', (0, 1):'0.5'}
        self.temperature = {'values': values, 'spatial': False}

        self.analysis = 'Modal'

        self.modalSettings = {'Modes': 5, 'Normalization': 'Mass'} 

        self.timeHistorySettings = {'Alpha': 0.005, 'Beta': 0.005, 
                'Period': 10, 'Increment': 0.1, 'Load case': 0}


    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name


    def setModel(self, model):
        self.model = model

    def getModel(self):
        return self.model


    def setThickness(self, thickness):
        self.thickness = thickness

    def getThickness(self):
        return self.thickness


    def setDamage(self, damage):
        self.damage = damage

    def getDamage(self):
        return self.damage


    def setMaterial(self, values, temperature):

        self.material['values'] = values
        self.material['temperature'] = temperature

    def getMaterial(self):
        return self.material


    def setBoundaries(self, values1, values2, values3, temperature, identical):

        self.boundaries['values1'] = values1
        self.boundaries['values2'] = values2
        self.boundaries['values3'] = values3
        self.boundaries['temperature'] = temperature
        self.boundaries['identical'] = identical

    def getBoundaries(self):
        return self.boundaries


    def setCorrosion(self, values, spatial):
        self.corrosion['values'] = values
        self.corrosion['spatial'] = spatial

    def getCorrosion(self):
        return self.corrosion


    def setTemperature(self, values, spatial):
        self.temperature['values'] = values
        self.temperature['spatial'] = spatial

    def getTemperature(self):
        return self.temperature


    def setAnalysis(self, analysis):
        self.analysis = analysis

    def getAnalysis(self):
        return self.analysis


    def setModalSettings(self, modes, normalization):
        self.modalSettings['Modes'] = modes
        self.modalSettings['Normalization'] = normalization

    def getModalSettings(self):
        return self.modalSettings


    def setTimeHistorySettings(self, alpha, beta, period, increment, lcase):
        self.timeHistorySettings['Alpha'] = alpha
        self.timeHistorySettings['Beta'] = beta
        self.timeHistorySettings['Period'] = period
        self.timeHistorySettings['Increment'] = increment
        self.timeHistorySettings['Load case'] = lcase

    def getTimeHistorySettings(self):
        return self.timeHistorySettings




class Scenario:


    def __init__(self, main, row=0, column=0, width=35):
        self.main = main
        self.width = width

        self.row = row
        self.column = column

        self.jobs = {}


    def createJobsList(self):

        """
        """

        frame = tk.LabelFrame(self.main.root, text='List of jobs',
                width=self.width, height=15)
        frame.grid(row=self.row, column=self.column, padx=(15, 10), pady=(10, 5), 
                sticky=tk.N+tk.E+tk.S+tk.W)

        listBox = tk.Listbox(frame, width=self.width+10, height=7)
        listBox.activate(0) # Select the first entry
        # listBox.insert(0, 'Case 1')
        # listBox.insert(1, 'Case 2')
        listBox.configure(exportselection=False)
        # listBox.select_set(0)
        listBox.grid(row=0, column=self.column, columnspan=3,
                padx=(10, 0), pady=(10, 5), sticky=tk.N+tk.E+tk.S+tk.W)
        self.widgets = {'listbox': listBox}

        scrollbar = tk.Scrollbar(frame, command=listBox.yview, width=10)
        scrollbar.grid(row=0, column=3, sticky=tk.N+tk.W+tk.S+tk.E, 
                padx=(0, 10), pady=(10, 5))
        listBox['yscrollcommand'] = scrollbar.set


        # entry = tk.Entry(frame)
        # entry['width'] = self.width

        # entry.insert(0, 'Click on an item in the listbox')
        # entry.grid(row=2, column=0, columnspan=3, padx=10, pady=10)


        edit = tk.Button(frame, text='Edit', width=11, state='disable',
                command=self.callbackEdit)
        edit.grid(row=1, column=self.column, padx=(10, 5), pady=(5, 2),
                sticky=tk.N+tk.S+tk.W)
        self.widgets['edit'] = edit

        delete = tk.Button(frame, text='Delete', width=11, state='disable',
                command=self.callbackDelete)
        delete.grid(row=1, column=self.column+1, padx=(5, 5), pady=(5, 2),
                sticky=tk.N+tk.S+tk.W)
        self.widgets['delete'] = delete

        deleteall = tk.Button(frame, text='Delete All', width=11, state='disable',
                command=lambda : self.callbackDelete('all'))
        deleteall.grid(row=1, column=self.column+2, padx=(5, 10), pady=(5, 2),
                sticky=tk.N+tk.S+tk.W, columnspan=2)
        self.widgets['deleteall'] = deleteall

        submit = tk.Button(frame, text='Run jobs', width=self.width,
                state='disable', command=self.callbackRun)
        submit.grid(row=2, column=self.column, padx=10, pady=(3, 10), columnspan=4,
                sticky=tk.N+tk.E+tk.W)
        self.widgets['submit'] = submit


    def callbackEdit(self):

        selection = self.widgets['listbox'].curselection()
        name = self.widgets['listbox'].get(selection)
        self.main.retrieveJob(self.main.scenario.jobs[name])
        


    def callbackDelete(self, items=None):

        selection = self.widgets['listbox'].curselection()

        if selection == () and items is None:
            pass
        elif items is None:
            selection = self.widgets['listbox'].curselection()
            job = self.widgets['listbox'].get(selection)
            self.printMessage('Job "{}" deleted.\n'.format(job))
            self.widgets['listbox'].delete(selection)
        # elif selection == () and items != None:
        #     pass
        else:
            if self.widgets['listbox'].get(0, tk.END) != ():
                self.printMessage('All jobs deleted.\n')

            self.widgets['listbox'].delete(0, tk.END)

        self.switchButtons()


    def callbackRun(self):

        print('Submit callback function to be written.')

        # Run each job separately and print message

        for item in self.main.scenario.jobs.keys():

            pass

            # Call main.main(self.scenario.jobs[job])

            # print(self.main.scenario.jobs[item].material)
            # print(self.main.scenario.jobs[item].boundaries)
            # print(self.main.scenario.jobs[item].corrosion)
            # print(self.main.scenario.jobs[item].temperature)




    def switchButtons(self):

        if self.widgets['listbox'].get(0, tk.END) == ():
            state = 'disable'
        else:
            state = 'normal'

        self.widgets['edit'].configure(state=state)
        self.widgets['delete'].configure(state=state)
        self.widgets['deleteall'].configure(state=state)
        self.widgets['submit'].configure(state=state)



    def createMessageBox(self):

        """ Create Message box widget. """

        frame = tk.LabelFrame(self.main.root, text='Messages',
                width=self.width-20, height=22)
        frame.grid(row=self.row+1, column=self.column, padx=(15, 10), pady=(5, 5), 
                rowspan=2, sticky=tk.N+tk.E+tk.S+tk.W)

        text = tk.Text(frame, width=self.width-2, spacing3=2.2, height=17, 
                exportselection=0, state='disabled')
        text.grid(row=0, column=self.column, padx=(10, 0), pady=10,
                sticky=tk.N+tk.E+tk.S+tk.W)

        scrollbar = tk.Scrollbar(frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.N+tk.E+tk.W+tk.S, 
                padx=(0, 10), pady=10)
        text['yscrollcommand'] = scrollbar.set

        self.widgets['message'] = text
        self.widgets['scrollbar'] = scrollbar


    def printMessage(self, message):

        """ Print message in Message box widget. """

        self.widgets['message'].configure(state='normal')
        self.widgets['message'].insert(tk.END, message)
        self.widgets['message'].configure(state='disabled')
        self.widgets['message'].see(tk.END)



    def createButtons(self):

        """
        Create "Submit", "Close" and "Help" buttons at the very bottom of the
        left column.
        """

        # submit = tk.Button(self.main.root, text='Submit', width=self.width,
        #         command=self.main.callbackSubmit)
        # submit.grid(row=self.row+3, column=self.column, padx=10, pady=(5, 2), 
        #         sticky=tk.N+tk.E+tk.W)

        hlp = tk.Button(self.main.root, text='Help', width=self.width, 
                command=self.main.callbackHelp)
                # command=self.main.model.updateModelPlot)
        hlp.grid(row=self.row+4, column=self.column, padx=(15, 10), pady=(8, 2),# pady=(18, 2),# pady=(32, 5), 
                sticky=tk.N+tk.E+tk.W)

        close = tk.Button(self.main.root, text='Close', width=self.width,
                command=self.main.callbackClose)
        close.grid(row=self.row+5, column=self.column, padx=(15, 10), pady=(2, 20),# pady=(59, 5), 
                sticky=tk.N+tk.E+tk.W)
        
        self.widgets['hlp'] = hlp
        self.widgets['close'] = close


    def switchWidgets(self, state):

        """ Switch state of widgets. """

        for key in self.widgets.keys():
            if key != 'scrollbar':
                self.widgets[key].configure(state=state)
    

class Model:

    def __init__(self, main, row, column, width=10):

        self.main = main
        self.width = width

        self.row = row
        self.column = column
        self.plots = {}


    def createModelPlot(self):

        frame = tk.LabelFrame(self.main.root, text='Model preview', 
                width=self.width, height=15)
        frame.grid(row=self.row, column=self.column, columnspan=2, 
                padx=(5, 10), pady=(10, 5), sticky=tk.N+tk.W+tk.E+tk.S)

        files = {0: './pictures/healthy.jpg',
                 1: './pictures/damage_1.jpg',
                 2: './pictures/damage_2.jpg',
                 3: './pictures/damage_3.jpg',
                 4: './pictures/damage_4.jpg',
                 5: './pictures/damage_5.jpg',
                 6: './pictures/damage_6.jpg'}

        label = tk.Label(frame)
        label.img = ImageTk.PhotoImage(file=files[self.main.job.model], master=frame)
        label.config(image=label.img)
        label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.S+tk.N)

        self.frame = frame
        self.label = label



    def updateModelPlot(self, case):

        if case == (0,):
            file = './pictures/healthy.jpg'
        elif case == (1,):
            file = './pictures/damage_1.jpg'
        elif case == (2,):
            file = './pictures/damage_2.jpg'
        elif case == (3,):
            file = './pictures/damage_3.jpg'
        elif case == (4,):
            file = './pictures/damage_4.jpg'
        elif case == (5,):
            file = './pictures/damage_5.jpg'
        elif case == (6,):
            file = './pictures/damage_6.jpg'

        self.label.img = ImageTk.PhotoImage(file=file, master=self.frame)
        self.label.config(image=self.label.img)


    def destroyModelPlot(self):

        """ Destroy model plot. """

        # plt.close(self.widgets[0])
        pass





class Material:

    """ Material properties widget."""

    def __init__(self, parent):

        self.parent = parent
        w = self.parent.root.winfo_x()
        h = self.parent.root.winfo_y()

        self.root = tk.Toplevel()
        self.root.title('Material properties')
        self.root.protocol("WM_DELETE_WINDOW", self.callbackCancel)
        self.root.resizable(False, False)
        # self.root.geometry("%dx%d+%d+%d" % (w, h, 300+10, 500+20))

        self.createTable()
        self.createButtons()

        # Switch all parent widgets to 'disable' state
        self.parent.switchWidgets('disable')
        self.root.mainloop()


    def openWidget(self):
        self.root.mainloop()


    def createTable(self):

        labelFrame = tk.LabelFrame(self.root, text='Material properties')
        labelFrame.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky=tk.N+tk.W)

        temp = tk.IntVar()
        check = tk.Checkbutton(labelFrame, text=' Temperature-dependent data', 
                variable=temp, onvalue=1, offvalue=0, width=30, 
                command=self.callbackTemperatureDependency, anchor=tk.W)
        check.grid(row=0, column=0, columnspan=3, padx=(5, 0), pady=(10, 0), 
                sticky=tk.N+tk.W+tk.E)

        label = tk.Message(labelFrame, text="Young's Modulus", width=50)
        label.grid(row=1, column=0, padx=(5, 0), pady=(5, 0), sticky=tk.N+tk.W)

        label = tk.Message(labelFrame, text="Poisson's Ratio", width=50)
        label.grid(row=1, column=1, padx=0, pady=(5, 0), sticky=tk.N+tk.W)

        label = tk.Message(labelFrame, text='Temp', width=50)
        label.grid(row=1, column=2, padx=0, pady=(5, 0), sticky=tk.N+tk.W)

        rows = []
        padsy = {0: (2, 0), 14:(0, 10)}
        padsx = {0: (10, 0), 2:(0, 10)}
        wds = {0:12, 1:11, 2:6}

        for i in range(15):
            py = padsy[i] if i in (0, 14) else (0, 0)

            columns = []
            for j in range(3):
                px = padsx[j] if j in (0, 2) else (0, 0)

                entry = tk.Entry(labelFrame, width=wds[j], justify=tk.RIGHT, bd=1)
                entry.grid(row=i+2, column=j, padx=px, pady=py, sticky=tk.N+tk.W+tk.E)

                columns.append(entry)
            rows.append(columns)

        # Set checkbox status, according to job definition
        if self.parent.job.material['temperature']:
            check.select()

        # Insert table values, from job definition
        for (i, j) in self.parent.job.material['values'].keys():
            rows[i][j].insert(tk.END, self.parent.job.material['values'][(i, j)])

        self.widgets = {'cells':rows, 'temp':temp}
        self.callbackTemperatureDependency()


    def callbackTemperatureDependency(self):

        """ Switch state of table cells related to temperature dependency. """

        state = 'normal' if self.widgets['temp'].get() == 1 else 'disable'

        for j, row in enumerate(self.widgets['cells']):
            for k, column in enumerate(row):
                if (j, k) not in [(0, 0), (0, 1)]:
                    self.widgets['cells'][j][k].configure(state=state)


    def createButtons(self):

        """ Create "Ok" and "Cancel" buttons. """

        ok = tk.Button(self.root, text='Ok', width=5, command=self.callbackOk)
        ok.grid(row=1, column=0, pady=5)

        cancel = tk.Button(self.root, text='Cancel', width=5, 
                command=self.callbackCancel)
        cancel.grid(row=1, column=1, pady=5)


    def callbackOk(self):

        """ Callback function of "Ok" button. """

        # Check input variables

        # Store non-zero table data into a dictionary
        values = {}
        for i, columns in enumerate(self.widgets['cells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    values[(i, j)] = value

        # Save material data into the current job
        self.parent.job.setMaterial(values, self.widgets['temp'].get())

        # Switch parent widgets back to normal state
        self.parent.switchWidgets('normal')
        self.root.destroy()

    def callbackCancel(self):

        """ Callback function of "Cancel" button. """

        # Switch parent widgets back to normal state
        self.parent.switchWidgets('normal')
        self.root.destroy()



class BoundaryConditions:

    """ Buundary conditions widget. """

    def __init__(self, parent):
        
        self.root = tk.Toplevel()
        self.root.title('Boundary conditions')
        self.root.protocol("WM_DELETE_WINDOW", self.callbackCancel)
        self.root.resizable(False, False)
        self.parent = parent

        self.createTable()
        self.createButtons()

        self.parent.switchWidgets('disable')
        # self.parent.root.iconify()
        # self.parent.configure(state='disable')
        self.root.mainloop()


    def createTable(self):

        labelFrame = tk.LabelFrame(self.root, text='Boundary conditions')
        labelFrame.grid(row=0, column=0, padx=10, pady=5, columnspan=2, 
                sticky=tk.N+tk.W)

        identicalBCs = tk.IntVar()
        check1 = tk.Checkbutton(labelFrame, text=' Identical BCs',
                variable=identicalBCs, onvalue=1, offvalue=0, width=30, 
                command=self.callbackIdenticalBCs, anchor=tk.W)
        check1.grid(row=0, column=0, columnspan=3, padx=(5, 0), pady=(10, 0), 
                sticky=tk.N+tk.W)

        temp = tk.IntVar()
        check2 = tk.Checkbutton(labelFrame, text=' Temperature-dependent data', 
                variable=temp, onvalue=1, offvalue=0, width=30, 
                command=self.callbackTemperatureDependency, anchor=tk.W)
        check2.grid(row=1, column=0, columnspan=3, padx=(5, 0), pady=(10, 0), 
                sticky=tk.N+tk.W)
        self.widgets = {'identicalBCs':identicalBCs, 'temp':temp}

        notebook = ttk.Notebook(labelFrame)
        ltab = ttk.Frame(notebook)      # Left tab
        mtab = ttk.Frame(notebook)      # Mid tab
        rtab = ttk.Frame(notebook)      # Right tab
        notebook.add(ltab, text='Left')
        notebook.add(mtab, text='Mid')
        notebook.add(rtab, text='Right')
        notebook.grid(row=2, column=0, padx=10, pady=10, sticky=tk.N+tk.W)

        def createTabWidgets(tab):

            label = tk.Message(tab, text="Kx", width=50)
            label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky=tk.N+tk.W)

            label = tk.Message(tab, text="Ky", width=50)
            label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky=tk.N+tk.W)

            label = tk.Message(tab, text="Temp", width=50)
            label.grid(row=0, column=2, padx=5, pady=(5, 0), sticky=tk.N+tk.W)

            rows = []
            padsy = {0: (5, 0), 14:(0, 10)}
            padsx = {0: (10, 0), 2:(0, 10)}
            wds = {0:12, 1:12, 2:6}

            for i in range(15):
                py = padsy[i] if i in (0, 14) else (0, 0)

                columns = []
                for j in range(3):
                    px = padsx[j] if j in (0, 2) else (0, 0)

                    entry = tk.Entry(tab, width=wds[j], justify=tk.RIGHT, bd=1)
                    entry.grid(row=i+2, column=j, padx=px, pady=py, sticky=tk.N+tk.W)

                    columns.append(entry)
                rows.append(columns)

            return rows

        self.widgets['lcells'] = createTabWidgets(ltab)
        self.widgets['mcells'] = createTabWidgets(mtab)
        self.widgets['rcells'] = createTabWidgets(rtab)
        self.widgets['notebook'] = notebook

        # Set temperature checkbox status, based on job definition
        if self.parent.job.boundaries['identical']:
            check1.select()

        # Set identical BCs checkbox status, based on job definition
        if self.parent.job.boundaries['temperature']:
            check2.select()

        # Insert table values to all three boundaries, based on job definition
        for (i, j) in self.parent.job.boundaries['values1'].keys():
            value = self.parent.job.boundaries['values1'][(i, j)]
            self.widgets['lcells'][i][j].insert(tk.END, value)

        for (i, j) in self.parent.job.boundaries['values2'].keys():
            value = self.parent.job.boundaries['values2'][(i, j)]
            self.widgets['mcells'][i][j].insert(tk.END, value)

        for (i, j) in self.parent.job.boundaries['values3'].keys():
            value = self.parent.job.boundaries['values3'][(i, j)]
            self.widgets['rcells'][i][j].insert(tk.END, value)

        self.callbackIdenticalBCs()
        self.callbackTemperatureDependency()


    def callbackIdenticalBCs(self):

        """ Activate/deactivate identical boundary conditions. """

        tabids = self.widgets['notebook'].tabs()

        if self.widgets['identicalBCs'].get() == 1:
            self.widgets['notebook'].select(tabids[0])
            self.widgets['notebook'].tab(tabids[0], text='Left-mid-right')
            self.widgets['notebook'].hide(tabids[1])
            self.widgets['notebook'].hide(tabids[2])
        else:
            self.widgets['notebook'].tab(tabids[0], text='Left')
            self.widgets['notebook'].add(tabids[1])
            self.widgets['notebook'].add(tabids[2])


    def callbackTemperatureDependency(self):

        """ Switch state of table cells related to temperature dependency. """

        state = 'normal' if self.widgets['temp'].get() == 1 else 'disable'

        for key in ['lcells', 'mcells', 'rcells']:
            for j, row in enumerate(self.widgets[key]):
                for k, column in enumerate(row):
                    if (j, k) not in [(0, 0), (0, 1)]:
                        self.widgets[key][j][k].configure(state=state)


    def createButtons(self):

        """ Create "Ok" and "Cancel"  buttons. """

        ok = tk.Button(self.root, text='Ok', width=5, command=self.callbackOk)
        ok.grid(row=1, column=0, pady=5)

        cancel = tk.Button(self.root, text='Cancel', width=5, 
                command=self.callbackCancel)
        cancel.grid(row=1, column=1, pady=5)


    def callbackOk(self):

        """ Callback function of "Ok" button. """

        # Check input variables


        # Store non-zero table data of all three supports into a dictionary
        values1 = {}
        for i, columns in enumerate(self.widgets['lcells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    values1[(i, j)] = value

        values2 = {}
        for i, columns in enumerate(self.widgets['mcells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    values2[(i, j)] = value

        values3 = {}
        for i, columns in enumerate(self.widgets['rcells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    values3[(i, j)] = value

        # Save material data into the current job
        temp = self.widgets['temp'].get()
        identical = self.widgets['identicalBCs'].get()
        # print('1', temp, identical)
        self.parent.job.setBoundaries(values1, values2, values3, temp, identical)
        # print('2', self.parent.job.boundaries['temperature'], self.parent.job.boundaries['identical'])

        # Switch parent widgets back to normal state
        self.parent.switchWidgets('normal')
        self.root.destroy()


    def callbackCancel(self):

        """ Callback function of "Cancel" button. """

        self.parent.switchWidgets('normal')
        self.root.destroy()



class Corrosion:

    def __init__(self, parent):

        self.parent = parent
        self.root = tk.Toplevel()
        self.root.title('Corrosion')
        self.root.protocol("WM_DELETE_WINDOW", self.callbackCancel)
        self.root.resizable(False, False)

        self.createTable()
        self.createButtons()

        self.parent.switchWidgets('disable')
        self.root.mainloop()


    def createTable(self):

        labelFrame = tk.LabelFrame(self.root, text='Corrosion wastage')
        labelFrame.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky=tk.N+tk.W)

        space = tk.IntVar()
        check = tk.Checkbutton(labelFrame, text=' Spatial-dependency', 
                variable=space, onvalue=1, offvalue=0, width=5, 
                command=self.callbackSpatialDependency, anchor=tk.W)
        check.grid(row=0, column=0, columnspan=3, padx=(5, 0), pady=(10, 0), 
                sticky=tk.N+tk.W+tk.E)

        label = tk.Label(labelFrame, text="Wastage [%]", anchor=tk.W)
        label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky=tk.N+tk.W)

        label = tk.Message(labelFrame, text="x / L [-]", width=80)
        label.grid(row=1, column=1, padx=0, pady=(5, 0), sticky=tk.N+tk.W)

        # label = tk.Message(labelFrame, text='Temp', width=60)
        # label.grid(row=1, column=2, padx=0, pady=(5, 0), sticky=tk.N+tk.W)

        rows = []
        padsy = {0: (5, 0), 14:(0, 10)}
        padsx = {0: (10, 0), 1:(0, 10)}
        wds = {0:12, 1:9}

        for i in range(15):
            py = padsy[i] if i in (0, 14) else (0, 0)

            columns = []
            for j in range(2):
                px = padsx[j] if j in (0, 1) else (0, 0)

                entry = tk.Entry(labelFrame, width=wds[j], justify=tk.RIGHT, bd=1)
                entry.grid(row=i+2, column=j, padx=px, pady=py, sticky=tk.N+tk.W+tk.E)

                columns.append(entry)
            rows.append(columns)

        
        # Set checkbox status, according to job definition
        if self.parent.job.corrosion['spatial']:
            check.select()

        # Insert table values, from job definition
        for (i, j) in self.parent.job.corrosion['values'].keys():
            rows[i][j].insert(tk.END, self.parent.job.corrosion['values'][(i, j)])

        # Save widgets in class attributes
        self.widgets = {'cells':rows, 'space':space}
        self.callbackSpatialDependency()


    def callbackSpatialDependency(self):

        """ Switch state of table cells related to spatial-dependency. """

        state = 'normal' if self.widgets['space'].get() == 1 else 'disable'

        for j, row in enumerate(self.widgets['cells']):
            for k, column in enumerate(row):
                if (j, k) not in [(0, 0)]:
                    self.widgets['cells'][j][k].configure(state=state)



    def createButtons(self):

        """ Create "Ok" and "Cancel" buttons. """

        ok = tk.Button(self.root, text='Ok', width=5, command=self.callbackOk)
        ok.grid(row=1, column=0, pady=5)

        cancel = tk.Button(self.root, text='Cancel', width=5, 
                command=self.callbackCancel)
        cancel.grid(row=1, column=1, pady=5)


    def callbackOk(self):

        """ Callback function of "Ok" button. """

        # Check input variables

        # Store non-zero table data into a dictionary
        values = {}
        for i, columns in enumerate(self.widgets['cells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    values[(i, j)] = value

        # Save material data into the current job
        self.parent.job.setCorrosion(values, self.widgets['space'].get())

        # Switch parent widgets back to normal state
        self.parent.switchWidgets('normal')
        self.root.destroy()


    def callbackCancel(self):

        """ Callback function of "Cancel" button. """

        self.parent.switchWidgets('normal')
        self.root.destroy()



class Temperature:

    def __init__(self, parent):

        self.parent = parent
        w = self.parent.root.winfo_x()
        h = self.parent.root.winfo_y()

        self.root = tk.Toplevel()
        self.root.title('Temperature')
        self.root.protocol("WM_DELETE_WINDOW", self.callbackCancel)
        self.root.resizable(False, False)

        self.root.geometry("%dx%d+%d+%d" % (185, 435, w+20, h+20))

        self.createTable()
        self.createButtons()

        self.parent.switchWidgets('disable')
        self.root.mainloop()


    def createTable(self):

        labelFrame = tk.LabelFrame(self.root, text='Temperature field')
        labelFrame.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky=tk.N+tk.W)

        space = tk.IntVar()
        check = tk.Checkbutton(labelFrame, text=' Spatial-dependency',
                variable=space, onvalue=1, offvalue=0, width=5, 
                command=self.callbackSpatialDependency, anchor=tk.W)
        check.grid(row=0, column=0, columnspan=3, padx=(5, 0), pady=(10, 0), 
                sticky=tk.N+tk.W+tk.E)

        label = tk.Label(labelFrame, text="Temperature", anchor=tk.W)
        label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky=tk.N+tk.W)

        label = tk.Message(labelFrame, text="x / L [-]", width=80)
        label.grid(row=1, column=1, padx=0, pady=(5, 0), sticky=tk.N+tk.W)

        # label = tk.Message(labelFrame, text='Temp', width=60)
        # label.grid(row=1, column=2, padx=0, pady=(5, 0), sticky=tk.N+tk.W)

        rows = []
        padsy = {0: (5, 0), 14:(0, 10)}
        padsx = {0: (10, 0), 1:(0, 10)}
        wds = {0:12, 1:9}

        for i in range(15):
            py = padsy[i] if i in (0, 14) else (0, 0)

            columns = []
            for j in range(2):
                px = padsx[j] if j in (0, 1) else (0, 0)

                entry = tk.Entry(labelFrame, width=wds[j], justify=tk.RIGHT, bd=1)
                entry.grid(row=i+2, column=j, padx=px, pady=py, sticky=tk.N+tk.W+tk.E)

                columns.append(entry)
            rows.append(columns)

        # Set checkbox status, according to job definition
        if self.parent.job.temperature['spatial']:
            check.select()

        # Insert table values, from job definition
        for (i, j) in self.parent.job.temperature['values'].keys():
            rows[i][j].insert(tk.END, self.parent.job.temperature['values'][(i, j)])

        # Save widgets in class attributes
        self.widgets = {'cells':rows, 'space':space}
        self.callbackSpatialDependency()


    def callbackSpatialDependency(self):

        """ Switch state of table cells related to spatial-dependency. """

        state = 'normal' if self.widgets['space'].get() == 1 else 'disable'

        for j, row in enumerate(self.widgets['cells']):
            for k, column in enumerate(row):
                if (j, k) not in [(0, 0)]:
                    self.widgets['cells'][j][k].configure(state=state)


    def createButtons(self):

        """ Create "Ok" and "Cancel" buttons. """

        ok = tk.Button(self.root, text='Ok', width=5, command=self.callbackOk)
        ok.grid(row=1, column=0, pady=5)

        cancel = tk.Button(self.root, text='Cancel', width=5, 
                command=self.callbackCancel)
        cancel.grid(row=1, column=1, pady=5)


    def callbackOk(self):

        """ Callback function of "Ok" button. """

        # Check input variables

        # Store non-zero table data into a dictionary
        values = {}
        for i, columns in enumerate(self.widgets['cells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    values[(i, j)] = value

        # Save material data into the current job
        self.parent.job.setTemperature(values, self.widgets['space'].get())

        # Switch parent widgets back to normal state
        self.parent.switchWidgets('normal')
        self.root.destroy()


    def callbackCancel(self):

        """ Callback function of "Cancel" button. """

        self.parent.switchWidgets('normal')
        self.root.destroy()




class Settings:

    def __init__(self, main, row=0, column=3, width=35):
        self.main = main
        self.row = row
        self.column = column
        self.width = width



    def createModelConfiguration(self):

        """ Create model configuration widget. """

        self.modelConfiguration = []
        frame = tk.LabelFrame(self.main.root, 
                text='1. Model configuration', width=self.width-10)
        frame.grid(row=self.row, column=self.column, padx=(5, 5), 
                pady=(5, 2), rowspan=2, sticky=tk.N+tk.W+tk.E+tk.S)

        self.var2 = tk.StringVar()
        listBox = tk.Listbox(frame, height=6, width=self.width+3) # -6 
        listBox.bind('<<ListboxSelect>>', self.callbackListbox)
        listBox.activate (0)
        listBox.insert(0, 'Healthy state')
        listBox.insert(1, 'Damaged state 1')
        listBox.insert(2, 'Damaged state 2')
        listBox.insert(3, 'Damaged state 3')
        listBox.insert(4, 'Damaged state 4')
        listBox.insert(5, 'Damaged state 5')
        listBox.insert(6, 'Damaged state 6')
        listBox['selectmode'] = tk.SINGLE
        listBox.configure(exportselection=False)
        listBox.select_set(self.main.job.model)
        listBox.grid(row=0, column=0, padx=10, pady=(10, 10), columnspan=2,
                sticky=tk.N+tk.W+tk.E+tk.S)
        self.modelConfiguration.append(listBox)

        # scrollbar = tk.Scrollbar(listBox, command=listBox.yview, width=10)
        # scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E, 
        #         padx=(0, 10), pady=(10, 5))
        # listBox['yscrollcommand'] = scrollbar.set

        # Label and entry for thickness

        label = tk.Label(frame, text='Thickness [m]', anchor=tk.W)
        label.grid(row=1, column=0, padx=(7, 0), pady=(5, 0), 
                sticky=tk.W+tk.N+tk.E)
        self.modelConfiguration.append(label)

        thickness = tk.Entry(frame, width=12)
        thickness.insert(tk.END, self.main.job.thickness)
        thickness.grid(row=2, column=0, padx=(10, 10), pady=(0, 10), sticky=tk.W+tk.N+tk.E)
        self.modelConfiguration.append(thickness)

        # Label and entry for damage

        label = tk.Label(frame, text='Damage [%]', state='disable', anchor=tk.W)
        label.grid(row=1, column=1, padx=(7, 0), pady=(5, 0), sticky=tk.W+tk.N+tk.E)
        self.modelConfiguration.append(label)

        damage = tk.Entry(frame, width=12)
        damage.insert(tk.END, self.main.job.damage)
        damage.configure(state='disable')
        damage.grid(row=2, column=1, padx=(10, 10), pady=(0, 10), sticky=tk.W+tk.N+tk.E)
        self.modelConfiguration.append(damage)


        # Material, boundary, corrosion and temperature buttons

        #  self.material = Material(self.main)
        material = tk.Button(frame, text='Material properties',
                command=lambda : Material(self.main))
        material.grid(row=3, column=0, padx=10, pady=5, columnspan=2, sticky=tk.N+tk.W+tk.E)
        self.modelConfiguration.append(material)

        boundary = tk.Button(frame, text='Boundary conditions',
                command=lambda : BoundaryConditions(self.main))
        boundary.grid(row=4, column=0, padx=10, pady=5, columnspan=2, sticky=tk.N+tk.W+tk.E)
        self.modelConfiguration.append(boundary)

        corrosion  =tk.Button(frame, text='Corrosion wastage',
                command=lambda : Corrosion(self.main))
        corrosion.grid(row=5, column=0, padx=10, pady=5, columnspan=2, sticky=tk.N+tk.W+tk.E)
        self.modelConfiguration.append(corrosion)

        temperature = tk.Button(frame, text='Environmental temperature',
                command=lambda : Temperature(self.main), width=self.width-15)
        temperature.grid(row=6, column=0, padx=10, pady=(5, 10), columnspan=2, sticky=tk.N+tk.W+tk.E)
        self.modelConfiguration.append(temperature)


    def callbackListbox(self, event):

        selection = self.modelConfiguration[0].curselection()
        self.main.model.updateModelPlot(selection)
        
        state = 'disable' if selection == (0,) else 'normal'
        self.modelConfiguration[4].configure(state=state)
        self.modelConfiguration[3].configure(state=state)


    def switchWidgets(self, state):

        """ Switch state of "Settings" widgets. """

        for widget in self.modelConfiguration:
            widget.configure(state=state)

        if state == 'normal':
            self.callbackListbox(None)




class Analysis:

    def __init__(self, main, row=0, column=4, width=35):
        self.main = main
        self.row = row
        self.column = column
        self.width = width


    def createAnalysisType(self):

        """ Create "Type of analysis" widget. """

        self.analysisType = []
        self.analysisTypeVariables = {'Analysis': tk.StringVar()}

        labelFrame = tk.LabelFrame(self.main.root, 
                text='2. Type of analysis')#, width=self.width)
        labelFrame.grid(row=3, column=self.column-1, padx=(5, 5),
                rowspan=3, pady=(0, 20), sticky=tk.N+tk.W+tk.E+tk.S)

        modal = tk.Radiobutton(labelFrame, text=' Modal analysis')
        modal['width'] = self.width-20
        modal['anchor'] = tk.W
        modal['variable'] = self.analysisTypeVariables['Analysis']
        modal['value'] = 'Modal'
        modal['state'] = tk.ACTIVE
        modal.select()
        modal['command'] = self.callbackAnalysisType
        modal.grid(row=0, column=0, padx=20, pady=(5, 0), sticky=tk.N+tk.W)
        self.analysisType.append(modal)

        history = tk.Radiobutton(labelFrame, text=' Time history')
        history['width'] = self.width-22
        history['anchor'] = tk.W
        history['variable'] = self.analysisTypeVariables['Analysis']
        history['value'] = 'Time history'
        history['state'] = tk.ACTIVE
        # history.deselect()
        history['command'] = self.callbackAnalysisType
        history.grid(row=1, column=0, padx=20, pady=(0, 5), sticky=tk.N+tk.W)
        self.analysisType.append(history)

        if self.main.job.analysis == 'Time history':
            history.select()



    def switchAnalysisType(self, state):

        """ Switch state of "Analysis type" widget. """

        for widget in self.analysisType:
            widget.configure(state=state)
        


    def callbackAnalysisType(self):

        if self.analysisTypeVariables['Analysis'].get() == 'Modal':
            self.switchModalSettings(state='normal')
            self.switchTimeHistorySettings(state='disable')
        else:
            self.switchModalSettings(state='disable')
            self.switchTimeHistorySettings(state='normal')



    def createModalSettings(self):

        """ Create "Modal settings" widget. """

        self.modalSettings = []
        self.modalSettingsVariables = {
                'Modes': tk.StringVar(), 'Normalization': tk.StringVar()}

        self.msettingsvars = {'var1': tk.StringVar(), 'var2': tk.StringVar()}
        frame = tk.LabelFrame(self.main.root)
        frame['text'] = '2a. Modal analysis settings'
        frame['width'] = self.width-20
        # frame['height'] = 300
        frame.grid(row=self.row, column=self.column, padx=(5, 10), 
            pady=(5, 0), sticky=tk.N+tk.E+tk.S+tk.W)
            # pady=(90, 10), sticky=tk.W+tk.N+tk.E)

        label = tk.Label(frame, text='Number of modes:')
        label.grid(row=0, column=0, padx=(10, 0), pady=5, sticky=tk.W)
        self.modalSettings.append(label)

        entry = tk.Entry(frame, width=6)
        entry['textvariable'] = self.modalSettingsVariables['Modes']
        entry.insert(tk.END, self.main.job.modalSettings['Modes'])
        entry.grid(row=0, column=1, padx=(0, 5), sticky=tk.W)
        self.modalSettings.append(entry)


        label = tk.Label(frame, text='Normalize eigenvectors by:', anchor=tk.W)
        label.grid(row=2, column=0, padx=10, pady=5, columnspan=2, sticky=tk.W)
        self.modalSettings.append(label)

        mass = tk.Radiobutton(frame, text=' Mass')#, width=self.width-15)
        mass['anchor'] = tk.W
        mass['value'] = 1
        mass['variable'] = self.modalSettingsVariables['Normalization']
        mass['state'] = tk.ACTIVE
        mass.select()
        mass.grid(row=3, column=0, padx=20, pady=(0, 0), columnspan=2, sticky=tk.N+tk.W)
        self.modalSettings.append(mass)

        disp = tk.Radiobutton(frame, text=' Displacement')
        disp.deselect()
        # disp['width'] = self.width-15
        disp['anchor'] = tk.W
        disp['variable'] = self.modalSettingsVariables['Normalization']
        disp['value'] = 2
        disp.grid(row=4, column=0, padx=20, pady=(0, 5), columnspan=2, sticky=tk.N+tk.W)
        self.modalSettings.append(disp)

        # Adjust radio button selection according to the job definition

        if self.main.job.modalSettings['Normalization'] == 'Displacement':
            disp.select()

        # Adjust modal analysis widgets according to the job definition

        if self.main.job.analysis == 'Time history':
            self.switchModalSettings('disable')



    def switchModalSettings(self, state):

        """ Switch state of "Modal settings" widget. """

        for item in self.modalSettings:
            item.configure(state=state)



    def createTimeHistorySettings(self):

        """ Create "Time history settings" widget. """

        frame = tk.LabelFrame(self.main.root, text='2b. Time history settings',
                width=self.width-20)
        frame.grid(row=self.row+1, column=self.column,
                padx=(5, 10), pady=(0, 2), sticky=tk.N+tk.E+tk.W+tk.S)
                # padx=(5, 10), pady=(129, 10), sticky=tk.W+tk.N+tk.E)
                # padx=(5, 10), pady=(215, 10), sticky=tk.W+tk.N+tk.E)

        label = tk.Label(frame, text='Damping')
        label.grid(row=0, column=0, padx=(7, 10), pady=2, sticky=tk.W+tk.N)

        self.hsettingsvars = {
                'var1': tk.StringVar(), 
                'var2': tk.StringVar(),
                'var3': tk.StringVar(),
                'var4': tk.StringVar(),
                'var5': tk.StringVar()}

        self.historySettings = [label]

        label = tk.Label(frame, text='Alpha', anchor=tk.W)
        label.grid(row=1, column=0, padx=(7, 10), pady=(0, 1), sticky=tk.W+tk.N)
        self.historySettings.append(label)

        alpha = tk.Entry(frame, width=12, textvariable=self.hsettingsvars['var1'])
        alpha.insert(tk.END, self.main.job.timeHistorySettings['Alpha'])
        alpha.grid(row=2, column=0, padx=10, pady=(0, 2), sticky=tk.W+tk.N)
        self.historySettings.append(alpha)

        label = tk.Label(frame, text='Beta', anchor=tk.W)
        label.grid(row=1, column=1, padx=(7, 10), pady=(0, 1), sticky=tk.W+tk.N)
        self.historySettings.append(label)

        beta = tk.Entry(frame, width=12, textvariable=self.hsettingsvars['var2'])
        beta.insert(tk.END, self.main.job.timeHistorySettings['Alpha'])
        beta.grid(row=2, column=1, padx=10, pady=(0, 2), sticky=tk.W+tk.N)
        self.historySettings.append(beta)

        label = tk.Label(frame, text='Time period', anchor=tk.W)
        label.grid(row=3, column=0, padx=(7, 10), pady=(3, 2), sticky=tk.W+tk.N)
        self.historySettings.append(label)

        period = tk.Entry(frame, width=12, textvariable=self.hsettingsvars['var3'])
        period.insert(tk.END, self.main.job.timeHistorySettings['Period'])
        period.grid(row=4, column=0, padx=(10, 12), pady=(0, 2), sticky=tk.W+tk.N)
        self.historySettings.append(period)

        label = tk.Label(frame, text='Incerement', anchor=tk.W)
        label.grid(row=3, column=1, padx=(7, 10), pady=(3, 2), sticky=tk.W+tk.N)
        self.historySettings.append(label)

        increment = tk.Entry(frame, width=12, textvariable=self.hsettingsvars['var4'])
        increment.insert(tk.END, self.main.job.timeHistorySettings['Increment'])
        increment.grid(row=4, column=1, padx=10, pady=(0, 2), sticky=tk.W+tk.N)        
        self.historySettings.append(increment)

        label = tk.Label(frame, text='Load case', anchor=tk.W)
        label.grid(row=5, column=0, padx=10, pady=(3, 2), sticky=tk.W+tk.N)
        self.historySettings.append(label)


        case = ttk.Combobox(frame, values=['Load case 1', 'Load case 2', 
                'Load case 3'], state='readonly')
        case.current(self.main.job.timeHistorySettings['Load case'])
        case.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 10), 
                sticky=tk.W+tk.N+tk.E)
        self.historySettings.append(case)

        # Adjust modal analysis widgets according to the job definition

        if self.main.job.analysis == 'Modal':
            self.switchTimeHistorySettings('disable')


    def switchTimeHistorySettings(self, state):

        """ Switch state of time history settings. """

        for item in self.historySettings:
            item.configure(state=state)

        if state == 'normal':
            self.historySettings[-1].configure(state='readonly')



    def createJobWidgets(self):

        frame = tk.LabelFrame(self.main.root, text='3. Job name')
        frame.grid(row=self.row+2, column=self.column, padx=(5, 10), 
                pady=(0, 20), rowspan=3, sticky=tk.W+tk.N+tk.E+tk.S)

        # label = tk.Label(frame, text='Job name', anchor=tk.W)
        # label.grid(row=0, column=0, padx=10, pady=(5, 1),
        #         sticky=tk.W+tk.N+tk.E)

        var2 = tk.StringVar()
        job = tk.Entry(frame, width=16, textvariable=var2)
        job.insert(tk.END, 'Job-1')
        job.grid(row=1, column=0, padx=10, pady=(19, 5), 
                sticky=tk.W+tk.N+tk.E)

        save = tk.Button(frame, text='Save', width=7, height=1,
                command=self.callbackSave)
        save.grid(row=1, column=1, rowspan=2, padx=(5, 10), pady=(15, 3),
                sticky=tk.N+tk.E+tk.S+tk.W)

        # self.jobWidgets = [label, job, save]
        self.jobWidgets = {'job':job, 'save':save}


    def callbackSave(self):

        # 1. Check if all parameters are filled-in
        # 2. Check if parameters are correctly defined

        listbox = self.main.scenario.widgets['listbox']
        jobs = listbox.get(0, tk.END)
        job = self.jobWidgets['job'].get()

        print(job, type(job))

        # Check if file name contains any invalid characters

        specials = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', 
                ',', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']',
                '^', '{', '|', '}', '~']

        for special in specials:
            if special in job:
                special = ' '.join(specials)
                message = 'The job name contains invalid characters.\n\n'
                message += 'The following characters are not allowed: {}'
                message = message.format(special)
                messagebox.showwarning('Warning', message)
                return

        # Check if job name already exists

        if job in jobs:
            message = 'Job name already exists!'
            messagebox.showwarning('Warning', message)
            return

        listbox.insert(len(jobs), job)
        message = 'Job "{}" saved.\n'.format(job)
        self.main.scenario.printMessage(message)

        # Save job settings to the current job instance

        # self.main.job.setName(job)
        self.main.saveJob()

        # Save job to the list of jobs

        self.main.scenario.jobs[job] = copy.deepcopy(self.main.job)


        self.main.scenario.widgets['listbox'].see(tk.END)
        self.main.scenario.switchButtons()


    def switchJobWidgets(self, state):

        """ Switch state of time history settings. """

        for key in self.jobWidgets.keys():
            self.jobWidgets[key].configure(state=state)


    def switchWidgets(self, state):

        """ Switch state of "Analysis" widgets. """

        self.switchAnalysisType(state=state)
        self.switchModalSettings(state=state)
        self.switchTimeHistorySettings(state=state)
        self.switchJobWidgets(state=state)

        if state == 'normal':
            self.callbackAnalysisType()






if __name__ == '__main__':
    main = Main()
    main.createScenario()
    main.createModel()
    main.createAnalysis()
    main.createSettings()

    main.run()