library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
library work; use work.cordic_pkg.all;

entity tb_selfcheck is
  generic (
    G_IN_FILE  : string  := "input_iq.txt";
    G_REF_FILE : string  := "golden_iq.txt";
    G_NSAMP    : integer := 16384;
    G_CTRLW    : integer := 214259029
  );
end entity;

architecture sim of tb_selfcheck is
  constant TCLK   : time    := 1.017 ns;      -- 983.04 MHz
  constant LAT    : integer := C_N_ITER + 6;  -- 16 taktova

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
    file fin  : text;
    file fref : text;
    variable st : file_open_status;
    variable li, lr : line;
    variable vi, vq : integer;
    variable ri, rq : integer;
    variable nchk   : integer := 0;
    variable nerr   : integer := 0;
    -- red za poravnanje kasnjenja protocne obrade
    type t_q is array (0 to LAT) of integer;
    variable qi, qq : t_q := (others => 0);
    variable valid  : integer := 0;
  begin
    file_open(st, fin,  G_IN_FILE,  read_mode);
    assert st = open_ok report "ne moze da se otvori: " & G_IN_FILE severity failure;
    file_open(st, fref, G_REF_FILE, read_mode);
    assert st = open_ok report "ne moze da se otvori: " & G_REF_FILE severity failure;

    rst_n <= '0'; en <= '0';
    wait for 5*TCLK;
    rst_n <= '1';
    ctrl_w <= to_unsigned(G_CTRLW, C_PHASE_W);
    en <= '1';
    wait until rising_edge(clk);

    for k in 0 to G_NSAMP-1 loop
      -- dovodjenje ulaznog odbirka
      if not endfile(fin) then
        readline(fin, li); read(li, vi); read(li, vq);
      else
        vi := 0; vq := 0;
      end if;
      i_in <= to_signed(vi, C_DATA_W);
      q_in <= to_signed(vq, C_DATA_W);

      wait until rising_edge(clk);

      -- poslije LAT taktova izlaz odgovara odbirku (k-LAT)
      if k >= LAT then
        if not endfile(fref) then
          readline(fref, lr); read(lr, ri); read(lr, rq);
          nchk := nchk + 1;
          if to_integer(i_out) /= ri or to_integer(q_out) /= rq then
            nerr := nerr + 1;
            report "neslaganje na odbirku " & integer'image(k-LAT) &
                   ": rtl=(" & integer'image(to_integer(i_out)) & "," &
                   integer'image(to_integer(q_out)) & ")" &
                   "  ref=(" & integer'image(ri) & "," & integer'image(rq) & ")"
              severity error;
            assert nerr < 10
              report "previse neslaganja - prekid" severity failure;
          end if;
        end if;
      end if;
    end loop;

    file_close(fin); file_close(fref);

    -- provjera mora biti u stanju da padne: nula provjera je greska
    assert nchk > 1000
      report "testbenc nije provjerio dovoljno odbiraka (nchk=" &
             integer'image(nchk) & ")" severity failure;

    assert nerr = 0
      report "rtl se ne poklapa sa referentnim modelom, neslaganja: " &
             integer'image(nerr) severity failure;

    report "prolaz: provjereno " & integer'image(nchk) &
           " odbiraka, sva se poklapaju bit-tacno." severity note;

    done <= true;
    wait;
  end process;

end architecture sim;