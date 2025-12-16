
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd


import sys
import matplotlib
import matplotlib.pyplot as plt
from LicelReader import *
from LicelUtil import *

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

# create the root window
root = tk.Tk()
root.title('python min viewer')
root.resizable(True, True)
root.geometry('1200x1000')


axes = None
figure = None
figure_canvas = None
line1 = None
varline = None
file = None




    
class App(tk.Tk):
    
    def draw_Data(self):
 
        ds = self.varline.current()
        if ds < 0 :
            self.varline.current(0)
            ds = 0 
        x = self.file.dataSet[ds].x_axis_m()
        y = self.file.dataSet[ds].physData
        if self.file.dataSet[ds].dataType == 0 :
            y = 1000 * self.file.dataSet[ds].physData
        if self.line1 == None :
            self.line1, = self.axes.plot(x,y)
        else :
            self.line1.set_xdata(x)
            self.line1.set_ydata(y)
        ymin = np.min(y)
        ymax =  np.max(y) + 0.02 * (np.max(y) - np.min(y))    
        self.axes.set_ylim(ymin, ymax)
        self.axes.autoscale(enable=True, axis='x')
        L = self.axes.legend([self.line1], [self.file.dataSet[ds].getDescString()])
        plt.setp(L.texts, family='Consolas')
        self.axes.set_title(self.filename)
        #if (file.dataSet[ds]) :
        if self.file.dataSet[ds].dataType == 0 :
            self.axes.set_ylabel('mV')
        elif self.file.dataSet[ds].dataType == 1 :
            self.axes.set_ylabel('MHz')
        else :             
            self.axes.set_ylabel('AU')
        self.axes.set_xlabel('m')
        self.figure_canvas.draw()
    def baseline(self):
        ds = self.varline.current()
        if ds < 0 :
            self.varline.current(0)
            ds = 0 
        y = self.file.dataSet[ds].physData
        if self.file.dataSet[ds].dataType == 0 :
            y = 1000 * self.file.dataSet[ds].physData
        if self.file.dataSet[ds].dataType == 0 or self.file.dataSet[ds].dataType == 1 :
            base_start = -1000
            base_end = -1
        else:
            base_start = 0
            base_end = 100
        

        mean = np.median(y[base_start:base_end])
        self.axes.set_ylim(mean + 5 * (np.min(y[base_start:base_end] - mean)),mean + 5*(np.max(y[base_start:base_end])  -mean))
        self.figure_canvas.draw()
    def DreieckZoom(self):
        ds = self.varline.current()
        if ds < 0 :
            self.varline.current(0)
            ds = 0
        y = self.file.dataSet[ds].physData
        if self.file.dataSet[ds].dataType == 0 :
            y = 1000 * self.file.dataSet[ds].physData
        start_idx = 400
        end_idx = 600
        self.axes.set_ylim(y[end_idx], y[start_idx])
        self.axes.set_xlim(self.file.dataSet[ds].x_axis_m()[start_idx], self.file.dataSet[ds].x_axis_m()[end_idx])
        self.figure_canvas.draw()
    def openDataFile(self):
        self.file = LicelFileReader(self.filename)
        self.varline['values'] = self.file.shortDescr
        if self.varline.current() < 0:
          self.varline.set(0) 
          self.varline.configure(textvariable = self.file.shortDescr[0]) 
        self.draw_Data()

    def select_file(self):
        filetypes = (
            [('All files', '*.*')]
        )
       
        self.filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        self.openDataFile()
        
    def change(self, event):
        self.draw_Data()
    def ds_down(self, event):
         ds = self.varline.current()
         ds += 1
         if ds >= len(self.varline['values']) :
             ds = 0
         self.varline.current(ds)
         self.draw_Data()
    def ds_up(self, event):
         ds = self.varline.current()
         ds -= 1
         if ds < 0 :
             ds = len(self.varline['values']) - 1
         self.varline.current(ds)
         self.draw_Data()
    def nextFile(self,event):
        head_tail = os.path.split(self.filename)
        dir_content = os.listdir(head_tail[0])
        index = dir_content.index(head_tail[1])
        if  (index >= 0) and (index < len(dir_content) - 1):
            self.filename = os.path.join(head_tail[0], dir_content[index + 1])
        self.openDataFile()
    def prevFile(self,event):
        head_tail = os.path.split(self.filename)
        dir_content = os.listdir(head_tail[0])
        index = dir_content.index(head_tail[1])
        if  index >= 1 :
            self.filename = os.path.join(head_tail[0], dir_content[index - 1])
        self.openDataFile()

    def __init__(self):
        # open button
        open_button = ttk.Button(
        root,
        text='Open a File',
        command=self.select_file
        )

        # configure the grid
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=50)

        open_button.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        figure = Figure(figsize=(14, 8), dpi=100)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(figure)

        # create the toolbar
        toolbar = NavigationToolbar2Tk(self.figure_canvas, pack_toolbar=False)
        # create axes
        self.axes = figure.add_subplot()
        self.figure_canvas.get_tk_widget().grid(column=1, row=0, rowspan= 2, sticky=tk.E, padx=5, pady=5)
        toolbar.grid(column=1, row=2, sticky=tk.W, padx=5, pady=5)
        self.line1 = None
        n = tk.StringVar() 
        self.varline = ttk.Combobox(root, width = 20,  textvariable = n, state="readonly") 
        self.varline.grid(column = 0, row = 1, sticky=tk.W, padx=5, pady=5) 
        self.varline['values'] = ['']
        self.varline.current(0)
        self.varline.bind("<<ComboboxSelected>>", lambda event: self.change(event))
        root.bind('<Up>', lambda event : self.ds_up(event))
        root.bind('<Down>', lambda event : self.ds_down(event))
        root.bind('<space>', lambda event : self.ds_down(event))
        root.bind('<Right>', lambda event : self.nextFile(event))
        root.bind('<Left>', lambda event : self.prevFile(event))
        root.bind('<b>', lambda event : self.baseline())
        root.bind('<d>', lambda event : self.DreieckZoom())
        print(sys.argv)
        if len(sys.argv) > 1:
            self.filename = sys.argv[1]
            self.openDataFile()
        else :
           self.select_file()
        
        
if __name__ == '__main__':
    app = App()
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        #keep the window displaying
        root.mainloop()

