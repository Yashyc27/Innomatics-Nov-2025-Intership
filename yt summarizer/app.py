import streamlit as st
import os
import zipfile
import io
from dotenv import load_dotenv

# Logic is now imported from summarizer.py
from summarizer import full_service_pipeline

load_dotenv()

st.set_page_config(page_title="Mistral Content Engine", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #000; color: white; height: 3em; }
    .stDownloadButton>button { width: 100%; border-radius: 8px; background-color: #2e7bcf; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 AI Video Repurposer")


with st.sidebar:
    st.header("Pipeline Info")
    st.write("This tool automatically routes videos based on length:")
    st.markdown("- **Short Videos:** Direct summarization.")
    st.markdown("- **Long Videos:** Chunked processing via Agents.")
    st.divider()

url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Generate Project"):
    if url:
        try:
            with st.status("Running Summarizer Pipeline...", expanded=True) as status:
                st.write("📥 Processing transcript and generating web code...")
                
                # Using the pipeline from summarizer.py
                web_code = full_service_pipeline.invoke(url)
                
                st.write("📦 Creating ZIP package...")
                
                tags = {'index.html': '--html--', 'style.css': '--css--', 'script.js': '--js--'}
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for filename, delimiter in tags.items():
                        if delimiter in web_code:
                            try:
                                content = web_code.split(delimiter)[1].strip()
                                zip_file.writestr(filename, content)
                            except:
                                pass
                
                status.update(label="✅ Success!", state="complete", expanded=False)

            st.success("Files generated successfully.")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Preview Output")
                st.code(web_code, language="markdown")
            
            with col2:
                st.subheader("Download")
                st.download_button(
                    label="📥 Download Project ZIP",
                    data=zip_buffer.getvalue(),
                    file_name="summarized_web_project.zip",
                    mime="application/zip"
                )
                
        except Exception as e:
            st.error(f"Pipeline Error: {e}")
    else:
        st.warning("Please enter a URL.")

st.divider()
st.markdown("<p style='text-align: center;'>Yash Ritesh Chaudhary</p>", unsafe_allow_html=True)