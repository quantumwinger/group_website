import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import time
from app_theme import HTML_THEME, apply_html_theme

theme = {
    **HTML_THEME,
    "solid": HTML_THEME["accent_amber"], "liquid": HTML_THEME["accent"],
}

st.set_page_config(layout="wide", page_title="Make a Crystal: Freezing Game")
apply_html_theme()
st.sidebar.title("Chemistry with Computers")
st.sidebar.markdown("_Explore how a dense liquid freezes into a solid crystal lattice._")
st.sidebar.markdown("---")
st.sidebar.subheader("Controls")
epsilon    = st.sidebar.slider("Attraction Strength (ε)", 0.1, 2.0, 0.5, 0.1)
temperature_k = st.sidebar.slider("Temperature (K)", 100, 600, 300, 10)
temperature = temperature_k / 300.0
col_b1, col_b2 = st.sidebar.columns(2)

L = 12.0; N = 100; mass = 1.0; sigma = 1.0; dt = 0.005

def init_state():
    st.session_state.pos    = np.random.rand(N, 2) * L
    st.session_state.vel    = (np.random.rand(N, 2) - 0.5) * 2.0
    st.session_state.forces = np.zeros((N, 2))
    st.session_state.running   = False
    st.session_state.time_step = 0
    st.session_state.history_size = []
    st.session_state.history_time = []

if "pos" not in st.session_state:
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

with st.sidebar.expander("💡 Science Idea"):
    st.write("When temperature drops, molecules lose kinetic energy. If intermolecular attractions are strong enough, they lock into a structured **crystal lattice**, transitioning from a disordered liquid to a solid.")
with st.sidebar.expander("🎯 Challenge"):
    st.write("- Lower **Temperature** to freeze the liquid.\n- Increase **Attraction Strength** to help molecules bind.\n- Aim for **Crystal Score > 40%** to win!")
with st.sidebar.expander("🔬 Try This"):
    st.write("1. Set Attraction = 1.5, Temperature = 100 K. Watch bonds form!\n2. Increase Temperature to 450 K. Does the crystal melt?\n3. How large a crystal can you make by tuning both sliders?")

def compute_forces(pos, eps):
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    diff = diff - L * np.round(diff / L)
    r2 = np.sum(diff**2, axis=-1)
    np.fill_diagonal(r2, np.inf)
    r2 = np.maximum(r2, 0.5)
    r6 = (sigma**2 / r2)**3; r12 = r6**2
    force_mag = 4 * eps * (12 * r12 - 6 * r6) / r2
    return np.column_stack((np.sum(force_mag * diff[:,:,0], axis=1),
                            np.sum(force_mag * diff[:,:,1], axis=1)))

def get_largest_cluster(pos):
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    diff = diff - L * np.round(diff / L)
    r2 = np.sum(diff**2, axis=-1)
    adj_dense = (r2 > 0.01) & (r2 < (1.2 * sigma)**2)
    is_solid = np.sum(adj_dense, axis=1) >= 5
    adj = adj_dense & is_solid[:, np.newaxis] & is_solid[np.newaxis, :]
    visited = np.zeros(N, dtype=bool); max_cluster = []
    for i in range(N):
        if is_solid[i] and not visited[i]:
            cluster, queue = [], [i]; visited[i] = True
            while queue:
                cur = queue.pop(0); cluster.append(cur)
                for n in np.where(adj[cur])[0]:
                    if not visited[n]: visited[n] = True; queue.append(n)
            if len(cluster) > len(max_cluster): max_cluster = cluster
    return max_cluster, is_solid, adj_dense

if st.session_state.running:
    pos, vel, forces = st.session_state.pos, st.session_state.vel, st.session_state.forces
    for _ in range(15):
        vel += 0.5 * dt * forces / mass
        pos = (pos + dt * vel) % L
        forces = compute_forces(pos, epsilon)
        vel += 0.5 * dt * forces / mass
        cur_T = 0.5 * mass * np.sum(vel**2) / N
        if cur_T > 0: vel *= (1.0 + 0.05 * (np.sqrt(temperature / cur_T) - 1.0))
    st.session_state.pos = pos; st.session_state.vel = vel; st.session_state.forces = forces
    st.session_state.time_step += 1
    if st.session_state.time_step % 2 == 0:
        cluster, _, _ = get_largest_cluster(pos)
        st.session_state.history_size.append(len(cluster))
        st.session_state.history_time.append(st.session_state.time_step)
        if len(st.session_state.history_size) > 200:
            st.session_state.history_size.pop(0); st.session_state.history_time.pop(0)

