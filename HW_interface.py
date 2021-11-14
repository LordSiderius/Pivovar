import os
import glob
import time
import RPi.GPIO as gpio

from multiprocessing import Value, Array

class HW_Interface(object):
    def __init__(self):
        #Intial setting of temperature probe
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

        #default setting for pin output
        gpio.setmode(gpio.BCM)
        gpio.setup(2, gpio.OUT)
        gpio.setup(3, gpio.OUT)

        gpio.output(2, 0)
        gpio.output(3, 0)

#definition of functions for temperature read
    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
       
        
    def run(self, tem_queue, power_to_dev):
        
        while True:
            
            #temperature reading from probe
            tem_queue.value = self.read_temp()

            # writting to pins to control power inout
            [self.power_heater, self.power_coil] = power_to_dev[:]
            gpio.output(2, self.power_coil)
            gpio.output(3, self.power_heater)
            
            # sleeps for 1 second
            time.sleep(1)
            
        
if __name__ == "__main__":
    tem_queue = Value('d', 0.0)
    power_to_dev = Array('i', 2)
    power_to_dev[0]= 1
    hw_interface = HW_Interface()
    hw_interface.run(tem_queue, power_to_dev)
