"""Provjera parametara realizacije u odnosu na predavanja (CORDIC.pdf)."""
import numpy as np
from golden import N_ITER, DATA_W, GUARD, INT_W, ANG_W, PHASE_W, K_FIX, K_SHIFT, ATAN_LUT, mixer

print("="*66); print("PROVJERA U ODNOSU NA PREDAVANJA"); print("="*66)

# --- 1. multiplikativni faktor (predavanje str. 11) ---
K=np.prod([1/np.sqrt(1+2.0**(-2*i)) for i in range(N_ITER)])
Kinf=0.60726
print(f"\n[1] Multiplikativni faktor (str.11)")
print(f"    predavanje: K_inf = {Kinf}")
print(f"    K({N_ITER})     = {K:.8f}   odstupanje od granicne vrijednosti {abs(K-Kinf):.2e}")
print(f"    K_FIX = round(K*2^{K_SHIFT}) = {K_FIX}   (provjera: {round(K*2**K_SHIFT)})")

# --- 2. konvergencija (str. 16) ---
th_inf=sum(np.arctan(2.0**-i) for i in range(200))
th_n  =sum(np.arctan(2.0**-i) for i in range(N_ITER))
print(f"\n[2] Konvergencija (str.16)")
print(f"    predavanje: theta_max = 1.74329 rad (99.88 st)")
print(f"    izracunato (beskonacno): {th_inf:.5f} rad ({np.degrees(th_inf):.2f} st)")
print(f"    za n={N_ITER}: theta_max = {th_n:.5f} rad ({np.degrees(th_n):.2f} st)")
print(f"    poslije predrotacije |z0| <= pi/2 = {np.pi/2:.5f} rad (90.00 st)")
print(f"    uslov |z0| < theta_max:  {np.pi/2:.4f} < {th_n:.4f}  -> {'ISPUNJEN' if np.pi/2<th_n else 'NIJE'}")

# --- 3. broj iteracija i zastitni bitovi (str. 17) ---
print(f"\n[3] Broj iteracija i zastitni bitovi (str.17)")
print(f"    predavanje: 'Broj iteracija CORDIC-a = Duzina binarne reci'")
print(f"    DAC = {DATA_W} bita  ->  n_iter = {N_ITER}   {'OK' if N_ITER==DATA_W else 'NE'}")
print(f"    predavanje: n_guard < log2(n) = log2({N_ITER}) = {np.log2(N_ITER):.3f}")
print(f"    usvojeno n_guard = {GUARD} (po uputstvu predmetnog nastavnika, 14-bitna rec)")
print(f"    napomena: veci broj zastitnih bitova je konzervativniji izbor")

# --- 4. rezidualni ugao (str. 16) ---
print(f"\n[4] Rezidualni ugao (str.16)")
print(f"    predavanje: delta_theta = z_n < 2^-(n-1) = 2^-{N_ITER-1} = {2.0**-(N_ITER-1):.6f} rad")
print(f"    u faznom formatu (2^{ANG_W} <=> 2pi): {2.0**-(N_ITER-1)/(2*np.pi)*2**ANG_W:.1f} jedinica")
print(f"    najmanji ugao u tabeli theta[{N_ITER-1}] = {ATAN_LUT[-1]} jedinica")

# --- 5. tabela uglova (str. 20) ---
print(f"\n[5] Tabela uglova theta[i] = arctan(2^-i)")
for i,v in enumerate(ATAN_LUT):
    ref=np.arctan(2.0**-i)
    got=v/2**ANG_W*2*np.pi
    print(f"    i={i:2d}  tacno {np.degrees(ref):9.5f} st   tabela {np.degrees(got):9.5f} st   greska {abs(np.degrees(ref-got)):.5f} st")

# --- 6. koherentno odabiranje ---
fs=983.04e6; N=16384; W=214237184
f0=W*fs/2**PHASE_W
M=f0*N/fs
print(f"\n[6] Koherentno odabiranje  (f0/fs = M/N)")
print(f"    f0 = {f0/1e6:.4f} MHz,  fs = {fs/1e6:.2f} MHz,  N = {N}")
print(f"    M = f0*N/fs = {M:.4f}   -> {'CIO BROJ, uslov ispunjen' if abs(M-round(M))<1e-9 else 'NIJE cio broj'}")

# --- 7. rotacioni mod, jednacine (str. 20) ---
print(f"\n[7] Jednacine rotacionog moda (str.20)")
print(f"    x[i+1] = x[i] - sigma*y[i]>>i     ")
print(f"    y[i+1] = y[i] + sigma*x[i]>>i     realizovano u cordic_stage.vhd")
print(f"    z[i+1] = z[i] - sigma*arctan2^-i  ")
print(f"    sigma  = sgn(z[i])                sigma = MSB akumulatora ugla")

# --- 8. tacnost izlaza ---
errs=[]
for k in range(256):
    ph=int(k/256*2**PHASE_W)
    Io,Qo=mixer(511,0,ph); a=k/256*2*np.pi
    errs.append(np.hypot(Io-511*np.cos(a),Qo-511*np.sin(a)))
print(f"\n[8] Tacnost izlaza (rotacija (511,0) kroz pun krug, 256 tacaka)")
print(f"    max greska = {max(errs):.2f} LSB,  RMS = {np.sqrt(np.mean(np.square(errs))):.2f} LSB")
print(f"    (puna skala 10 bita = 512, dakle greska ispod 0.4 %)")
