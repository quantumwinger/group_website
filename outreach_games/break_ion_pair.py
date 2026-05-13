import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
import time
from app_theme import HTML_THEME, apply_html_theme

theme = {
    **HTML_THEME,
    "cation": HTML_THEME["accent_red"], "anion": HTML_THEME["accent"], "solvent": HTML_THEME["muted"],
}

st.set_page_config(layout="wide", page_title="Break the Ion Pair: Salt Dissolving Game")
apply_html_theme()
st.sidebar.title("Chemistry with Computers")
st.sidebar.markdown("_Explore how water dissolves salt by pulling ions apart._")
st.sidebar.markdown("---")
st.sidebar.subheader("Controls")
solvent_strength = st.sidebar.slider("Solvent Strength", 0.0, 2.0, 0.7, 0.05)
ion_attraction   = st.sidebar.slider("Ion Attraction Strength", 0.5, 3.0, 1.5, 0.05)
col_b1, col_b2   = st.sidebar.columns(2)

L = 16.0; N_solvent = 50; dt = 0.02; D = 0.8; ION_R = 0.7; SOL_R = 0.35

def init_state():
    pos = np.zeros((N_solvent+2, 2))
    pos[0] = [L/2 - 0.8, L/2]   # cation
    pos[1] = [L/2 + 0.8, L/2]   # anion
    occupied = pos[:2].tolist()
    placed = 2
    attempts = 0
    while placed < N_solvent + 2 and attempts < 50000:
        p = np.random.rand(2) * (L - 2) + 1.0
        dists = np.linalg.norm(pos[:placed] - p, axis=1)
        if dists.min() > 0.9:
            pos[placed] = p; placed += 1
        attempts += 1
    vel = (np.random.rand(N_solvent+2, 2) - 0.5) * 0.5
    st.session_state.pos = pos
    st.session_state.vel = vel
    st.session_state.running = False
    st.session_state.time_step = 0
    st.session_state.history_dist = []
    st.session_state.history_time = []
    st.session_state.win_frames = 0

if st.session_state.get("current_game") != "break_ion_pair" or "pos" not in st.session_state:
    for k in list(st.session_state.keys()):
        if k != "current_game": del st.session_state[k]
    st.session_state.current_game = "break_ion_pair"
    init_state()

def full_reset():
    for k in list(st.session_state.keys()): del st.session_state[k]
    init_state()

with col_b1:
    if st.sidebar.button("Start / Pause", use_container_width=True):
        st.session_state.running = not st.session_state.running
with col_b2:
    if st.sidebar.button("Reset", use_container_width=True):
        full_reset(); st.rerun()

st.sidebar.markdown("### 💡 Science Idea")
st.sidebar.info("Dissolving salt is a **tug-of-war** between ion-ion attraction and ion-water attraction. "
             "When water molecules are strong enough, they peel ions apart one by one.")
st.sidebar.markdown("### 🎯 Challenge")
st.sidebar.success("- Increase **Solvent Strength** to pull ions apart.\n"
             "- Reduce **Ion Attraction** to make it easier.\n"
             "- Keep ions separated (distance > 3.0) to win!")
st.sidebar.markdown("### 🔬 Try This")
st.sidebar.warning("1. Set solvent strength = 0.1. Do the ions separate?\n"
             "2. Push solvent to 1.8. How quickly does salt dissolve?\n"
             "3. With ion attraction = 3.0, what solvent strength is needed?")

