import datetime
import os
import csv
from time import sleep
from multiprocessing import Queue
import time
import numpy as np


class Logger(object):
    def __init__(self):
        if not os.path.exists("result"):
            os.mkdir("result")

        self.path = 'result\\temperature' + datetime.datetime.today().strftime('%Y%m%d') + '_' \
                    + str(datetime.datetime.now().strftime('%H%M%S')) + '.csv'
        csv_file = open(self.path, 'a', newline='\n')
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(['Time[min]', 'Temperature[°C]', 'Reference Temperature[°C]', 'Power[W]',
                         'Power Heater[W]', 'Power Coil[W]', 'Observer state Temperature[°C]',
                         'Observer state Power[W]', 'Observer state Ambient temperature[°C]'])
        self.time0 = time.time()

    def write_csv(self, temperature, power_req, states_shared, timeMPC, desired_time, desired_temps, power_heater,
                  power_coil):
        while True:
            csv_file = open(self.path, 'a', newline='\n')
            writer = csv.writer(csv_file, delimiter=';')

            # reference calculation
            reftemp = str(np.interp(timeMPC.value, desired_time, desired_temps))
            temp = str(temperature.value)
            power = str(power_req.value)
            powerHeater = str(power_heater.value)
            powerCoil = str(power_coil.value)

            # print(states_shared[0])
            writer.writerow([str(round((time.time() - self.time0)/60, 2)), temp, reftemp, power, powerHeater, powerCoil,
                             str(states_shared[0]), str(states_shared[1]), str(states_shared[2])])
            csv_file.close()
            sleep(10)

if __name__ == "__main__":
    temp = Queue()
