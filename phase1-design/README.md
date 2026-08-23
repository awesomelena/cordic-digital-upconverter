# Phase 1 — System design

Design and analysis of the transmitter signal path, carried out in Python.

Covered in `design.ipynb`:

1. **Multistage interpolator, ×16** — cascade of 2×2×2×2, the first three stages
   half-band. Filter lengths, band edges and operation counts, compared against a
   direct single-stage implementation.
2. **CORDIC NCO parameters** — number of iterations, guard bits, phase
   accumulator width for sub-hertz resolution.
3. **NRZ compensation filter** — inverse-sinc FIR that flattens the zero-order
   hold droop of the DAC to within ±0.025 dB over F ∈ [0, 0.4].
4. **Aperture jitter** — maximum tolerable clock jitter for the quantisation
   noise of a 10-bit converter.

## Files

| File | Purpose |
|---|---|
| `design.ipynb` | The notebook itself |
| `remezhb.py` | Half-band filter design helper (provided with the assignment) |
| `remezlp.py` | Low-pass filter design helper (provided with the assignment) |
| `testsignal.txt` | Complex baseband test signal, 1024 samples at 61.44 MHz |

## Running

```bash
pip install numpy scipy matplotlib jupyter
jupyter notebook design.ipynb
```

Run the cells top to bottom. The notebook prints the filter lengths and
operation counts and saves the spectrum figures next to itself.

The full write-up is in [`../docs/phase1-report.pdf`](../docs/phase1-report.pdf).
