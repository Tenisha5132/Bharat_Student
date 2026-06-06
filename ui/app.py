import streamlit as st
import requests
import os
import sys

# Add path for config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

API_HOST = os.getenv("API_HOST", "localhost")
if API_HOST == "0.0.0.0":
    API_HOST = "localhost"
API_BASE_URL = f"http://{API_HOST}:{settings.API_PORT}"

st.set_page_config(page_title="BharatStudent", layout="wide", page_icon="🎓")

# PREMIUM CSS INJECTION
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* Main background gradient */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    color: #e2e8f0;
}

/* Glassmorphism sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Beautiful gradient buttons with hover animations */
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 20px rgba(168, 85, 247, 0.4) !important;
}

/* Styled text inputs */
.stTextInput>div>div>input {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 8px !important;
}

/* Markdown and headings */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# BANNER IMAGE
try:
    st.image("ui/assets/banner.png", use_column_width=True)
except Exception:
    pass

st.sidebar.title("BharatStudent Modes")
try:
    st.sidebar.image("ui/assets/logo.png", width=150)
except Exception:
    pass
mode = st.sidebar.radio("Select Application Mode:", ("Rights Assistant", "College Research"))

if mode == "Rights Assistant":
    st.title("⚖️ Student Rights Assistant")
    st.markdown("Ask questions about educational rights, UGC regulations, and legal protections.")
    
    with st.sidebar:
        st.subheader("📚 Knowledge Base")
        uploaded_file = st.file_uploader("Upload Legal PDF (UGC/AICTE)", type=["pdf"])
        if uploaded_file is not None:
            if st.button("Ingest Document"):
                with st.spinner("Processing PDF..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    try:
                        res = requests.post(f"{API_BASE_URL}/api/upload", files=files)
                        res.raise_for_status()
                        st.success(f"Ingested {uploaded_file.name} successfully!")
                    except Exception as e:
                        st.error(f"Upload failed: {e}")
                        
        st.subheader("Filter Context")
        state_filter = st.selectbox("State Regulations:", ["All India", "Telangana", "Maharashtra", "Tamil Nadu", "Delhi"])

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Quick Questions
    st.markdown("### Quick Questions")
    col1, col2, col3, col4 = st.columns(4)
    quick_q = None
    if col1.button("Certificate Withholding?"): quick_q = "Can college withhold my original certificate?"
    if col2.button("Max Fee Hike?"): quick_q = "What is the max fee hike allowed?"
    if col3.button("Anti-Ragging Rules?"): quick_q = "What are anti-ragging rules?"
    if col4.button("File a Grievance?"): quick_q = "How to file a grievance?"
        
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("View Sources"):
                    for s in message["sources"]:
                        st.caption(f"- **{s.get('source', 'Unknown')}** (Page {s.get('page', '?')}, Section: {s.get('legal_section', 'N/A')})")

    prompt = quick_q or st.chat_input("E.g., What are the anti-ragging regulations?")
    
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Consulting legal documents..."):
            try:
                response = requests.post(f"{API_BASE_URL}/api/chat", json={"query": prompt})
                response.raise_for_status()
                data = response.json()
                answer = data.get("answer", "No answer provided.")
                sources = data.get("sources", [])
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    if sources:
                        with st.expander("View Sources"):
                            for s in sources:
                                st.caption(f"- **{s.get('source', 'Unknown')}** (Page {s.get('page', '?')}, Section: {s.get('legal_section', 'N/A')})")
                
                st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {e}")

elif mode == "College Research":
    st.title("🏢 College Intelligence Research")
    st.markdown("Verify authenticity, accreditations, and trust score.")
    
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_query = st.text_input("Enter College Name:", placeholder="e.g., IIT Bombay")
    with col_s2:
        state_query = st.selectbox("State Filter:", ["All", "Telangana", "Maharashtra", "Tamil Nadu", "Delhi"])
    with col_s3:
        type_query = st.selectbox("Type Filter:", ["All", "Public", "Private"])
        
    if st.button("Search Colleges"):
        payload = {"query": search_query}
        if state_query != "All": payload["state"] = state_query
        if type_query != "All": payload["type"] = type_query
        
        try:
            res = requests.post(f"{API_BASE_URL}/api/college/search", json=payload)
            res.raise_for_status()
            results = res.json().get("results", [])
            if not results:
                st.warning("No colleges found matching criteria.")
            else:
                st.success(f"Found {len(results)} colleges. Click one to generate report:")
                for r in results:
                    name = r['basic']['name']
                    if st.button(f"Generate Report for {name}", key=r['id']):
                        st.session_state["selected_college"] = name
        except Exception as e:
            st.error(f"Search failed: {e}")
            
    college_name = st.session_state.get("selected_college", search_query)
    
    if st.button("Generate Intelligence Report (Directly)") or st.session_state.get("selected_college"):
        if college_name.strip():
            with st.spinner("Analyzing data from MongoDB..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/api/college/{college_name.strip()}")
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Report generated successfully for {data['college_name']}!")
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.subheader("Trust Score Metrics")
                            score = data["trust_metrics"]["score"]
                            color = "green" if score >= 7.5 else "orange" if score >= 5.0 else "red"
                            st.markdown(f"<h1 style='color: {color}; font-size: 60px;'>{score}/10</h1>", unsafe_allow_html=True)
                            
                            st.write("**Positive Signals:**")
                            for pos in data["trust_metrics"]["positives"]:
                                st.markdown(f"✅ {pos}")
                                
                            if data["trust_metrics"].get("risk_factors"):
                                st.write("**Risk Factors:**")
                                for risk in data["trust_metrics"]["risk_factors"]:
                                    st.markdown(f"⚠️ {risk}")
                                    
                        with col2:
                            st.subheader("Analyst Report")
                            st.markdown(data["report_markdown"])
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to connect to the backend API: {e}.")
            
            # Reset state so it doesn't auto-run next time unless clicked
            if "selected_college" in st.session_state:
                del st.session_state["selected_college"]
