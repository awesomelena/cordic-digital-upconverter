from _paths import F, OUT
import numpy as np
from golden import mixer, PHASE_W
I,Q=np.loadtxt(F('input_iq.txt'),dtype=int,unpack=True)
out=np.loadtxt(F('output_iq.txt'),dtype=int); Ih,Qh=out[:,0],out[:,1]
W=214259029; M=1<<PHASE_W; LAT=16; PM=1
n=len(I)
Ig=np.empty(n,int); Qg=np.empty(n,int)
for k in range(n):
    Ig[k],Qg[k]=mixer(int(I[k]),int(Q[k]),((k+PM)*W)%M)
dI=Ih[LAT:LAT+n]-Ig; dQ=Qh[LAT:LAT+n]-Qg
print(f"odbiraka: {n}")
print(f"max|dI|={np.max(np.abs(dI))}  max|dQ|={np.max(np.abs(dQ))}")
print(">>> BIT-TACNO POKLAPANJE <<<" if (np.all(dI==0) and np.all(dQ==0)) else "NESLAGANJE")
np.savetxt(OUT('golden_iq.txt'), np.column_stack([Ig,Qg]), fmt='%d')
