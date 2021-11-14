# PWM for SSR reley
# imput will be power,whcih will be recalcualted to time zone.
# amplitute of coil is 2000 W, so base time period for heating will be 30 seconds.
#  with 5 seconds as minimal time and 25 seconds maximal.

# Timer will be needed, interrupt of one cycle is not possible. Only by stop command

import time
from multiprocessing import Value, Array

def power_to_PWM(power_to_Ard, power_req, power_heater, power_coil):
        while True:
            # Input
            power = power_req.value  # required power
            # print("power", power)
            # model parametrization
            Pc = 2000  # ma power of coil in [W]
            Ph = 1500  # max power of heater [W]
            tmax = 20  # heating cycle period [s]
            kc = 0.2  # minimum weight for time when coil is used[-]
            # kc = 0.0 # minimum weight for time when coil is used[-]

            #  power request distribution
            Preq_h = power * (1 - kc)  # power request fot heater
            Preq_c = power * kc  # power request for coil

            th = Preq_h * tmax / Ph  # time, when heater will be active
            tc = Preq_c * tmax / Pc  # time, when coil will be active

            # searching algorithm, if power is not enough 1500 - 2000 W
            while tc + th > tmax:
                tc = tc + 0.1
                th = (power * tmax - Pc * tc) / Ph

            # calculated heating times saturation
            tc = min(max(tc, 0), tmax)
            th = min(max(th, 0), tmax)

            power_heater.value = th/tmax * Ph
            power_coil.value = tc/tmax * Pc

            # debugging check
            # print('th, tc', [th, tc])
            # print('power', power)

            time0 = time.time()
            while time.time() < time0 + th:
                # sets if [heater, coil] is active
                power_to_Ard[:] = [1, 0]
                # print('power:', power_to_Ard[:])
                time.sleep(0.05)

            time0 = time.time()
            while time.time() < time0 + tc:
                # sets if [heater, coil] is active
                power_to_Ard[:] = [0, 1]
                # print('power:', power_to_Ard[:])
                time.sleep(0.05)

            time0 = time.time()
            while time.time() < time0 + (tmax - tc - th):
                # sets if [heater, coil] is active
                power_to_Ard[:] = [0, 0]
                # print('power:', power_to_Ard[:])
                time.sleep(0.05)
            # print('cycle end')

if __name__ == "__main__":
    power_req = Value('d', 0.0)
    power_to_Ard = Array('i', 2)
    power_req.value = 600

    ser = power_to_PWM(power_to_Ard, power_req)



