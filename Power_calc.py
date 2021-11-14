import numpy as np

# AC dimmer calculation for 2kW heating coil
power = [1997, 1985, 1904, 1705, 1388, 1198, 998, 798, 608, 437, 291, 176, 93, 11, 0]
super_power = np.ones(len(power))*2000 - power

percents = [0, 10, 20, 30, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100]
rev_percents = np.ones(len(power))*100 - percents


def pwr_to_prc(pwr):
    return int(np.interp(pwr, super_power, percents))


def prc_to_pwr(prc):
    return int(np.interp(prc, percents, super_power))
