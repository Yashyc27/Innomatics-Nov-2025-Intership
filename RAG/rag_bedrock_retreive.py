import os
import boto3
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="KB + Gemini Chat", page_icon="💬")
st.title("Bedrock KB + Gemini 2.5 Flash")

aws_region = os.getenv("AWS_REGION", "eu-north-1")
knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", "DDSGHZ5O1L")
os.environ['GEMINI_API_KEY'] = os.getenv("gemini_key")

st.write("This app retrieves context from Bedrock and uses Gemini 2.5 Flash to answer.")

question = st.text_input("Enter your question")

if st.button("Ask"):
    if not knowledge_base_id:
        st.error("Please set KNOWLEDGE_BASE_ID in your .env file.")
    elif not question.strip():
        st.error("Please enter a question.")
    else:
        bedrock = boto3.client("bedrock-agent-runtime", region_name=aws_region)

        with st.spinner("Searching Knowledge Base..."):
            # Step 1: Retrieve only (no generation yet)
            kb_response = bedrock.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery={"text": question},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": 5
                    }
                },
            )

        # Step 2: Extract text chunks
        chunks = []
        for item in kb_response.get("retrievalResults", []):
            text = item.get("content", {}).get("text", "")
            if text:
                chunks.append(text)

        context = "\n\n".join(chunks)

        # Step 3: Create a grounded prompt for Gemini
        prompt = f"""
        Answer the user's question using ONLY the context provided below.
        If the answer is not in the context, say you don't know.

        Context:
        {context}

        Question:
        {question}
        """

        with st.spinner("Generating response with Gemini..."):
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

        st.subheader("Answer")
        st.write(response.text)

        with st.expander("View Retrieved Context"):
            st.write(context if context else "No relevant context found.")