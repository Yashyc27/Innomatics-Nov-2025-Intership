import os
import streamlit as st
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Simple KB Chat", page_icon="💬")
st.title("Simple Bedrock Knowledge Base Chat")

# Configuration from .env or defaults
region = os.getenv("AWS_REGION", "eu-north-1")
knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", "DDSGHZ5O1L")
model_arn = "eu.amazon.nova-2-lite-v1:0"

st.write("Ask a question to your Amazon Bedrock Knowledge Base.")

question = st.text_input("Enter your question")

if st.button("Ask"):
    if not knowledge_base_id:
        st.error("Please set KNOWLEDGE_BASE_ID in your .env file.")
    elif not question.strip():
        st.error("Please enter a question.")
    else:
        # Initialize the Bedrock Runtime client
        client = boto3.client("bedrock-agent-runtime", region_name=region)

        with st.spinner("Retrieving from Knowledge Base and generating answer..."):
            response = client.retrieve_and_generate(
                input={"text": question},
                retrieveAndGenerateConfiguration={
                    "type": "KNOWLEDGE_BASE",
                    "knowledgeBaseConfiguration": {
                        "knowledgeBaseId": knowledge_base_id,
                        "modelArn": model_arn,
                    },
                },
            )

        answer = response["output"]["text"]
        st.subheader("Answer")
        st.write(answer)