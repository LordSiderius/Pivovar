% Script to calculate and optimize paramters for brewery SW
% ARX model try outs
% State model as comparison

close all
clear xsim theta yhat y u
data = csvread('16-04-2020_Mnich_10.csv',1);
time = data(3:end, 2)*60;
temp = data(3:end, 3);
tempref = data(3:end, 4);
power = data(3:end, 5);

% Time[min],
% Temperature[°C],
% Reference Temperature[°C],
% Power[W],
% Observer state Temperature[°C],
% Observer state Power[W],
% Observer state Ambient temperature[°C]
tmax = 1;
uh = zeros(1, length(power));
uc = zeros(1, length(power));
for item = 1:length(power)   
    th = power(item)/1500;
        if th > tmax
        for k = 0.2:0.2:1
            th = (1-k) * power(item) / 1500;
            tc = k * power(item) / 2000;
            if th + tc <= tmax
                uh(item) = th*1500;
                uc(item) = tc *2000;
            end
        end
        else
            uc(item)
            uh(item) = power(item);
    end
end

Nstart = 1;
Nend = 500;

temp = temp(Nstart:Nend);
uh = uh(Nstart:Nend);
uc = uc(Nstart:Nend);
power = power(Nstart:Nend);

N = round(length(temp));
Tamb = 20 * ones(1,N);

gain = 1.05;
alpha = 11;
tau1 = 1/4200/12;
tau2 = 300; 
A = [-alpha*tau1    tau1    alpha*tau1; 
            0                    -1/tau2                  0          ;
            0                       0                       0];

B = [      0            tau1;
        gain/tau2    0;
                0             0];
            
 C = [1 0 1];
 
 D = [0 0];

y = [temp(1:N-1)';
        Tamb(1:N-1)];
    
u =[uh(1:N-1)/1500;
        uc(1:N-1)/2000];

% u =  power(1:N-1)'/2000;
    
Z = [y' u'];   
    
yhat = temp(2:N);
theta = Z\(yhat);

xsim(1) = temp(1);
xmod(:,1) = [temp(1), 0, 20]';

for t = 1:N-1
    dt = (time(t+1) - time(t));
    Ad = A * dt + eye(3);
    Bd = B * dt;
    
    xmod(:,t+1) = Ad * xmod(:,t) + Bd * [uh(t), uc(t)]';
    
    z = [xsim(t), Tamb(t), uh(t)/1500, uc(t)/2000];
% z = [xsim(t), Tamb(t), power(t)/2000];
    xsim(t + 1) = theta' * z';
end
    
figure(1)
plot(time(1:N-1), temp(1:N-1), 'k')
hold on
plot(time(1:N-1), xsim(1:N-1))
plot(time(1:N-1), xmod(1 ,1:N-1), 'c')
xlabel('time [s]')
ylabel('temperature [°C]')
legend('Reference', 'ARX sim', 'Model')

figure(2)
plot(time(1:N-1), uh(1:N-1)/1500 , 'r')
hold on
plot(time(1:N-1), uc(1:N-1)/2000 , 'b')
