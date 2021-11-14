# This is main control script:
# One rule them all. You know!

from multiprocessing import Queue, Process, Value, Array
import Gui_py
import Serial_com
import PWM
import Algo
from Logger import Logger

if __name__ == "__main__":
    # +++ OBJECT INITIALIZATION +++
    algo = Algo.Algo()
    ser = Serial_com.SerComm()
    logger = Logger()
    # --- END OF OBJECT INIT ---

    gui_output = Queue()
    gui_input = Queue()
    sp = Queue()
    power_to_Ard = Array('i', 2)
    power_req = Value('d', 0.0)
    temperature = Value('d', 0.0)

    p1 = Process(target=algo.run, args=[temperature, power_req, gui_output, gui_input])
    p2 = Process(target=PWM.power_to_PWM, args=[power_to_Ard, power_req])
    p3 = Process(target=ser.run, args=[temperature, power_to_Ard])
    p4 = Process(target=Gui_py.Gui, args=[sp, temperature, power_to_Ard, gui_output, gui_input])
    p5 = Process(target=logger.write_csv, args=[temperature, power_req])

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
