import streamlit as st

def home():
    st.title("Chemistry with Computers")
    st.write("Explore how computers help chemists understand molecules, reactions, and materials.")
    st.write("These interactive games let users change molecular parameters and see how chemistry responds in real time.")
    
    st.markdown("### Available simulations")
    st.page_link("nucleation.py", label="Make a Crystal", icon="❄️")
    st.page_link("break_ion_pair.py", label="Break the Ion Pair", icon="⚡")
    st.page_link("nanopore_filter.py", label="Design a Water Filter", icon="🚰")
    st.page_link("reaction_detective.py", label="Reaction Quest", icon="🔍")
    st.page_link("catalyst_game.py", label="Lower the Hill", icon="📉")

home_page = st.Page(home, title="Home", icon="🏠")
p1 = st.Page("nucleation.py", title="Make a Crystal", icon="❄️")
p2 = st.Page("break_ion_pair.py", title="Break the Ion Pair", icon="⚡")
p3 = st.Page("nanopore_filter.py", title="Design a Water Filter", icon="🚰")
p4 = st.Page("reaction_detective.py", title="Reaction Quest", icon="🔍")
p5 = st.Page("catalyst_game.py", title="Lower the Hill", icon="📉")

pg = st.navigation([home_page, p1, p2, p3, p4, p5])
st.set_page_config(page_title="Chemistry with Computers", page_icon="🧪", layout="wide")
pg.run()
