# CORDIC Digital Up-Converter

Design and FPGA implementation of a digital up-converter (DUC) for a 10-bit DAC
transmitter: a 16× multistage interpolator and a **pipelined CORDIC complex mixer**
written in VHDL, verified bit-exactly against a Python golden model.

Course project for *Hardware-Software Signal Processing* (13E044HSOS),
School of Electrical Engineering, University of Belgrade.

---

## What it does

A complex baseband signal sampled at 61.44 MHz is interpolated by a factor of 16
to 983.04 MHz, then translated to an intermediate frequency of 196.16 MHz by a
complex mixer built from a CORDIC rotator and a numerically controlled oscillator.

```
 x(n)          ×2        ×2        ×2        ×2                    e^{jΩ₀n}
 ─────► ┌────┐──►┌────┐──►┌────┐──►┌────┐──► ┌──────────────┐ ──────►
61.44   │ HB1│   │ HB2│   │ HB3│   │ LP4│    │ CORDIC mixer │   196.16 MHz
 MHz    └────┘   └────┘   └────┘   └────┘    └──────────────┘   @ 983.04 MHz
        │◄──────── interpolator, ×16 ──────►│  │◄─ VHDL, this repo ─►│
```

The interpolator is designed and analysed in Python (phase 1); the CORDIC mixer
is implemented in VHDL and taken through synthesis and implementation (phase 2).

---

## Results

| | |
|---|---|
| CORDIC iterations | 10 (one accuracy bit per iteration, 10-bit DAC) |
| Latency | 16 clock cycles |
| Throughput | 1 sample per clock cycle |
| SFDR | **68.9 dB** (exceeds the 61.96 dB quantisation limit for 10 bits) |
| Output error | 1.54 LSB peak, 0.75 LSB RMS at full scale (512) |
| Verification | bit-exact against a Python golden model, 16 384 samples |

**Implementation on PYNQ-Z2 (Xilinx XC7Z020-1):**

| Resource | Used | Available | Utilisation |
|---|---|---|---|
| LUT | 517 | 53 200 | 1.0 % |
| FF | 535 | 106 400 | 0.5 % |
| Slice | 180 | 13 300 | 1.4 % |
| DSP48E1 | 2 | 220 | 0.9 % |

Maximum clock frequency **317.5 MHz** (3.150 ns period, all timing checks met).
The critical path lies inside the CORDIC core: it starts at the sign bit of the
angle accumulator, which drives the adders of the following stage — a fan-out of
41 nets. The limit is therefore set by the algorithm structure itself, not by
surrounding logic.

---

## Repository layout

```
├── phase1-design/          Interpolator and CORDIC parameter design (Python)
│   ├── design.ipynb        Jupyter notebook: filters, spectra, NRZ compensation, jitter
│   ├── README.md           What the notebook covers, and how to run it
│   ├── remezhb.py          Half-band filter design helper
│   ├── remezlp.py          Low-pass filter design helper
│   └── testsignal.txt      Complex baseband test signal, 1024 samples
│
├── phase2-hardware/        Pipelined CORDIC mixer (VHDL)
│   ├── rtl/
│   │   ├── cordic_pkg.vhd      Constants, arctangent table, types
│   │   ├── cordic_stage.vhd    One pipeline stage (shift-add-register)
│   │   ├── cordic_core.vhd     Ten stages in cascade
│   │   └── cordic_mixer.vhd    Top level: NCO, pre-rotation, core, output stage
│   ├── sim/
│   │   ├── tb_demo.vhd         Nine hand-picked vectors, self-checking
│   │   ├── tb_selfcheck.vhd    16 384 samples against the golden model
│   │   ├── tb_mixer.vhd        Produces output samples for spectrum plots
│   │   └── tb_tone.vhd         Constant input, for SFDR measurement
│   ├── constraints/
│   │   ├── cordic_mixer.xdc    Timing constraints
│   │   └── build.tcl           Batch synthesis and implementation
│   ├── python/
│   │   ├── golden.py           Bit-exact reference model
│   │   ├── verify.py           Compares RTL output against the model
│   │   ├── theory_check.py     Checks parameters against the course material
│   │   ├── plots.py            Input and output spectra
│   │   ├── sfdr.py             Oscillator spectral purity
│   │   └── run_all.py          Runs every check and produces every figure
│   └── data/                   Input samples and reference output
│
└── docs/
    ├── phase1-report.pdf
    └── phase2-report.pdf
```

