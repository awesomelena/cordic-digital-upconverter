from _paths import F, OUT
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
fclk=983.04e6; LAT=16; N=16384
o=np.loadtxt(F('const_out.txt'),dtype=int)[LAT:LAT+N]
x=o[:,0]+1j*o[:,1]
X=np.fft.fft(x)/N
P=np.abs(X)**2
k0=np.argmax(P)
f=np.arange(N)/N*fclk/1e6
print(f"nosilac u bin {k0} -> f = {f[k0]:.3f} MHz (ocekivano 196.14)")
Ps=P[k0]
Pn=P.copy(); Pn[k0]=0
k1=np.argmax(Pn)
SFDR=10*np.log10(Ps/Pn[k1])
SNR =10*np.log10(Ps/np.sum(Pn))
print(f"SFDR = {SFDR:.2f} dB   (najveci spur u binu {k1}, f={f[k1]:.2f} MHz)")
print(f"SNR  = {SNR:.2f} dB   (10-bitni teorijski SQNR = 61.96 dB)")

PdB=10*np.log10(P/Ps+1e-20)
fh=np.fft.fftshift(np.arange(N)/N-0.5)*0  # placeholder
ff=(np.arange(N)/N-0.5)*fclk/1e6
plt.figure(figsize=(7,3.4))
plt.plot(ff,np.fft.fftshift(PdB),lw=0.7)
plt.axhline(-SFDR,color='r',ls='--',lw=1,label=f'SFDR = {SFDR:.1f} dB')
plt.ylim(-120,5); plt.grid(alpha=.3); plt.legend(fontsize=8)
plt.xlabel("f [MHz]"); plt.ylabel("[dBc]")
plt.title("Spektar izlaza CORDIC NCO, konstantan ulaz (koherentno odabiranje)")
plt.tight_layout(); plt.savefig('spektar_nco.png',dpi=140)
print("slika: spektar_nco.png")
