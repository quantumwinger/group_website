import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
from app_theme import HTML_THEME, apply_html_theme

theme = {
    **HTML_THEME,
    "water": HTML_THEME["accent"], "cation": HTML_THEME["accent_red"], "anion": HTML_THEME["accent_amber"],
    "membrane": HTML_THEME["card_border"],
}

st.set_page_config(layout="wide", page_title="Design a Water Filter: Simulation")
apply_html_theme()
st.sidebar.title("Chemistry with Computers")
st.sidebar.markdown("_Design a membrane that lets water through but blocks salt ions._")
st.sidebar.markdown("---")
st.sidebar.subheader("Controls")
pore_size   = st.sidebar.slider("Pore Size",     0.5, 4.0, 1.5, 0.1)
pore_charge = st.sidebar.slider("Pore Charge",  -2.0, 2.0, 0.0, 0.1)
pressure    = st.sidebar.slider("Pressure Push", 0.0, 2.0, 1.0, 0.1)
col_b1, col_b2 = st.sidebar.columns(2)

L = 15.0; N_water = 60; N_pos = 15; N_neg = 15; N = N_water + N_pos + N_neg
MAX_STEPS = 300; dt = 0.02; D = 1.0

radii = np.zeros(N); radii[:N_water] = 0.3; radii[N_water:] = 0.6
charges = np.zeros(N); charges[N_water:N_water+N_pos] = 1.0; charges[N_water+N_pos:] = -1.0

def init_state():
    pos = np.random.rand(N, 2)
    pos[:, 0] = pos[:, 0] * (L/2 - 2.0) + 0.5
    pos[:, 1] = pos[:, 1] * (L - 1.0) + 0.5
    st.session_state.pos = pos
    st.session_state.running = False; st.session_state.time_step = 0
    st.session_state.passed = np.zeros(N, dtype=bool)
    st.session_state.history_water = []; st.session_state.history_time = []

if st.session_state.get("current_simulation") != "nanopore" or "pos" not in st.session_state:
    for k in list(st.session_state.keys()):
        if k != "current_simulation": del st.session_state[k]
    st.session_state.current_simulation = "nanopore"
    init_state()

def full_reset():
    for k in list(st.session_state.keys()): del st.session_state[k]
    init_state()

with col_b1:
    if st.sidebar.button("Start / Pause", use_container_width=True):
        if st.session_state.time_step < MAX_STEPS:
            st.session_state.running = not st.session_state.running
with col_b2:
    if st.sidebar.button("Reset", use_container_width=True):
        full_reset(); st.rerun()

st.sidebar.markdown("### 💡 Science Idea")
st.sidebar.info("Nanoporous membranes separate solutes by **size** (steric exclusion) and **charge** (electrostatic repulsion). Real desalination membranes have pores just a few nanometers wide.")
st.sidebar.markdown("### 🎯 Challenge")
st.sidebar.success("- Set **Pore Size** so water (small) passes but ions (larger) are blocked.\n- Use **Pore Charge** to electrostatically repel ions.\n- Maximize water passed while keeping ions < 5.")
st.sidebar.markdown("### 🔬 Try This")
st.sidebar.warning("1. Pore Size = 1.0, Charge = 0.0. How many ions leak?\n2. Add Pore Charge = +1.5. Does it block positive ions?\n3. Find the smallest pore that lets > 50% water through.")

def apply_boundaries(new_pos, old_pos):
    ml = L/2 - 0.5; mr = L/2 + 0.5
    pt = L/2 + pore_size/2; pb = L/2 - pore_size/2
    for i in range(N):
        x, y = new_pos[i]; r = radii[i]
        x = np.clip(x, r, L-r); y = np.clip(y, r, L-r)
        if ml - r < x < mr + r:
            if y > pt - r or y < pb + r:
                ox = old_pos[i, 0]
                if ox <= ml - r:   x = ml - r
                elif ox >= mr + r: x = mr + r
                else:
                    if y > pt - r: y = pt - r
                    if y < pb + r: y = pb + r
        new_pos[i] = [x, y]
    return new_pos

