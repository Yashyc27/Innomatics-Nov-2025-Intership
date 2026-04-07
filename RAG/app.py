import boto3
import streamlit as st
import time
from datetime import datetime
from botocore.exceptions import ClientError

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TechNova Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURATION (Updated for your us-east-1 Setup) ---
AWS_REGION = "us-east-1" 
KNOWLEDGE_BASE_ID = "AZR110GTJH"
# Using Titan Text Express for generation (Make sure this is enabled in Model Access)
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1:0"

# --- MODERN ENTERPRISE UI (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }

    /* Header */
    .header-container {
        background: white;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px;
    }
    .header-title { color: #1E293B; font-weight: 600; font-size: 1.5rem; margin:0; }
    .header-subtitle { color: #64748B; font-size: 0.85rem; }

    /* Chat Bubbles */
    .chat-bubble {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        max-width: 80%;
        line-height: 1.6;
        font-size: 0.95rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .user-bubble {
        background-color: #3B82F6;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 2px;
    }
    .assistant-bubble {
        background-color: white;
        color: #1E293B;
        margin-right: auto;
        border-bottom-left-radius: 2px;
        border: 1px solid #E2E8F0;
    }

    /* Citation/Source Cards */
    .source-card {
        background: #F1F5F9;
        border-radius: 8px;
        padding: 0.8rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        border-left: 4px solid #3B82F6;
        color: #334155;
    }

    /* Sidebar Metric Cards */
    .metric-box {
        background: #1E293B;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
    .metric-val { font-size: 1.4rem; font-weight: 600; color: #60A5FA; }
    
    /* Clean Divider */
    .divider { height: 1px; background: #334155; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

# --- BEDROCK CLIENT ---
@st.cache_resource
def get_bedrock_agent_client():
    return boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)

# --- CORE LOGIC: QUERY KNOWLEDGE BASE ---
def query_kb(user_query):
    client = get_bedrock_agent_client()
    try:
        response = client.retrieve_and_generate(
            input={'text': user_query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': MODEL_ARN,
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 5  # Top 5 chunks
                        }
                    }
                }
            }
        )
        return response
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ThrottlingException':
            return {"error": "System is busy (429). Please wait a moment and try again."}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("### ⚙️ Control Center")
    st.info(f"Connected: **{AWS_REGION}**")
    
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-val">{st.session_state.query_count}</div>
        <div style="font-size:0.7rem; color:#94A3B8; letter-spacing: 1px;">TOTAL SESSIONS</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

# --- MAIN HEADER ---
st.markdown(f"""
<div class="header-container">
    <div>
        <div class="header-title">TechNova Intelligence</div>
        <div class="header-subtitle">Proprietary Knowledge Access • Powered by Amazon Bedrock</div>
    </div>
    <div style="text-align:right">
        <span style="background:#E0F2FE; color:#0369A1; padding:5px 14px; border-radius:20px; font-size:0.75rem; font-weight:600;">ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- CHAT RENDERING ---
for msg in st.session_state.messages:
    role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Display citations if they exist
    if msg.get("citations"):
        with st.expander("🔍 Viewed Sources"):
            for cit in msg["citations"]:
                st.markdown(f"""
                <div class="source-card">
                    <small><b>Source:</b> {cit['source']}</small><br>
                    {cit['text']}
                </div>
                """, unsafe_allow_html=True)

# --- CHAT INPUT ---
prompt = st.chat_input("Ask a question about the uploaded documents...")

if prompt:
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.query_count += 1
    
    # Show loading state
    with st.spinner("Analyzing Document Chunks..."):
        response = query_kb(prompt)
        
        if "error" in response:
            st.error(response["error"])
        else:
            # Parse Answer
            answer_text = response["output"]["text"]
            
            # Parse Citations
            citations = []
            for citation in response.get("citations", []):
                for ref in citation.get("retrievedReferences", []):
                    s3_uri = ref["location"]["s3Location"]["uri"]
                    citations.append({
                        "source": s3_uri.split("/")[-1],
                        "text": ref["content"]["text"][:250] + "..."
                    })
            
            # Save assistant response
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer_text,
                "citations": citations
            })
            
    # Refresh app to show new messages
    st.rerun()