cluster, is_solid, adj_dense = get_largest_cluster(st.session_state.pos)
score = len(cluster) / N * 100

# ── Layout ──────────────────────────────────────────────────────────────────
st.markdown("<h2 style='text-align:center;color:#e2e8f0'>❄️ Make a Crystal: Liquid-to-Solid Freezing Game</h2>", unsafe_allow_html=True)
col_anim, col_info = st.columns([2, 1])

with col_anim:
    st.subheader("Live 2D Particle Animation")
    fig, ax = plt.subplots(figsize=(6, 6), facecolor=theme["bg"])
    ax.set_facecolor(theme["plot_bg"]); ax.set_xlim(0, L); ax.set_ylim(0, L)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.add_patch(plt.Rectangle((0,0), L, L, fill=False, color=theme["primary"], lw=2))
    pos = st.session_state.pos
    # Draw crystal bonds
    lines = []
    for i in range(N):
        if is_solid[i]:
            for j in range(i+1, N):
                if is_solid[j] and adj_dense[i, j]:
                    if abs(pos[i,0]-pos[j,0]) < L/2 and abs(pos[i,1]-pos[j,1]) < L/2:
                        lines.append([(pos[i,0],pos[i,1]),(pos[j,0],pos[j,1])])
    if lines:
        ax.add_collection(LineCollection(lines, colors=theme["solid"], linewidths=2, alpha=0.7, zorder=1))
    colors = [theme["solid"] if is_solid[i] else theme["liquid"] for i in range(N)]
    ax.scatter(pos[:,0], pos[:,1], c=colors, s=150, edgecolors="white", linewidths=0.8, alpha=0.92, zorder=2)
    ax.set_title(f"🟠 Solid (crystallized)   🔵 Liquid (disordered)   |   Step {st.session_state.time_step}", fontsize=9)
    st.pyplot(fig); plt.close(fig)

with col_info:
    st.subheader("Score & Status")
    if score > 40:    smsg, scol = "❄️ Crystal formed! You win!", theme["success"]
    elif score > 15:  smsg, scol = "🧊 Nucleating: crystals forming…", theme["warning"]
    else:             smsg, scol = "💧 Liquid: particles are disordered", theme["primary"]
    st.markdown(f"<div style='background:{scol};padding:10px;border-radius:8px;color:white;"
                f"text-align:center;font-weight:bold;font-size:1.1rem'>{smsg}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Crystal Score", f"{score:.1f}%")
    c2.metric("Crystal Particles", f"{len(cluster)}/{N}")
    if score > 40:   st.success("Excellent! A stable crystal lattice has formed.")
    elif score > 15: st.warning("Clusters are growing – lower temperature more!")
    else:            st.info("Increase attraction or lower temperature to nucleate.")

    st.subheader("Live Plot: Crystal Size")
    fig2, ax2 = plt.subplots(figsize=(5, 2.2))
    if st.session_state.history_time:
        ax2.fill_between(st.session_state.history_time, st.session_state.history_size, alpha=0.2, color=theme["solid"])
        ax2.plot(st.session_state.history_time, st.session_state.history_size, color=theme["solid"], lw=2)
    ax2.axhline(N * 0.4, color=theme["success"], linestyle="--", lw=1.5, label="Goal (40%)")
    ax2.set_xlabel("Time (steps)", fontsize=8); ax2.set_ylabel("Crystal Particles", fontsize=8)
    ax2.set_xlim(left=max(0, st.session_state.time_step-200), right=st.session_state.time_step+10)
    ax2.set_ylim(0, N+5); ax2.legend(fontsize=7); ax2.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig2); plt.close(fig2)

if st.session_state.running:
    time.sleep(0.04)
    st.rerun()
