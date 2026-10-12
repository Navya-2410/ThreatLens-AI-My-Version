
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
    st.caption(
        "Demo data only. No live accounts are being scanned."
    )

    brands = load_brands()

    if not brands:
        st.info("Please register a brand in Brand Profile first.")
    else:
        brand_profile = st.selectbox(
            "Choose a registered brand",
            brands,
            format_func=lambda brand: brand["brand_name"]
        )

        sample_profiles = [
            {
                "name": brand_profile["brand_name"],
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
            findings = monitor_social_profiles(
                brand_profile, sample_profiles
            )

            st.subheader("Monitoring Results")
            st.write("Sample profiles reviewed:", len(sample_profiles))

            if findings:
                for profile in findings:
                    st.write("---")
                    st.write("**Name:**", profile["name"])
                    st.write("**Username:**", profile["username"])
                    st.write("**Platform:**", profile["platform"])
                    st.write(
                        "**Risk score:**",
                        str(profile["risk_score"]) + "/100"
                    )
                    st.write("**Risk level:**", profile["risk_level"])
                    st.write(
                        "**Reasons:**",
                        ", ".join(profile["reasons"])
                    )

                    if profile["risk_level"] == "High":
                        st.error("High-risk indicators detected. Review this profile.")
                    elif profile["risk_level"] == "Medium":
                        st.warning("Potential risk detected. Further review is recommended.")
                    else:
                        st.success("Low risk based on current rules.")
            else:
                st.info("No findings returned.")



elif page == "App Store Monitoring":
    st.header("App Store Monitoring")
    st.caption("Demonstration data only; no live app store is being scanned.")

    brands = load_brands()

    if not brands:
        st.info("Register a brand profile first.")
    else:
        brand_profile = brands[0]

        app_listings = [
            {
                "name": "ThreatLens Security",
                "developer": "Unknown Developer",
                "description": "Protect your account.",
                "store": "Sample data",
                "url": ""
            }
        ]

        findings = monitor_apps(brand_profile, app_listings)

        if findings:
            st.write("### Potentially suspicious apps")

            for app in findings:
                st.warning(
                    f"**{app.get('name', 'Unknown app')}** — "
                    f"risk score: {app.get('risk_score', 0)}/100"
                )

                st.write(
                    "Risk level: "
                    + app.get("risk_level", "Unknown")
                )

                st.write(
                    "Reasons: "
                    + ", ".join(app.get("reasons", []))
                )
        else:
            st.success(
                "No suspicious apps found in the current sample listings."
            )


elif page == "Risk Reports":
    st.header("Risk Reports")
    st.write("Generate and download a sample report.")

    sample_results = [
        {
            "name": "NovaKart Shopping",
            "risk_score": 85,
            "risk_level": "High",
            "reasons": ["High name similarity"]
        },
        {
            "name": "Safe Example App",
            "risk_score": 10,
            "risk_level": "Low",
            "reasons": ["No strong risk indicators found"]
        }
    ]

    if st.button("Generate Sample Report"):
        report_data = generate_report(sample_results)

        st.success("Sample report generated!")

        col1, col2 = st.columns(2)
        col1.metric(
            "Items Scanned",
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
