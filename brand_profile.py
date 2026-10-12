
import streamlit as st


def show_brand_profile():
    st.header("Brand Profile")

    if "brand_profile" not in st.session_state:
        st.session_state["brand_profile"] = None

    saved = st.session_state["brand_profile"]

    if saved is not None:
        st.success("Brand profile registered successfully!")

        st.subheader("Registered Brand Details")
        st.json(saved)

        if st.button("Register Another Brand"):
            st.session_state["brand_profile"] = None
            st.rerun()

        return

    st.write("Register a brand and its official assets.")

    with st.form("brand_profile_form"):
        brand_name = st.text_input("Brand / Company Name")
        website = st.text_input("Official Website")
        logo_url = st.text_input("Logo URL (optional)")

        st.subheader("Official Social Media Accounts")
        instagram = st.text_input("Instagram Username or URL")
        facebook = st.text_input("Facebook Page URL")
        linkedin = st.text_input("LinkedIn Page URL")
        other_social = st.text_input("Other Official Account URLs")

        st.subheader("Official Mobile App")
        app_name = st.text_input("Official App Name")
        developer = st.text_input("Official App Developer / Publisher")

        submitted = st.form_submit_button("Register Brand")

        if submitted:
            if not brand_name.strip():
                st.error("Please enter a brand name.")
            else:
                st.session_state["brand_profile"] = {
                    "brand_name": brand_name.strip(),
                    "website": website.strip(),
                    "logo_url": logo_url.strip(),
                    "social_accounts": {
                        "instagram": instagram.strip(),
                        "facebook": facebook.strip(),
                        "linkedin": linkedin.strip(),
                        "other": other_social.strip()
                    },
                    "official_app": {
                        "name": app_name.strip(),
                        "developer": developer.strip()
                    }
                }

                st.success("Brand profile registered!")
                st.json(st.session_state["brand_profile"])
