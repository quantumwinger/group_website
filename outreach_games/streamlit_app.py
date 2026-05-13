import streamlit as st

def home():
    st.title("Computers in Chemistry")
    st.subheader("Interactive computational chemistry outreach games")
    st.write("Explore how computers help chemists study reactions, energy landscapes, molecular motion, nucleation, and reaction pathways.")
    
    st.markdown("### Available games")
    st.page_link("nucleation.py", label="Make a Droplet", icon="💧")
    st.page_link("break_ion_pair.py", label="Break the Ion Pair", icon="⚡")
    st.page_link("nanopore_filter.py", label="Design a Water Filter", icon="🚰")
    st.page_link("catalyst_game.py", label="Lower the Hill", icon="📉")
    st.page_link("reaction_detective.py", label="Reaction Quest", icon="🔍")

home_page = st.Page(home, title="Home", icon="🏠")
p1 = st.Page("nucleation.py", title="Make a Droplet", icon="💧")
p2 = st.Page("break_ion_pair.py", title="Break the Ion Pair", icon="⚡")
p3 = st.Page("nanopore_filter.py", title="Design a Water Filter", icon="🚰")
p4 = st.Page("catalyst_game.py", title="Lower the Hill", icon="📉")
p5 = st.Page("reaction_detective.py", title="Reaction Quest", icon="🔍")

pg = st.navigation([home_page, p1, p2, p3, p4, p5])
st.set_page_config(page_title="Computers in Chemistry", page_icon="🧪", layout="wide")
pg.run()
