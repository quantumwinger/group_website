import time

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from app_theme import HTML_THEME, apply_html_theme


theme = {
    **HTML_THEME,
    "water": HTML_THEME["accent"],
    "reactant": HTML_THEME["success"],
    "ts": HTML_THEME["warning"],
    "product": HTML_THEME["accent_purple"],
    "membrane": HTML_THEME["card_border"],
}


st.set_page_config(layout="wide", page_title="Reaction Pathway Explorer")
apply_html_theme()


def init_state():
    st.session_state.running = False
    st.session_state.time_step = 0
    st.session_state.path_s = 0.0


if "running" not in st.session_state:
    init_state()


def full_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


st.sidebar.title("Chemistry with Computers")
st.sidebar.markdown("_Use a reaction coordinate scan to map a molecular pathway._")
st.sidebar.markdown("---")

with st.sidebar.expander("💡 Science Idea"):
    st.write(
        "Computational chemists can study a reaction by calculating the energy at many points as the "
        "**Nu-C distance** gets shorter and the **C-Lg distance** gets longer. The full energy curve "
        "shows the reactants, the highest-energy transition-state region, and the products."
    )
with st.sidebar.expander("🎯 Challenge"):
    st.write(
        "- Adjust the molecular setup to lower the energy barrier.\n"
        "- Watch the moving marker trace the pathway.\n"
        "- Use the energy plot to identify the transition state and reaction energy."
    )
with st.sidebar.expander("🔬 Try This"):
    st.write(
        "1. Increase the attack angle and Nu-C bond-making strength. What happens to the barrier?\n"
        "2. Make the C-Lg bond easier to break. What changes on the energy plot?\n"
        "3. Compare a low-barrier and high-barrier pathway using the plot."
    )

st.markdown(
    "<h2 style='text-align:center;color:#e2e8f0'>Reaction Pathway Explorer</h2>",
    unsafe_allow_html=True,
)

col_anim, col_info = st.columns([2, 1])

with col_info:
    st.subheader("Controls")
    bond_making_strength = st.slider("Nu-C Bond-Making Strength", 0.0, 2.0, 1.0, 0.1)
    bond_breaking_ease = st.slider("C-Lg Bond-Breaking Ease", 0.0, 2.0, 1.0, 0.1)
    molecular_alignment = st.slider("Attack Angle (degrees)", 120, 180, 170, 5)
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("Start / Pause", use_container_width=True):
            if st.session_state.path_s >= 1.0:
                st.session_state.path_s = 0.0
                st.session_state.time_step = 0
            st.session_state.running = not st.session_state.running
    with col_b2:
        if st.button("Reset", use_container_width=True):
            full_reset()
            st.rerun()

sigma = 0.12
s_vals = np.linspace(0.0, 1.0, 300)
alignment_fraction = molecular_alignment / 180.0

barrier_height = (
    35
    - 7 * bond_making_strength
    - 7 * bond_breaking_ease
    - 10 * alignment_fraction
    + 20 * (1 - alignment_fraction) ** 2
)

reaction_energy = 5 - 3 * bond_making_strength
energy_curve = barrier_height * np.exp(-((s_vals - 0.5) ** 2) / (2 * sigma**2)) + reaction_energy * s_vals
energy_relative = energy_curve - energy_curve[0]

ts_idx = int(np.argmax(energy_relative))
ts_s = float(s_vals[ts_idx])
ts_energy = float(energy_relative[ts_idx])
reactant_energy = float(energy_relative[0])
product_energy = float(energy_relative[-1])
ea = float(np.max(energy_relative) - energy_relative[0])
delta_e = float(energy_relative[-1] - energy_relative[0])

current_s = float(np.clip(st.session_state.path_s, 0.0, 1.0))
current_energy = float(np.interp(current_s, s_vals, energy_relative))

if ea < 8:
    status_msg, status_col = "✅ Low-barrier pathway found.", theme["success"]
elif ea < 25:
    status_msg, status_col = "⚠️ Moderate barrier: pathway exists but is harder.", theme["warning"]
else:
    status_msg, status_col = "❌ High barrier: the computer predicts a difficult pathway.", theme["error"]

score = max(0, int(100 - 3 * ea - 8 * max(delta_e, 0)))

