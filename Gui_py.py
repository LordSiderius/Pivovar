from tkinter import *
from multiprocessing import Queue

class Gui(object):
    def __init__(self, sp, temperature, power_queue, gui_output, gui_input):
        root = Tk()
        temp_bar = LabelFrame(root, text="Temperature", padx=10, pady=10)
        pwr_bar = LabelFrame(root, text="Power", padx=10, pady=10)
        # koef_bar = LabelFrame(root, text="Koeficient", padx=10, pady=10)

        self.a = 20
        self.b = 30
        self.temperature = 20
        # definition of output

        self.stop = True
        self.run = False
        self.pause = False

        # TEMPERATURE WINDOW
        def stop():
            self.stop = True
            self.pause = False
            self.run = False

        def pause():
            self.stop = False
            self.pause = True
            self.run = False

        def run():
            self.stop = False
            self.run = True
            self.pause = False

        self.v = StringVar()
        self.v.set(self.temperature)

        self.temp_label = Label(temp_bar, textvariable=self.v)
        self.temp_label.grid(row=0, column=1, padx=5, pady=5)

        sp = StringVar()
        sp.set(20)

        self.e1 = Label(temp_bar, textvariable=sp)
        self.e1.grid(row=1, column=1)

        a = Label(temp_bar, text="Temperature [°C]:")
        a.grid(row=0, column=0, padx=5, pady=5)

        a = Label(temp_bar, text="Set point [°C]")
        a.grid(row=1, column=0, padx=5, pady=5)

        a = Label(temp_bar, text="Timer [min]:")
        a.grid(row=0, column=2, padx=5, pady=5)

        a = Label(temp_bar, text="Set point [min]")
        a.grid(row=1, column=2, padx=5, pady=5)

        timer = StringVar()
        timer.set(0)

        set_time = StringVar()
        set_time.set(0)

        a = Label(temp_bar, textvariable=timer)
        a.grid(row=0, column=3, padx=5, pady=5)

        a = Label(temp_bar, textvariable=set_time)
        a.grid(row=1, column=3, padx=5, pady=5)

        state_text = Label(temp_bar, text="stop", bg="gray", width=40)
        state_text.grid(row=2, column=0, columnspan=4, pady=5)

        b = Button(temp_bar, text="stop", width=6, command=stop)
        b.grid(row=3, column=0, padx=5, pady=5)

        b = Button(temp_bar, text="pause", width=6, command=pause)
        b.grid(row=3, column=1, padx=5, pady=5)

        b = Button(temp_bar, text="run", width=6, command=run)
        b.grid(row=3, column=2, padx=5, pady=5)

        # POWER WINDOW

        rb = IntVar()
        rb.set(1)

        power_var = StringVar()
        power_var.set(0)

        a = Label(pwr_bar, text='Power [W]:')
        a.grid(row=0, column=0, padx=5, pady=5)

        a = Label(pwr_bar, textvariable=power_var)
        a.grid(row=0, column=1, padx=5, pady=5)

        Radiobutton(pwr_bar, text="auto", indicatoron=0, variable=rb, value=1).grid(row=1, column=0, padx=5, pady=5)
        Radiobutton(pwr_bar, text="manual", indicatoron=0, variable=rb, value=2).grid(row=1, column=1, padx=5, pady=5)

        self.e2 = Entry(pwr_bar)
        self.e2.grid(row=2, column=0, padx=5, pady=5)



        def set_pwr():
            if rb.get() == 1:
                pass
            else:
                power = self.e2.get()
                try:
                    power = float(self.e2.get())
                except:
                    power = 0
                # if power_queue.full is True:
                #     power_queue.get()
                # # print('power:', power)
                # power_queue.put(power)


        b = Button(pwr_bar, text="set", width=6, command=set_pwr)
        b.grid(row=2, column=1, padx=5, pady=5)

        # # KOEFICIENT WINDOW
        #
        # def koef_set():
        #     pass
        #
        # def koef_max():
        #     pass
        #
        # self.e3 = Entry(koef_bar)
        # self.e3.grid(row=0, column=0, columnspan= 2, padx=5, pady=5)
        #
        # b = Button(koef_bar, text="set", width=6, command=koef_set)
        # b.grid(row=1, column=0, padx=5, pady=5)
        #
        # b = Button(koef_bar, text="max", width=6, command=koef_max)
        # b.grid(row=1, column=1, padx=5, pady=5)
        #
        # koef_bar.grid(row=1, column=1, padx=5, pady=5)

        temp_bar.grid(row=0, column=0, rowspan=4, padx=5, pady=5)
        pwr_bar.grid(row=0, column=1, padx=5, pady=5)


        def read_temperature():
            root.after(300, read_temperature)

            self.temperature = temperature.value
                # print('temperature get:', self.temperature)
            self.v.set(self.temperature)
            # print('run', self.run)
            # print('pause', self.pause)
            # print('stop', self.stop)
        def gui_output2():
            root.after(300, gui_output2)
            gui_output.put([self.run, self.pause, self.stop])

            if gui_input.empty() is False:
                [state_var, goal_temp, goal_time, timer0, power] = gui_input.get()
                sp.set(goal_temp)
                timer.set(round(timer0, 2))
                set_time.set(goal_time)
                state_text.config(text=state_var)
                power_var.set(round(power, 0))

                if state_var == "heating":
                    state_text.config(bg="orange")
                elif state_var == "holding":
                    state_text.config(bg="green")
                elif state_var == "pause":
                    state_text.config(bg="yellow")
                else:
                    state_text.config(bg="red")

                # print('run', self.run)

        root.after(300, read_temperature)
        root.after(100, gui_output2)
        # print('run', self.run)
        root.mainloop()

if __name__ == "__main__":
    sp = Queue()
    power_queue = Queue()
    power_req_queue = Queue()
    temperature = Value('d', 0.0)
    gui_output = Queue()
    gui = Gui(sp, temperature, power_req_queue, gui_output)