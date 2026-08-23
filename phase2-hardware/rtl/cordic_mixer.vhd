library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.cordic_pkg.all;

entity cordic_mixer is
  port (
    clk     : in  std_logic;
    rst_n   : in  std_logic;
    en      : in  std_logic;
    -- Omega0 = 2*pi*W / 2^C_PHASE_W
    ctrl_w  : in  unsigned(C_PHASE_W-1 downto 0);
    -- ulazni kompleksni odbirak
    i_in    : in  signed(C_DATA_W-1 downto 0);
    q_in    : in  signed(C_DATA_W-1 downto 0);
    -- izlazni kompleksni odbirak
    i_out   : out signed(C_DATA_W-1 downto 0);
    q_out   : out signed(C_DATA_W-1 downto 0)
  );
end entity cordic_mixer;

architecture rtl of cordic_mixer is

  -- NCO
  signal phase_acc : unsigned(C_PHASE_W-1 downto 0) := (others => '0');

  -- protocni stepen: predrotacija kvadranta
  constant C_PRE_W : integer := C_DATA_W + 1;      -- 11 bita (zbog -(-512))
  signal xp_r : signed(C_PRE_W-1 downto 0);
  signal yp_r : signed(C_PRE_W-1 downto 0);
  signal z1_r : signed(C_ANG_W-1 downto 0);

  -- registar na ulazu mnozaca
  signal xm_r : signed(C_PRE_W-1 downto 0) := (others => '0');
  signal ym_r : signed(C_PRE_W-1 downto 0) := (others => '0');
  signal z2_r : signed(C_ANG_W-1 downto 0) := (others => '0');

  -- registar proizvoda
  constant C_MUL_W : integer := C_PRE_W + 16;      
  signal xmul_r : signed(C_MUL_W-1 downto 0) := (others => '0');
  signal ymul_r : signed(C_MUL_W-1 downto 0) := (others => '0');
  signal z3_r   : signed(C_ANG_W-1 downto 0);

  -- skaliranje faktorom K
  signal x0_r : signed(C_INT_W-1 downto 0) := (others => '0');
  signal y0_r : signed(C_INT_W-1 downto 0) := (others => '0');
  signal z0_r : signed(C_ANG_W-1 downto 0) := (others => '0');

  -- izlaz jezgra
  signal xn, yn : signed(C_INT_W-1 downto 0);
  signal zn     : signed(C_ANG_W-1 downto 0);

  -- izlazni protocni stepeni
  signal xr_r, yr_r : signed(C_INT_W-C_GUARD downto 0);

  -- skaliranje konstantom K: (v * K_FIX) >> (K_SHIFT - GUARD)
  function scale_k (v : signed) return signed is
    variable prod : signed(v'length + 16 - 1 downto 0);
  begin
    prod := v * to_signed(C_K_FIX, 16);
    return resize(shift_right(prod, C_K_SHIFT - C_GUARD), C_INT_W);
  end function;

  function round_add (v : signed) return signed is
  begin
    return resize(v, v'length + 1) + to_signed(2**(C_GUARD-1), v'length + 1);
  end function;

  function sat_out (t : signed) return signed is
    variable top : signed(t'length-1 downto C_DATA_W-1);
  begin
    top := t(t'length-1 downto C_DATA_W-1);
    if top = (top'range => '0') or top = (top'range => '1') then
      return resize(t, C_DATA_W);                      
    elsif t(t'length-1) = '0' then
      return to_signed(2**(C_DATA_W-1) - 1, C_DATA_W);   -- +FS
    else
      return to_signed(-(2**(C_DATA_W-1)), C_DATA_W);    -- -FS
    end if;
  end function;

begin

  process (clk, rst_n)
    variable quad : unsigned(1 downto 0);
  begin
    if rst_n = '0' then
      phase_acc <= (others => '0');
      xp_r      <= (others => '0');
      yp_r      <= (others => '0');
      z1_r      <= (others => '0');
    elsif rising_edge(clk) then
      if en = '1' then
        phase_acc <= phase_acc + ctrl_w;
        quad := phase_acc(C_PHASE_W-1 downto C_PHASE_W-2);
        z1_r <= signed(resize(
                  phase_acc(C_PHASE_W-3 downto C_PH_TRUNC), C_ANG_W));
        case quad is
          when "00" =>
            xp_r <=  resize(i_in, C_PRE_W);  yp_r <=  resize(q_in, C_PRE_W);
          when "01" =>
            xp_r <= -resize(q_in, C_PRE_W);  yp_r <=  resize(i_in, C_PRE_W);
          when "10" =>
            xp_r <= -resize(i_in, C_PRE_W);  yp_r <= -resize(q_in, C_PRE_W);
          when others =>
            xp_r <=  resize(q_in, C_PRE_W);  yp_r <= -resize(i_in, C_PRE_W);
        end case;
      end if;
    end if;
  end process;

  process (clk)
  begin
    if rising_edge(clk) then
      if en = '1' then
        -- registar mnozaca
        xm_r <= xp_r;
        ym_r <= yp_r;
        z2_r <= z1_r;
        -- registar proizvoda
        xmul_r <= xm_r * to_signed(C_K_FIX, 16);
        ymul_r <= ym_r * to_signed(C_K_FIX, 16);
        z3_r   <= z2_r;
        -- pomjeranje i skracivanje na internu sirinu
        x0_r <= resize(shift_right(xmul_r, C_K_SHIFT - C_GUARD), C_INT_W);
        y0_r <= resize(shift_right(ymul_r, C_K_SHIFT - C_GUARD), C_INT_W);
        z0_r <= z3_r;
      end if;
    end if;
  end process;

  u_core : entity work.cordic_core
    port map (
      clk   => clk,
      rst_n => rst_n,
      en    => en,
      x0    => x0_r,
      y0    => y0_r,
      z0    => z0_r,
      xn    => xn,
      yn    => yn,
      zn    => zn
    );

  process (clk, rst_n)
  begin
    if rst_n = '0' then
      xr_r <= (others => '0');
      yr_r <= (others => '0');
    elsif rising_edge(clk) then
      if en = '1' then
        xr_r <= resize(shift_right(round_add(xn), C_GUARD), C_INT_W-C_GUARD+1);
        yr_r <= resize(shift_right(round_add(yn), C_GUARD), C_INT_W-C_GUARD+1);
      end if;
    end if;
  end process;

  process (clk, rst_n)
  begin
    if rst_n = '0' then
      i_out <= (others => '0');
      q_out <= (others => '0');
    elsif rising_edge(clk) then
      if en = '1' then
        i_out <= sat_out(xr_r);
        q_out <= sat_out(yr_r);
      end if;
    end if;
  end process;

end architecture rtl;