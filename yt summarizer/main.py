import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "be/" in url:
        return url.split("be/")[1]
    return url

def fetch_transcript(video_url):
    try:
        video_id = get_video_id(video_url)
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript_data])
        return full_text
    except Exception as e:
        return f"Error: {e}"

def generate_content(transcript_text):
    prompt = f"""
    Convert the following YouTube transcript into a professional article.
    
    Structure:
    1. TL;DR Summary: A 3-bullet point summary.
    2. Title: An engaging H1 headline.
    3. Content: Use H2 and H3 headers.
    4. Style: Use bolding and bullet points.
    5. Conclusion: A final summary.

    Format: Markdown.

    Transcript:
    {transcript_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a content strategist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def save_output(content, filename="article.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def run_pipeline():
    if not os.getenv("OPENAI_API_KEY"):
        print("API Key missing")
        return

    url = input("Enter YouTube URL: ").strip()
    
    print("Processing...")
    transcript = fetch_transcript(url)
    
    if "Error" not in transcript:
        article = generate_content(transcript)
        save_output(article)
        print("Saved to article.md")
    else:
        print(transcript)

if __name__ == "__main__":
    run_pipeline()