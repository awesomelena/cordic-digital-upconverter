library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.cordic_pkg.all;

entity cordic_stage is
  generic (
    G_STAGE : integer := 0            -- redni broj iteracije i
  );
  port (
    clk    : in  std_logic;
    en     : in  std_logic;
    x_in   : in  signed(C_INT_W-1 downto 0);
    y_in   : in  signed(C_INT_W-1 downto 0);
    z_in   : in  signed(C_ANG_W-1 downto 0);
    x_out  : out signed(C_INT_W-1 downto 0) := (others => '0');
    y_out  : out signed(C_INT_W-1 downto 0) := (others => '0');
    z_out  : out signed(C_ANG_W-1 downto 0) := (others => '0')
  );
end entity cordic_stage;

architecture rtl of cordic_stage is

  constant C_THETA : signed(C_ANG_W-1 downto 0) :=
      to_signed(C_ATAN_LUT(G_STAGE), C_ANG_W);

  signal x_shift : signed(C_INT_W-1 downto 0);
  signal y_shift : signed(C_INT_W-1 downto 0);
  signal sigma_n : std_logic;   -- 1 kada je z < 0  (sigma = -1)

begin

  -- fiksni aritmeticki pomeraci
  x_shift <= shift_right(x_in, G_STAGE);
  y_shift <= shift_right(y_in, G_STAGE);

  -- rotacioni mod: sigma = sgn(z)
  sigma_n <= z_in(C_ANG_W-1);

  process (clk)
  begin
    if rising_edge(clk) then
      if en = '1' then
        if sigma_n = '0' then          -- z >= 0  ->  sigma = +1
          x_out <= x_in - y_shift;
          y_out <= y_in + x_shift;
          z_out <= z_in - C_THETA;
        else                           -- z <  0  ->  sigma = -1
          x_out <= x_in + y_shift;
          y_out <= y_in - x_shift;
          z_out <= z_in + C_THETA;
        end if;
      end if;
    end if;
  end process;

end architecture rtl;