---

## Getting started

### Simulate with GHDL (no licence needed)

```bash
cd phase2-hardware
ghdl -a --std=93 rtl/cordic_pkg.vhd rtl/cordic_stage.vhd \
                 rtl/cordic_core.vhd rtl/cordic_mixer.vhd sim/tb_demo.vhd
ghdl -e --std=93 tb_demo
ghdl -r --std=93 tb_demo
```

Expected output:

```
 br |   I_ul |   Q_ul |  ugao |  I_izl |  Q_izl |  I_ocek |  Q_ocek | ok
----+--------+--------+-------+--------+--------+---------+---------+----
  0 |    511 |      0 |     0 |    511 |      1 |     511 |       1 | DA
  1 |    511 |      0 |    30 |    443 |    255 |     443 |     255 | DA
  2 |    511 |      0 |    45 |    362 |    361 |     362 |     361 | DA
  ...
  SVI TESTOVI PROLAZE (9 vrijednosti)
```

Rotating (511, 0) by 45° gives (362, 361); the exact values are
511·cos 45° = 511·sin 45° = 361.33, so the error stays below one LSB.

### Synthesise for PYNQ-Z2

```bash
cd phase2-hardware
vivado -mode batch -source constraints/build.tcl
```

Reports are written to `vivado_out/`. To find the maximum frequency, reduce
`create_clock -period` in `constraints/cordic_mixer.xdc` and re-run until the
worst negative slack turns negative.

### Reproduce the analysis and figures

```bash
cd phase2-hardware/python
pip install numpy scipy matplotlib
python gen_input.py     # builds the interpolated input samples
python run_all.py       # runs every check and produces every figure
```

`run_all.py` skips the steps whose simulation outputs are missing and says which
testbench to run, so it is safe to call at any point.

---

## Design notes

A few decisions that are not obvious from the code alone.

**Internal word width is 15 bits, not 14.** The output of a complex mixer is a
rotated vector, so a single component can reach |I + jQ| ≤ √2 · FS. With 10-bit
inputs and 4 guard bits the worst case is 512·√2·2⁴ = 11 585, which overflows a
14-bit word (±8191). One extra headroom bit resolves this.

**Quadrant pre-rotation is mandatory.** CORDIC in rotation mode converges only
for |z₀| ≤ 1.7413 rad (99.77°), while the NCO phase covers the full circle. The
two most significant phase bits select the quadrant and the remainder lies in
[0, π/2), which is inside the convergence region. Because the remainder is simply
the lower phase bits, no subtraction is needed — the pre-rotation costs only
multiplexers.

**The angle datapath is 16 bits, not 30.** The phase accumulator needs 30 bits
for sub-hertz resolution, but the CORDIC angle path only carries the remainder
after the quadrant is removed. Measurements showed accuracy is unchanged down to
16 bits and degrades below that, so the longest adder in the core was halved.

**Pipeline registers have no reset.** Registers inside a DSP48E1 support only
synchronous reset, so a register described with an asynchronous reset cannot be
packed into the DSP block. Leaving the multiplier without its internal pipeline
registers costs about 4 ns — more than the entire clock period. Data pipeline
registers do not need a reset anyway; wrong values simply flush through.

---

## A note on language

The README and the repository structure are in English. Source comments,
console output of the testbenches and the two reports in `docs/` are in
Serbian, which is the language the course is taught in.

## Tools

Vivado 2025.2 · GHDL 4.1 · Python 3 (NumPy, SciPy, Matplotlib) · VHDL-93

---

## License

MIT — see [LICENSE](LICENSE).

The reports in `docs/` are coursework and are provided for reference.
