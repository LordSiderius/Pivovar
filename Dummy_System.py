from multiprocessing import Value, Array
from time import sleep

class Dummyplant(object):
    def __init__(self):
        m = 15
        C = 4200
        self.temperature = 17.0
        self.accHeat = C * m * self.temperature
        self.alpha = 11.25
        self.time0 = 0
        self.simBoost = 1.0

    def calculateTemp(self, temperature, timeElapsed, statesShared, powerToPwm):
        # +++ for debug only +++
        # timeElapsed.value += 0.5
        # --- for debug only ---

        m = 15
        C = 4200
        currentTime = timeElapsed.value
        Ts = (currentTime - self.time0) * 60
        # print('Ts: ', Ts)
        addedHeat = Ts * statesShared[1]
        # print('real power: ', statesShared[1])
        # print('addedHeat: ', addedHeat)
        # print('statesShared: ', statesShared[2])
        # print('temperature: ', temperature.value)
        heatLos = - self.alpha * (temperature.value - statesShared[2]) * Ts
        # print('heatLos: ', heatLos)
        # print('power to PWM: ', powerToPwm.value)
        deltaHeat = (addedHeat + heatLos) * self.simBoost
        self.accHeat += deltaHeat
        self.temperature = self.accHeat / m / C
        self.time0 = currentTime
        temperature.value = self.temperature
        # print(temperature.value)

    def run(self, active, temperature, timeElapsed, statesShared, powerToPwm):
        while(active.value == 1):
            self.calculateTemp(temperature, timeElapsed, statesShared, powerToPwm)
            sleep(0.5)



if __name__ == "__main__":
    # +++ INTERFACE +++
    temperature = Value('d', 22.0)
    timeElapsed = Value('d', 0.0)
    powerToPwm = Value('d', 2000.0)
    statesShared = Array('d', [17, 0, 22])
    active = Value('i', 1)
    # --- INTERFACE ---
    DSy_interface = [active, temperature, timeElapsed, statesShared, powerToPwm]

    plant = Dummyplant()
    plant.run(active, temperature, timeElapsed, statesShared, powerToPwm)
