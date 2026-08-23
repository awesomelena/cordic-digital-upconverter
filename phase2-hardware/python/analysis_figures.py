"""Dodatne slike za izvjestaj: konvergencija i tacnost CORDIC algoritma."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from golden import N_ITER, ATAN_LUT, ANG_W, PHASE_W, mixer, cordic_rot, prerotate, K_FIX, K_SHIFT, GUARD

# ---------- 1. KONVERGENCIJA: rezidualni ugao po iteracijama ----------
def rezidual(theta):
    """Vraca |z_i| poslije svake iteracije, u radijanima."""
    z = int(round(theta/(2*np.pi)*2**ANG_W))
    out=[abs(z)/2**ANG_W*2*np.pi]
    for i in range(N_ITER):
        s = -1 if z<0 else 1
        z = z - s*ATAN_LUT[i]
        out.append(abs(z)/2**ANG_W*2*np.pi)
    return out

plt.figure(figsize=(6.4,3.6))
for th_deg in [10,30,50,70,89]:
    r=rezidual(np.radians(th_deg))
    plt.semilogy(range(len(r)), r, 'o-', ms=3.5, lw=1.1, label=f"$z_0$ = {th_deg}°")
gran=[2.0**-(i-1) for i in range(1,N_ITER+2)]
plt.semilogy(range(N_ITER+1), gran, 'k--', lw=1.3, label="granica $2^{-(i-1)}$")
plt.xlabel("broj izvršenih iteracija $i$"); plt.ylabel("$|z_i|$  [rad]")
plt.title("Konvergencija: smanjenje rezidualnog ugla")
plt.grid(True, which='both', alpha=.3); plt.legend(fontsize=8); plt.xticks(range(N_ITER+1))
plt.tight_layout(); plt.savefig('konvergencija.png', dpi=140); plt.close()
print("napravljena: konvergencija.png")

# ---------- 2. TACNOST: greska po uglu, kroz pun krug ----------
Ng=1024
ang=np.arange(Ng)/Ng*2*np.pi
err=[]; Io=[]; Qo=[]
for k in range(Ng):
    ph=int(k/Ng*2**PHASE_W)
    a,b=mixer(511,0,ph); Io.append(a); Qo.append(b)
    err.append(np.hypot(a-511*np.cos(ang[k]), b-511*np.sin(ang[k])))
err=np.array(err)

fig,axs=plt.subplots(1,2,figsize=(9.2,3.6))
axs[0].plot(np.degrees(ang), err, lw=0.8)
axs[0].axhline(err.mean(), color='r', ls='--', lw=1, label=f"srednja {err.mean():.2f} LSB")
axs[0].set_xlabel("zadati ugao [°]"); axs[0].set_ylabel("greška [LSB]")
axs[0].set_title(f"Greška izlaza (max {err.max():.2f} LSB, RMS {np.sqrt((err**2).mean()):.2f} LSB)")
axs[0].grid(alpha=.3); axs[0].legend(fontsize=8); axs[0].set_xlim(0,360)

axs[1].plot(Io, Qo, '.', ms=1.6)
t=np.linspace(0,2*np.pi,400)
axs[1].plot(511*np.cos(t), 511*np.sin(t), 'r--', lw=0.9, label="idealna kružnica")
axs[1].set_aspect('equal'); axs[1].grid(alpha=.3); axs[1].legend(fontsize=8)
axs[1].set_xlabel("$x_n$ (I)"); axs[1].set_ylabel("$y_n$ (Q)")
axs[1].set_title("Izlaz jezgra pri rotaciji kroz pun krug")
plt.tight_layout(); plt.savefig('tacnost.png', dpi=140); plt.close()
print("napravljena: tacnost.png")

# ---------- 3. TABELA UGLOVA ----------
plt.figure(figsize=(6.4,3.4))
i=np.arange(N_ITER)
tacno=np.degrees(np.arctan(2.0**-i))
plt.semilogy(i, tacno, 'o-', ms=4, lw=1.2, label=r"$\theta_i=\arctan 2^{-i}$")
plt.semilogy(i, np.degrees(2.0**-i), 's--', ms=3, lw=1, alpha=.7, label=r"$2^{-i}$ (aproksimacija)")
plt.xlabel("iteracija $i$"); plt.ylabel(r"$\theta_i$  [°]")
plt.title("Uglovi mikrorotacija")
plt.grid(True, which='both', alpha=.3); plt.legend(fontsize=8); plt.xticks(i)
plt.tight_layout(); plt.savefig('uglovi.png', dpi=140); plt.close()
print("napravljena: uglovi.png")
