import time

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.collections import LineCollection

from app_theme import HTML_THEME, apply_html_theme


theme = {
    **HTML_THEME,
    "solid": HTML_THEME["accent_amber"],
    "liquid": "#38bdf8",
    "bond": "#fbbf24",
    "guide": "#fde68a",
}

st.set_page_config(layout="wide", page_title="Make a Crystal: Simulation")
apply_html_theme()

L = 14.0
N = 144
mass = 1.0
sigma = 1.0
dt = 0.004
STEPS_PER_FRAME = 18


def phase_drive(eps, temp_k):
    """Returns 0 for liquid-like settings and 1 for strongly solid-like settings."""
    cold_term = (300 - temp_k) / 70
    attraction_term = 2.9 * (eps - 1.0)
    return float(1 / (1 + np.exp(-(cold_term + attraction_term))))


def make_lattice_points(n, box_length):
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    spacing = box_length / (cols + 0.8)
    y_spacing = spacing * np.sqrt(3) / 2
    width = spacing * (cols - 1 + 0.5)
    height = y_spacing * (rows - 1)
    x0 = (box_length - width) / 2
    y0 = (box_length - height) / 2

    points = []
    for row in range(rows):
        for col in range(cols):
            x = x0 + spacing * (col + 0.5 * (row % 2))
            y = y0 + y_spacing * row
            points.append((x, y))
            if len(points) == n:
                return np.array(points)
    return np.array(points[:n])


LATTICE_POINTS = make_lattice_points(N, L)

st.sidebar.title("Chemistry with Computers")
st.sidebar.markdown("_Explore how a dense liquid freezes into a solid crystal lattice._")
st.sidebar.markdown("---")
st.sidebar.subheader("Controls")
epsilon = st.sidebar.slider(
    "Attraction Strength (ε)",
    0.1,
    2.0,
    0.8,
    0.1,
    help="Higher attraction makes particles bond and line up more easily.",
)
temperature_k = st.sidebar.slider(
    "Temperature (K)",
    100,
    600,
    360,
    10,
    help="Lower temperature slows particles and helps the crystal lock in.",
)
temperature = temperature_k / 300.0
solid_drive = phase_drive(epsilon, temperature_k)
col_b1, col_b2 = st.sidebar.columns(2)


def init_state():
    st.session_state.pos = (LATTICE_POINTS + np.random.normal(0, 0.82, (N, 2))) % L
    st.session_state.vel = np.random.normal(0, np.sqrt(temperature), (N, 2))
    st.session_state.forces = np.zeros((N, 2))
    st.session_state.anchor_order = np.arange(N)
    st.session_state.running = False
    st.session_state.time_step = 0
    st.session_state.history_size = []
    st.session_state.history_time = []
    st.session_state.n_particles = N


if (
    st.session_state.get("current_simulation") != "nucleation"
    or st.session_state.get("n_particles") != N
    or "pos" not in st.session_state
):
    for key in list(st.session_state.keys()):
        if key != "current_simulation":
            del st.session_state[key]
    st.session_state.current_simulation = "nucleation"
    init_state()


def full_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


with col_b1:
    if st.sidebar.button("Start / Pause", use_container_width=True):
        st.session_state.running = not st.session_state.running
with col_b2:
    if st.sidebar.button("Reset", use_container_width=True):
        full_reset()
        st.rerun()

