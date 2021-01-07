from time import time, sleep
from copy import copy
from multiprocessing import Value
import winsound

# # +++ INTERFACE +++
# # INPUTS
# temperature = Value('d', 17.0)
# powerInGui = Value('d', 10.0)
# stateRequest = Value('i', 3)
# methodRequest = Value('i', 3)
# powerAdding = Value('d', 0.0)
# powerManual = Value('d', 0.0)
# powerFromMpc = Value('d', 10.0)
# powerFromPid = Value('d', 10.0)
# # OUTPUTS
# stateOfControl = Value('i', 3)
# powerToPwm = Value('d', 0.0)
# timeElapsed = Value('d', 0.0)
# timeMPC = Value('d', 10.0)


class LogicControl(object):
    def __init__(self):
        # timer since beginning init
        self.timer0 = time()
        self.timer = copy(self.timer0)
        self.timeMPC = 0
        # internal state of simulation
        #  1 - RUN - both timers run, u = f(T, t)
        #  2 - PAUSE - MPC timer stops, u = 0
        #  3 - STOP - resets both timers and set them to 0, u = 0
        self.stateofControlInter = 3


        # threshold temperature [°C] whether heating coil can be used (to avoid burning of malt on coil)
        self.coilThreshold = 65
        self.noMaltThreshold = 35
        # saturated power max
        self.satMin = 0
        # saturated power for heater only
        self.satMiddle = 1500
        # saturated power max - maximal power of system
        self.satMax = 2000

        # Initialization for alarms
        self.alarmsActive = True
        self.waitinForCond = True
        self.flagTemp = True
        self.flagTime = True


    def timer_elapsed(self, loopTime, timeElapsed):
        self.timer += loopTime/60
        timeElapsed.value = round(self.timer, 3)


    def timer_MPC(self, loopTime, timeMPC):
        self.timeMPC += loopTime/60
        timeMPC.value = round(self.timeMPC, 3)

    def power_selector(self, methodRequest, powerFromMpc, powerFromPid, powerManual, powerAdding, temperature, powerToPwm):
        # selecting power based on control method
        # 1 - MPC
        # 2 - PID
        # 3 - manual
        # to MPC and PID can be manually added some value
        if methodRequest.value == 1:
            u = powerFromMpc.value + powerAdding.value
        elif methodRequest.value == 2:
            u = powerFromPid.value + powerAdding.value
        elif methodRequest.value == 3:
            u = powerManual.value
        else:
            u = 0
            print("error in power selector if condition")

        if temperature.value > self.noMaltThreshold and temperature.value < self.coilThreshold:
            u = max(self.satMin, min(self.satMiddle, u))
        else:
            u = max(self.satMin, min(self.satMax, u))

        powerToPwm.value = u

    def internal_status(self, stateRequest, stateOfControl):
        # internal state of simulation and control
        #  1 - RUN - both timers run, u = f(T, t)
        #  2 - PAUSE - MPC timer stops, u = 0
        #  3 - STOP - resets both timers and set them to 0, u = 0
        if stateRequest.value == 1:
           self.stateofControlInter = 1
        elif stateRequest.value == 2:
           self.stateofControlInter = 2
        elif stateRequest.value == 3:
           self.stateofControlInter = 3
        else:
            self.stateofControlInter = 3
            print("error in power selector if condition")

        stateOfControl.value = self.stateofControlInter

    def alarms(self, temperature, timeMPC):

        if self.waitinForCond and self.alarmsActive:
            try:
                [self.alarmTemp, self.alarmTime, self.alarmMessage] = self.alarmsList.pop(0)
                self.waitinForCond = False
                self.flagTemp = False

            except:
                self.waitinForCond = False
                self.alarmsActive = False

        if self.alarmsActive and not self.flagTemp and temperature.value >= self.alarmTemp:
            self.alarmTime0 = timeMPC.value
            self.flagTime = False
            self.flagTemp = True

        if self.alarmsActive and not self.flagTime and timeMPC.value - self.alarmTime0 >= self.alarmTime:
            print(self.alarmMessage)
            [winsound.Beep(800, 1000) for i in range(5)]
            self.waitinForCond = True
            self.flagTemp = True
            self.flagTime = True

    def run(self, temperature, stateRequest, methodRequest, powerAdding, powerManual, powerFromMpc,
                       powerFromPid, active, stateOfControl, powerToPwm, timeElapsed, timeMPC, alarmsList):
        timeLast = 0
        self.alarmsList = alarmsList
        while active.value == 1:
            # +++ debug ONLY +++
            # temperature.value += 0.1
            # --- debug ONLY ---
            actualTime = time()
            loopTime = actualTime - timeLast
            timeLast = actualTime

            self.internal_status(stateRequest, stateOfControl)
            # RUN state
            if self.stateofControlInter == 1:
                self.power_selector(methodRequest, powerFromMpc, powerFromPid, powerManual, powerAdding, temperature, powerToPwm)
                self.timer_elapsed(loopTime, timeElapsed)
                self.timer_MPC(loopTime, timeMPC)
                self.alarms(temperature, timeMPC)
            # PAUSE state
            elif self.stateofControlInter == 2:
                powerToPwm.value = 0
                self.timer_elapsed(loopTime, timeElapsed)
                self.timer_MPC(0, timeMPC)
            # STOP state
            elif self.stateofControlInter == 3:
                powerToPwm.value = 0
                self.timer = 0
                self.timeMPC = 0
            else:
                print("error in runtime")

            sleep(0.1)

if __name__ == "__main__":
    alarmsList = [[17.0, 0.0, 'shot'], [17.0, 0.1, 'shit']]
    # +++ INTERFACE +++
    # INPUTS
    temperature = Value('d', 18.0)
    stateRequest = Value('i', 1)
    methodRequest = Value('i', 1)
    powerAdding = Value('d', 0.0)
    powerManual = Value('d', 0.0)
    powerFromMpc = Value('d', 10.0)
    powerFromPid = Value('d', 10.0)
    active = Value('i', 1)

    # OUTPUTS
    stateOfControl = Value('i', 1)
    powerToPwm = Value('d', 0.0)
    timeElapsed = Value('d', 0.0)
    timeMPC = Value('d', 10.0)

    l_ctr_interface = [temperature, stateRequest, methodRequest, powerAdding, powerManual, powerFromMpc,
                       powerFromPid, active, stateOfControl, powerToPwm, timeElapsed, timeMPC]
    controler = LogicControl()
    controler.run(temperature,  stateRequest, methodRequest, powerAdding, powerManual, powerFromMpc,
                       powerFromPid, active, stateOfControl, powerToPwm, timeElapsed, timeMPC, alarmsList)