"""
Priprema ulaznih odbiraka za simulaciju druge faze.

Pravi:
  data/input_iq.txt  - interpolirani test signal (izlaz Faze 1), 10 bita
  data/const_in.txt  - konstantan ulaz I=511, Q=0 (za mjerenje SFDR)

Pokretanje:  python gen_input.py
"""
import os
import numpy as np
import scipy.signal as signal
from remezhb import remezhb
from remezlp import remezlp

# --- gdje su podaci ---------------------------------------------------
def data_dir():
    for d in (os.path.join('..', 'data'), 'data', '.'):
        if os.path.isdir(d):
            return d
    os.makedirs('data', exist_ok=True)
    return 'data'

def find(name):
    for p in (name, os.path.join('..', 'data', name), os.path.join('data', name)):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        f"Ne mogu da nadjem {name}. Provjeri da je u istom folderu ili u data/.")

OUT = data_dir()

# --- parametri iz prve faze -------------------------------------------
fs   = 61.44e6
fmax = 25.0e6
AdB  = 60.0
delta = 10.0**(-AdB/20.0)

x = np.array([complex(l) for l in open(find('testsignal.txt'))])

def interp_stage(x, h, M):
    """Ekspander (faktor M) + FIR filtar, sa ciklicnim produzenjem."""
    N = len(h)
    up = np.zeros(len(x)*M, dtype=complex)
    up[::M] = x
    ext = np.concatenate((up[-(N-1):], up))
    return np.roll(signal.lfilter(h, 1, ext)[N-1:], -(N//2))

# kaskada 2 x 2 x 2 x 2 (tri polupojasna + jedan niskopropusni)
h1 = remezhb(fmax/(2*fs),  AdB); y = interp_stage(x, h1, 2)
h2 = remezhb(fmax/(4*fs),  AdB); y = interp_stage(y, h2, 2)
h3 = remezhb(fmax/(8*fs),  AdB); y = interp_stage(y, h3, 2)
Fp4 = fmax/(16*fs); Fst4 = (8*fs - fmax)/(16*fs)
h4 = remezlp(Fp4, Fst4, delta, delta); y = interp_stage(y, h4, 2)

print(f"broj koeficijenata: HB1={len(h1)}, HB2={len(h2)}, HB3={len(h3)}, LP4={len(h4)}")
print(f"interpoliranih odbiraka: {len(y)}   (fs_izlaz = 983.04 MHz)")

# --- kvantizacija na 10 bita ------------------------------------------
# skalira se tako da |I+jQ| ostane unutar pune skale, bez prelivanja
peak  = np.max(np.abs(y))
scale = (2**9 - 1)/peak * 0.98
I = np.clip(np.round(np.real(y)*scale).astype(int), -512, 511)
Q = np.clip(np.round(np.imag(y)*scale).astype(int), -512, 511)
print(f"max|I+jQ| = {np.max(np.hypot(I,Q)):.1f}  (granica 724)")

p_in = os.path.join(OUT, 'input_iq.txt')
np.savetxt(p_in, np.column_stack([I, Q]), fmt='%d')
print(f"upisano: {p_in}")

# --- konstantan ulaz za mjerenje SFDR ---------------------------------
N = len(I)
p_const = os.path.join(OUT, 'const_in.txt')
np.savetxt(p_const, np.column_stack([np.full(N, 511), np.zeros(N, int)]), fmt='%d')
print(f"upisano: {p_const}   (I=511, Q=0)")
