import json
import os

import streamlit as st


DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "sample_data.json",
)


def load_brands():
    """Load registered brand profiles from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return []

        brands = data.get("brands", [])
        return brands if isinstance(brands, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_brands(brands):
    """Save brands while preserving other JSON data."""
    data = {}

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

        except (json.JSONDecodeError, OSError):
            st.error(
                "Could not read existing data. "
                "No changes were saved."
            )
            return False

    if not isinstance(data, dict):
        st.error(
            "The data file has an invalid structure. "
            "No changes were saved."
        )
        return False

    data["brands"] = brands

    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return True

    except OSError:
        st.error("Could not save the brand profiles.")
        return False


def show_brand_profile():
    """Display registered brands and the brand registration form."""
    st.header("Brand Profile")
    st.write(
        "Register and manage official brand assets used "
        "for social media and app monitoring."
    )

    brands = load_brands()

    # Display registered brands.
    st.subheader("Registered Brands")

    valid_brands = [
        brand for brand in brands
        if isinstance(brand, dict)
    ]

    if valid_brands:
        for brand in valid_brands:
            brand_name = (
                str(brand.get("brand_name", "")).strip()
                or "Unnamed Brand"
            )

            with st.expander(brand_name):
                # Official website.
                st.write("**Official Website**")
                website = brand.get("website", "")

                if website:
                    st.write(website)
                else:
                    st.caption("Not provided")

                # Official logo.
                st.write("**Official Logo**")
                logo_url = brand.get("logo_url", "")

                if logo_url:
                    st.write(logo_url)
                    if logo_url.startswith(("https://", "http://")):
                        st.image(logo_url, width=150)
                else:
                    st.caption("Not provided")

                # Social accounts.
                st.write("**Official Social Media Accounts**")
                social_accounts = brand.get("social_accounts", {})

                if isinstance(social_accounts, dict) and social_accounts:
                    for platform, account in social_accounts.items():
                        st.write(
                            f"**{platform.capitalize()}:** "
                            f"{account or 'Not provided'}"
                        )
                else:
                    st.caption("No social accounts registered")

                # Official app.
                st.write("**Official Mobile App**")
                official_app = brand.get("official_app", {})

                if not isinstance(official_app, dict):
                    official_app = {}

                st.write(
                    f"**App name:** "
                    f"{official_app.get('name') or 'Not provided'}"
                )
                st.write(
                    f"**Developer / Publisher:** "
                    f"{official_app.get('developer') or 'Not provided'}"
                )
                st.write(
                    f"**Description:** "
                    f"{official_app.get('description') or 'Not provided'}"
                )
    else:
        st.info("No brands registered yet. Add a brand below.")

    # Registration form.
    st.subheader("Register a New Brand")

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
        developer = st.text_input(
            "Official App Developer / Publisher"
        )
        app_description = st.text_area("Official App Description")

        submitted = st.form_submit_button("Register Brand")

        if submitted:
            clean_brand_name = brand_name.strip()

            if not clean_brand_name:
                st.error("Please enter a brand name.")

            elif any(
                str(brand.get("brand_name", "")).strip().casefold()
                == clean_brand_name.casefold()
                for brand in valid_brands
            ):
                st.warning(
                    "A brand with this name is already registered."
                )

            else:
                new_brand = {
                    "brand_name": clean_brand_name,
                    "website": website.strip(),
                    "logo_url": logo_url.strip(),
                    "social_accounts": {
                        "instagram": instagram.strip(),
                        "facebook": facebook.strip(),
                        "linkedin": linkedin.strip(),
                        "other": other_social.strip(),
                    },
                    "official_app": {
                        "name": app_name.strip(),
                        "developer": developer.strip(),
                        "description": app_description.strip(),
                    },
                }

                updated_brands = brands + [new_brand]

                if save_brands(updated_brands):
                    st.success("Brand profile saved successfully!")
                    st.json(new_brand)
                else:
                    st.error(
                        "Brand registration failed. "
                        "Please check the data file and try again."
                    )