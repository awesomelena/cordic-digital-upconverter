library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
library work; use work.cordic_pkg.all;

entity tb_demo is end entity;

architecture sim of tb_demo is

  constant TCLK  : time    := 3.150 ns;   -- ostvarena radna ucestanost
  constant CEKAJ : integer := 25;         -- taktova po testu

  -- (I_ulaz, Q_ulaz, prirast faze, I_ocekivano, Q_ocekivano)
  type t_vec is record
    i_in  : integer;
    q_in  : integer;
    dfaza : integer;
    i_ok  : integer;
    q_ok  : integer;
  end record;
  type t_vec_niz is array (natural range <>) of t_vec;

  constant TESTOVI : t_vec_niz := (
    (  511,     0,          0,   511,     1),  -- rotacija za 0 st, ugao 0 st
    (  511,     0,   89478485,   443,   255),  -- rotacija za 30 st, ugao 30 st
    (  511,     0,   44739243,   362,   361),  -- rotacija za 45 st, ugao 45 st
    (  511,     0,  134217728,    -1,   511),  -- rotacija za 90 st, ugao 90 st
    (  511,     0,  268435456,  -511,    -1),  -- rotacija za 180 st, ugao 180 st
    (  511,     0,  268435456,     1,  -511),  -- rotacija za 270 st, ugao 270 st
    (    0,   511,  536870912,  -511,    -1),  -- ulaz na +90 st, ugao 90 st
    (  346,   200,  939524096,   104,   386),  -- 400 pod 30 st, +45 st, ugao 45 st
    ( -400,   300,   44739243,  -459,  -197)  -- negativan ulaz, ugao 60 st
  );

  signal clk, rst_n, en : std_logic := '0';
  signal ctrl_w : unsigned(C_PHASE_W-1 downto 0) := (others=>'0');
  signal i_in, q_in, i_out, q_out : signed(C_DATA_W-1 downto 0) := (others=>'0');

  -- signali samo za prikaz na talasnim oblicima
  signal test_id : integer := -1;
  signal ugao_st : real    := 0.0;
  signal i_ocek  : integer := 0;
  signal q_ocek  : integer := 0;
  signal prolaz  : std_logic := '0';

  signal kraj : boolean := false;

begin

  clk <= not clk after TCLK/2 when not kraj else '0';

  dut : entity work.cordic_mixer
    port map (clk=>clk, rst_n=>rst_n, en=>en, ctrl_w=>ctrl_w,
              i_in=>i_in, q_in=>q_in, i_out=>i_out, q_out=>q_out);

  stim : process
    variable greske : integer := 0;
    variable ugao   : real;
  begin
    rst_n <= '0'; en <= '0';
    wait for 5*TCLK;
    rst_n <= '1';
    en <= '1';
    wait until rising_edge(clk);

    for k in TESTOVI'range loop
      test_id <= k;
      i_ocek  <= TESTOVI(k).i_ok;
      q_ocek  <= TESTOVI(k).q_ok;

      -- jedan takt sa prirastom faze pomjeri akumulator na trazeni ugao
      ctrl_w <= to_unsigned(TESTOVI(k).dfaza, C_PHASE_W);
      wait until rising_edge(clk);
      ctrl_w <= (others => '0');

      -- dovodjenje ulaznog odbirka i cekanje da se protocna obrada isprazni
      i_in <= to_signed(TESTOVI(k).i_in, C_DATA_W);
      q_in <= to_signed(TESTOVI(k).q_in, C_DATA_W);
      for t in 0 to CEKAJ-1 loop
        wait until rising_edge(clk);
      end loop;

      -- provjera
      if to_integer(i_out) = TESTOVI(k).i_ok and
         to_integer(q_out) = TESTOVI(k).q_ok then
        prolaz <= '1';
      else
        prolaz <= '0';
        greske := greske + 1;
      end if;
      wait for 0 ns;

    end loop;

    assert greske = 0
      report "test nije prosao" severity failure;

    kraj <= true;
    wait;
  end process;

  process (test_id)
    variable akum : real := 0.0;
  begin
    if test_id >= 0 then
      akum := akum + real(TESTOVI(test_id).dfaza) / 2.0**C_PHASE_W * 360.0;
      while akum >= 360.0 loop akum := akum - 360.0; end loop;
      ugao_st <= akum;
    end if;
  end process;

end architecture sim;