
import streamlit as st
from src.embedding import load_embedding_model
from src.rag_pipeline import answer_question

st.set_page_config(
    page_title="Migration Intelligence | Oracle → Snowflake",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CSS ----------------
st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }

    .hero {
        padding: 1.5rem 1.8rem;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        background: linear-gradient(120deg, #f0f7ff, #ffffff);
        margin-bottom: 1.5rem;
    }

    .eyebrow {
        color: #2563eb;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #172554;
        font-size: 32px;
        margin: 8px 0;
        font-weight: 750;
    }

    .hero p {
        color: #475569;
        margin-bottom: 0;
        font-size: 15px;
    }

    .section-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 8px;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid #e8edf3;
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }

    [data-testid="stChatInput"] {
        border-radius: 16px;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }

    .source-note {
        color: #64748b;
        font-size: 12px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ---------------- MODEL ----------------
@st.cache_resource
def get_embedding_model():
    return load_embedding_model()

model = get_embedding_model()


# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🔷 Migration Intelligence")
    st.caption("Oracle → Snowflake")
    st.divider()

    st.markdown("**YOUR WORKSPACE**")
    st.caption("Knowledge assistant")
    st.caption("Semantic retrieval + RAG")

    st.divider()

    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.markdown("---")
    st.caption("PROJECT")
    st.markdown("**Migration Knowledge Assistant**")
    st.caption("Local application · Streamlit")
    st.caption("PostgreSQL + pgvector · Groq")


# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">DATA ENGINEERING · GENAI</div>
    <h1>Oracle → Snowflake</h1>
    <p>
        Migration Intelligence Assistant<br>
        Ask migration questions and explore the retrieved knowledge
        behind each answer.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Migration knowledge assistant")
st.caption(
    "Ask a question about migration rules, Snowflake features "
    "or Oracle-to-Snowflake conversions."
)


# ---------------- SUGGESTED QUESTIONS ----------------
if not st.session_state.messages:
    st.markdown("**Try asking**")

    suggestions = [
        "How do I migrate Oracle NVL to Snowflake?",
        "What are the benefits of Snowflake migration?",
        "How do I migrate Oracle sequences?",
    ]

    cols = st.columns(3)
    for i, question in enumerate(suggestions):
        with cols[i]:
            if st.button(
                question,
                key=f"suggestion_{i}",
                use_container_width=True,
            ):
                st.session_state.pending_question = question
                st.rerun()


# ---------------- SOURCE DISPLAY ----------------
def show_sources(sources):
    with st.expander(
        f"📚 Retrieved sources · {len(sources)} chunks",
        expanded=False,
    ):
        if not sources:
            st.info("No source chunks were retrieved.")
            return

        for index, source in enumerate(sources, start=1):
            st.markdown(f"**{index}. {source['chunk_id']}**")
            st.caption(
                f"{source.get('source', 'Unknown source')} · "
                f"{source.get('source_type', 'unknown type')}"
            )

            similarity = source.get("similarity")
            if similarity is not None:
                st.caption(
                    f"Retrieval similarity: {similarity:.3f}"
                )

            metadata = source.get("metadata", {})
            if metadata:
                title = metadata.get("title")
                if title:
                    st.caption(f"Topic: {title}")

            st.write(source["content"])
            if index < len(sources):
                st.divider()


# ---------------- CHAT HISTORY ----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            show_sources(message["sources"])


# ---------------- CHAT INPUT ----------------
question = st.chat_input(
    "Ask your migration question..."
)

if question:
    st.session_state.pending_question = question

question_to_process = st.session_state.pending_question

if question_to_process:
    st.session_state.pending_question = None

    st.session_state.messages.append({
        "role": "user",
        "content": question_to_process,
    })

    with st.chat_message("user"):
        st.markdown(question_to_process)

    with st.chat_message("assistant"):
        with st.spinner("Searching migration knowledge..."):
            try:
                answer, sources = answer_question(
                    model, question_to_process
                )

                st.markdown(answer)
                show_sources(sources)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except Exception:
                st.error(
                    "Unable to generate the answer. "
                    "Please check your database and LLM connection."
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        "I couldn't process this request. "
                        "Please check the application connection "
                        "and try again."
                    ),
                })
