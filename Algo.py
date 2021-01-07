# This is main control script
from multiprocessing import Queue, Value
from time import sleep
from Power_limiter import power_limiter, power_loses
import time
import random
# from matplotlib import pyplot as plt
import copy



class Simulation(object):
    def __init__(self, t0=20):
        self.energy_of_system = 0
        self.t0 = t0

    def simulation(self, power, temp, looptime):
        energy_add = power * looptime * 60
        power_lost = (11 * temp - 220) * looptime * 60
        self.energy_of_system += energy_add * 3
        self.energy_of_system -= (power_lost + random.randrange(-20, 50))
        temp = self.energy_of_system / 4200 / 15 + self.t0
        return temp


class Algo(object):
    def __init__(self):
        # infuze
        # self.start_times =            [10, 20, 30, 30, 15, 90]
        # self.start_temperatures =     [37, 55, 62, 72, 78, 98.4]
        self.start_times = [220]
        self.start_temperatures = [98.3]
        self.goal_times =        copy.copy(self.start_times)
        self.goal_temperatures = copy.copy(self.start_temperatures)
        self.temperature = 20
        self.stop = False
        self.running = False
        self.pause = False

    def run(self, temperature, power_req, gui_output, gui_input):
        t0 = 35  # will be measured
        goal_time = self.start_times[0]

        time0 = time.time()
        times = 0
        timer = 0
        power = 0
        end = False

        # power offset for temperature in transitions
        offset = 1

        # for simulation purposes
        plant = Simulation(t0)

        # +++ DIAGRAM ENTRY +++
        state = 'stop'

        while True:
            # +++ TIMER START +++
            # calculation of timers
            # output: timer, looptime
            support_var = time.time()
            looptime = round((support_var - time0) / 60, 3)
            time0 = support_var
            timer += looptime
            #  --- TIMER END ---

            # ==== READING INPUTS ====
            # +++ READING GUI LOGIC +++
            while gui_output.empty() is False:
                [self.running, self.pause, self.stop] = gui_output.get()
            #  --- READING GUI END ---

            # +++TEMPERATURE PART +++

            # # +++ for SIMULATION only +++
            # tem = round(plant.simulation(power, self.temperature, looptime), 3)
            # temperature.value = tem
            # --- for SIMULATION only ---

            self.temperature = temperature.value

            # --- TEMPERATURE END ---

            #  +++ PREPARATION FOR POWER LOSES ON REAL DEVICE +++
            adding = power_loses(self.temperature)
            #  --- PREPARATION END ---

            # +++ TRANSITON PART +++
            stop_entry = False
            hold_entry = False
            heat_entry = False
            pause_entry = False

            if self.running and state == 'stop':
                if self.temperature <= goal_temp - offset:
                    heat_entry = True
                    times = 0
                else:
                    hold_entry = True

            if state == 'heating' and self.temperature >= goal_temp - offset:
                try:
                    goal_time = self.goal_times.pop(0)
                except:
                    end = True
                hold_entry = True

            if state == 'holding' and times > goal_time:
                try:
                    goal_temp = self.goal_temperatures.pop(0)
                except:
                    end = True
                heat_entry = True
                times = 0

            if self.pause is True and (state == 'heating' or state == 'holding'):
                pause_entry = True

            if state == 'pause' and self.temperature <= goal_temp - offset and self.running:
                heat_entry = True

            if state == 'pause' and self.temperature > goal_temp - offset and self.running:
                hold_entry = True

            if self.stop is True:
                stop_entry = True
                hold_entry = False
                heat_entry = False
                pause_entry = False

            if end is True:
                print('BREWERY END')
                break

            #  --- TRANSITION PART END ---

            # +++ STATE ENTRY PART ++++
            # enter holding
            if hold_entry:
                state = 'holding'

            # enter heating
            if heat_entry:
                state = 'heating'

            # enter pause
            if pause_entry:
                state = 'pause'

            if stop_entry:
                state = 'stop'

            # --- STATE ENTRY END ---


            # +++ STATE ACTIONS +++
            # holding action
            if state == 'holding':
                # algo for holding
                error = goal_temp - self.temperature
                power = adding - 220 + 1500 * error
                times += looptime
                # heating action
            elif state == 'heating':
                #     algo for heating
                if self.temperature < 33:
                    power = 1500
                elif self.temperature > 72:
                    power = 2000
                else:
                    power = adding + 0.7 * 15 * 4200 / 60 - 220
                # stop action
            elif state == 'stop':
                self.goal_times = copy.copy(self.start_times)
                self.goal_temperatures = copy.copy(self.start_temperatures)
                times = 0
                power = 0
                try:
                    goal_temp = self.goal_temperatures.pop(0)
                    goal_time = copy.copy(self.start_times[0])
                except:
                    end = True
                    break
            else:
                power = 0

            # state end
            # if last_state == 'pause' and state != 'pause':
            #     state = self.memory_state

            #  --- STATE ACTIONS END ---

            #  +++ POWER WRITING PART START +++
            power = max(0, min(2000, power))

            #  filling Value
            power_req.value = power
            #  +++ POWER WRITING PART END +++


            #  +++ SEND DATA FOR GUI +++
            while gui_input.empty() is False:
                gui_input.get_nowait()
            gui_input.put([state, goal_temp, goal_time, times, power])

            #  --- END SEND DATA FOR GUI ---

            # +++ CONSOLE INFORMATION START +++
            # debugg
            # print('Time:', timer)
            # print('Goal temperature', goal_temp)
            # print('Temperature:', tem)
            # print('State', state)
            # print('Timer', times)
            # print('Goal time', goal_time)
            # print('Power:', power)
            # print('-----==============-----')
            # result_log_time.append(timer)
            #
            # if state == 'heating':
            #     result_log_states.append(1)
            # else:
            #     result_log_states.append(0)
            #
            # result_log_goal_temp.append(goal_temp)
            # result_log_temp.append(temp)
            # result_log_power.append(power)
            #  --- CONSOLE INFORMATION END ----

            #  +++ SIMULATION TIME +++
            sleep(0.4)

            # --- SIMULATION  END ---

        # debug
        # plt.figure()
        # plt.plot(result_log_time, result_log_temp)
        # plt.title('Temperature')
        # plt.xlabel('time[s]')
        # plt.ylabel('temperature[C]')
        # plt.figure()
        # plt.plot(result_log_time, result_log_states)
        # plt.title('States')
        # plt.xlabel('time[s]')
        # plt.ylabel('Heating - 1 / holding = 0')
        # plt.figure()
        # plt.plot(result_log_time, result_log_goal_temp)
        # plt.title('Goal Temperature')
        # plt.xlabel('time[s]')
        # plt.ylabel('temperature[C]')
        # plt.figure()
        # plt.plot(result_log_time, result_log_power)
        # plt.title('Power')
        # plt.xlabel('time[s]')
        # plt.ylabel('power[W]')
        # plt.show()


if __name__ == "__main__":
    power_req = Value('d', 0.0)
    temperature = Value('d', 0.0)
    gui_output = Queue()
    algo = Algo()
    gui_input = Queue()
    algo.run(temperature, power_req, gui_output, gui_input)
