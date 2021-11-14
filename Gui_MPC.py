# Info:
# Gui for control of MPC brewery heating
# Heating can be started, pasued and reset
#
# INPUTS:
#   - Temperature from measurement
#   - Set point temperature
#   - Elapsed time
#   - MPC trajectory navigation time
#   - Power from algo
#   - State of controller
# OUTPUTS:
#   - RUN/PAUSE/STOP - one signal
#   - MPC/PID/MANUAL - one signal
#   - Adding power - one signal
#   - Manual power - one signal
#
from tkinter import *
from multiprocessing import Value
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from time import sleep
import numpy as np

class Gui(object):
    def __init__(self, temperature, tempSetPoint, timeElapsed, timeMPC, powerInGui, stateOfControl, stateRequest, methodRequest, powerAdding, powerManual, desired_time, fp):
        # Initialization of window
        root = Tk()
        root.wm_title("Dej Bůh štěstí!")
        # list of bars used
        info_bar = LabelFrame(root, text="Information bar", padx=10, pady=10)
        run_bar = LabelFrame(root, text="Control bar", padx=10, pady=10)
        method_bar = LabelFrame(root, text="Heating method selection", padx=10, pady=10)
        chart_bar = LabelFrame(root, text="Scope", padx=10, pady=10)

# Initizalization:
        # Init of variables for info_bar
        temp = StringVar()
        tempSet = StringVar()
        time = StringVar()
        tiMPC = StringVar()
        power = StringVar()

        temp.set('0')
        tempSet.set('0')
        time.set('0')
        tiMPC.set('0')
        power.set('0')

        # Init of variables for control_bar
        self.state = 3
        statusText = StringVar()
        statusText.set('Status is stopped.')

        # Init of variables for method_bar
        mpm = IntVar()
        pwrMan = StringVar()
        pwrAdd = StringVar()

        mpm.set(1)
        pwrMan.set(0)
        pwrAdd.set(0)

    # Init of variables for chart_bar
        time_period = 20  # measured period of time dor chart in minutes
        point_count = round(time_period/0.3*60)  # number of points in chart
        self.x = [0] * point_count
        self.y = [0] * point_count

    ######### Info bar part #########

        # Info screen will have 4 rows and 4 columns
        #    temp  ----   time
        #  tempset ---- mpc time

        temp_label = Label(info_bar, text='temperature of content')
        temp_label.grid(row=0, column=0, padx=5, pady=5)

        temp_value = Label(info_bar, textvariable=temp, bg='white', width=10)
        temp_value.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        temp_symbol = Label(info_bar, text="°C", width=3)
        temp_symbol.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tempSet_label = Label(info_bar, text='temperature setpoint')
        tempSet_label.grid(row=2, column=0, padx=5, pady=5)

        tempSet_value = Label(info_bar, textvariable=tempSet, bg='white', width=10)
        tempSet_value.grid(row=3, column=0, padx=5, pady=5, sticky='e')

        tempSet_symbol = Label(info_bar, text="°C", width=3)
        tempSet_symbol.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        time_label = Label(info_bar, text='elapsed time')
        time_label.grid(row=0, column=2, padx=5, pady=5)

        time_value = Label(info_bar, textvariable=time, bg='white', width=10)
        time_value.grid(row=1, column=2, padx=5, pady=5, sticky='e')

        time_symbol = Label(info_bar, text="min", width=3)
        time_symbol.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        timeMPC_label = Label(info_bar, text='time in MPC navigation')
        timeMPC_label.grid(row=2, column=2, padx=5, pady=5)

        timeMPC_value = Label(info_bar, textvariable=tiMPC, bg='white', width=10)
        timeMPC_value.grid(row=3, column=2, padx=5, pady=5, sticky='e')

        timeMPC_symbol = Label(info_bar, text="min", width=3)
        timeMPC_symbol.grid(row=3, column=3, padx=5, pady=5, sticky='w')

        power_label = Label(info_bar, text='Power from network')
        power_label.grid(row=4, column=0, padx=5, pady=5)

        power_value = Label(info_bar, textvariable=power,  bg='white', width=10)
        power_value.grid(row=5, column=0, padx=5, pady=5, sticky='e')

        power_symbol = Label(info_bar, text="W", width=3)
        power_symbol.grid(row=5, column=1, padx=5, pady=5, sticky='w')


        info_bar.grid(row=0, column=0, columnspan = 4, padx=5, pady=5)

    ######### Control bar part #########

        # state signal encoded:
        # RUN - 1
        # PAUSE - 2
        # STOP - 3

        # run_bar variables
        def stop():
            self.state = 3
            write_status()

        def pause():
            self.state = 2
            write_status()

        def run():
            self.state = 1
            write_status()

        statusLabel = Label(run_bar, bg= 'grey', width=48, textvariable=statusText)
        statusLabel.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        runB = Button(run_bar, text="run", width=6, command=run)
        runB.grid(row=1, column=0, padx=5, pady=5)

        pauseB = Button(run_bar, text="pause", width=6, command=pause)
        pauseB.grid(row=1, column=1, padx=5, pady=5)

        stopB = Button(run_bar, text="stop", width=6, command=stop)
        stopB.grid(row=1, column=2, padx=5, pady=5)


        run_bar.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

    ######### Method bar part #########
        def write_method():
            methodRequest.value = int(mpm.get())
            # print(mpm.get()) # debug
        def set():
            # reads value from gui for power adding and manual power
            powerManual.value = float(pwrMan.get())
            powerAdding.value = float(pwrAdd.get())
            # print(pwrMan.get()) # debug
            # print(pwrAdd.get()) # debug

        # chages method MPC/PID/MANUAL
        Radiobutton(method_bar, text="MPC", indicatoron=0, variable=mpm, value=1, width=10, command=write_method).grid(row=0, column=0, padx=5, pady=5)
        Radiobutton(method_bar, text="PID", indicatoron=0, variable=mpm, value=2, width=10, command=write_method).grid(row=0, column=1, padx=5, pady=5)
        Radiobutton(method_bar, text="Manual", indicatoron=0, variable=mpm, value=3, width=10, command=write_method).grid(row=0, column=2, padx=5, pady=5)

        powerMan_label = Label(method_bar, text="Power Add", width=10)
        powerMan_label.grid(row=1, column=0)

        powerAdd_label = Label(method_bar, text="Manual power", width=10)
        powerAdd_label.grid(row=1, column=1)

        powerMan = Entry(method_bar, textvariable=pwrAdd, bg='white', width=10)
        powerMan.grid(row=2, column=0)

        powerAdd = Entry(method_bar, textvariable=pwrMan, bg='white', width=10)
        powerAdd.grid(row=2, column=1)

        setB = Button(method_bar, text="set", width=10, command=set)
        setB.grid(row=2, column=2, padx=5, pady=5)

        method_bar.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

    ############ Chart_bar ##############
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=chart_bar)  # A tk.DrawingArea.
        subfig = fig.add_subplot(111)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        def plot():
            if self.state == 3:
                self.x = [0] * point_count
                self.y = [0] * point_count

            reftemp = np.interp(self.x, desired_time, fp)
            tempSet.set(round(reftemp[-1], 1))
            subfig.clear()
            subfig.set_title('Beer temperature')
            subfig.set_xlabel('time [min]')
            subfig.set_ylabel('temperature [°C]')
            subfig.grid(True)
            # plot variable
            subfig.plot(self.x, self.y, linewidth=1, label='measured')
            # plot setpoint
            subfig.plot(self.x, reftemp, label='setpoint')
            legend = subfig.legend(loc='best', shadow=False)
            # Put a nicer background color on the legend.
            # legend.get_frame().set_facecolor('C0')
            canvas.draw()

        chart_bar.grid(row=0, column=4, rowspan=3, padx=5, pady=5)
    ############ GUI Logic ##############

        def read_param():
            #  repeat reading method every 300ms
            root.after(1000, read_param)
            # print('Hallo') # debug
            # variables to be read - shared inputs
            temp.set(round(temperature.value, 1))
            # tempSet.set(round(tempSetPoint.value, 1))
            time.set(round(timeElapsed.value, 1))
            tiMPC.set(round(timeMPC.value, 1))
            power.set(round(powerInGui.value, 1))
            # stateOfControl.value # to be used

            # debug only!!!
            # temperature.value = temperature.value + 10/(temperature.value)/60
            # timeElapsed.value += 0.3/60
            # debug only end !!!

            if int(stateOfControl.value) == 1:
                statusLabel.config(bg='green')
                statusText.set('Running OK!')
            elif int(stateOfControl.value) == 2:
                statusLabel.config(bg='yellow')
                statusText.set('Control algo is paused')
            elif int(stateOfControl.value) == 3:
                statusLabel.config(bg='red')
                statusText.set('Status is stopped.')
            else:
                statusLabel.config(bg='grey')
                statusText.set('ERROR')

            # chart variables
            self.x.pop(0)
            self.x.append(timeMPC.value)
            self.y.pop(0)
            self.y.append(temperature.value)
            plot()
            
        def write_status():
            # sends request to algo to switch mode RUN/PAUSE/STOP
            stateRequest.value = int(self.state)
            # print(self.state) # debug
            pass

        # calls read of variables for first time
        read_param()
        # calls gui loop
        root.mainloop()
        # RAP OS version mainloop()

