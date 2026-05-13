import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from app_theme import HTML_THEME, apply_html_theme

theme = {
    **HTML_THEME,
    "reactant": HTML_THEME["accent_red"], "product": HTML_THEME["success"],
}

st.set_page_config(layout="wide", page_title="Lower the Hill: Catalyst Reaction Game")
apply_html_theme()
st.sidebar.title("Chemistry with Computers")
st.sidebar.markdown("_Watch how a catalyst lowers the activation energy of a reaction._")
st.sidebar.markdown("---")
st.sidebar.subheader("Controls")
cat_strength = st.sidebar.slider("Catalyst Strength", 0.0, 1.0, 0.0, 0.05)
temperature_k = st.sidebar.slider("Temperature (K)", 100, 600, 300, 10)
temperature = temperature_k / 300.0
col_b1, col_b2 = st.sidebar.columns(2)

N = 100; MAX_STEPS = 300; dt = 0.01

def init_state():
    st.session_state.x = np.random.randn(N) * 0.2 - 1.6
    st.session_state.y_offsets = np.random.rand(N) * 2.5 + 0.5
    st.session_state.running = False; st.session_state.time_step = 0
    st.session_state.history_products = []; st.session_state.history_time = []

if st.session_state.get("current_game") != "catalyst" or "x" not in st.session_state:
    for k in list(st.session_state.keys()):
        if k != "current_game": del st.session_state[k]
    st.session_state.current_game = "catalyst"
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
st.sidebar.info("A catalyst provides an **alternative pathway** with lower activation energy, letting more molecules cross the energy barrier. Temperature supplies kinetic energy to help molecules climb the hill.")
st.sidebar.markdown("### 🎯 Challenge")
st.sidebar.success("- Increase **Catalyst Strength** to lower the barrier.\n- Raise **Temperature** for more kinetic energy.\n- Aim for **> 80 products** before the timer runs out!")
st.sidebar.markdown("### 🔬 Try This")
st.sidebar.warning("1. Catalyst = 0.6, Temperature = 150 K. What happens?\n2. Catalyst = 0.0, Temperature = 450 K. Compare reaction speed.\n3. Find the minimum catalyst + temperature combo to reach > 80 products.")

def E_curve(x, cat):
    return 0.5*x**4 - 3*x**2 - 1.5*x + 12.0*(1.0-cat)*np.exp(-x**2)

def force(x, cat):
    return -(2*x**3 - 6*x - 1.5 + 12.0*(1.0-cat)*(-2*x)*np.exp(-x**2))

if st.session_state.running:
    x = st.session_state.x
    for _ in range(10):
        x += dt * force(x, cat_strength) + np.sqrt(2*temperature*dt*2.0)*np.random.randn(N)
        x = np.clip(x, -2.8, 2.8)
    st.session_state.x = x; st.session_state.time_step += 1
    if st.session_state.time_step >= MAX_STEPS: st.session_state.running = False
    products = int(np.sum(x > 0))
    if st.session_state.time_step % 2 == 0:
        st.session_state.history_products.append(products)
        st.session_state.history_time.append(st.session_state.time_step)
        if len(st.session_state.history_products) > 200:
            st.session_state.history_products.pop(0); st.session_state.history_time.pop(0)

products = int(np.sum(st.session_state.x > 0))
pct      = products / N * 100

# ── Layout ───────────────────────────────────────────────────────────────────
st.markdown("<h2 style='text-align:center;color:#e2e8f0'>⚗️ Lower the Hill: Catalyst Reaction Game</h2>", unsafe_allow_html=True)
col_anim, col_info = st.columns([2, 1])

