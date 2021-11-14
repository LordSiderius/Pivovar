# This is main control script:
# One rule them all. You know!
#
#
#

from matplotlib import pyplot as pl
from multiprocessing import Process, Value, Array
import Gui_MPC
import Serial_com
import PWM
import PID
from Logger import Logger
import MPC
from Logic_control import LogicControl
from Dummy_System import Dummyplant
from HW_interface import HW_Interface

if __name__ == "__main__":
    # +++ TRAJECTORY DEFINITION +++
    # test scheme for brewing, where pause is necessary
    desired_time =   [0,  5, 25, 45, 75, 105, 115, 145, 155, 185, 195, 210, 211, 250, 340]
    desired_temps = [25, 25, 37, 37, 55,  55,  62,  62,  72,  72,  80,  80,  65,  99, 99]
    # desired_time =   [0, 10, 20, 40,  55, 80, 90, 105, 105.1, 135,225]
    # desired_temps = [55,  55,  62,  62,  72,  72,  80,  80,  65,  99, 99]
	# desired_time = [0, 10, 20, 40, 55, 80, 90, 105, 105.1, 135, 225]
    # desired_temps = [55, 55, 62, 62,  72, 72, 80,  80,    65,  99,  99]
    # DEBUG ONLY
    # desired_time =   [0, 35, 125]
    # desired_temps =  [65,  99, 99]
    # DEBUG ONLY END
    # alarms list in format [temperature, time from condition, information]
    alarmsList = [[37.0, 0.0, 'pridat slad'], [78.0, 20.0, 'konec infuze'], [98.0, 0.0, 'zacatek chmelovaru - prvni chmeleni'],
                  [98.0, 30.0, '2. chmeleni'], [98.0, 60.0, '3. chmeleni'], [98.0, 90.0, 'konec chmelovaru']]
    # DEBUG ONLY
    # alarmsList = [[17.0, 0.1, 'pridat slad']]
    # DEBUG ONLY END
    pl.plot(desired_time, desired_temps, color='red')
    # for item in alarmsList:
    #     pl.plot(25, item[0], color='blue')
    #     print(item[0])
    pl.grid()
    pl.xlabel('time [min]')
    pl.ylabel('temperature [°C]')
    pl.title('Reference temperature')
    pl.show()
    # --- TRAJECTORY DEFINITION ---

    # +++ INTERFACE +++
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
    power_coil = Value('d', 0.0)
    power_heater = Value('d', 0.0)
    # --- INTERFACE ---


    # +++ OBJECT INITIALIZATION +++
    ser = Serial_com.SerComm()
    controler = LogicControl()
    dsy = Dummyplant()
    mpc = MPC.MPC(desired_time, desired_temps)
    pid = PID.Pid()
    logger = Logger()
    hw_interface = HW_Interface()
    # --- END OF OBJECT INIT ---

    # +++ PROCESSES INTERFACE +++
    ser_interface = [temperature, powerToArd]
    gui_interface = [temperature, tempSetPoint, timeElapsed, timeMPC, powerToPwm, stateOfControl, stateRequest, methodRequest,
                     powerAdding, powerManual, desired_time, desired_temps]
    l_ctr_interface = [temperature, stateRequest, methodRequest, powerAdding, powerManual, powerFromMpc,
                       powerFromPid, active, stateOfControl, powerToPwm, timeElapsed, timeMPC, alarmsList]
    DSy_interface = [active, temperature, timeElapsed, statesShared, powerToPwm]
    mpc_interface = [temperature, powerFromMpc, statesShared, timeMPC, powerToPwm]
    pid_interface = [desired_time, desired_temps, temperature, powerFromPid, timeMPC, active]
    pwm_interface = [powerToArd, powerToPwm, power_heater, power_coil]
    log_interface = [temperature, powerToPwm, statesShared, timeMPC, desired_time, desired_temps, power_heater, power_coil]
    # --- PROCESSES INTERFACE ---


    # +++ PROCESSES INITIALIZATION +++
    comP = Process(target=hw_interface.run, args=ser_interface) # communication
    guiP = Process(target=Gui_MPC.Gui, args=gui_interface)
    l_ctrP = Process(target=controler.run, args=l_ctr_interface)
    # OFFLINE DUMMY PLANT
    # DSP = Process(target=dsy.run, args=DSy_interface)
    # OFFLINE DUMMY PLANT END
    mpcP = Process(target=mpc.run, args=mpc_interface)
    pidP = Process(target=pid.calculate, args=pid_interface)
    pwmP = Process(target=PWM.power_to_PWM, args=pwm_interface)
    logP = Process(target=logger.write_csv, args=log_interface)
    # --- PROCESSES INITIALIZATION ---

    # +++ PROCESSES START +++
    comP.start()
    guiP.start()
    l_ctrP.start()
    # DSP.start()
    mpcP.start()
    pidP.start()
    pwmP.start()
    logP.start()
    # --- PROCESSES START ---

    #  +++ WAIT FOR PROCESSES END +++
    # comP.join()
    guiP.join()
    l_ctrP.join()
    # DSP.join()
    mpcP.join()
    pidP.join()
    # pwmP.join()
    logP.join()
    #  --- WAIT FOR PROCESSES END ---
