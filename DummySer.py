

def simulate():
    temperature = 30
    while True:
        temperature += 0.1

    tem_queue.put(temperature)
    tem_queue.put(temperature)
    tem_queue.put(temperature)

    # reads value from serial communication
            value = ser.readline()
            # make some converting and rounding and sends out
            tem = float(value.decode('UTF-8').replace('\r\n', ''))
            if tem < 0:
                tem = self.last_temp
            tem = 0.8*tem + 0.2*self.last_temp
            self.last_temp = tem
            temperature = round(tem, 1)


