import streamlit as st
from sequencial import app

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Content Pipeline",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(99,102,241,0.12), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(168,85,247,0.10), transparent 30%),
        #080b12;
    color: #f5f7ff;
}

/* Remove default top padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Header */

.hero {
    text-align: center;
    padding: 30px 20px 25px 20px;
}

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(129,140,248,0.25);
    color: #a5b4fc;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 15px;
}

.hero h1 {
    font-size: 48px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -2px;
    background: linear-gradient(90deg, #ffffff, #a5b4fc, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #9ca3af;
    font-size: 17px;
    margin-top: 12px;
}

/* Pipeline */

.pipeline {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 25px 0 35px 0;
}

.stage {
    padding: 12px 18px;
    border-radius: 12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: #d1d5db;
    font-size: 14px;
    font-weight: 600;
}

.arrow {
    color: #6366f1;
    font-size: 20px;
}

/* Cards */

.card {
    background: rgba(17,24,39,0.72);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.18);
}

.card-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 5px;
}

.card-subtitle {
    color: #8b93a7;
    font-size: 13px;
    margin-bottom: 15px;
}

/* Output */

.output-card {
    background: linear-gradient(
        145deg,
        rgba(99,102,241,0.08),
        rgba(168,85,247,0.05)
    );
    border: 1px solid rgba(129,140,248,0.18);
    border-radius: 18px;
    padding: 25px;
    margin-top: 25px;
}

.output-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 15px;
}

/* Button */

.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 48px;
    border: none;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    font-weight: 700;
    font-size: 15px;
    transition: 0.2s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(99,102,241,0.35);
}

/* Text area */

textarea {
    border-radius: 12px !important;
}

/* Footer */

.footer {
    text-align: center;
    color: #626b7f;
    font-size: 12px;
    margin-top: 40px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">

<div class="hero-badge">
⚡ LANGGRAPH • MULTI-STAGE AI PIPELINE
</div>

<h1>AI Content Pipeline</h1>

<p>
Transform raw ideas into polished, engaging Hinglish content.
</p>

</div>
""", unsafe_allow_html=True)


# ---------------- PIPELINE VISUAL ----------------

st.markdown("""
<div class="pipeline">

<div class="stage">✍️ Editor</div>

<div class="arrow">→</div>

<div class="stage">🎬 Scriptwriter</div>

<div class="arrow">→</div>

<div class="stage">🇮🇳 Hinglish</div>

<div class="arrow">→</div>

<div class="stage">✨ Final Output</div>

</div>
""", unsafe_allow_html=True)


# ---------------- MAIN COLUMNS ----------------

left, right = st.columns([1, 1], gap="large")


# ---------------- INPUT ----------------

with left:

    st.markdown("""
    <div class="card">

    <div class="card-title">📝 Raw Content</div>

    <div class="card-subtitle">
    Enter your idea, article, notes, or rough content.
    </div>

    </div>
    """, unsafe_allow_html=True)

    raw_input = st.text_area(
        "Input",
        height=350,
        placeholder="""Example:

The quick brown fox jumps over the lazy dog.

This sentence is a pangram, meaning it contains every
letter of the English alphabet at least once.""",
        label_visibility="collapsed"
    )

    generate = st.button(
        "⚡ Generate Content",
        use_container_width=True
    )


# ---------------- PROCESSING ----------------

with right:

    st.markdown("""
    <div class="card">

    <div class="card-title">🤖 AI Pipeline</div>

    <div class="card-subtitle">
    Three specialized stages transform your content.
    </div>

    </div>
    """, unsafe_allow_html=True)

    stage1 = st.empty()
    stage2 = st.empty()
    stage3 = st.empty()


# ---------------- RUN PIPELINE ----------------

if generate:

    if not raw_input.strip():

        st.warning("Please enter some content first.")

    else:

        # Stage 1
        stage1.info("✍️ **Editor** — Cleaning grammar and improving clarity...")

        try:

            results = app.invoke({
                "raw_input": raw_input
            })

            stage1.success("✅ **Editor** — Content cleaned and refined.")

            stage2.success("✅ **Scriptwriter** — Script generated.")

            stage3.success("✅ **Translator** — Hinglish conversion completed.")

            # ---------------- OUTPUT ----------------

            st.markdown("""
            <div class="output-card">

            <div class="output-title">
            ✨ Final Hinglish Output
            </div>

            </div>
            """, unsafe_allow_html=True)

            st.text_area(
                "Final Output",
                value=results["final_output"],
                height=350,
                label_visibility="collapsed"
            )

            # ---------------- STATS ----------------

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Pipeline Stages",
                    "3"
                )

            with col2:
                st.metric(
                    "Input Characters",
                    len(raw_input)
                )

            with col3:
                st.metric(
                    "Output Characters",
                    len(results["final_output"])
                )

        except Exception as e:

            st.error(f"Pipeline Error: {e}")


# ---------------- FOOTER ----------------

st.markdown("""
<div class="footer">
Built with LangGraph + LangChain + Groq
</div>
""", unsafe_allow_html=True)