with col_anim:
    st.subheader(f"Live Molecular Animation  —  Step {st.session_state.time_step}")
    st.progress(current_s)

    fig, ax = plt.subplots(figsize=(8, 5), facecolor=theme["bg"])
    ax.set_facecolor(theme["plot_bg"])
    ax.set_xlim(-4.8, 4.8)
    ax.set_ylim(-2.8, 2.8)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    x_c, y_c = 0.0, 0.0
    lg_distance = 2.0 + 2.1 * current_s
    x_lg, y_lg = lg_distance, 0.0
    nu_distance = 4.0 - 2.3 * current_s
    attack_rad = np.radians(molecular_alignment)
    x_nu = -nu_distance * np.sin(attack_rad - np.pi / 2)
    y_nu = nu_distance * np.cos(attack_rad - np.pi / 2)

    h_y_base = np.array([1.25, -1.25, 0.0])
    h_x_shift = -0.95 + 1.9 * current_s
    h_flatten = 1.0 - 0.28 * np.exp(-((current_s - 0.5) ** 2) / (2 * 0.14**2))
    h_positions = np.column_stack(
        (
            h_x_shift + np.array([0.0, 0.0, 0.25 * np.cos(np.pi * current_s)]),
            h_y_base * h_flatten,
        )
    )

    if current_s < 0.92:
        lg_width = max(1.2, 4.4 * (1 - current_s))
        lg_style = "-" if current_s < ts_s else "--"
        ax.plot([x_c, x_lg], [y_c, y_lg], color="gray", lw=lg_width, ls=lg_style, zorder=1)
    if current_s > 0.08:
        nu_width = max(1.2, 4.4 * current_s)
        nu_style = "--" if current_s < ts_s else "-"
        ax.plot([x_c, x_nu], [y_c, y_nu], color="gray", lw=nu_width, ls=nu_style, zorder=1)

    for hx, hy in h_positions:
        ax.plot([x_c, hx], [y_c, hy], color="gray", lw=2.4, zorder=1)
        ax.scatter(hx, hy, c="#bdc3c7", s=220, edgecolors="white", linewidths=1.2, zorder=2)
        ax.text(hx, hy + 0.2, "H", ha="center", va="center", fontsize=8, color="#7f8c8d")

    ax.scatter(x_c, y_c, c=theme["membrane"], s=520, edgecolors="white", linewidths=2.0, zorder=4)
    ax.text(x_c, y_c, "C", ha="center", va="center", color="white", fontweight="bold", zorder=5)

    ax.scatter(x_nu, y_nu, c=theme["reactant"], s=520, edgecolors="white", linewidths=2.0, zorder=4)
    ax.text(x_nu, y_nu, "Nu", ha="center", va="center", color="white", fontweight="bold", zorder=5)

    ax.scatter(x_lg, y_lg, c=theme["product"], s=560, edgecolors="white", linewidths=2.0, zorder=4)
    ax.text(x_lg, y_lg, "LG", ha="center", va="center", color="white", fontweight="bold", zorder=5)

    ax.text(-4.3, 2.2, f"Nu-C distance = {nu_distance:.2f}", fontsize=10, color=theme["primary"], fontweight="bold")
    ax.text(-4.3, 1.8, f"C-Lg distance = {lg_distance:.2f}", fontsize=10, color=theme["primary"], fontweight="bold")
    ax.text(-4.3, 1.4, f"Relative energy = {current_energy:.1f}", fontsize=10, color=theme["primary"])

    if abs(current_s - ts_s) < 0.08:
        ax.text(0, -2.2, "Transition-state region", ha="center", color=theme["warning"], fontweight="bold", fontsize=12)
    elif current_s < ts_s:
        ax.text(0, -2.2, "Reactant side of the pathway", ha="center", color=theme["primary"], fontsize=11)
    else:
        ax.text(0, -2.2, "Product side of the pathway", ha="center", color=theme["success"], fontsize=11)

    st.pyplot(fig)
    plt.close(fig)

