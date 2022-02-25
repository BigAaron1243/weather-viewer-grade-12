# Some code by Reblochon Masque used - https://stackoverflow.com/questions/46332192/displaying-matplotlib-inside-tkinter 
# Some code by TmZn used - https://stackoverflow.com/questions/45905665/is-there-a-way-to-clear-all-widgets-from-a-tkinter-window-in-one-go-without-refe

# Import libraries to be used
import matplotlib
import tkinter as tk
import csv
import numpy
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

# This function returns a list of all children in a tkinter frame
def all_children (window) :
    _list = window.winfo_children()
    for item in _list :
        if item.winfo_children() :
            _list.extend(item.winfo_children())
    return _list

# This function takes the list from the above function and removes all of the widgets in the window, allowing new data to be drawn
def resetAll():
    widget_list = all_children(root)
    for item in widget_list:
        item.pack_forget()
    drawEverything(root)

# This class creates a frame for all of the graphs to be drawn on, it contains all functions that add items to the frame
class GraphPage(tk.Frame):

    # Initialise the frame with a title
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, height=800, width=200)
        self.title = tk.Label(self, text = "Weather Data Rendering Application", font=("cambria", 16))
        self.title.pack()
        self.pack()

    # This function adds a TkAgg canvas to render the matplotlib item inside, it also adds the 'expand' and 'analyse' buttons, and a title for the graph
    def add_mpl_figure(self, fig, title, plotID, filename):

        self.mpl_canvas = FigureCanvasTkAgg(fig, self)
        self.mpl_canvas.draw()
        self.mpl_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.mpl_canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        if (title != ""):
            self.textbox=tk.Frame(self, height=18, width=500)
            self.label = tk.Label(self.textbox, text=title, padx =10)
            self.label.pack(side=tk.LEFT)
            self.button = tk.Button(self.textbox, text="Expand", command=lambda : self.RenderIndependantFigure(plotID, filename, 0, self.textbox))
            self.button.pack(side=tk.RIGHT)
            self.button2 = tk.Button(self.textbox, text="Analyse", command=lambda : self.RenderIndependantFigure(plotID, filename, 1, self.textbox))
            self.button2.pack(side=tk.RIGHT)
            self.textbox.pack()
    
    # This simple function allows for the easy creation of labels from outside of the class
    def add_label(self, someText):
        self.label = tk.Label(self, text=someText, bg='white', width=500)
        self.label.pack()

    # This function handles the 'expand' and 'analyse' buttons, when expand is pressed, it will render a simple pyplot, when analyse is pressed, it will render
    # a message box showing relevant data
    def RenderIndependantFigure(self, plotID, flnm, mode, textContainer):
        yValue, timeVar, color = [0],[0],[0]

        # This loop gets the data from the selected csv, to deal with anomalous data, it has both a try:except: and various threshold checks
        with open(flnm) as data:
            for line in csv.reader(data):
                if (line[0] != "Time"):
                    try:
                        tL = list(map(int, line[0].split(":")))
                        timeVar.append(tL[0] * 3600 + tL[1] * 60 + tL[2])
                        wNum = float(line[plotID])
                        if (plotID == 2 and ((wNum > yValue[-1] + 100) or (wNum < yValue[-1] - 100) or (wNum == 0)) == False):
                            yValue.append(wNum)
                        elif ((wNum > yValue[-1] + 25) or (wNum < yValue[-1] - 25)): 
                            yValue.append(yValue[-1])
                        else:
                            yValue.append(wNum)
                    except:
                        print("CSV Corrupted! Could not process data!")
                        yValue.append(yValue[-1])
                else:
                    title = line[plotID]
        yValue.pop(0)
        timeVar.pop(0)

        # Depending on the option, show the graph or the messagebox 
        if (mode == 0):
            plt.plot(timeVar,yValue)
            plt.gcf().autofmt_xdate()
            plt.show()
        elif (mode == 1):
            aData = numpy.array(yValue)
            tk.messagebox.showinfo('Analysis Results for ' + title + ':', 'Average: ' + str(round(numpy.average(aData)*100)/100) + '\nMaximum: ' + str(round(numpy.amax(aData)*100)/100) + '\nMinimum: ' + str(round(numpy.amin(aData)*100)/100) + '\nStandard Deviation: ' + str(round(numpy.std(aData)*100)/100) + '                         ')

