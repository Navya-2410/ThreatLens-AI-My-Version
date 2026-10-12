
import json
import streamlit as st

from report import generate_report
from app_monitor import monitor_apps
from brand_profile import show_brand_profile, load_brands
from social_monitor import monitor_social_profiles

st.set_page_config(
    page_title="ThreatLens AI",
    page_icon="🛡️",
    layout="wide"
)

if "profiles_reviewed" not in st.session_state:
    st.session_state.profiles_reviewed = 0

if "apps_reviewed" not in st.session_state:
    st.session_state.apps_reviewed = 0

if "scan_results" not in st.session_state:
    st.session_state.scan_results = []

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
    brands = load_brands()

    col1, col2, col3 = st.columns(3)
    col1.metric("Brands Registered", len(brands))
    col2.metric("Profiles Reviewed", st.session_state.profiles_reviewed)
    col3.metric("Apps Reviewed", st.session_state.apps_reviewed)

    st.write("### Welcome to ThreatLens AI")
    st.write(
        "Register a brand and review possible look-alike profiles and apps."
    )
    st.info(
        "Monitoring results appear here after you scan sample profiles and apps."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Social Media Monitoring")
        st.write("Detect potential fake or look-alike accounts.")
    with col2:
        st.subheader("App Store Monitoring")
        st.write("Identify apps with similar names or publishers.")

elif page == "Brand Profile":
    show_brand_profile()

elif page == "Social Media Monitoring":
    st.header("Social Media Monitoring")
    st.caption("Demo data only. No live accounts are being scanned.")

    brands = load_brands()

    if not brands:
        st.info("Please register a brand in Brand Profile first.")
    else:
        brand = st.selectbox(
            "Choose a registered brand",
            brands,
            format_func=lambda item: item["brand_name"]
        )

        sample_profiles = [
            {
                "name": brand["brand_name"],
                "username": "@novakart_fake",
                "platform": "Instagram",
                "url": "https://example.com/fake"
            },
            {
                "name": "Random Store",
                "username": "@randomstore",
                "platform": "Instagram",
                "url": "https://example.com/random"
            }
        ]

        if st.button("Scan Sample Profiles"):
            findings = monitor_social_profiles(brand, sample_profiles)
            st.session_state.profiles_reviewed += len(sample_profiles)

            for item in findings:
                result = dict(item)
                result["source"] = "Social Media"
                st.session_state.scan_results.append(result)

            st.subheader("Monitoring Results")
            st.write("Sample profiles reviewed:", len(sample_profiles))

            if findings:
                for item in findings:
                    st.write("---")
                    st.write("**Name:**", item.get("name", "Unknown"))
                    st.write("**Username:**", item.get("username", ""))
                    st.write("**Platform:**", item.get("platform", ""))
                    st.write(
                        "**Risk score:**",
                        f'{item.get("risk_score", 0)}/100'
                    )
                    st.write("**Risk level:**", item.get("risk_level", "Unknown"))
                    st.write("**Reasons:**", ", ".join(item.get("reasons", [])))
            else:
                st.info("No findings returned.")

elif page == "App Store Monitoring":
    st.header("App Store Monitoring")
    st.caption("Demo data only. No live app stores are being scanned.")

    brands = load_brands()

    if not brands:
        st.info("Register a brand profile first.")
    else:
        brand = st.selectbox(
            "Choose a registered brand",
            brands,
            format_func=lambda item: item["brand_name"]
        )
        official_app = brand.get("official_app", {})

        app_listings = [
            {
                "name": official_app.get("name") or brand["brand_name"],
                "developer": official_app.get("developer", ""),
                "description": official_app.get("description", ""),
                "store": "Sample data",
                "url": ""
            },
            {
                "name": brand["brand_name"] + " Customer Support",
                "developer": "Unknown Developer",
                "description": "Get help with your account and shopping orders.",
                "store": "Sample data",
                "url": ""
            }
        ]

        if st.button("Scan Sample Apps"):
            findings = monitor_apps(brand, app_listings)
            st.session_state.apps_reviewed += len(app_listings)

            for item in findings:
                result = dict(item)
                result["source"] = "App Store"
                st.session_state.scan_results.append(result)

            if findings:
                st.write("### Potentially suspicious apps")
                for item in findings:
                    st.warning(
                        f'**{item.get("name", "Unknown app")}** — '
                        f'Risk score: {item.get("risk_score", 0)}/100'
                    )
                    st.write("Risk level:", item.get("risk_level", "Unknown"))
                    st.write("Reasons:", ", ".join(item.get("reasons", [])))
            else:
                st.success("No suspicious apps found in these sample listings.")

elif page == "Risk Reports":
    st.header("Risk Reports")
    st.caption("Reports include findings from scans run during this app session.")

    results = st.session_state.scan_results

    if not results:
        st.info(
            "No scan findings have been saved yet. Run a sample scan "
            "in Social Media Monitoring or App Store Monitoring first."
        )
    else:
        st.write("### Saved scan findings")
        st.write("Findings saved:", len(results))

        for item in results:
            st.write("---")
            st.write("**Source:**", item.get("source", "Unknown"))
            st.write("**Name:**", item.get("name", "Unknown"))
            st.write("**Risk score:**", f'{item.get("risk_score", 0)}/100')
            st.write("**Risk level:**", item.get("risk_level", "Unknown"))
            st.write("**Reasons:**", ", ".join(item.get("reasons", [])))

        if st.button("Generate Scan Report"):
            report_data = generate_report(results)

            st.success("Report generated from saved scan findings.")
            col1, col2 = st.columns(2)
            col1.metric(
                "Items in Report",
                report_data["total_items_scanned"]
            )
            col2.metric(
                "Items Flagged",
                report_data["flagged_items"]
            )
            st.json(report_data)

            report_json = json.dumps(
                report_data,
                indent=4,
                ensure_ascii=False
            )

            st.download_button(
                label="Download JSON Report",
                data=report_json,
                file_name="threat_report.json",
                mime="application/json"
            )

        if st.button("Clear Saved Scan Findings"):
            st.session_state.scan_results = []
            st.success(
                "Saved scan findings cleared. Open Risk Reports again to refresh."
            )