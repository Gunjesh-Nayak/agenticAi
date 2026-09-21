import streamlit as st
from conditional_RAG import app


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="College AI",
    page_icon="🎓",
    layout="wide"
)


# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0b0f19;
    color: white;
}

/* Main container */

.block-container {
    max-width: 1000px;
    padding-top: 40px;
}


/* Header */

.title {
    text-align: center;
    font-size: 45px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #8b93a7;
    margin-bottom: 40px;
}


/* Cards */

.card {
    padding: 22px;
    border-radius: 16px;
    background-color: #111827;
    border: 1px solid #1f2937;
    margin-bottom: 15px;
}


/* Sidebar */

section[data-testid="stSidebar"] {
    background-color: #0f1420;
}


/* Buttons */

.stButton button {
    border-radius: 10px;
}


/* Chat */

[data-testid="stChatMessage"] {
    border-radius: 15px;
    border: 1px solid #1f2937;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# SESSION STATE
# =====================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "programme" not in st.session_state:
    st.session_state.programme = None


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("## 🎓 College AI")

    st.caption("AI-powered college assistant")

    st.markdown("---")

    st.markdown("### Select Programme")

    programme = st.selectbox(
        "Programme",
        ["BBA", "BCA", "BCOM(H)"],
        index=None,
        placeholder="Choose your programme",
        label_visibility="collapsed"
    )

    if programme:
        st.session_state.programme = programme

    st.markdown("---")

    st.markdown("### You can ask")

    st.markdown("""
    📚 **Academic**
    
    • Attendance  
    • Exams  
    • Credits  
    • Courses  

    💰 **Fees**
    
    • Tuition fees  
    • Scholarships  
    • Refunds  
    • Payment  

    💬 **General**
    
    • College information  
    • Greetings
    """)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.chat_history = []

        st.rerun()


# =====================================================
# HEADER
# =====================================================

st.markdown(
    '<div class="title">🎓 College Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about academics, fees and college information'
    '</div>',
    unsafe_allow_html=True
)


# =====================================================
# PROGRAMME CARD
# =====================================================

if st.session_state.programme:

    st.markdown(
        f"""
        <div class="card">
            <b>🎓 Programme</b><br>
            <span style="color:#9ca3af">
            {st.session_state.programme}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# CHAT HISTORY
# =====================================================

for message in st.session_state.chat_history:

    with st.chat_message(
        message["role"],
        avatar="🧑‍🎓" if message["role"] == "user" else "🤖"
    ):

        st.markdown(message["content"])


# =====================================================
# CHAT INPUT
# =====================================================

user_query = st.chat_input(
    "Ask something about your college..."
)


if user_query:

    # -----------------------------------------------
    # Programme check
    # -----------------------------------------------

    if not st.session_state.programme:

        st.warning(
            "⚠️ Please select your programme from the sidebar."
        )

        st.stop()


    # -----------------------------------------------
    # Display user message
    # -----------------------------------------------

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message(
        "user",
        avatar="🧑‍🎓"
    ):

        st.markdown(user_query)


    # -----------------------------------------------
    # AI RESPONSE
    # -----------------------------------------------

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner("Thinking..."):

            try:

                result = app.invoke({
                    "programe": st.session_state.programme,
                    "messages": [
                        ("human", user_query)
                    ]
                })

                answer = result["messages"][-1].content

            except Exception as e:

                st.error(
                    f"Something went wrong:\n\n{e}"
                )

                answer = "I couldn't process your question."


        st.markdown(answer)


    # -----------------------------------------------
    # Save response
    # -----------------------------------------------

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })