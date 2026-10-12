
from brand_profile import show_brand_profile
import streamlit as st

st.set_page_config(
    page_title="ThreatLens AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ ThreatLens AI")
st.subheader("Digital Risk Protection Platform")

st.write(
    "Monitor possible fake social media profiles "
    "and suspicious mobile apps."
)

st.info(
    "Prototype mode: This dashboard uses sample data "
    "until approved data sources are connected."
)

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a module",
    [
        "Dashboard",
        "Brand Profile",
        "Social Media Monitoring",
        "App Store Monitoring",
        "Risk Reports"
    ]
)

if page == "Dashboard":
    st.header("Security Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Brands Registered", 0)
    col2.metric("Profiles Reviewed", 0)
    col3.metric("Apps Reviewed", 0)

    st.write("### Welcome to ThreatLens AI")
    st.write(
        "Register a brand and review possible "
        "look-alike profiles and apps."
    )

elif page == "Brand Profile":
    show_brand_profile()

elif page == "Social Media Monitoring":
    st.header("Social Media Monitoring")
    st.write("Review possible impersonating profiles.")

elif page == "App Store Monitoring":
    st.header("App Store Monitoring")
    st.write("Review apps with similar names or branding.")

elif page == "Risk Reports":
    st.header("Risk Reports")
    st.write("Review risk scores and detection reasons.")
