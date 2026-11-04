
import base64
from pathlib import Path
from datetime import datetime
from html import escape
from textwrap import dedent

import streamlit as st

from groq import (
    RateLimitError,
    AuthenticationError,
    APIConnectionError,
    APIStatusError,
)

from safety.guardrails import validate_scenario
from core.scenario_generator import generate_scenario


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="What If Scenario Generator",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "scenario_history": [],
    "generated_result": None,
    "current_scenario": "",
    "scenario_input": "",
    "current_perspectives": 2,
    "current_detail": "Short",
    "generation_error": None,
    "theme_choice": "Cosmic Night",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HTML HELPER
# =========================================================

def render_html(content):
    st.html(dedent(content).strip())


# =========================================================
# THEME AND CSS
# =========================================================

theme = st.session_state.theme_choice

BASE_DIR = Path(__file__).resolve().parent

css_path = BASE_DIR / "assets" / "style.css"
background_path = BASE_DIR / "assets" / "Background.jpg"

if not css_path.exists():
    st.error("Missing assets/style.css. Please check your project folder.")
    st.stop()

if not background_path.exists():
    st.error("Background.jpg not found inside the assets folder.")
    st.stop()

# Read existing CSS
css = css_path.read_text(encoding="utf-8")

# Convert background image into Base64
encoded_image = base64.b64encode(
    background_path.read_bytes()
).decode("utf-8")

background_url = (
    f"url('data:image/jpeg;base64,{encoded_image}')"
)

# Replace previous background image references
css = css.replace(
    'url("Background.jpg")',
    background_url
)

css = css.replace(
    'url("background.jpg")',
    background_url
)

css = css.replace(
    "url('Background.jpg')",
    background_url
)

css = css.replace(
    "url('background.jpg')",
    background_url
)


# =========================================================
# COSMIC LIGHT THEME
# =========================================================

if theme == "Cosmic Light":

    css += """
    :root {
        color-scheme: light;

        --page-1: #e9e7ff;
        --page-2: #dcecff;
        --page-3: #f6e5f7;

        --text: #242344;
        --muted: #4e5276;
        --subtle: #686b91;

        --panel: rgba(255, 255, 255, 0.62);
        --panel-strong: rgba(255, 255, 255, 0.82);
        --sidebar: rgba(239, 235, 255, 0.90);

        --input: rgba(255, 255, 255, 0.92);
        --input-text: #252443;
        --placeholder: #737797;

        --select: rgba(255, 255, 255, 0.94);
        --menu: #ffffff;
        --menu-hover: #e9e2ff;

        --border: rgba(113, 87, 190, 0.35);
        --border-soft: rgba(113, 87, 190, 0.18);

        --accent: #7545df;
        --accent-2: #5268e9;
        --accent-3: #18a9d5;
        --accent-glow: rgba(130, 91, 226, 0.22);

        --shadow: 0 18px 55px rgba(72, 70, 140, 0.13);
        --card-shadow: 0 14px 42px rgba(78, 75, 145, 0.13);

        --button-text: #ffffff;
    }
    """

    background_overlay = """
        linear-gradient(
            rgba(235, 240, 255, 0.62),
            rgba(235, 240, 255, 0.72)
        )
    """

else:

    background_overlay = """
        linear-gradient(
            rgba(8, 11, 29, 0.70),
            rgba(8, 11, 29, 0.80)
        )
    """


# =========================================================
# APPLY BACKGROUND IMAGE
# =========================================================

css += f"""
.stApp {{
    background:
        radial-gradient(
            ellipse at 12% 12%,
            rgba(112, 75, 220, 0.18),
            transparent 38%
        ),
        radial-gradient(
            ellipse at 88% 22%,
            rgba(42, 114, 205, 0.15),
            transparent 38%
        ),
        {background_overlay},
        {background_url}
        center center / cover fixed no-repeat !important;

    color: var(--text);
}}

[data-testid="stAppViewContainer"] {{
    background: transparent !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}
"""

