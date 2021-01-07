


if __name__ == "__main__":
    desired_time = [0, 5, 20, 30, 66, 86, 96, 116, 131, 151, 160, 175]
    xp = [x * 60 for x in desired_time]
    fp = [10, 10, 37, 37, 55, 55, 62, 62, 72, 72, 78, 78]

    temperature = Value('d', 0.0)
    temp_update = Value('i', 0)
    algo = Algo_MPC()
    algo.run(temperature, temp_update, [[10], [0], [20]])

