library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

library work; use work.cordic_pkg.all;

entity tb_tone is
  generic (
    G_IN_FILE  : string  := "const_in.txt";
    G_OUT_FILE : string  := "const_out.txt";
    G_NSAMP    : integer := 16384;
    -- W = round(2^30 * 196.16e6 / 983.04e6)
    G_CTRLW    : integer := 214237184
  );
end entity;

architecture sim of tb_tone is
  constant TCLK : time := 1.017 ns;            -- 983.04 MHz
  signal clk, rst_n, en : std_logic := '0';
  signal ctrl_w : unsigned(C_PHASE_W-1 downto 0) := (others=>'0');
  signal i_in,q_in,i_out,q_out : signed(C_DATA_W-1 downto 0) := (others=>'0');
  signal done : boolean := false;
begin
  clk <= not clk after TCLK/2 when not done else '0';

  dut : entity work.cordic_mixer
    port map (clk=>clk, rst_n=>rst_n, en=>en, ctrl_w=>ctrl_w,
              i_in=>i_in, q_in=>q_in, i_out=>i_out, q_out=>q_out);

  stim : process
    file fi : text;
    file fo : text;
    variable li, lo : line;
    variable vi, vq : integer;
    variable st     : file_open_status;
  begin
    file_open(st, fi, G_IN_FILE,  read_mode);
    assert st = open_ok
      report "ne moze se otvoriti ulazni fajl: " & G_IN_FILE severity failure;
    file_open(st, fo, G_OUT_FILE, write_mode);
    assert st = open_ok
      report "ne moze se otvoriti izlazni fajl: " & G_OUT_FILE severity failure;

    rst_n<='0'; en<='0'; wait for 5*TCLK;
    rst_n<='1'; ctrl_w<=to_unsigned(G_CTRLW,C_PHASE_W); en<='1';
    wait until rising_edge(clk);

    for k in 0 to G_NSAMP-1 loop
      if not endfile(fi) then
        readline(fi, li); read(li, vi); read(li, vq);
      else vi:=0; vq:=0; end if;
      i_in <= to_signed(vi, C_DATA_W);
      q_in <= to_signed(vq, C_DATA_W);
      wait until rising_edge(clk);
      write(lo, integer'image(to_integer(i_out)) & " " &
                integer'image(to_integer(q_out)));
      writeline(fo, lo);
    end loop;

    i_in<=(others=>'0'); q_in<=(others=>'0');
    for k in 0 to 20 loop
      wait until rising_edge(clk);
      write(lo, integer'image(to_integer(i_out)) & " " &
                integer'image(to_integer(q_out)));
      writeline(fo, lo);
    end loop;

    file_close(fi); file_close(fo);
    done<=true;
    report "tb_tone: zavrseno, upisano u " & G_OUT_FILE severity note;
    wait;
  end process;
end architecture;