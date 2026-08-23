from _paths import F, OUT
import numpy as np
from golden import mixer, PHASE_W
M=1<<PHASE_W

print("="*66)
print("TEST 1: rotacija vektora (511,0) za male pozitivne uglove")
print("="*66)
print("Matematicki pozitivan smer => y treba da RASTE (vektor ide ka +90 st.)")
for deg in [0,15,30,45,60,75,90]:
    ph=int(deg/360*M)
    I,Q=mixer(511,0,ph)
    ang=np.degrees(np.arctan2(Q,I))%360
    print(f"  zadato {deg:3d} st -> izlaz ({I:5d},{Q:5d}), izmereni ugao = {ang:7.2f} st")

print("\n"+"="*66)
print("TEST 2: rotacija vektora koji vec ima fazu (provera (I+jQ)*e^{+j0})")
print("="*66)
# ulaz pod 30 st, rotacija za 45 st -> ocekuje se 75 st
I0=int(round(400*np.cos(np.radians(30)))); Q0=int(round(400*np.sin(np.radians(30))))
ph=int(45/360*M)
I,Q=mixer(I0,Q0,ph)
print(f"  ulaz  ({I0},{Q0}) = 400 pod 30 st")
print(f"  izlaz ({I},{Q}) = {np.hypot(I,Q):.1f} pod {np.degrees(np.arctan2(Q,I)):.2f} st")
print(f"  ocekivano: 400 pod 75.00 st  -> {'TACNO' if abs(np.degrees(np.arctan2(Q,I))-75)<1 else 'GRESKA'}")

print("\n"+"="*66)
print("TEST 3: smer pomeraja spektra")
print("="*66)
fclk=983.04e6; LAT=13
o=np.loadtxt(F('const_out.txt'),dtype=int)[LAT:LAT+16384]
x=o[:,0]+1j*o[:,1]
X=np.abs(np.fft.fft(x))**2
k=np.argmax(X); N=len(x)
f=k/N*fclk/1e6
f_signed = f if f<fclk/2e6 else f-fclk/1e6
print(f"  nosilac u binu {k} od {N} -> f = {f_signed:+.2f} MHz")
print(f"  {'POZITIVNA ucestanost -> mnozenje sa e^{+j*Omega0*n} -> POZITIVAN smer' if f_signed>0 else 'NEGATIVNA -> pogresan smer!'}")
