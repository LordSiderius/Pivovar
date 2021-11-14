from time import sleep
from multiprocessing import Value, Array


class SerComm(object):
    def __init__(self):
        # creates communication object
        self.tamb = 22.0
        self.last_temp = 20.0
        self.power_heater = 0
        self.power_coil = 0
        self.last_power_heater = 0.0

    def run(self, tem_queue, power_to_ard):
        while True:
            [self.power_heater, self.power_coil] = power_to_ard[:]
            power_heat = 0.01 * self.power_heater + 0.99 * self.last_power_heater
            self.last_power_heater = power_heat

            # make some converting and rounding and sends out
            if self.last_temp < 90.0:
                temAdd = (2000 * self.power_coil + 1500 * power_heat * 0.8 + 10 * (self.tamb - self.last_temp)) / 4200\
                         / 15 * 0.2
                tem = temAdd + self.last_temp
            else:
                temAdd = (2000 * self.power_coil + 1500 * power_heat * 0.8 + 10 * (self.tamb - self.last_temp) - 500) \
                         / 4200 / 15 * 0.2
                tem = temAdd + self.last_temp

            self.last_temp = tem
            temperature = round(tem, 1)

            # sends value to other processes
            tem_queue.value = temperature

            sleep(0.2)


if __name__ == "__main__":
    tem_queue = Value('d', 0.0)
    power_to_Ard = Array('i', 2)
    ser = SerComm()
    ser.run(tem_queue, power_to_Ard)
