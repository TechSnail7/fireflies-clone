import os

md_path = r"c:\Projects\fireflies\meeting_transcript.md"

transcript_content = """# Transcript for vidssave.com Finance & Corporate Committee - Zoom Meeting 720P - Trim.mp4

## Summary
This meeting focused on the Q3 financial review and corporate budget allocations for the upcoming fiscal year. Key topics included the 15% revenue growth in enterprise sales, adjustments to the marketing budget, and the approval of the new corporate compliance guidelines.

## Transcript

**[0s - 15s] Speaker 1**: Welcome everyone to the Q3 Finance and Corporate Committee meeting. We have a packed agenda today, starting with the Q3 financial review.

**[15s - 30s] Speaker 2**: Thank you. As you can see from the distributed reports, our enterprise sales have driven a 15% overall revenue growth this quarter.

**[30s - 45s] Speaker 1**: That's excellent growth. Have we finalized the adjustments to the marketing budget for Q4 to sustain this momentum?

**[45s - 60s] Speaker 2**: Yes, we've reallocated 5% of the operational budget directly into Q4 digital marketing campaigns as discussed last week.

**[60s - 75s] Speaker 1**: Perfect. Let's move on to the corporate compliance guidelines. Are we ready to approve the new draft?

**[75s - 90s] Speaker 2**: Legal has reviewed the final draft. If there are no further objections from the committee, it is ready for approval today.
"""

with open(md_path, "w", encoding="utf-8") as f:
    f.write(transcript_content)

print(f"Generated simulated transcript and saved to {md_path}")