# Inject CSS ONCE. Do not add nested style tags.
st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    render_html("""
    <div class="sidebar-brand">
        <div class="sidebar-eyebrow">APPEARANCE</div>
        <div class="sidebar-product">🌌 &nbsp; COSMIC INTERFACE</div>
    </div>
    """)

    if theme == "Cosmic Night":
        theme_button = "☀️  Switch to Cosmic Light"
    else:
        theme_button = "🌙  Switch to Cosmic Night"

    if st.button(
        theme_button,
        key="theme_toggle",
        use_container_width=True
    ):
        st.session_state.theme_choice = (
            "Cosmic Light"
            if theme == "Cosmic Night"
            else "Cosmic Night"
        )
        st.rerun()

    render_html(f"""
    <div class="theme-note">✦ {escape(theme)} experience</div>
    <div class="sidebar-separator"></div>
    """)

    st.markdown("### ◷  Scenario History")

    if st.session_state.scenario_history:

        history_items = list(
            range(len(st.session_state.scenario_history))
        )

        selected = st.selectbox(
            "Your generated scenarios",
            history_items,
            format_func=lambda i: (
                st.session_state.scenario_history[i]["scenario"][:34]
                + (
                    "…"
                    if len(
                        st.session_state.scenario_history[i]["scenario"]
                    ) > 34
                    else ""
                )
            ),
            label_visibility="collapsed",
            key="history_select"
        )

        if st.button(
            "↶  Load selected scenario",
            use_container_width=True
        ):
            item = st.session_state.scenario_history[selected]

            st.session_state.scenario_input = item["scenario"]
            st.session_state.generated_result = item["result"]
            st.session_state.current_scenario = item["scenario"]
            st.session_state.current_perspectives = item["perspectives"]
            st.session_state.current_detail = item["detail"]
            st.session_state.generation_error = None

            st.rerun()

        if st.button(
            "Clear history",
            use_container_width=True
        ):
            st.session_state.scenario_history = []
            st.rerun()

    else:
        render_html("""
        <p class="sidebar-muted">
            Your generated scenarios will appear here.
        </p>
        """)

    render_html('<div class="sidebar-separator"></div>')

    st.markdown("### ⓘ  About")

    render_html("""
    <p class="sidebar-muted">
        Explore alternative realities using artificial intelligence.
    </p>
    <div class="powered-pill">
        Powered by Groq <span>⚡</span>
    </div>
    """)


# =========================================================
# HERO SECTION
# =========================================================

render_html("""
<section class="hero-panel">

    <div class="hero-kicker">
        <span class="kicker-dot"></span>
        MULTIVERSE EXPLORATION ENGINE
    </div>

    <div class="hero-title-row">
        <span class="hero-globe">🌍</span>
        <h1>What If Scenario Generator</h1>
    </div>

    <h2>Explore alternative realities with AI.</h2>

    <p class="hero-description">
        Ever wondered what would happen if history took a different turn?
        Enter a hypothetical situation and explore its possible consequences.
    </p>

    <div class="cosmic-divider">
        <span>✧</span>
    </div>

</section>
""")


# =========================================================
# SCENARIO INPUT
# =========================================================

render_html("""
<div class="section-heading">
    <span>✦</span> Enter Your Scenario
</div>
<div class="section-description">
    Imagine a different possibility. Your next reality starts here.
</div>
<div class="suggestion-label">
    NEED A SPARK? TRY A POSSIBILITY
</div>
""")

suggestions = [
    "What if humans had never discovered electricity?",
    "What if dinosaurs had never gone extinct?",
    "What if artificial intelligence became conscious?",
    "What if the Roman Empire had never fallen?",
]

suggestion_labels = [
    "⚡ Electricity",
    "🦖 Dinosaurs",
    "🤖 Conscious AI",
    "🏛️ Roman Empire",
]

suggestion_cols = st.columns(4)

for idx, suggestion in enumerate(suggestions):

    with suggestion_cols[idx]:

        if st.button(
            suggestion_labels[idx],
            key=f"suggestion_{idx}",
            use_container_width=True,
            help=suggestion
        ):
            st.session_state.scenario_input = suggestion
            st.rerun()

scenario = st.text_area(
    "What if...",
    placeholder="Example: What if humans had never discovered electricity?",
    height=140,
    key="scenario_input"
)