# standalone version for debug
if __name__ == "__main__":

    # list of shared variables used
    # INPUTS
    temperature = Value('d', 17.0)
    tempSetPoint = Value('d', 10.0)
    timeElapsed = Value('d', 0.0)
    timeMPC = Value('d', 10.0)
    powerInGui = Value('d', 10.0)
    stateOfControl = Value('i', 3)
    # OUTPUTS
    stateRequest = Value('i', 3)
    methodRequest = Value('i', 3)
    powerAdding = Value('d', 0.0)
    powerManual = Value('d', 0.0)
    powerToPwm = Value('d', 0.0)
    # test scheme, where pause is necessary
    desired_time = [0,  25, 45, 75, 105, 115, 145, 155, 185, 195, 210, 211, 250]
    desired_temps =           [17, 37, 37, 55,  55,  62,  62,  72,  72,  78,  78,  65,  99]
    # gui call
    gui_interface = [temperature, tempSetPoint, timeElapsed, timeMPC, powerToPwm, stateOfControl, stateRequest, methodRequest,
                     powerAdding, powerManual, desired_time, desired_temps]
    gui = Gui(temperature, tempSetPoint, timeElapsed, timeMPC, powerToPwm, stateOfControl, stateRequest, methodRequest,
                     powerAdding, powerManual, desired_time, desired_temps)


