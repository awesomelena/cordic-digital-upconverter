library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package cordic_pkg is

  -- parametri iz prve faze
  constant C_N_ITER  : integer := 10;   -- broj cordic iteracija (sirina rijeci DAC)
  constant C_DATA_W  : integer := 10;   -- sirina ulazne/izlazne rijeci (DAC 10 bita)
  constant C_GUARD   : integer := 4;    -- zastitni bitovi
  constant C_HEAD    : integer := 1;    
  constant C_INT_W   : integer := C_DATA_W + C_GUARD + C_HEAD;  -- 15 bita

  constant C_PHASE_W : integer := 30;   -- fazni akumulator (rezolucija 0.9155 Hz)

  constant C_ANG_W   : integer := 16;   -- 2^16 <=> 2*pi
  constant C_PH_TRUNC: integer := C_PHASE_W - C_ANG_W;  -- odbaceni donji bitovi faze

  --   K(10) = 0.607253321 ;  K_FIX = round(K * 2^15) = 19898
  constant C_K_SHIFT : integer := 15;
  constant C_K_FIX   : integer := 19898;

  type t_atan_lut is array (0 to C_N_ITER-1) of integer;
  constant C_ATAN_LUT : t_atan_lut := (
      8192,  -- i=0  arctan(2^-0) =  45.00000
      4836,  -- i=1  arctan(2^-1) =  26.56505
      2555,  -- i=2  arctan(2^-2) =  14.03624
      1297,  -- i=3  arctan(2^-3) =   7.12502
       651,  -- i=4  arctan(2^-4) =   3.57633
       326,  -- i=5  arctan(2^-5) =   1.78991
       163,  -- i=6  arctan(2^-6) =   0.89517
        81,  -- i=7  arctan(2^-7) =   0.44761
        41,  -- i=8  arctan(2^-8) =   0.22381
        20   -- i=9  arctan(2^-9) =   0.11191
  );

  type t_xy_array  is array (natural range <>) of signed(C_INT_W-1 downto 0);
  type t_ang_array is array (natural range <>) of signed(C_ANG_W-1 downto 0);

end package cordic_pkg;