# this class simply prepares a matplotlib graph to be rendered in the add_mpl_figure defined above
class MPLGraph(Figure):

    def __init__(self, varIndex, CSVLoc):
        Figure.__init__(self, figsize=(5, .9), dpi=90)
        self.plot = self.add_subplot(111)
        timeVar, yValue = [0],[0]
        # This is a while loop for gathering data similar to the one earlier, unfortunately it had to be duplicated as I could not find a way to re-use
        try:
            with open(CSVLoc) as data:
                for line in csv.reader(data):
                    if (line[0] != "Time"):
                        try:
                            tL = list(map(int, line[0].split(":")))
                            timeVar.append(tL[0] * 3600 + tL[1] * 60 + tL[2])
                            wNum = float(line[varIndex])
                            if (varIndex ==2 and ((wNum > yValue[-1] +100) or (wNum < yValue[-1] - 100)) == False):
                                yValue.append(wNum)
                            elif ((wNum > yValue[-1] + 25) or (wNum < yValue[-1] - 25)): 
                                yValue.append(yValue[-1])
                            else:
                                yValue.append(wNum)
                        except:
                            print("CSV Corrupted! Could not process data!")
                            yValue.append(yValue[-1])
        except FileNotFoundError:
            quit()
        yValue.pop(0)
        timeVar.pop(0)
        self.plot.plot(timeVar, yValue)

# This function puts all of the elements defined above into the frame
class drawEverything(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=500, height=800,  bg='white')
        flnm = tk.filedialog.askopenfilename(initialdir="/csv/", title = "Select CSV file", filetypes=(("CSV files","*.csv"),))
        if(flnm == ''):
            quit()
        graph_page = GraphPage(root)
        graph_page.add_label("Time (hours)")
        timeVar = []

        # This loop adds a simple time scale in hours above all of the graphs
        with open(flnm) as data:
            for line in csv.reader(data):
                if (line[0] != "Time"):
                    tL = list(map(int, line[0].split(":")))
                    timeVar.append(tL[0] * 3600 + tL[1] * 60 + tL[2])
        hours = timeVar[-1] / 3600
        bop=""
        for x in range(62):
            bop = bop + (" ")
        graph_page.add_label("-" + str(int((timeVar[-1]/3600)*10)/10) + bop + "-" + str(int((timeVar[int(len(timeVar)/2)]/3600)*10)/10) + bop +  "-0")
        graph_page.add_mpl_figure(MPLGraph(1, flnm), "Temperature (c)", 1, flnm)           
        graph_page.add_mpl_figure(MPLGraph(2, flnm), "Humidity (%)", 2, flnm)
        graph_page.add_mpl_figure(MPLGraph(3, flnm), "Soil Moisture (1-1024)", 3, flnm)
        graph_page.add_mpl_figure(MPLGraph(5, flnm), "Wind Speed (km/h)", 5, flnm)
        graph_page.add_mpl_figure(MPLGraph(6, flnm), "Rain (mm)", 6, flnm)
        padde = tk.Frame(root, height=18, width=500, bg='white')
        padde.pack(expand=True)
        leCSVButt = tk.Button(root, text="Select CSV", command=resetAll)
        fileIdentify = tk.Label(root, text="Currently viewing: " + flnm, bg='white', wraplength=500, justify=tk.LEFT, font=('Arial', 7))
        signature = tk.Label(root, text="Program designed by Oscar Coghlan", bg = 'white', wraplength=500, justify=tk.LEFT, font=('Arial', 7))
        leCSVButt.pack()
        fileIdentify.pack()
        signature.pack()
        self.pack(fill = tk.BOTH, expand=True)

# Finally the root is rendered
root = tk.Tk(className="weather viewer")
root.configure(bg = 'white')
root.geometry("600x800")
drawEverything(root)

root.mainloop()


