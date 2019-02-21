import sys
import copy
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

        # Instantiate the GUI widgets

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
        
        self.material = {(0, 0): '210000000000', (0, 1):'0.3', (0, 2): '25'}
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




    def callbackHelp(self):
        pass


    def callbackClose(self):

        # destroy model plot
        self.model.destroyModelPlot()

        try:
            self.root.destroy()
        except:
            pass



class Job:

    """ Class for defining and interfacing with Job properties. """

    def __init__(self):
        values = {(0, 0): '210000000000', (0, 1):'0.3', (0, 2): '25'}
        self.material = {'values': values, 'temperature': False}

        values = {(0, 0): '200000000000', (0, 1): '200000000000', (0, 2): '25'}
        self.boundaries = {'left': values, 'mid':values, 
                'right': values, 'temperature': False, 'identical': False}

        values = {(0, 0): '10', (0, 1):'0.5'}
        self.corrosion = {'values': values, 'spatial': False}

        values = {(0, 0): '10', (0, 1):'0.5'}
        self.temperature = {'values': values, 'spatial': False}
        self.jobs = {}


    def setMaterial(self, values, temperature):

        self.material['values'] = values
        self.material['temperature'] = temperature


    def setBoundaries(self, left, mid, right, temperature, identical):

        self.boundaries['left'] = left
        self.boundaries['mid'] = mid
        self.boundaries['right'] = right
        self.boundaries['temperature'] = temperature
        self.boundaries['identical'] = identical


    def setCorrosion(self, values, spatial):

        self.corrosion['values'] = values
        self.corrosion['temperature'] = temperature


    def setTemperature(self, values, spatial):

        self.temperature['values'] = values
        self.temperature['spatial'] = spatial



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

        print('Callback function to be written.')


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

        self.plots = {}
        fig = plt.figure(figsize=(6, 2))
        ax = fig.add_subplot(111)
        ax.get_yaxis().set_ticks([])
        reference, = ax.plot(np.arange(100), np.random.rand(100))

        plt.tight_layout()
        plt.xlim([0, 100])
        plt.ylim([0, 1])
        plt.axis('off')
        
        self.plots['Reference'] = reference

        # self.image = Image.open("Model.jpeg")
        # self.model = ImageTk.PhotoImage(self.image)
        # (iwidth, iheight) = self.image.size
        # # model = tk.PhotoImage(file = 'Model.png')

        # canvas = tk.Canvas(frame, width=440, height=180, bg='white')
        # canvas.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.S+tk.N)
        # canvas.create_image(0, 0, image=self.model, anchor=tk.N)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvasw = canvas.get_tk_widget()
        canvasw['width'] = 440
        canvasw['height'] = 180
        canvasw.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.S+tk.N)

        self.widgets = [fig]
        self.canvas = canvas


    def updateModelPlot(self, case):

        x = np.arange(100)

        if case == (0,):
            self.plots['Reference'].set_data(x, np.random.rand(100))
            self.plots['Reference'].set_color('blue')
            self.plots['Reference'].set_linestyle(':')
        elif case == (1,):
            self.plots['Reference'].set_data(x, np.random.rand(100))
            self.plots['Reference'].set_color('red')
            self.plots['Reference'].set_linestyle(':')
        elif case == (2,):
            self.plots['Reference'].set_data(x, np.random.rand(100))
            self.plots['Reference'].set_color('green')
            self.plots['Reference'].set_linestyle(':')
        elif case == (3,):
            self.plots['Reference'].set_data(x, np.random.rand(100))
            self.plots['Reference'].set_color('yellow')
            self.plots['Reference'].set_linestyle(':')
        elif case == (4,):
            self.plots['Reference'].set_data(x, np.random.rand(100))
            self.plots['Reference'].set_color('black')
            self.plots['Reference'].set_linestyle(':')
        elif case == (5,):
            self.plots['Reference'].set_data(x, np.random.rand(100))
            self.plots['Reference'].set_color('orange')
            self.plots['Reference'].set_linestyle(':')
        elif case == (6,):
            self.plots['Reference'].set_data(x, np.random.rand(100))
            self.plots['Reference'].set_color('pink')
            self.plots['Reference'].set_linestyle(':')

        self.canvas.draw()


    def destroyModelPlot(self):

        """ Destroy model plot. """

        plt.close(self.widgets[0])





