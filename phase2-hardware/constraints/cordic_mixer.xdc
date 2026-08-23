## =====================================================================
##  cordic_mixer.xdc
##  Ogranicenja za PYNQ-Z2 (Zynq-7000, XC7Z020-1CLG400C)
##
##  CORDIC jezgro je namijenjeno kao IP blok unutar veceg sistema, a ne
##  kao samostalan cip. Zato se analiziraju SAMO putanje registar-registar
##  unutar jezgra, dok se putanje ka/od fizickih pinova iskljucuju iz
##  analize. U suprotnom rezultat odredjuje kasnjenje ulazno-izlaznih
##  bafera (OBUF ~3.3 ns), a ne logika CORDIC-a.
## =====================================================================

# ---------------------------------------------------------------------
#  Radni takt. Smanjivati periodu dok WNS ne postane negativan da bi se
#  odredila maksimalna radna ucestanost jezgra.
# ---------------------------------------------------------------------
create_clock -period 3.150 -name clk [get_ports clk]

# ---------------------------------------------------------------------
#  Iskljucivanje ulazno-izlaznih putanja iz analize.
#  Ostaju samo putanje registar -> registar, tj. stvarna kriticna
#  putanja CORDIC stepena.
# ---------------------------------------------------------------------
set_false_path -from [all_inputs]
set_false_path -to   [all_outputs]

# ---------------------------------------------------------------------
#  Za rad na ploci sa 125 MHz referentnim taktom (PYNQ-Z2):
#    set_property PACKAGE_PIN H16 [get_ports clk]
#    set_property IOSTANDARD LVCMOS33 [get_ports clk]
# ---------------------------------------------------------------------