with col_anim:
    st.subheader(f"Live Animation  —  Step {st.session_state.time_step}/{MAX_STEPS}")
    st.progress(st.session_state.time_step / MAX_STEPS)
    fig, ax = plt.subplots(figsize=(8, 4), facecolor=theme["bg"])
    ax.set_facecolor(theme["plot_bg"])
    X_plot = np.linspace(-3, 3, 300)
    Y_plot = E_curve(X_plot, cat_strength)
    # Shaded wells
    ax.fill_between(X_plot[X_plot < 0], -20, Y_plot[X_plot < 0], color="#fadbd8", alpha=0.5)
    ax.fill_between(X_plot[X_plot > 0], -20, Y_plot[X_plot > 0], color="#d5f5e3", alpha=0.5)
    ax.plot(X_plot, Y_plot, color=theme["primary"], lw=3, zorder=3)
    # Particles
    x_p = st.session_state.x; y_p = E_curve(x_p, cat_strength) + st.session_state.y_offsets
    is_prod = x_p > 0
    ax.scatter(x_p[~is_prod], y_p[~is_prod], c=theme["reactant"], s=80, edgecolors="white", linewidths=0.6, zorder=5, alpha=0.85)
    ax.scatter(x_p[is_prod],  y_p[is_prod],  c=theme["product"],  s=80, edgecolors="white", linewidths=0.6, zorder=5, alpha=0.85)
    # Labels
    ymax = max(Y_plot)
    ax.text(-1.8, ymax+3, "⚛ Reactants", fontsize=13, ha="center", fontweight="bold", color=theme["reactant"])
    ax.text( 1.8, ymax+3, "✅ Products",  fontsize=13, ha="center", fontweight="bold", color=theme["product"])
    barrier = E_curve(0, cat_strength) - E_curve(-1.6, cat_strength)
    ax.text(0, ymax+5, f"Activation Energy: {barrier:.1f}", fontsize=11, ha="center", color="gray")
    ax.annotate("", xy=(0, E_curve(0, cat_strength)), xytext=(0, E_curve(-1.6, cat_strength)),
                arrowprops=dict(arrowstyle="<->", color="#2980b9", lw=2))
    ax.set_xlim(-3, 3); ax.set_ylim(-15, max(18, ymax+8))
    ax.set_xticks([]); ax.set_yticks([])
    st.pyplot(fig); plt.close(fig)

with col_info:
    st.subheader("Score & Status")
    game_over = st.session_state.time_step >= MAX_STEPS
    if game_over:
        if products > 80:    smsg, scol = "🏆 Fast reaction! Catalyst wins!", theme["success"]
        elif products > 30:  smsg, scol = "⚠️ Moderate – try more catalyst or heat", theme["warning"]
        else:                smsg, scol = "❌ Too slow – barrier was too high", theme["error"]
    else:
        if products < 5:     smsg, scol = "⏳ Few molecules have enough energy…", theme["dim"]
        elif products < 40:  smsg, scol = "🔥 Reaction is proceeding!", theme["warning"]
        else:                smsg, scol = "🚀 Fast reaction! Products forming!", theme["success"]
    st.markdown(f"<div style='background:{scol};padding:10px;border-radius:8px;color:white;"
                f"text-align:center;font-weight:bold;font-size:1.05rem'>{smsg}</div>", unsafe_allow_html=True)
    if game_over: st.markdown("**⏱ Game Over!**")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Products", f"{products}")
    c2.metric("Conversion", f"{pct:.1f}%")
    if products > 80 and game_over: st.success("Outstanding! You optimised the reaction perfectly.")
    elif pct > 50:                  st.warning("More than half converted – keep going!")
    else:                           st.info("Raise catalyst strength or temperature to speed up.")

    st.subheader("Live Plot: Products vs Time")
    fig2, ax2 = plt.subplots(figsize=(5, 2.2))
    if st.session_state.history_time:
        ax2.fill_between(st.session_state.history_time, st.session_state.history_products, alpha=0.2, color=theme["product"])
        ax2.plot(st.session_state.history_time, st.session_state.history_products, color=theme["product"], lw=2)
    ax2.axhline(80, color=theme["success"], linestyle="--", lw=1.5, label="Goal (80)")
    ax2.set_xlabel("Time (steps)", fontsize=8); ax2.set_ylabel("Products", fontsize=8)
    ax2.set_xlim(left=max(0, st.session_state.time_step-200), right=st.session_state.time_step+10)
    ax2.set_ylim(0, N+5); ax2.legend(fontsize=7); ax2.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig2); plt.close(fig2)

if st.session_state.running:
    time.sleep(0.04)
    st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© Dasgupta Research Group @ K-State <a href='https://www.drgatksu.com' target='_blank' style='color: gray; text-decoration: underline;'>www.drgatksu.com</a></p>", unsafe_allow_html=True)
