from _paths import F, OUT
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

fclk=983.04e6; LAT=16
I,Q=np.loadtxt(F('input_iq.txt'),dtype=int,unpack=True)
out=np.loadtxt(F('output_iq.txt'),dtype=int)
Io,Qo=out[LAT:LAT+len(I),0], out[LAT:LAT+len(I),1]
xin=I+1j*Q; xout=Io+1j*Qo
n=len(xin); f=(np.arange(n)/n-0.5)*fclk/1e6

def sp(x):
    X=np.fft.fftshift(np.abs(np.fft.fft(x)))
    return 20*np.log10(X/np.max(X)+1e-15)

fig,axs=plt.subplots(2,1,figsize=(7,5.4),sharex=True)
axs[0].plot(f,sp(xin),lw=0.7)
axs[0].set_title("Spektar ulaznog signala (osnovni opseg, $f_s=983.04$ MHz)")
axs[0].set_ylabel("[dB]"); axs[0].set_ylim(-90,5); axs[0].grid(alpha=.3)
axs[0].axvline(-25,color='r',ls='--',lw=.8); axs[0].axvline(25,color='r',ls='--',lw=.8)

axs[1].plot(f,sp(xout),lw=0.7,color='tab:green')
axs[1].set_title("Spektar izlaznog signala (translirano na $f_0=196.16$ MHz)")
axs[1].set_ylabel("[dB]"); axs[1].set_xlabel("f [MHz]"); axs[1].set_ylim(-90,5); axs[1].grid(alpha=.3)
axs[1].axvline(196.16,color='r',ls='--',lw=1.0,label='$f_0$=196.16 MHz')
axs[1].axvline(196.16-25,color='r',ls=':',lw=.8); axs[1].axvline(196.16+25,color='r',ls=':',lw=.8)
axs[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig('spektri_mesac.png',dpi=140); plt.close()

# centar mase spektra izlaza -> provera translacije
P=np.abs(np.fft.fftshift(np.fft.fft(xout)))**2
fc=np.sum(f*P)/np.sum(P)
Pin=np.abs(np.fft.fftshift(np.fft.fft(xin)))**2
fcin=np.sum(f*Pin)/np.sum(Pin)
print(f"tezisna ucestanost ULAZA  = {fcin:8.3f} MHz")
print(f"tezisna ucestanost IZLAZA = {fc:8.3f} MHz   (pomak {fc-fcin:.3f} MHz, ocekivano 196.160)")
print("slika: spektri_mesac.png")