with col_info:
    st.subheader("Score & Status")
    st.markdown(
        f"<div style='background:{status_col};padding:10px;border-radius:8px;color:white;"
        f"text-align:center;font-weight:bold;font-size:1.05rem'>{status_msg}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Barrier Ea", f"{ea:.1f}")
    c2.metric("ΔE", f"{delta_e:.1f}")
    c3.metric("Score", f"{score}")

    if delta_e < 0:
        st.success("Products lie lower in energy than reactants in this toy model.")
    elif delta_e < 5:
        st.warning("Products are near the reactants in energy.")
    else:
        st.info("Products end higher in energy, even if the path still exists.")

    st.markdown("**How to read the plot**")
    st.write(
        "The moving dot shows the current geometry. As Nu gets closer to C and Lg moves farther away, "
        "the highest point on the curve marks the transition state, and the vertical arrow marks the activation barrier."
    )

st.subheader("Live Energy Plot")
fig2, ax2 = plt.subplots(figsize=(12, 3.8), facecolor=theme["bg"])
ax2.set_facecolor(theme["plot_bg"])
ax2.plot(s_vals, energy_relative, color=theme["primary"], lw=3.2)
ax2.axhline(0, color="gray", linestyle="--", lw=1)

ax2.scatter([0], [reactant_energy], c=theme["reactant"], s=110, edgecolors="white", linewidths=1.4, zorder=5)
ax2.scatter([ts_s], [ts_energy], c=theme["ts"], s=120, edgecolors="white", linewidths=1.4, zorder=5)
ax2.scatter([1], [product_energy], c=theme["product"], s=110, edgecolors="white", linewidths=1.4, zorder=5)
ax2.scatter([current_s], [current_energy], c=theme["accent"], s=140, edgecolors="white", linewidths=1.8, zorder=6)

ax2.text(0.0, reactant_energy + 1.5, "Reactants", color=theme["reactant"], fontsize=10, fontweight="bold", ha="left")
ax2.text(ts_s, ts_energy + 1.8, "Transition State", color=theme["ts"], fontsize=10, fontweight="bold", ha="center")
ax2.text(1.0, product_energy + 1.5, "Products", color=theme["product"], fontsize=10, fontweight="bold", ha="right")

arrow_x = ts_s
ax2.annotate(
    "",
    xy=(arrow_x, ts_energy),
    xytext=(arrow_x, reactant_energy),
    arrowprops=dict(arrowstyle="<->", color=theme["accent"], lw=2.2),
)
ax2.text(
    min(arrow_x + 0.04, 0.92),
    0.5 * (ts_energy + reactant_energy),
    f"Ea = {ea:.1f}",
    color=theme["accent"],
    fontsize=10,
    fontweight="bold",
    va="center",
)

delta_mid_x = 0.82
delta_mid_y = 0.5 * (product_energy + reactant_energy)
ax2.annotate(
    "",
    xy=(delta_mid_x, product_energy),
    xytext=(delta_mid_x, reactant_energy),
    arrowprops=dict(arrowstyle="<->", color=theme["product"], lw=1.8, alpha=0.9),
)
ax2.text(
    delta_mid_x + 0.02,
    delta_mid_y,
    f"ΔE = {delta_e:.1f}",
    color=theme["product"],
    fontsize=10,
    fontweight="bold",
    va="center",
)

ax2.text(
    0.02,
    0.95,
    f"Activation barrier: {ea:.1f}\nReaction energy: {delta_e:.1f}",
    transform=ax2.transAxes,
    fontsize=10,
    ha="left",
    va="top",
    bbox=dict(boxstyle="round,pad=0.35", facecolor="#fdfefe", edgecolor="#d5dbdb"),
)

ax2.set_xlabel("Reaction coordinate (0 = reactants, 1 = products)", fontsize=10)
ax2.set_ylabel("Relative energy", fontsize=10)
ax2.set_xlim(0, 1)
ax2.set_ylim(np.min(energy_relative) - 4, np.max(energy_relative) + 8)
ax2.grid(True, linestyle="--", alpha=0.35)
st.pyplot(fig2)
plt.close(fig2)

if st.session_state.running:
    st.session_state.path_s = min(1.0, st.session_state.path_s + 0.02)
    st.session_state.time_step += 1
    if st.session_state.path_s >= 1.0:
        st.session_state.running = False
    time.sleep(0.04)
    st.rerun()
