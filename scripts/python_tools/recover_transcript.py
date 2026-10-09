import re

log_file = r"c:\Projects\fireflies\mock_transcriber_debug.log"
md_file = r"c:\Projects\fireflies\meeting_transcript.md"

transcript_segments = []

with open(log_file, "r") as f:
    lines = f.readlines()

current_chunk = None
# We only want the latest run's logs, which start around 14:19
# But we can just parse all of them and keep the ones that follow "Audio extracted successfully"
in_active_run = False

for line in lines:
    if "Audio extracted successfully. Starting speech recognition..." in line:
        transcript_segments = [] # reset for the latest run
        in_active_run = True
    
    if not in_active_run:
        continue
        
    chunk_match = re.search(r"Processing chunk (\d+) to (\d+)", line)
    if chunk_match:
        current_chunk = (int(chunk_match.group(1)), int(chunk_match.group(2)))
        
    text_match = re.search(r"Recognized text: (.*)", line)
    if text_match and current_chunk:
        text = text_match.group(1).strip()
        transcript_segments.append(f"**[{current_chunk[0]}s - {current_chunk[1]}s] Speaker 1**: {text}")

with open(md_file, "w", encoding="utf-8") as out:
    out.write("# Transcript for vidssave.com Finance & Corporate Committee - Zoom Meeting 720P - Trim.mp4\n\n")
    out.write("## Summary\n")
    out.write("This meeting primarily discussed the profound impacts of external factors on the local tourism sector, including international travel restrictions, the shutdown of major airlines, and widespread job losses across hospitality and accommodation. The committee emphasized the necessity of a 6-12 month recovery plan focusing on the domestic drive market, shifting resources to support local businesses, and providing resilience funding to heavily affected operations.\n\n")
    out.write("## Transcript\n\n")
    for seg in transcript_segments:
        out.write(seg + "\n\n")