def compute_forces(pos, sol_str, ion_att):
    N = len(pos)
    F = np.zeros((N, 2))
    charges = np.zeros(N); charges[0] = +1.0; charges[1] = -1.0

    for i in range(N):
        for j in range(i+1, N):
            d = pos[i] - pos[j]
            r = np.linalg.norm(d) + 1e-9
            if r > L/2: continue

            is_ion_i = (i < 2); is_ion_j = (j < 2)
            is_ion_pair = is_ion_i and is_ion_j

            # Ion-ion Coulomb (with tunable strength)
            if is_ion_pair:
                q = ion_att * charges[i] * charges[j]  # negative = attraction for +/-
                f_coulomb = -q * 8.0 / (r**2)
                F[i] += f_coulomb * d / r
                F[j] -= f_coulomb * d / r

            # LJ-style short-range repulsion (all pairs)
            sigma_ij = (ION_R if is_ion_i else SOL_R) + (ION_R if is_ion_j else SOL_R)
            if r < sigma_ij * 2.2:
                sr = (sigma_ij / r) ** 6
                f_rep = 24.0 * (2*sr*sr - sr) / r**2
                F[i] += f_rep * d
                F[j] -= f_rep * d

            # Solvent-ion attraction
            if is_ion_i != is_ion_j:   # one ion, one solvent
                f_sol = sol_str * 5.0 * np.exp(-r / 2.0) / r
                F[i] -= f_sol * d
                F[j] += f_sol * d

    return np.clip(F, -60, 60)

def step(pos, vel, sol_str, ion_att):
    F = compute_forces(pos, sol_str, ion_att)
    new_vel = vel + dt * F
    new_vel = np.clip(new_vel, -4.0, 4.0)
    new_pos = pos + dt * new_vel + np.sqrt(2*D*dt) * np.random.randn(*pos.shape)
    # Reflecting walls
    for k in range(2):
        hit_lo = new_pos[:, k] < 0.4
        hit_hi = new_pos[:, k] > L - 0.4
        new_pos[hit_lo, k] = 0.4; new_vel[hit_lo, k] *= -0.5
        new_pos[hit_hi, k] = L - 0.4; new_vel[hit_hi, k] *= -0.5
    return new_pos, new_vel

def ion_distance(pos):
    return float(np.linalg.norm(pos[0] - pos[1]))

def get_state(dist):
    if dist < 1.5:   return "Contact ion pair",          theme["cation"]
    elif dist < 3.0: return "Solvent-separated ion pair", theme["warning"]
    else:            return "Dissociated ions! 🎉",       theme["success"]

# Run simulation
if st.session_state.running:
    pos, vel = st.session_state.pos, st.session_state.vel
    for _ in range(4):
        pos, vel = step(pos, vel, solvent_strength, ion_attraction)
    st.session_state.pos = pos; st.session_state.vel = vel
    st.session_state.time_step += 1
    dist = ion_distance(pos)
    if dist > 3.0: st.session_state.win_frames += 1
    else: st.session_state.win_frames = max(0, st.session_state.win_frames - 1)
    if st.session_state.time_step % 2 == 0:
        st.session_state.history_dist.append(dist)
        st.session_state.history_time.append(st.session_state.time_step)
        if len(st.session_state.history_dist) > 200:
            st.session_state.history_dist.pop(0); st.session_state.history_time.pop(0)

pos  = st.session_state.pos
dist = ion_distance(pos)
state_str, state_col = get_state(dist)
avg_dist = float(np.mean(st.session_state.history_dist)) if st.session_state.history_dist else dist
won = st.session_state.win_frames >= 15

st.markdown("<h2 style='text-align:center;color:#e2e8f0'>⚗️ Break the Ion Pair: Salt Dissolving Game</h2>", unsafe_allow_html=True)
col_anim, col_info = st.columns([2, 1])