class Material:

    """ Material properties widget."""

    def __init__(self, parent):

        self.root = tk.Toplevel()
        self.root.title('Material properties')
        self.root.protocol("WM_DELETE_WINDOW", self.callbackCancel)
        self.root.resizable(False, False)
        self.parent = parent

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
                    
                    # if (i, j) == (0, 0):
                    #     entry.insert(tk.END, '200000000000')

                    # if (i, j) == (0, 1):
                    #     entry.insert(tk.END, '200000000000')

                    # if (i, j) == (0, 2):
                    #     entry.insert(tk.END, '25')

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
        for (i, j) in self.parent.job.boundaries['left'].keys():
            value = self.parent.job.boundaries['left'][(i, j)]
            self.widgets['lcells'][i][j].insert(tk.END, value)

        for (i, j) in self.parent.job.boundaries['mid'].keys():
            value = self.parent.job.boundaries['mid'][(i, j)]
            self.widgets['mcells'][i][j].insert(tk.END, value)

        for (i, j) in self.parent.job.boundaries['right'].keys():
            value = self.parent.job.boundaries['right'][(i, j)]
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
        valuesLeft = {}
        for i, columns in enumerate(self.widgets['lcells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    valuesLeft[(i, j)] = value

        valuesMid = {}
        for i, columns in enumerate(self.widgets['mcells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    valuesMid[(i, j)] = value

        valuesRight = {}
        for i, columns in enumerate(self.widgets['rcells']):
            for j, column in enumerate(columns):
                value = column.get()
                if value != '':
                    valuesRight[(i, j)] = value

        # Save material data into the current job
        temp = self.widgets['temp'].get()
        identical = self.widgets['identicalBCs'].get()

        print('1', temp, identical)
        self.parent.job.setBoundaries(valuesLeft, valuesMid, valuesRight, temp, identical)
        print('2', self.parent.job.boundaries['temperature'], self.parent.job.boundaries['identical'])

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
                
                if (i, j) == (0, 0):
                    entry.insert(tk.END, '10')

                if (i, j) == (0, 1):
                    entry.insert(tk.END, '0.5')

                columns.append(entry)
            rows.append(columns)

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

        self.parent.switchWidgets('normal')
        self.root.destroy()


    def callbackCancel(self):

        """ Callback function of "Cancel" button. """

        self.parent.switchWidgets('normal')
        self.root.destroy()



class Temperature:

    def __init__(self, parent):

        self.parent = parent
        self.root = tk.Toplevel()
        self.root.title('Temperature')
        self.root.protocol("WM_DELETE_WINDOW", self.callbackCancel)
        self.root.resizable(False, False)

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
                
                if (i, j) == (0, 0):
                    entry.insert(tk.END, '10')

                if (i, j) == (0, 1):
                    entry.insert(tk.END, '0.5')

                columns.append(entry)
            rows.append(columns)

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
        listBox.select_set(0)
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
        thickness.insert(tk.END, '0.1')
        thickness.grid(row=2, column=0, padx=(10, 10), pady=(0, 10), 
                sticky=tk.W+tk.N+tk.E)
        self.modelConfiguration.append(thickness)

        # Label and entry for damage

        label = tk.Label(frame, text='Damage [%]', state='disable', 
        		anchor=tk.W)
        label.grid(row=1, column=1, padx=(7, 0), pady=(5, 0), 
                sticky=tk.W+tk.N+tk.E)
        self.modelConfiguration.append(label)

        damage = tk.Entry(frame, width=12)
        damage.insert(tk.END, '10')
        damage.configure(state='disable')
        damage.grid(row=2, column=1, padx=(10, 10), pady=(0, 10), 
                sticky=tk.W+tk.N+tk.E)
        self.modelConfiguration.append(damage)


        # Material, boundary, corrosion and temperature buttons

        #  self.material = Material(self.main)
        material = tk.Button(frame, text='Material properties',
                command=lambda : Material(self.main))
        material.grid(row=3, column=0, padx=10, pady=5, columnspan=2,
                sticky=tk.N+tk.W+tk.E)
        self.modelConfiguration.append(material)

        boundary = tk.Button(frame, text='Boundary conditions',
                command=lambda : BoundaryConditions(self.main))
        boundary.grid(row=4, column=0, padx=10, pady=5, columnspan=2,
                sticky=tk.N+tk.W+tk.E)
        self.modelConfiguration.append(boundary)

        corrosion  =tk.Button(frame, text='Corrosion wastage',
                command=lambda : Corrosion(self.main))
        corrosion.grid(row=5, column=0, padx=10, pady=5, columnspan=2,
                sticky=tk.N+tk.W+tk.E)
        self.modelConfiguration.append(corrosion)

        temperature = tk.Button(frame, text='Environmental temperature',
                command=lambda : Temperature(self.main), width=self.width-15)
        temperature.grid(row=6, column=0, padx=10, pady=(5, 10), columnspan=2,
                sticky=tk.N+tk.W+tk.E)
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
        history.deselect()
        history['command'] = self.callbackAnalysisType
        history.grid(row=1, column=0, padx=20, pady=(0, 5), sticky=tk.N+tk.W)
        self.analysisType.append(history)


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
        entry.insert(tk.END, '5')
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
        mass.grid(row=3, column=0, padx=20, pady=(0, 0), columnspan=2, 
                sticky=tk.N+tk.W)
        self.modalSettings.append(mass)

        disp = tk.Radiobutton(frame, text=' Displacement')
        disp.deselect()
        # disp['width'] = self.width-15
        disp['anchor'] = tk.W
        disp['variable'] = self.modalSettingsVariables['Normalization']
        disp['value'] = 2
        disp.grid(row=4, column=0, padx=20, pady=(0, 5), columnspan=2, 
                sticky=tk.N+tk.W)
        self.modalSettings.append(disp)


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
        alpha.insert(tk.END, 0.005)
        alpha.grid(row=2, column=0, padx=10, pady=(0, 2), sticky=tk.W+tk.N)
        self.historySettings.append(alpha)

        label = tk.Label(frame, text='Beta', anchor=tk.W)
        label.grid(row=1, column=1, padx=(7, 10), pady=(0, 1), sticky=tk.W+tk.N)
        self.historySettings.append(label)

        beta = tk.Entry(frame, width=12, textvariable=self.hsettingsvars['var2'])
        beta.insert(tk.END, 0.005)
        beta.grid(row=2, column=1, padx=10, pady=(0, 2), sticky=tk.W+tk.N)
        self.historySettings.append(beta)

        label = tk.Label(frame, text='Time period', anchor=tk.W)
        label.grid(row=3, column=0, padx=(7, 10), pady=(3, 2), sticky=tk.W+tk.N)
        self.historySettings.append(label)

        period = tk.Entry(frame, width=12, textvariable=self.hsettingsvars['var3'])
        period.insert(tk.END, 10)
        period.grid(row=4, column=0, padx=(10, 12), pady=(0, 2), sticky=tk.W+tk.N)
        self.historySettings.append(period)

        label = tk.Label(frame, text='Incerement', anchor=tk.W)
        label.grid(row=3, column=1, padx=(7, 10), pady=(3, 2), sticky=tk.W+tk.N)
        self.historySettings.append(label)

        period = tk.Entry(frame, width=12, textvariable=self.hsettingsvars['var4'])
        period.insert(tk.END, 10)
        period.grid(row=4, column=1, padx=10, pady=(0, 2), sticky=tk.W+tk.N)        
        self.historySettings.append(period)

        label = tk.Label(frame, text='Load case', anchor=tk.W)
        label.grid(row=5, column=0, padx=10, pady=(3, 2), sticky=tk.W+tk.N)
        self.historySettings.append(label)


        case = ttk.Combobox(frame, values=['Load case 1', 'Load case 2', 
                'Load case 3', 'Load case 4'], state='readonly')
        case.current(0)
        case.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 10), 
                sticky=tk.W+tk.N+tk.E)
        self.historySettings.append(case)

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
        # 3. Check if job name exists

        listbox = self.main.scenario.widgets['listbox']
        jobs = listbox.get(0, tk.END)
        job = self.jobWidgets['job'].get()

        if job in jobs:
            message = 'Job name already exists!'
            messagebox.showwarning('Warning', message)
        else:
            listbox.insert(len(jobs), job)
            self.main.scenario.printMessage('Job "{}" saved.\n'.format(job))

        self.main.scenario.widgets['listbox'].see(tk.END)
        self.main.scenario.switchButtons()

        # 4. Save job to joblist and model specifics

        self.main.scenario.jobs['job'] = copy.deepcopy(self.main.job)


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