def step_dynamics(pos):
    old_pos = pos.copy(); forces = np.zeros((N, 2))
    forces[:, 0] += pressure
    pc = np.array([L/2, L/2]); diff = pos - pc
    r = np.maximum(np.linalg.norm(diff, axis=1), 0.3)
    f_mag = pore_charge * charges * 15.0 / r**2
    forces[:, 0] += f_mag * diff[:, 0] / r
    forces[:, 1] += f_mag * diff[:, 1] / r
    new_pos = pos + dt * forces + np.sqrt(2*D*dt) * np.random.randn(N, 2)
    new_pos = apply_boundaries(new_pos, old_pos)
    diff2 = new_pos[:, np.newaxis, :] - new_pos[np.newaxis, :, :]
    dist = np.linalg.norm(diff2, axis=-1); np.fill_diagonal(dist, np.inf)
    rad_sum = radii[:, np.newaxis] + radii[np.newaxis, :]
    for i in range(N):
        for j in range(i+1, N):
            if (rad_sum[i,j] - dist[i,j]) > 0:
                direction = diff2[i,j] / dist[i,j]; ov = (rad_sum[i,j] - dist[i,j]) * 0.5
                new_pos[i] += direction * ov; new_pos[j] -= direction * ov
    return apply_boundaries(new_pos, old_pos)

if st.session_state.running:
    pos = st.session_state.pos
    for _ in range(8): pos = step_dynamics(pos)
    st.session_state.pos = pos; st.session_state.time_step += 1
    st.session_state.passed = pos[:, 0] > (L/2 + 0.5)
    if st.session_state.time_step >= MAX_STEPS: st.session_state.running = False
    wp = int(np.sum(st.session_state.passed[:N_water]))
    if st.session_state.time_step % 2 == 0:
        st.session_state.history_water.append(wp)
        st.session_state.history_time.append(st.session_state.time_step)
        if len(st.session_state.history_water) > 200:
            st.session_state.history_water.pop(0); st.session_state.history_time.pop(0)

water_passed = int(np.sum(st.session_state.passed[:N_water]))
pos_passed   = int(np.sum(st.session_state.passed[N_water:N_water+N_pos]))
neg_passed   = int(np.sum(st.session_state.passed[N_water+N_pos:]))
ions_passed  = pos_passed + neg_passed
score        = water_passed - 5 * ions_passed

# ── Layout ───────────────────────────────────────────────────────────────────
st.markdown("<h2 style='text-align:center;color:#e2e8f0'>💧 Design a Water Filter: Simulation</h2>", unsafe_allow_html=True)
col_anim, col_info = st.columns([2, 1])