with col_anim:
    st.subheader("Live 2D Simulation")
    fig, ax = plt.subplots(figsize=(6, 6), facecolor=theme["bg"])
    ax.set_facecolor(theme["plot_bg"]); ax.set_xlim(0, L); ax.set_ylim(0, L)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")

    # Solvent particles
    sol_pos = pos[2:]
    ax.scatter(sol_pos[:,0], sol_pos[:,1], c=theme["solvent"], s=80, edgecolors="#aab7b8",
               linewidths=0.6, zorder=2, alpha=0.7, label="Water molecules")

    # Draw solvent close to ions with highlight
    for ion_idx in [0, 1]:
        d = np.linalg.norm(sol_pos - pos[ion_idx], axis=1)
        nearby = d < 2.8
        if nearby.any():
            ax.scatter(sol_pos[nearby,0], sol_pos[nearby,1],
                       c="#5dade2", s=100, edgecolors="#2980b9", linewidths=0.8, zorder=3, alpha=0.85)

    # Ion-ion line (thickness/alpha encodes bond strength)
    alpha_line = max(0.05, 1.0 - dist/5.0)
    lw_line = max(0.5, 4.0 * (1.5 / max(dist, 0.5)))
    ax.plot([pos[0,0], pos[1,0]], [pos[0,1], pos[1,1]],
            color="#c0392b", lw=min(lw_line, 5.0), alpha=alpha_line, linestyle="--", zorder=4)

    # Distance label along line
    mid = (pos[0] + pos[1]) / 2
    ax.text(mid[0], mid[1]+0.4, f"d = {dist:.2f}", ha="center", fontsize=9,
            color=theme["primary"], fontweight="bold", zorder=6,
            bbox=dict(facecolor=theme["card"], edgecolor=theme["card_border"], alpha=0.85, boxstyle='round,pad=0.2'))

    # Cation (red +)
    ax.add_patch(patches.Circle(pos[0], ION_R, facecolor=theme["cation"],
                                edgecolor="darkred", linewidth=2.5, zorder=5))
    ax.text(pos[0,0], pos[0,1], "+", ha="center", va="center",
            fontsize=18, fontweight="bold", color="white", zorder=6)

    # Anion (blue -)
    ax.add_patch(patches.Circle(pos[1], ION_R, facecolor=theme["anion"],
                                edgecolor="navy", linewidth=2.5, zorder=5))
    ax.text(pos[1,0], pos[1,1], "−", ha="center", va="center",
            fontsize=18, fontweight="bold", color="white", zorder=6)

    ax.legend(loc="upper right", fontsize=8, framealpha=0.8)
    st.pyplot(fig); plt.close(fig)

with col_info:
    st.subheader("Score & Status")
    st.markdown(
        f"<div style='background:{state_col};padding:10px;border-radius:8px;"
        f"color:white;text-align:center;font-weight:bold;font-size:1.1rem'>{state_str}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Ion Distance", f"{dist:.2f}")
    c2.metric("Avg Distance", f"{avg_dist:.2f}")

    if won:
        st.success("🏆 You win! Ions are fully dissociated!")
    elif state_str == "Solvent-separated ion pair":
        st.warning("💧 Getting closer – keep the water strong!")
    else:
        st.info("⚡ Ions are still attracted – increase solvent strength.")

    st.subheader("Live Plot: Ion Distance")
    fig2, ax2 = plt.subplots(figsize=(5, 2.2))
    if st.session_state.history_time:
        ax2.fill_between(st.session_state.history_time, st.session_state.history_dist, alpha=0.2, color=theme["anion"])
        ax2.plot(st.session_state.history_time, st.session_state.history_dist, color=theme["anion"], lw=2)
    ax2.axhline(3.0, color=theme["success"], linestyle="--", lw=1.5, label="Dissociated (3.0)")
    ax2.axhline(1.5, color=theme["cation"],  linestyle=":",  lw=1.5, label="Contact (1.5)")
    ax2.set_xlabel("Time (steps)", fontsize=8); ax2.set_ylabel("Distance", fontsize=8)
    ax2.set_xlim(left=max(0, st.session_state.time_step-200), right=st.session_state.time_step+10)
    ax2.set_ylim(0, max(st.session_state.history_dist, default=5)+1)
    ax2.legend(fontsize=7); ax2.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig2); plt.close(fig2)

if st.session_state.running:
    time.sleep(0.04)
    st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© Dasgupta Research Group @ K-State <a href='https://www.drgatksu.com' target='_blank' style='color: gray; text-decoration: underline;'>www.drgatksu.com</a></p>", unsafe_allow_html=True)
