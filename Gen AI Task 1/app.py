import streamlit as st
import time
from chatbot_engine import FinanceBotEngine

st.set_page_config(page_title="Penny Wise AI", layout="wide")


st.markdown("""
<style>
    .stApp { 
        background-color: #121212; 
        color: #E0E0E0; 
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #D4AF37;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }
    section[data-testid="stSidebar"] {
        background-color: #1E1E1E !important;
        border-right: 2px solid #D4AF37;
    }
    h1, h2, h3 { 
        color: #D4AF37 !important; 
    }
    .stChatInputContainer {
        border: 1px solid #D4AF37 !important;
        background: #1E1E1E !important;
    }
</style>
""", unsafe_allow_html=True)


if "bot" not in st.session_state:
    st.session_state.bot = FinanceBotEngine()

if "chat_session" not in st.session_state:
    st.session_state.chat_session = st.session_state.bot.start_new_session()
    st.session_state.messages = []

with st.sidebar:
    st.title(" Penny Wise")
    st.metric(label="Status", value="Online", delta="Gold Mode")
    if st.button(" Reset Audit", use_container_width=True):
        st.session_state.chat_session = st.session_state.bot.start_new_session()
        st.session_state.messages = []
        st.rerun()


st.title("Penny Wise: Witty Wealth AI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Deposit your financial query here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = st.session_state.chat_session.send_message(prompt)
            full_response = response.text
            

            displayed_text = ""
            for char in full_response:
                displayed_text += char
                message_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.005)
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f" Error: {e}")