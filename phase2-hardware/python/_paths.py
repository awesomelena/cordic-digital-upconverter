"""Trazenje ulaznih/izlaznih fajlova u python/ ili data/ folderu."""
import os, sys

_KANDIDATI = ('.', os.path.join('..', 'data'), 'data', os.path.join('..', '..', 'data'))

def F(name):
    """Vraca putanju do fajla; ako ga nema, ispisuje jasno objasnjenje."""
    for d in _KANDIDATI:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    _objasni(name)
    sys.exit(1)

def OUT(name):
    """Putanja za upis rezultata - u data/ ako postoji, inace u tekuci folder."""
    for d in (os.path.join('..', 'data'), 'data'):
        if os.path.isdir(d):
            return os.path.join(d, name)
    return name

_PORUKE = {
    'input_iq.txt':  "Pokreni:  python gen_input.py",
    'const_in.txt':  "Pokreni:  python gen_input.py",
    'output_iq.txt': ("Ovo je IZLAZ iz simulacije. Pokreni testbenc tb_mixer u Vivadu,\n"
                      "  pa prekopiraj output_iq.txt iz\n"
                      "     <projekat>.sim\\sim_1\\behav\\xsim\\\n"
                      "  u folder data\\"),
    'const_out.txt': ("Ovo je IZLAZ iz simulacije. Pokreni testbenc tb_tone u Vivadu,\n"
                      "  pa prekopiraj const_out.txt iz\n"
                      "     <projekat>.sim\\sim_1\\behav\\xsim\\\n"
                      "  u folder data\\"),
    'golden_iq.txt': "Pokreni:  python verify3.py  (pravi referentni niz)",
}

def _objasni(name):
    print()
    print("="*66)
    print(f"  NEDOSTAJE FAJL: {name}")
    print("="*66)
    print("  Trazen je u:")
    for d in _KANDIDATI:
        print(f"     {os.path.abspath(os.path.join(d, name))}")
    if name in _PORUKE:
        print()
        print("  " + _PORUKE[name])
    print("="*66)
