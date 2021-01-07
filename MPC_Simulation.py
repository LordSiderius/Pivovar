import numpy as nu
import os
import copy
from matplotlib import pyplot as pl
import cvxopt as cx

# MPC required, Desired data, actual time and actual state of system


# def mpc(X0, actual_time):
#
#
#
#
#    return [times, us]

desired_time = [0, 5, 20, 30, 66, 86, 96, 116, 131, 151, 160, 175]
xp = [x*60 for x in desired_time]
fp = [10, 10, 37, 37, 55, 55, 62, 62, 72, 72, 78, 78]


#  Model - parametrization
mas = 15
C = 4200
Tau1 = 1 / mas / C
Tau2 = 265
gain = 1.27
alpha = 11.25

# Simulation - parametrization
Ts = 0.1
final_time = int(10500 / Ts)

# Prediction - parametrization
Tpred = 65  # prediction step in seconds
Thor = 5 * 260  # prediction horizon in seconds
N = round(Thor / Tpred)  # prediction steps
Tpred_period = 65  # prediction execution period

# State model matrices Calculation
A = nu.matrix([[-alpha * Tau1, Tau1, alpha * Tau1], [0, -1 / Tau2, 0], [0, 0, 0]])
X0 = nu.matrix([[10], [0], [22]])

B = nu.matrix([[0], [gain / Tau2], [0]])
u = nu.matrix([200])

C = nu.matrix([1, 0, 0])
# Simulation - Init  conditions for simulation
X = copy.copy(X0)

DXO = nu.matrix([[0], [0], [0]])
XO = nu.matrix([[10], [0], [22]])

L = nu.matrix([[0.1], [0.5], [0]])
y = 55

temp_sim = []
temp_beer = []
power_real = []
temp_ambient = []
time = []
for k in range(1):
   time.append(k * Ts)
   # simualtion
   DX = nu.add(nu.dot(A, X), nu.dot(B, u))
   X = nu.add(X, DX * Ts)
   # print(X)
   y = nu.dot(C, X)
   temp_sim.append(round(y.item(0), 1))

   # observer
   XO = nu.add(XO, DXO * Ts)
   yo = nu.dot(C, XO)

   DXO = nu.add(nu.add(nu.dot(A, XO), nu.dot(B, u)), nu.multiply(L, nu.subtract(y, yo[0])))
   temp_beer.append(round(XO.item(0), 1))
   power_real.append(round(XO.item(1)))
   temp_ambient.append(round(XO.item(2), 1))

# MPC part
desired_data = [10, 10, 37, 37, 55, 55, 62,  62,  72,  72,  78, 78]
desired_time = [ 0,  5, 20, 30, 66, 86, 96, 116, 131, 151, 160, 175] * 60



# Discretization of state Matrixes
Ad = nu.add(A * Tpred, nu.eye(3))
Bd = B * Tpred
AA = Ad
SubBB = Bd
SubAA = Ad

for kk in range(N):
   # print(nu.dot(SubAA, Bd))
   SubBB = nu.concatenate((SubBB, nu.dot(SubAA, Bd)), axis=0)
   # = nu.matrix([, [nu.dot(SubAA, Bd)]])
   SubAA = nu.dot(Ad, SubAA)
   AA = nu.concatenate((AA, SubAA), axis=0)

# size of Bd m = 3
m = 3
BB = nu.zeros((m * N, N))

for kk in range(N):
   for jj in range(m*N  - m*kk):
       BB[jj + m*kk][kk] = SubBB[jj]

# MPC bounds
# weigth matrix
Qz = nu.eye(N)



aa = nu.zeros((N,3))
for gg in range(N):
   for nn in range(3):
      aa[gg] = AA[m * gg]

bb = nu.zeros((N,N))

for gg in range(N):
   for nn in range(N):
       bb[gg][nn] = BB[m * gg][nn]

H = nu.dot(nu.dot(bb.T, Qz), bb)
H = 0.5 * nu.add(H, H.T)
P = cx.matrix(H)

# Constrain matrixes
# matrix with maximal limits for u
G1 = nu.eye(N)
G2 = -1 * nu.eye(N)
G = nu.concatenate((G1, G2), axis=0)

# G = nu.concatenate((G, bb), axis=0)
G = cx.matrix(G)

print(G)

h1 = cx.matrix(nu.ones((N, 1)) * 1700)
h2 = cx.matrix(nu.ones((N, 1)) * 0)

# h3 = cx.matrix(nu.ones((N, 1)) * 5)

h = nu.concatenate((h1, h2), axis=0)
# h = nu.concatenate((h, h3), axis=0)
h = cx.matrix(h)
print(h)
rep_matr = nu.dot(-bb.T, Qz)

sim_time = []
temp_sim = []
u_total = []
X = X0
for k in range(final_time):
   sim_time.append(k * Ts)
   time.append(k * Ts)
   # simualtion
   # # observer
   # XO = nu.add(XO, DXO * Ts)
   # yo = nu.dot(C, XO)
   # y = yo.item(0)
   # DXO = nu.add(nu.add(nu.dot(A, XO), nu.dot(B, u)), nu.multiply(L, nu.subtract(y, yo[0])))
   # temp_beer.append(round(XO.item(0), 1))
   # power_real.append(round(XO.item(1)))
   # temp_ambient.append(round(XO.item(2), 1))


   pred_timing = nu.linspace(k * Ts, Thor + (k * Ts), N)
   reference = nu.interp(pred_timing, xp, fp)
   pred_states = nu.dot(aa, X)

   r = [reference.item(kk)-pred_states.item(kk) for kk in range(N)]
   q = cx.matrix(nu.dot(rep_matr, r))
   # print("H: ", H)
   # print('Q: ', q)

   # print((k*Ts % Tpred))
   if (k*Ts % Tpred_period) == 0.0:
      u_pred = cx.solvers.qp(P, q, G, h)
      u_predx = [i for i in u_pred['x']]
   # print(u_pred)
   # print('end--------------------')
   # print(u_pred['x'])


   u = nu.interp(k*Ts, pred_timing, u_predx)

   DX = nu.add(nu.dot(A, X), nu.dot(B, u))
   X = nu.add(X, DX * Ts)
   # print(X)
   temp_sim.append(round(X.item(0), 2))
   u_total.append(u)

# print(temp_sim)
# pl.plot(sim_time, temp_sim)
# pl.plot(time, temp_beer)
# pl.plot(time, power_real)
# pl.plot(time, temp_ambient)
# pl.plot(xp, fp)
# pl.plot(sim_time, u_total)
fig, axs = pl.subplots(2)
fig.suptitle('Vertically stacked subplots')
axs[0].plot(sim_time, u_total)
axs[1].plot(sim_time, temp_sim)
axs[1].plot(xp, fp)
pl.show()
