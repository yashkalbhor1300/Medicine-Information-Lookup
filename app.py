
import html
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Medicine Information Lookup",
    page_icon="💊",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.header-box {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(135deg, #e8f5e9, #e3f2fd);
    margin-bottom: 25px;
}

.header-title {
    font-size: 36px;
    font-weight: 700;
    color: #173b35;
}

.header-subtitle {
    font-size: 16px;
    color: #555;
}

.medicine-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #ddd;
    background-color: #f8fafc;
    margin-bottom: 20px;
}

.info-card {
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e5e5;
    background-color: white;
    min-height: 115px;
    margin-bottom: 12px;
}

.info-title {
    font-size: 14px;
    color: #777;
    margin-bottom: 8px;
}

.info-value {
    font-size: 17px;
    font-weight: 600;
    color: #222;
    overflow-wrap: anywhere;
}

.disclaimer {
    padding: 18px;
    border-radius: 10px;
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
    color: #664d03;
    margin-top: 25px;
}

div[data-testid="stMetric"] {
    background: #f8fafc;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e5e5e5;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def safe_text(value):
    """Convert dataset values into safe display text."""
    if pd.isna(value):
        return "Not available"

    value = str(value).strip()

    return html.escape(value) if value else "Not available"


def display_info_card(title, value):
    """Display medicine information in a card."""
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">{html.escape(title)}</div>
            <div class="info-value">{safe_text(value)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_section(title, column, medicine, expanded=False):
    """Display medicine information inside an expander."""
    with st.expander(title, expanded=expanded):
        value = medicine.get(column, "")
        st.write(value if str(value).strip() else "Information not available.")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="header-title">💊 Medicine Information Lookup</div>
    <div class="header-subtitle">
        Search and explore basic information about medicines
        from the available medicine dataset.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("medicine_dataset.csv")

    df.columns = df.columns.str.strip().str.upper()

    df = df.fillna("")

    return df


try:
    df = load_data()

    if df.empty:
        st.error("The medicine dataset is empty.")
        st.stop()

    st.success(
        f"✅ Dataset loaded successfully — {len(df):,} medicines available"
    )

except FileNotFoundError:
    st.error(
        "❌ medicine_dataset.csv was not found. "
        "Place it in the same folder as app.py."
    )
    st.stop()

except Exception as e:
    st.error(f"❌ Error loading dataset: {e}")
    st.stop()


# ---------------------------------------------------------
# VALIDATE REQUIRED COLUMN
# ---------------------------------------------------------
if "NAME" not in df.columns:
    st.error("The dataset does not contain the required NAME column.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()


# ---------------------------------------------------------
# SEARCH SECTION
# ---------------------------------------------------------
st.markdown("## 🔎 Search Medicine")

search = st.text_input(
    "Enter medicine name",
    placeholder="Example: Avastin, Paracetamol, Azithromycin...",
    key="medicine_search"
)

# ---------------------------------------------------------
# SEARCH LOGIC
# ---------------------------------------------------------
if search.strip():

    search_text = search.strip().lower()

    name_series = df["NAME"].astype(str).str.strip()

    name_lower = name_series.str.lower()

    # Exact and partial search
    matches = df[
        name_lower.str.contains(
            search_text,
            case=False,
            regex=False,
            na=False
        )
    ].copy()

    # Word-based search
    if matches.empty:

        search_words = search_text.split()

        word_mask = pd.Series(False, index=df.index)

        for word in search_words:
            word_mask |= name_lower.str.contains(
                word,
                case=False,
                regex=False,
                na=False
            )

        matches = df[word_mask].copy()

    # -----------------------------------------------------
    # NO RESULTS
    # -----------------------------------------------------
    if matches.empty:

        st.warning("❌ No medicine found.")

        st.info(
            f'No medicine matching "{search}" was found. '
            "Try another spelling or a shorter medicine name."
        )

    else:

        st.success(
            f"✅ Found {len(matches)} matching medicine(s)."
        )

        # -------------------------------------------------
        # MEDICINE SELECTION
        # -------------------------------------------------
        # Include row position so duplicate names remain selectable.
        options = [
            f"{row['NAME']} (Record {position + 1})"
            for position, (_, row) in enumerate(matches.iterrows())
        ]

        selected_index = st.selectbox(
            "Select a medicine",
            range(len(options)),
            format_func=lambda i: options[i]
        )

        medicine = matches.iloc[selected_index]

        # -------------------------------------------------
        # MEDICINE HEADER
        # -------------------------------------------------
        st.markdown("---")

        st.markdown(
            f"""
            <div class="medicine-card">
                <h1>💊 {safe_text(medicine["NAME"])}</h1>
                <p>Medicine information from the available dataset.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # BASIC INFORMATION
        # -------------------------------------------------
        st.markdown("## 📋 Basic Information")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            display_info_card(
                "🧪 Composition",
                medicine.get("CONTAINS", "")
            )

        with col2:
            display_info_card(
                "🏷️ Therapeutic Class",
                medicine.get("THERAPEUTIC_CLASS", "")
            )

        with col3:
            display_info_card(
                "⚗️ Chemical Class",
                medicine.get("CHEMICAL_CLASS", "")
            )

        with col4:
            display_info_card(
                "🚫 Habit Forming",
                medicine.get("HABIT_FORMING", "")
            )

        # -------------------------------------------------
        # ACTION CLASS
        # -------------------------------------------------
        st.markdown("### 🔬 Action Class")

        action_class = medicine.get("ACTION_CLASS", "")

        st.info(
            action_class
            if str(action_class).strip()
            else "Information not available."
        )

        # -------------------------------------------------
        # MEDICINE INFORMATION
        # -------------------------------------------------
        st.markdown("## 📖 Medicine Information")

        display_section(
            "📖 Introduction",
            "INTRODUCTION",
            medicine,
            expanded=True
        )

        display_section(
            "🩺 Uses",
            "USES",
            medicine
        )

        display_section(
            "✅ Benefits",
            "BENEFITS",
            medicine
        )

        display_section(
            "⚠️ Side Effects",
            "SIDE_EFFECT",
            medicine
        )

        display_section(
            "💡 How to Use",
            "HOW_TO_USE",
            medicine
        )

        display_section(
            "⚙️ How It Works",
            "HOW_WORKS",
            medicine
        )

        display_section(
            "📌 Quick Tips",
            "QUICK_TIPS",
            medicine
        )

        # -------------------------------------------------
        # SAFETY INFORMATION
        # -------------------------------------------------
        st.markdown("## 🛡️ Safety Information")

        safety_data = {
            "🍷 Alcohol": medicine.get(
                "SAFETY_ADVICE_TO_ALCOHOL", ""
            ),
            "🤰 Pregnancy": medicine.get(
                "SAFETY_ADVICE_TO_PREGNANCY", ""
            ),
            "👶 Breastfeeding": medicine.get(
                "SAFETY_ADVICE_TO_BREAST_FEEDING", ""
            ),
            "🚗 Driving": medicine.get(
                "SAFETY_ADVICE_TO_DRIVING", ""
            ),
            "🫘 Kidney": medicine.get(
                "SAFETY_ADVICE_TO_KIDNEY", ""
            ),
            "🫀 Liver": medicine.get(
                "SAFETY_ADVICE_TO_LIVER", ""
            )
        }

        safety_df = pd.DataFrame(
            [
                {
                    "Category": category,
                    "Safety Information": (
                        value if str(value).strip()
                        else "Information not available."
                    )
                }
                for category, value in safety_data.items()
            ]
        )

        st.table(safety_df)

        # -------------------------------------------------
        # SOURCE
        # -------------------------------------------------
        link = str(medicine.get("LINK", "")).strip()

        if link.startswith(("https://", "http://")):
            st.markdown("## 🔗 Source")

            st.link_button(
                "View Original Medicine Information",
                link
            )

        elif link:
            st.caption("Source link is unavailable or invalid.")

# ---------------------------------------------------------
# INITIAL STATE
# ---------------------------------------------------------
else:

    st.info(
        "👆 Enter a medicine name above to view its information."
    )

    st.markdown("### 💡 Example Searches")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("💊 **Avastin**")

    with col2:
        st.write("💊 **Paracetamol**")

    with col3:
        st.write("💊 **Azithromycin**")


# ---------------------------------------------------------
# MEDICAL DISCLAIMER
# ---------------------------------------------------------
st.markdown("""
<div class="disclaimer">
    <b>⚠️ Medical Disclaimer</b>
    <br><br>
    This application provides general medicine information from
    the available dataset for educational and informational purposes only.
    It is not medical advice and should not be used for diagnosis,
    treatment, or self-medication.
    Always consult a qualified doctor or pharmacist before using
    or changing any medicine.
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")

st.caption(
    "Medicine Information Lookup | Educational Project"
)
