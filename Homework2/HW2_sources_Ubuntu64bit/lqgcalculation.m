function [ctrl,L,obs,K,Kf,sysd] = lqgcalculation(sys,Q,R1,R2,h,tau)
% Arguments:
% sys         The continuous time plant to be controlled.
% Q           The continuous time cost matrix Q (see above).
% R1          The state noise variance (in continuous time).
% R2          The output noise variance (in discrete time). This is
%             simply the error variance of each sample.
% h           The sample period of the controller (in seconds).
% 
% Optional arguments:
% tau         The delay (in seconds) in the plant. tau <= h, i.e.
%             the delay has to be less than one sample period.
% Return values:
% ctrl        The LQG controller as an LTI system.
% L           The control gain vector L. 
% Obs         The observer as an LTI system.
% K, Kbar     The observer gains.
% sysd        The sampled time-delayed plant as an LTI system.

origclass = class(sys);

sys = ss(sys);
A = sys.a;
B = sys.b;
C = sys.c;
D = sys.d;

totsize = size(A,2)+size(B,2);
outinsize = size(C,1)+size(B,2);
if (size(Q,1) ~= totsize | size(Q,2) ~= totsize)
  if (isempty(Q))
    % No cost
    Q = zeros(totsize);
  else
    if (size(Q,1) == outinsize & size(Q,2) == outinsize)
      % Input-output cost
      xutoyu = blkdiag(C,eye(size(B,2)));
      Q = xutoyu'*Q*xutoyu;
    else
     
    end
  end
end
if (size(R1,1) ~= size(A,1) | size(R1,2) ~= size(A,2))
  if (size(R1,1) == size(B,2) & size(R1,2) == size(B,2))
    % Input noise
    R1 = B*R1*B';
  else
  
  end
end

n = size(A,1);
sysc = ss(A,B,C,D);
sysd = c2d(sysc,h);
[Phi,Gamma] = ssdata(sysd);

if nargin == 5
  tau = 0;
end
% constant delay design
[Phi2,r,Q2] = calcc2d([A B;zeros(size(B,2),size(A,2)+size(B,2))],...
			blkdiag(R1,zeros(size(B,2))),Q,tau);
Gamma2 = Phi2(1:size(A,1),size(A,2)+1:size(A,2)+size(B,2));
[X,r,Q1] = calcc2d([A B;zeros(size(B,2),size(A,2)+size(B,2))],...
		     blkdiag(R1,zeros(size(B,2))),Q,h-tau);
Gamma2 = X(1:size(A,1),1:size(A,2))*Gamma2; % Slide
Gamma1 = X(1:size(A,1),size(A,2)+1:size(A,2)+size(B,2));
[Phi,R1,Q,Qconst] = ...
    calcc2d([A B;zeros(size(B,2),size(A,2)+size(B,2))],...
	      blkdiag(R1,zeros(size(B,2))),Q,h);
R1 = R1(1:size(A,1),1:size(A,2));
Phi = Phi(1:size(A,1),1:size(A,2));

L = dlqr([Phi Gamma2; zeros(size(B,2),size(A,2)+size(B,2))],...
	 [Gamma1; eye(size(B,2))],...
	 Q2+Phi2(1:size(A,1),:)'*Q1(1:size(A,1),1:size(A,2))*...
	 Phi2(1:size(A,1),:),...
	 Q1(size(A,1)+1:end,size(A,1)+1:end)+eps,... 
	 [Phi2(1:size(A,1),:)'*Q1(1:size(A,1),size(A,1)+1:end)]);

sys = ss([Phi Gamma2; zeros(size(B,2),size(A,2)+size(B,2))],...
	 [[Gamma1; eye(size(B,2))] [eye(size(A,1));zeros(size(B,2),size(A,1))]],[C zeros(size(C,1),size(B,2))],0,h);
[kest,K,p,Kf] = kalman(sys,R1,R2);
ctrl = (lqgreg(kest,L));
obs = kest;

sysd = ss([Phi Gamma2; zeros(size(B,2),size(A,2)+size(B,2))],...
	 [Gamma1; eye(size(B,2))],[C zeros(size(C,1),size(B,2))],0,h);


