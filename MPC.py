import numpy as nu
import cvxopt as cx
import time
from multiprocessing import Value

class MPC(object):
    def __init__(self, desired_times, desired_data):
        self.xp = desired_times
        self.fp = desired_data

        #  Model - parametrization
        mass = 25  # kg of water
        C = 4200  # thermal capacity of water
        Tau1 = 1 / mass / C
        Tau2 = 265  # intertia of heater time constant of heater transfer function
        gain = 1.0  # gain of heater transfer function
        alpha = 11.25  # energy loss coeficient
        max_power = 2500  # in watts

        # Prediction - parametrization
        self.Tpred = 65  # prediction step in seconds
        self.Thor = 5 * 260  # prediction horizon in seconds
        self.N = round(self.Thor / self.Tpred)  # predition steps

        # observer init
        self.XO = nu.matrix([15, 0, 22]).T
        self.DXO = nu.matrix([0, 0, 0]).T
        self.Time0 = 0
        # matrix of feedback
        self.L = nu.matrix([[0.1], [0.5], [0]])

        #  MAtrices of system used in prediction
        A = nu.matrix([[-alpha * Tau1, Tau1, alpha * Tau1], [0, -1 / Tau2, 0], [0, 0, 0]])
        B = nu.matrix([[0], [gain / Tau2], [0]])
        C = nu.matrix([1, 0, 0])
        self.Ad = A
        self.Bd = B

        self.C = C

        # Discretization of state matrices
        Ad = nu.add(A * self.Tpred, nu.eye(3))
        Bd = B * self.Tpred
        AA = Ad
        SubBB = Bd
        SubAA = Ad


        # Creation of Big matrixes for N states prediction
        for kk in range(self.N):
            # print(nu.dot(SubAA, Bd))
            SubBB = nu.concatenate((SubBB, nu.dot(SubAA, Bd)), axis=0)
            # = nu.matrix([, [nu.dot(SubAA, Bd)]])
            SubAA = nu.dot(Ad, SubAA)
            AA = nu.concatenate((AA, SubAA), axis=0)

        # size of Bd m = 3
        m = 3
        BB = nu.zeros((m * self.N, self.N))

        for kk in range(self.N):
            for jj in range(m * self.N - m * kk):
                BB[jj + m * kk][kk] = SubBB[jj]

        # MPC bounds
        # weigth matrix
        Qz = nu.eye(self.N)

        # Predicting only for first state, so matrices are reduced to decrease difficulty of calculation
        # AA to aa and BB to bb, where xx = XX/3 in state sense
        self.aa = nu.zeros((self.N, 3))
        for gg in range(self.N):
            for nn in range(3):
                self.aa[gg] = AA[m * gg]

        self.bb = nu.zeros((self.N, self.N))

        for gg in range(self.N):
            for nn in range(self.N):
                self.bb[gg][nn] = BB[m * gg][nn]

        # creatin of H matrix for use of qp solver
        H = nu.dot(nu.dot(self.bb.T, Qz), self.bb)
        #  secures symmetry of H matrix
        H = 0.5 * nu.add(H, H.T)
        # rename the amtrix for cvxopt solver H to P
        self.P = cx.matrix(H)

        # Constrain matrixes
        # matrix with maximal limits for u
        G1 = nu.eye(self.N)
        # matrix minimal bounds for u
        G2 = -1 * nu.eye(self.N)
        G = nu.concatenate((G1, G2), axis=0)

        # there could be added some limitation for states
        # G = nu.concatenate((G, bb), axis=0)
        self.G = cx.matrix(G)

        # bounds used for u
        ub = 2500  # upper bound
        lb = 0 # lower bound

        h1 = cx.matrix(nu.ones((self.N, 1)) * ub)
        h2 = cx.matrix(nu.ones((self.N, 1)) * lb)

        # bounds for state tolerance
        # h3 = cx.matrix(nu.ones((N, 1)) * 5)

        h = nu.concatenate((h1, h2), axis=0)

        # h = nu.concatenate((h, h3), axis=0)

        self.h = cx.matrix(h)

        # replacement matrix to q calcualtion
        self.rep_matr = nu.dot(-self.bb.T, Qz)
        cx.solvers.options['show_progress'] = False

    def predict(self, act_time):
    # def predict(self, act_time, X):
        # X = nu.matrix(X).T
        X = self.XO
        pred_timing = nu.linspace(act_time, self.Thor + act_time, self.N)
        reference = nu.interp(pred_timing/60, self.xp, self.fp)
        pred_states = nu.dot(self.aa, X)

        r = [reference.item(kk) - pred_states.item(kk) for kk in range(self.N)]
        q = cx.matrix(nu.dot(self.rep_matr, r))
        # silence the solver :D

        cx.solvers.options['show_progress'] = False
        # shut up you fool
        u_pred = cx.solvers.qp(self.P, q, self.G, self.h)
        u_predx = [round(i, 2) for i in u_pred['x']]

        return [pred_timing, u_predx]

    def observe(self, temperature, u, times):
        currentTime = times
        Ts = round(currentTime - self.Time0, 2)
        # print(Ts)
        # - for debug
        # Ts = 1
        self.XO = nu.add(self.XO, self.DXO * Ts)
        yo = nu.dot(self.C, self.XO)

        y = temperature.value
        self.DXO = nu.add(nu.add(nu.dot(self.Ad, self.XO), nu.dot(self.Bd, u)), nu.multiply(self.L, nu.subtract(y, yo[0])))
        # print(self.DXO)
        self.Time0 = currentTime

        return self.XO
        # print(self.XO)


    def run(self, temperature, powerFromMpc, statesShared, timeMPC, powerToPwm):
        u = 0.0
        counter = -1

        while True:
            # SOLVER CONDITION
            # if temperature.value > 35 and temperature.value < 65:
            #     ub = 1700  # upper bound
            # else:
            #     ub = 2000
            # lb = 0  # lower bound
            # h1 = cx.matrix(nu.ones((self.N, 1)) * ub)
            # h2 = cx.matrix(nu.ones((self.N, 1)) * lb)
            # h = nu.concatenate((h1, h2), axis=0)
            # self.h = cx.matrix(h)
            # SOlVER CONDITION END
            counter += 1
            times = timeMPC.value*60
            states = self.observe(temperature, powerToPwm.value, times)
            states =  nu.matrix.tolist(states)
            statesShared[:] = [states[0][0], states[1][0], states[2][0]]
            self.predict(times)
            if counter == 5 or counter == 0:
                counter = 0
                [pred_timing, u_pred] = self.predict(times)
            u = nu.interp(times, pred_timing, u_pred)
            # print('times: ', times)
            # print('MPC power: ', u)
            powerFromMpc.value = round(u)
            time.sleep(1)


if __name__ == "__main__":
    desired_time = [0, 5, 20, 30, 66, 86, 96, 116, 131, 151, 160, 175]
    xp = [x * 60 for x in desired_time]
    fp = [15, 15, 37, 37, 55, 55, 62, 62, 72, 72, 78, 78]
    # mpc = MPC(xp, fp)
    mpc = MPC(xp, fp)
    temperature = Value('d', 0.0)
    temperature.value = 55.0
    timeMPC = Value('d', 0.0)

    for times in range(0, 1000, 10):
        u = 0
        if times != 0:
            mpc.observe(temperature, u, timeMPC)
            [pred_timing, u_pred] = mpc.predict(times)
            u = nu.interp(times, pred_timing, u_pred)
            # print(u)