phase_name = "Solid" if solid_drive > 0.68 else "Mixed" if solid_drive > 0.32 else "Liquid"
phase_color = theme["solid"] if solid_drive > 0.68 else theme["warning"] if solid_drive > 0.32 else theme["liquid"]
st.sidebar.markdown("### Phase Tendency")
st.sidebar.progress(solid_drive)
st.sidebar.markdown(
    f"<div style='color:{phase_color};font-weight:700'>{phase_name}: "
    f"{solid_drive * 100:.0f}% solid-favoring conditions</div>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("### Science Idea")
st.sidebar.info(
    "Cold particles move slowly. Strong attractions let neighbors hold each other in place, "
    "so the liquid can lock into a repeating crystal lattice."
)
st.sidebar.markdown("### Challenge")
st.sidebar.success(
    "- Lower **Temperature** to freeze the liquid.\n"
    "- Increase **Attraction Strength** to help molecules bind.\n"
    "- Aim for **Crystal Score > 50%** to win!"
)
st.sidebar.markdown("### Try This")
st.sidebar.warning(
    "1. Set Attraction = 1.5 and Temperature = 120 K. Watch the ordered lattice grow.\n"
    "2. Increase Temperature to 480 K. The bonds should melt away.\n"
    "3. Tune both sliders to find the boundary between liquid and solid."
)


def compute_forces(pos, eps):
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    diff = diff - L * np.round(diff / L)
    r2 = np.sum(diff**2, axis=-1)
    np.fill_diagonal(r2, np.inf)
    r2 = np.maximum(r2, 0.45)
    r6 = (sigma**2 / r2) ** 3
    r12 = r6**2
    force_mag = 4 * eps * (12 * r12 - 6 * r6) / r2
    forces = np.column_stack(
        (
            np.sum(force_mag * diff[:, :, 0], axis=1),
            np.sum(force_mag * diff[:, :, 1], axis=1),
        )
    )
    force_norm = np.linalg.norm(forces, axis=1)
    scale = np.minimum(1.0, 55.0 / (force_norm + 1e-9))
    return forces * scale[:, np.newaxis]


def assigned_anchor_displacement(pos):
    targets = LATTICE_POINTS[st.session_state.anchor_order]
    displacement = targets - pos
    return displacement - L * np.round(displacement / L)


def local_structure(pos):
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    diff = diff - L * np.round(diff / L)
    r2 = np.sum(diff**2, axis=-1)
    adj_dense = (r2 > 0.01) & (r2 < (1.28 * sigma) ** 2)
    coordination = np.sum(adj_dense, axis=1)

    angles = np.arctan2(diff[:, :, 1], diff[:, :, 0])
    sixfold = np.sum(adj_dense * np.exp(6j * angles), axis=1)
    order = np.zeros(N)
    has_neighbors = coordination > 0
    order[has_neighbors] = np.abs(sixfold[has_neighbors]) / coordination[has_neighbors]
    return adj_dense, coordination, order


def get_largest_cluster(pos, drive):
    adj_dense, coordination, local_order = local_structure(pos)
    is_solid = (drive > 0.24) & (coordination >= 3) & (local_order > 0.38)
    adj = adj_dense & is_solid[:, np.newaxis] & is_solid[np.newaxis, :]
    visited = np.zeros(N, dtype=bool)
    max_cluster = []

    for i in range(N):
        if is_solid[i] and not visited[i]:
            cluster, queue = [], [i]
            visited[i] = True
            while queue:
                cur = queue.pop(0)
                cluster.append(cur)
                for neighbor in np.where(adj[cur])[0]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append(neighbor)
            if len(cluster) > len(max_cluster):
                max_cluster = cluster
    return max_cluster, is_solid, adj_dense, coordination, local_order


if st.session_state.running:
    pos = st.session_state.pos
    vel = st.session_state.vel
    forces = st.session_state.forces
    target_temperature = max(0.06, temperature)

    for _ in range(STEPS_PER_FRAME):
        lattice_force = (2.0 + 18.0 * solid_drive**2) * assigned_anchor_displacement(pos)
        forces = compute_forces(pos, epsilon) + solid_drive**2 * lattice_force
        vel += 0.5 * dt * forces / mass
        pos = (pos + dt * vel) % L

        lattice_force = (2.0 + 18.0 * solid_drive**2) * assigned_anchor_displacement(pos)
        forces = compute_forces(pos, epsilon) + solid_drive**2 * lattice_force
        vel += 0.5 * dt * forces / mass

        noise = np.random.normal(
            0,
            0.018 * np.sqrt(target_temperature) * (1 - 0.72 * solid_drive),
            vel.shape,
        )
        vel += noise

        cur_temperature = 0.5 * mass * np.sum(vel**2) / N
        if cur_temperature > 0:
            thermostat = 0.08 + 0.12 * solid_drive
            vel *= 1.0 + thermostat * (np.sqrt(target_temperature / cur_temperature) - 1.0)
        vel *= 1.0 - 0.035 * solid_drive

    st.session_state.pos = pos
    st.session_state.vel = vel
    st.session_state.forces = forces
    st.session_state.time_step += 1
    if st.session_state.time_step % 2 == 0:
        cluster, _, _, _, _ = get_largest_cluster(pos, solid_drive)
        st.session_state.history_size.append(len(cluster))
        st.session_state.history_time.append(st.session_state.time_step)
        if len(st.session_state.history_size) > 220:
            st.session_state.history_size.pop(0)
            st.session_state.history_time.pop(0)

cluster, is_solid, adj_dense, coordination, local_order = get_largest_cluster(
    st.session_state.pos, solid_drive
)
score = len(cluster) / N * 100

st.markdown(
    "<h2 style='text-align:center;color:#e2e8f0'>Make a Crystal: Liquid-to-Solid Simulation</h2>",
    unsafe_allow_html=True,
)
col_anim, col_info = st.columns([2, 1])

with col_anim:
    st.subheader("Live 2D Particle Animation")
    fig, ax = plt.subplots(figsize=(6.4, 6.4), facecolor=theme["bg"])
    ax.set_facecolor(theme["plot_bg"])
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.add_patch(plt.Rectangle((0, 0), L, L, fill=False, color=theme["primary"], lw=2))

    pos = st.session_state.pos
    vel = st.session_state.vel
    liquid_idx = np.where(~is_solid)[0]
    solid_idx = np.where(is_solid)[0]

    if solid_drive > 0.25:
        guide_alpha = 0.08 + 0.18 * solid_drive
        ax.scatter(
            LATTICE_POINTS[:, 0],
            LATTICE_POINTS[:, 1],
            c=theme["guide"],
            s=38,
            alpha=guide_alpha,
            linewidths=0,
            zorder=0,
        )

    if len(liquid_idx):
        ax.quiver(
            pos[liquid_idx, 0],
            pos[liquid_idx, 1],
            vel[liquid_idx, 0],
            vel[liquid_idx, 1],
            angles="xy",
            scale_units="xy",
            scale=9.5,
            color=theme["liquid"],
            alpha=max(0.18, 0.42 * (1 - solid_drive)),
            width=0.004,
            zorder=1,
        )

    lines = []
    for i in solid_idx:
        for j in solid_idx:
            if j <= i or not adj_dense[i, j]:
                continue
            if abs(pos[i, 0] - pos[j, 0]) < L / 2 and abs(pos[i, 1] - pos[j, 1]) < L / 2:
                lines.append([(pos[i, 0], pos[i, 1]), (pos[j, 0], pos[j, 1])])
    if lines:
        ax.add_collection(
            LineCollection(lines, colors=theme["bond"], linewidths=2.4, alpha=0.9, zorder=2)
        )

    if len(liquid_idx):
        liquid_size = 68 + 34 * min(temperature, 2.0)
        ax.scatter(
            pos[liquid_idx, 0],
            pos[liquid_idx, 1],
            c=theme["liquid"],
            s=liquid_size,
            edgecolors="#0f172a",
            linewidths=0.9,
            alpha=0.72,
            zorder=3,
            label="Liquid",
        )

    if len(solid_idx):
        ax.scatter(
            pos[solid_idx, 0],
            pos[solid_idx, 1],
            c=theme["solid"],
            s=260,
            alpha=0.18,
            linewidths=0,
            zorder=3,
        )
        ax.scatter(
            pos[solid_idx, 0],
            pos[solid_idx, 1],
            c=theme["solid"],
            s=145,
            edgecolors="white",
            linewidths=1.1,
            alpha=0.96,
            zorder=4,
            label="Solid",
        )

    ax.text(
        0.04,
        0.96,
        f"{phase_name.upper()} CONDITIONS",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        fontweight="bold",
        color=phase_color,
    )
    ax.set_title(
        f"blue = moving liquid, amber bonds = ordered solid | step {st.session_state.time_step}",
        fontsize=9,
    )
    ax.legend(loc="lower right", fontsize=8, framealpha=0.9)
    st.pyplot(fig)
    plt.close(fig)

with col_info:
    st.subheader("Score & Status")
    if score > 50:
        smsg, scol = "Crystal formed", theme["success"]
    elif score > 18:
        smsg, scol = "Nucleating crystals", theme["warning"]
    else:
        smsg, scol = "Liquid and disordered", theme["liquid"]
    st.markdown(
        f"<div style='background:{scol};padding:10px;border-radius:8px;color:white;"
        f"text-align:center;font-weight:bold;font-size:1.1rem'>{smsg}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Crystal Score", f"{score:.1f}%")
    c2.metric("Solid Particles", f"{int(np.sum(is_solid))}/{N}")
    c3, c4 = st.columns(2)
    c3.metric("Temperature", f"{temperature_k} K")
    c4.metric("Phase Drive", f"{solid_drive * 100:.0f}%")

    if score > 50:
        st.success("A stable, bonded lattice is visible.")
    elif solid_drive > 0.32:
        st.warning("Crystals are starting to organize. Lower temperature or raise attraction to finish freezing.")
    else:
        st.info("The liquid stays disordered because motion beats attraction.")

    st.subheader("Live Plot: Crystal Size")
    fig2, ax2 = plt.subplots(figsize=(5, 2.3))
    if st.session_state.history_time:
        ax2.fill_between(
            st.session_state.history_time,
            st.session_state.history_size,
            alpha=0.22,
            color=theme["solid"],
        )
        ax2.plot(
            st.session_state.history_time,
            st.session_state.history_size,
            color=theme["solid"],
            lw=2,
        )
    ax2.axhline(N * 0.5, color=theme["success"], linestyle="--", lw=1.5, label="Goal (50%)")
    ax2.set_xlabel("Time (steps)", fontsize=8)
    ax2.set_ylabel("Crystal Particles", fontsize=8)
    ax2.set_xlim(left=max(0, st.session_state.time_step - 220), right=st.session_state.time_step + 10)
    ax2.set_ylim(0, N + 5)
    ax2.legend(fontsize=7)
    ax2.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig2)
    plt.close(fig2)

if st.session_state.running:
    time.sleep(0.04)
    st.rerun()

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>© Dasgupta Research Group @ K-State "
    "<a href='https://www.drgatksu.com' target='_blank' "
    "style='color: gray; text-decoration: underline;'>www.drgatksu.com</a></p>",
    unsafe_allow_html=True,
)
