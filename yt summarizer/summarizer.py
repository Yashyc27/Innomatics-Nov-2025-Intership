
import os
import time
import zipfile
from typing import List
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

load_dotenv()
os.environ['MISTRAL_API_KEY'] = os.getenv('MISTRAL_API_KEY')

mistral_model = ChatMistralAI(model="mistral-large-latest", temperature=0.2)

def fetch_transcript(youtube_url: str) -> str:
    loader = YoutubeLoader.from_youtube_url(youtube_url)
    docs = loader.load()
    if not docs:
        raise ValueError("No transcript available for this video")
    return docs[0].page_content

def segment_text(text: str, size: int = 4000) -> List[str]:
    divider = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    return divider.split_text(text)

blog_editor_role = "You are a Technical Content Editor for Medium and Hashnode."

article_structure = """
Write a professional technical article based on this transcript:
- Tone: Authoritative first-person.
- Formatting: Use bold headers and clean bullet points.
- Content: Focus on code and logic; exclude 'vlogger' talk.
- Conclusion: Summarize the key impact.

Transcript:
{transcript}
"""

article_gen_prompt = ChatPromptTemplate.from_messages([
    ("system", blog_editor_role),
    ("user", article_structure)
])

short_video_chain = (
    RunnablePassthrough()
    | RunnableLambda(fetch_transcript)
    | article_gen_prompt
    | mistral_model
    | StrOutputParser()
)

summary_agent = create_agent(
    model=mistral_model,
    tools=[],
    system_prompt=blog_editor_role,
    middleware=[
        SummarizationMiddleware(
            model=mistral_model,
            trigger=("tokens", 800),
            keep=("tokens", 200)
        )
    ]
)

def process_long_video(raw_text: str):
    parts = segment_text(raw_text)
    final_draft = ""

    for part in parts:
        time.sleep(1.1)
        input_data = f"Current Draft: {final_draft}\n\nUpdate with: {part}"
        output = summary_agent.invoke({"messages": [{"role": "user", "content": input_data}]})
        final_draft = output["messages"][-1].content

    return final_draft

def route_input(url: str):
    content = fetch_transcript(url)
    if len(content) > 4000:
        return process_long_video(content)
    return content

frontend_role = "You are a Senior Web Architect. Output code inside --html--, --css--, and --js-- tags."

frontend_task = "Build a high-performance Medium-style page for: {article_content}"

web_dev_prompt = ChatPromptTemplate.from_messages([
    ("system", frontend_role),
    ("user", frontend_task)
])

full_service_pipeline = (
    RunnableLambda(route_input)
    | RunnableLambda(lambda x: (time.sleep(1.2), x)[1])
    | article_gen_prompt
    | mistral_model
    | StrOutputParser()
    | web_dev_prompt
    | mistral_model
    | StrOutputParser()
)

if __name__ == "__main__":
    vid_url = "https://youtu.be/nBpPe9UweWs?si=eKlekQisNxJeytdh"
    print("Generating article and webpage with Mistral AI...")

    web_code = full_service_pipeline.invoke(vid_url)

    tags = {'index.html': '--html--', 'style.css': '--css--', 'script.js': '--js--'}

    for filename, delimiter in tags.items():
        try:
            content = web_code.split(delimiter)[1].strip()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except:
            print(f"Error extracting {filename}")

    with zipfile.ZipFile('mistral_project.zip', 'w') as zh:
        for f in tags.keys():
            if os.path.exists(f):
                zh.write(f)

    print("Done! Files saved to mistral_project.zip")

