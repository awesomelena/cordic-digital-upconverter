"""Bit-tacan zlatni model protocnog CORDIC kompleksnog mesaca (ANG_W=16)."""
import numpy as np
N_ITER=10; DATA_W=10; GUARD=4; HEAD=1
INT_W=DATA_W+GUARD+HEAD          # 15
PHASE_W=30; ANG_W=16; PH_TRUNC=PHASE_W-ANG_W
K_SHIFT=15; K_FIX=19898
ATAN_LUT=[int(round(np.arctan(2.0**-i)/(2*np.pi)*2**ANG_W)) for i in range(N_ITER)]

def sat(v,w):
    lo,hi=-2**(w-1),2**(w-1)-1
    return max(lo,min(hi,v))

def cordic_rot(x,y,z):
    for i in range(N_ITER):
        s=-1 if z<0 else 1
        xn=x-s*(y>>i); yn=y+s*(x>>i); z=z-s*ATAN_LUT[i]
        x,y=sat(xn,INT_W+2),sat(yn,INT_W+2)
    return x,y,z

def prerotate(I,Q,phase):
    """Predrotacija se radi na ULAZNIM odbircima, prije skaliranja sa K."""
    quad=(phase>>(PHASE_W-2))&3
    resid=(phase>>PH_TRUNC)&((1<<(ANG_W-2))-1)
    if   quad==0: x,y=I,Q
    elif quad==1: x,y=-Q,I
    elif quad==2: x,y=-I,-Q
    else:         x,y=Q,-I
    return x,y,resid

def mixer(I,Q,phase):
    xp,yp,z0=prerotate(I,Q,phase)                  # 1. predrotacija
    x0=(xp*K_FIX)>>(K_SHIFT-GUARD)                 # 2. skaliranje sa K
    y0=(yp*K_FIX)>>(K_SHIFT-GUARD)
    xn,yn,_=cordic_rot(x0,y0,z0)
    Io=(xn+(1<<(GUARD-1)))>>GUARD; Qo=(yn+(1<<(GUARD-1)))>>GUARD
    return sat(Io,DATA_W),sat(Qo,DATA_W)
