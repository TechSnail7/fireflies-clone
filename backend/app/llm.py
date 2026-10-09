"""
Groq LLM Service for Meeting Summarization & Ask Fred Chatbot
Uses Groq's ultra-fast API with qwen/qwen3.8-27b.
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

_client = None

def get_groq_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def clean_json_string(raw: str) -> str:
    """Clean markdown backticks or extra formatting from LLM response."""
    clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE)
    return clean.strip()


def generate_meeting_summary(transcript_text: str, meeting_title: str = "Meeting", duration_seconds: int = 0) -> Dict[str, Any]:
    """
    Generate an executive summary, key topics, outline, and action items using Groq LLM.
    """
    if not transcript_text or len(transcript_text.strip()) < 10:
        return {
            "overview": "No speech detected in this meeting recording.",
            "key_topics": [],
            "chapters": [],
            "outline": [],
            "action_items": []
        }

    client = get_groq_client()

    prompt = f"""You are Fireflies AI, an elite executive meeting intelligence analyst.
Analyze the meeting titled '{meeting_title}' from the transcript below.

Generate a comprehensive, highly insightful breakdown in strictly VALID JSON format matching this schema:
{{
  "overview": "A detailed 2-3 paragraph executive summary of the meeting, background context, key discussion points, and outcomes.",
  "key_topics": [
    {{"title": "Topic Title", "description": "Concise summary of what was discussed and agreed upon for this topic."}}
  ],
  "chapters": [
    {{"title": "Chapter title", "start_time": 0, "end_time": {duration_seconds}, "summary": "Chapter summary"}}
  ],
  "outline": [
    {{"heading": "Section heading", "points": ["Key takeaway point 1", "Key takeaway point 2"]}}
  ],
  "action_items": [
    {{"text": "Specific task to complete", "assignee": "Person responsible or Team name"}}
  ]
}}

Transcript:
\"\"\"
{transcript_text[:12000]}
\"\"\"

Respond with ONLY the raw JSON object. Do not wrap in markdown or include conversational text.
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional meeting analysis engine. Output ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.2,
            max_tokens=2048
        )

        raw_content = response.choices[0].message.content or "{}"
        cleaned = clean_json_string(raw_content)
        data = json.loads(cleaned)

        return {
            "overview": data.get("overview", "Meeting summary generated."),
            "key_topics": data.get("key_topics", []),
            "chapters": data.get("chapters", []),
            "outline": data.get("outline", []),
            "action_items": data.get("action_items", [])
        }
    except Exception as e:
        print(f"[LLM Error] generate_meeting_summary failed: {e}")
        # Safe fallback
        return {
            "overview": f"Discussion regarding {meeting_title}.",
            "key_topics": [{"title": "Discussion", "description": transcript_text[:200] + "..."}],
            "chapters": [{"title": "Full Meeting", "start_time": 0, "end_time": duration_seconds, "summary": "Full session"}],
            "outline": [{"heading": "Summary", "points": [transcript_text[:150]]}],
            "action_items": [{"text": "Review meeting notes", "assignee": "You"}]
        }


def ask_fred_llm_chat(query: str, channel: str, context_docs: List[Dict[str, Any]]) -> str:
    """
    Power the Ask Fred chatbot using Groq LLM with live workspace meetings context.
    """
    client = get_groq_client()

    context_str = ""
    for idx, doc in enumerate(context_docs[:8]):
        context_str += f"\n--- Meeting {idx+1}: {doc.get('title')} (Date: {doc.get('date')}, Host: {doc.get('host')}) ---\n"
        if doc.get("overview"):
            context_str += f"Summary: {doc.get('overview')}\n"
        if doc.get("action_items"):
            context_str += f"Action Items: {', '.join([ai.get('text', '') for ai in doc.get('action_items', [])])}\n"
        if doc.get("transcript_excerpt"):
            context_str += f"Excerpts:\n{doc.get('transcript_excerpt')}\n"

    system_prompt = f"""You are Ask Fred, Fireflies' AI meeting assistant for workspace member ANKIT.
Current Channel: #{channel}

You have direct access to the user's meeting library, notes, summaries, and transcripts provided in the context below.

Your goal:
- Answer the user's question accurately, concisely, and insightfully based on their meetings.
- If they ask for action items, format them clearly with checkboxes (- [ ] task) and assignees.
- If they ask for key decisions, highlight them with 🎯.
- If they ask for key initiatives, highlight them with 📌.
- Reference the specific meeting name or speaker where the information originated.
- If the question cannot be answered from the provided meetings, politely state that and suggest what you can help with.
- Maintain a helpful, friendly, and executive tone.
"""

    user_prompt = f"""Context from meetings:
{context_str}

User Question: {query}"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=1024
        )
        return response.choices[0].message.content or "I couldn't process that query."
    except Exception as e:
        print(f"[LLM Error] ask_fred_llm_chat failed: {e}")
        return f"I encountered an issue querying the AI service: {e}. Please try again."
