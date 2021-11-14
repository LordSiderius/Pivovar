import serial
import struct
from time import sleep
from multiprocessing import Value, Array


class SerComm(object):
    def __init__(self):
        # creates communication object
        self.last_temp = 0
        self.power_heater = 0
        self.power_coil = 0

    def run(self, tem_queue, power_to_Ard):
        try:
            ser = serial.Serial('COM9', 9600)
        except:
            ser = serial.Serial('COM10', 9600)
            print('Port COM10 was used instead of COM7')

        while True:
            #  clears buffer of serial communication
            ser.flushInput()
            # reads value from serial communication
            value = ser.readline()
            # make some converting and rounding and sends out
            tem = 1.03 * float(value.decode('UTF-8').replace('\r\n', '')) - 1.0

            # low pass filter
            if tem < 0:
                tem = self.last_temp
            tem = 0.8*tem + 0.2*self.last_temp
            self.last_temp = tem
            temperature = round(tem, 1)

            # sends value to other processes
            tem_queue.value = temperature
            print("temperature:", temperature)

            [self.power_heater, self.power_coil] = power_to_Ard[:]
            ser.flushOutput()
            ser.write(struct.pack('>B', int(self.power_heater)))
            ser.write(struct.pack('>B', int(self.power_coil)))
            sleep(0.2)

if __name__ == "__main__":
    tem_queue = Value('d', 0.0)
    power_to_Ard = Array('i', 2)
    ser = SerComm()
    ser.run(tem_queue, power_to_Ard)