with col_anim:
    st.subheader(f"Live Animation  —  Step {st.session_state.time_step}/{MAX_STEPS}")
    st.progress(st.session_state.time_step / MAX_STEPS)
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=theme["bg"])
    ax.set_facecolor(theme["plot_bg"]); ax.set_xlim(0, L); ax.set_ylim(0, L)
    ax.set_xticks([]); ax.set_yticks([])
    ml = L/2-0.5; mr = L/2+0.5; pt = L/2+pore_size/2; pb = L/2-pore_size/2
    # Membrane
    ax.add_patch(patches.Rectangle((ml, pt), 1.0, L-pt, color=theme["membrane"], zorder=3))
    ax.add_patch(patches.Rectangle((ml, 0),  1.0, pb,    color=theme["membrane"], zorder=3))
    # Pore highlight
    ax.add_patch(patches.Rectangle((ml, pb), 1.0, pore_size, color="#5d6d7e", alpha=0.5, zorder=3))
    ax.text(L/2, L/2, f"Pore\n±{pore_size:.1f}", ha="center", va="center", fontsize=8,
            color="white", fontweight="bold", zorder=4)
    # Left/right labels
    ax.text(L/4, L-0.8, "← Salt Water (pressure →)", ha="center", fontsize=9, color=theme["primary"], style="italic")
    ax.text(3*L/4, L-0.8, "Fresh Water →", ha="center", fontsize=9, color=theme["success"], style="italic")
    # Pressure arrow
    ax.annotate("", xy=(L/4+1, L/2), xytext=(L/4-1, L/2),
                arrowprops=dict(facecolor="#aab7b8", alpha=0.35, width=8, headwidth=20))
    pos = st.session_state.pos
    ax.scatter(pos[:N_water,0], pos[:N_water,1], c=theme["water"], s=55, edgecolors="none", alpha=0.8, zorder=2, label="Water")
    ax.scatter(pos[N_water:N_water+N_pos,0], pos[N_water:N_water+N_pos,1], c=theme["cation"], s=200, edgecolors="darkred", linewidths=1.2, zorder=5, label="Na⁺")
    for i in range(N_water, N_water+N_pos):
        ax.text(pos[i,0], pos[i,1], "+", color="white", ha="center", va="center", fontweight="bold", fontsize=9, zorder=6)
    ax.scatter(pos[N_water+N_pos:,0], pos[N_water+N_pos:,1], c=theme["anion"], s=200, edgecolors="#7d6608", linewidths=1.2, zorder=5, label="Cl⁻")
    for i in range(N_water+N_pos, N):
        ax.text(pos[i,0], pos[i,1], "−", color="black", ha="center", va="center", fontweight="bold", fontsize=9, zorder=6)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.85)
    st.pyplot(fig); plt.close(fig)

with col_info:
    st.subheader("Score & Status")
    if ions_passed == 0 and water_passed > 15:  smsg, scol = "✅ Perfect filter! Water passes, ions blocked!", theme["success"]
    elif ions_passed > 10:                        smsg, scol = "❌ Too large: salt leaks through!", theme["error"]
    elif water_passed < 5:                        smsg, scol = "❌ Too small: water cannot pass!", theme["error"]
    else:                                         smsg, scol = "⚠️ Decent filter, but can be optimized", theme["warning"]
    st.markdown(f"<div style='background:{scol};padding:10px;border-radius:8px;color:white;"
                f"text-align:center;font-weight:bold;font-size:1.05rem'>{smsg}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("💧 Water",  f"{water_passed}")
    c2.metric("🧂 Ions",   f"{ions_passed}")
    c3.metric("🏆 Score",  f"{score}")
    if ions_passed == 0 and water_passed > 15: st.success("You built a real desalination membrane!")
    elif score > 10: st.warning("Good start – refine pore size and charge.")
    else:            st.info("Adjust pore size and charge to improve selectivity.")

    st.subheader("Live Plot: Water Passed")
    fig2, ax2 = plt.subplots(figsize=(5, 2.2))
    if st.session_state.history_time:
        ax2.fill_between(st.session_state.history_time, st.session_state.history_water, alpha=0.2, color=theme["water"])
        ax2.plot(st.session_state.history_time, st.session_state.history_water, color=theme["water"], lw=2)
    ax2.axhline(15, color=theme["success"], linestyle="--", lw=1.5, label="Goal (15)")
    ax2.set_xlabel("Time (steps)", fontsize=8); ax2.set_ylabel("Water Passed", fontsize=8)
    ax2.set_xlim(left=max(0, st.session_state.time_step-200), right=st.session_state.time_step+10)
    ax2.set_ylim(0, N_water+5); ax2.legend(fontsize=7); ax2.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig2); plt.close(fig2)

if st.session_state.running:
    time.sleep(0.04)
    st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© Dasgupta Research Group @ K-State <a href='https://www.drgatksu.com' target='_blank' style='color: gray; text-decoration: underline;'>www.drgatksu.com</a></p>", unsafe_allow_html=True)