# =========================================================
# GENERATION SETTINGS
# =========================================================

settings_left, settings_right = st.columns(2)

with settings_left:

    perspectives = st.selectbox(
        "◆  Number of possible outcomes",
        [2, 3, 4],
        index=[2, 3, 4].index(
            st.session_state.current_perspectives
        ),
        key="perspectives_select"
    )

with settings_right:

    detail_options = [
        "Short",
        "Detailed",
        "Comprehensive",
    ]

    detail = st.selectbox(
        "▥  Analysis depth",
        detail_options,
        index=detail_options.index(
            st.session_state.current_detail
        ),
        key="detail_select"
    )


# =========================================================
# GENERATE BUTTON
# =========================================================

render_html('<div class="button-spacer"></div>')

generate_clicked = st.button(
    "✦  Generate Alternative Reality  ›",
    type="primary",
    use_container_width=True
)

if generate_clicked:

    st.session_state.current_perspectives = perspectives
    st.session_state.current_detail = detail

    is_valid, message = validate_scenario(scenario)

    if not is_valid:

        st.session_state.generation_error = message

    else:

        st.session_state.generation_error = None

        try:

            with st.spinner(
                "✦  Opening pathways to alternative realities…"
            ):

                result = generate_scenario(
                    scenario,
                    perspectives,
                    detail
                )

            if not result:

                st.session_state.generation_error = (
                    "The AI returned an empty response. Please try again."
                )

            else:

                st.session_state.generated_result = result
                st.session_state.current_scenario = scenario

                st.session_state.scenario_history.append({
                    "scenario": scenario,
                    "perspectives": perspectives,
                    "detail": detail,
                    "result": result,
                    "timestamp": datetime.now().strftime(
                        "%d %b %Y, %I:%M %p"
                    ),
                })

        except AuthenticationError:

            st.session_state.generation_error = (
                "Groq authentication failed. Check your GROQ_API_KEY."
            )

        except RateLimitError:

            st.session_state.generation_error = (
                "Groq rate limit reached. Please wait and try again."
            )

        except APIConnectionError:

            st.session_state.generation_error = (
                "Unable to connect to Groq. Check your internet connection."
            )

        except APIStatusError as error:

            st.session_state.generation_error = (
                f"Groq API error: {error.status_code}"
            )

        except Exception as error:

            st.session_state.generation_error = (
                f"Something went wrong: {error}"
            )


# =========================================================
# ERROR DISPLAY
# =========================================================

if st.session_state.generation_error:

    st.error(
        st.session_state.generation_error,
        icon="⚠️"
    )


# =========================================================
# GENERATED RESULTS
# =========================================================

if st.session_state.generated_result:

    render_html("""
    <div class="results-divider"></div>
    <div class="section-heading">
        <span>✧</span> Your Alternative Reality
    </div>
    """)

    render_html(f"""
    <div class="result-scenario">
        <div class="result-label">EXPLORING THIS TIMELINE</div>
        <strong>{escape(st.session_state.current_scenario)}</strong>
    </div>
    """)

    with st.container(border=True):

        st.markdown(
            st.session_state.generated_result
        )

    download_col, regen_col = st.columns(2)

    with download_col:

        st.download_button(
            "↓  Download your results",
            data=st.session_state.generated_result,
            file_name="alternative_reality.md",
            mime="text/markdown",
            use_container_width=True
        )

    with regen_col:

        if st.button(
            "↻  Clear result and explore again",
            use_container_width=True
        ):
            st.session_state.generated_result = None
            st.session_state.current_scenario = ""
            st.rerun()

    with st.expander("Copy-friendly version"):

        st.code(
            st.session_state.generated_result,
            language=None,
            wrap_lines=True
        )


# =========================================================
# FOOTER
# =========================================================

render_html("""
<footer class="cosmic-footer">
    <span>✧</span>
    WHAT IF SCENARIO GENERATOR
    <span class="footer-separator">|</span>
    AI-POWERED ALTERNATIVE REALITY EXPLORATION
    <span>✧</span>
</footer>
""")
