"""
Pokrece sve provjere i pravi sve slike za izvjestaj druge faze.

    python pokreni_sve.py

Ako izlazi iz Vivado simulacije jos ne postoje, skripta to jasno
prijavi i preskoci te korake umjesto da pukne.
"""
import subprocess, sys, os

KORACI = [
    ("theory_check.py", "Provjera parametara u odnosu na predavanja", []),
    ("verify.py",         "Bit-tacno poredjenje RTL izlaza sa modelom", ["input_iq.txt","output_iq.txt"]),
    ("check_rotation.py",      "Provjera smjera rotacije",                   ["const_out.txt"]),
    ("plots.py",           "Spektri ulaza i izlaza -> spektri_mesac.png", ["input_iq.txt","output_iq.txt"]),
    ("sfdr.py",            "Cistoca oscilatora     -> spektar_nco.png",   ["const_out.txt"]),
    ("analysis_figures.py",   "Konvergencija i tacnost -> 3 slike",          []),
]

def ima(name):
    for d in ('.', os.path.join('..','data'), 'data'):
        if os.path.exists(os.path.join(d, name)):
            return True
    return False

preskoceni = []
for skripta, opis, potrebno in KORACI:
    if not os.path.exists(skripta):
        print(f"[preskocen] {skripta} nije pronadjen"); continue
    fale = [f for f in potrebno if not ima(f)]
    if fale:
        preskoceni.append((opis, fale))
        print(f"\n[preskocen] {opis}")
        print(f"            nedostaje: {', '.join(fale)}")
        continue
    print("\n" + "="*68)
    print(f">>> {opis}")
    print("="*68)
    if subprocess.run([sys.executable, skripta]).returncode != 0:
        print(f"!!! {skripta} je zavrsio sa greskom"); sys.exit(1)

print("\n" + "="*68)
if preskoceni:
    print("PRESKOCENI KORACI - nedostaju izlazi iz Vivado simulacije:")
    for opis, fale in preskoceni:
        print(f"   - {opis}  ({', '.join(fale)})")
    print()
    print("   U Vivadu pokreni testbenceve:")
    print("      tb_mixer  -> pravi output_iq.txt")
    print("      tb_tone   -> pravi const_out.txt")
    print("   pa prekopiraj oba fajla iz")
    print("      <projekat>.sim\\sim_1\\behav\\xsim\\")
    print("   u folder  data\\  i pokreni ovu skriptu ponovo.")
else:
    print("GOTOVO. Slike za izvjestaj:")
    for f in ["spektri_mesac.png","spektar_nco.png","konvergencija.png",
              "tacnost.png","uglovi.png","sema_stepena.png","lanac_stepena.png"]:
        print(f"   {f}  {'(napravljena)' if os.path.exists(f) else '(NEDOSTAJE)'}")
print("="*68)
