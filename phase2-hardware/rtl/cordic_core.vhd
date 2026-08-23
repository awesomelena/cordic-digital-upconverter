library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.cordic_pkg.all;

entity cordic_core is
  port (
    clk   : in  std_logic;
    rst_n : in  std_logic;
    en    : in  std_logic;
    x0    : in  signed(C_INT_W-1 downto 0);
    y0    : in  signed(C_INT_W-1 downto 0);
    z0    : in  signed(C_ANG_W-1 downto 0);
    xn    : out signed(C_INT_W-1 downto 0);
    yn    : out signed(C_INT_W-1 downto 0);
    zn    : out signed(C_ANG_W-1 downto 0)
  );
end entity cordic_core;

architecture rtl of cordic_core is

  signal x_pipe : t_xy_array (0 to C_N_ITER);
  signal y_pipe : t_xy_array (0 to C_N_ITER);
  signal z_pipe : t_ang_array(0 to C_N_ITER);

begin

  x_pipe(0) <= x0;
  y_pipe(0) <= y0;
  z_pipe(0) <= z0;

  gen_stages : for i in 0 to C_N_ITER-1 generate
    u_stage : entity work.cordic_stage
      generic map (
        G_STAGE => i
      )
      port map (
        clk   => clk,
        en    => en,
        x_in  => x_pipe(i),
        y_in  => y_pipe(i),
        z_in  => z_pipe(i),
        x_out => x_pipe(i+1),
        y_out => y_pipe(i+1),
        z_out => z_pipe(i+1)
      );
  end generate gen_stages;

  xn <= x_pipe(C_N_ITER);
  yn <= y_pipe(C_N_ITER);
  zn <= z_pipe(C_N_ITER);

end architecture rtl;