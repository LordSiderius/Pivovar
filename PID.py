from multiprocessing import Value, Array
import numpy as nu
from time import sleep
# calculate value for forward model of heating
def forward_value(mass=20.0, koef_ramp=0.8):
    return mass*4200.0*koef_ramp/60


class Pid(object):
    def __init__(self, p=300.0, i=50.0, d=0.0):
        self.time0 = 0.0
        self.u = 0
        self.p = p
        self.i = i
        self.d = d

        self.intg = 0.0
        self.forward = 0.0
        self.e = 0.0

        # error(step -1)
        self.e1 = 0.0
        # error(step-2)
        self.e2 = 0.0



    def calculate(self, desired_time, desired_temperature, temperature, powerFromPid, timeMPC, active, forward=0):
        while active.value == 1:
            currentTime = timeMPC.value
            loopTime = currentTime - self.time0

            setPoint = nu.interp(timeMPC.value, desired_time, desired_temperature)

            error = setPoint - temperature.value

            prop = self.p * (error - self.e1)
            intg = self.i * loopTime * error

            # print('intgr: ', intg)

            # protection from divison by zero
            if loopTime != 0.0:
                derv = self.d * (error - 2*self.e1 + self.e2) / loopTime
            else:
                print('Division by zero')
                derv = 0

            # print('prop', prop, 'intg', self.intg, 'derv', derv)
            self.u += prop + intg + derv + forward - self.forward

            # saturation to maximum power 0 - 2000W
            if self.u > 2000:
                self.u = 2000

            elif self.u < 0:
                self.u = 0

            # saving forward term, necessary because of integration character of PID equation
            self.forward = forward
            self.e1 = error
            self.e2 = self.e1

            self.time0 = currentTime
            # print('PID power', self.u)
            powerFromPid.value = self.u
            sleep(0.5)


if __name__ == '__main__':

    pid = Pid()

    desired_time =   [ 0,  1, 11, 25]
    desired_temps =  [20, 20, 25, 25]
    temperature = Value('d', 17.0)
    tempSetPoint = Value('d', 22.0)
    timeElapsed = Value('d', 0.0)
    timeMPC = Value('d', 0.0)
    stateOfControl = Value('i', 3)
    stateRequest = Value('i', 3)
    methodRequest = Value('i', 1)
    powerAdding = Value('d', 0.0)
    powerManual = Value('d', 0.0)
    powerToArd = Array('i', [0, 0])
    powerToPwm = Value('d', 0.0)
    statesShared = Array('d', [0, 0, 0])
    powerFromMpc = Value('d', 0.0)
    powerFromPid = Value('d', 0.0)
    active = Value('i', 1)

    while True:
        a = pid.calculate(desired_time, desired_temps, temperature, powerFromPid, timeMPC)

