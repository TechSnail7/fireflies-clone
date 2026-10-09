"""
Seed data for the Fireflies clone.
Creates realistic meetings with full transcripts, summaries, and action items.
"""
from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app.models import Base, Meeting, TranscriptSegment, Summary, ActionItem, Tag


def seed_database():
    """Populate the database with sample meetings."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded
    if db.query(Meeting).count() > 0:
        db.close()
        return

    print("Seeding database...")

    # ── Create Tags ──
    tags_data = [
        {"name": "Engineering", "color": "#818CF8"},
        {"name": "Product", "color": "#F59E0B"},
        {"name": "Design", "color": "#EC4899"},
        {"name": "Marketing", "color": "#10B981"},
        {"name": "Sprint Planning", "color": "#7C3AED"},
        {"name": "1:1", "color": "#06B6D4"},
        {"name": "All Hands", "color": "#F97316"},
        {"name": "Client", "color": "#EF4444"},
    ]
    tags = {}
    for td in tags_data:
        tag = Tag(**td)
        db.add(tag)
        db.flush()
        tags[td["name"]] = tag

    # ═══════════════════════════════════════════════════════════════
    # Meeting 1: Sprint Planning
    # ═══════════════════════════════════════════════════════════════
    m1 = Meeting(
        title="Q4 Sprint Planning — Platform Team",
        date=datetime.utcnow() - timedelta(days=1, hours=3),
        duration_seconds=2700,
        host="Sarah Chen",
        participants=["Sarah Chen", "Marcus Johnson", "Priya Patel", "David Kim"],
        status="completed",
        meeting_type="video",
    )
    db.add(m1)
    db.flush()
    m1.tags.append(tags["Engineering"])
    m1.tags.append(tags["Sprint Planning"])

    m1_segments = [
        {"speaker": "Sarah Chen", "text": "Alright everyone, let's kick off our Q4 sprint planning. We have a lot to cover today, so let's jump right in. I've pulled up the backlog and we have about 47 items to triage.", "start_time": 0, "end_time": 12},
        {"speaker": "Marcus Johnson", "text": "Before we start, I wanted to flag that the authentication service migration is more complex than we initially estimated. We might need to allocate extra points for that.", "start_time": 12, "end_time": 22},
        {"speaker": "Sarah Chen", "text": "Good call, Marcus. Let's discuss that when we get to the infrastructure items. Priya, can you walk us through the frontend priorities first?", "start_time": 22, "end_time": 30},
        {"speaker": "Priya Patel", "text": "Sure! So the biggest item is the new dashboard redesign. The design team finalized the mockups last week, and I've broken it down into about 6 sub-tasks. The main components are the metrics cards, the activity feed, and the new chart visualizations.", "start_time": 30, "end_time": 48},
        {"speaker": "David Kim", "text": "Are we using the existing charting library or switching to something new? I remember we discussed D3 versus Recharts last sprint.", "start_time": 48, "end_time": 56},
        {"speaker": "Priya Patel", "text": "We decided to go with Recharts. It integrates better with our React setup and has better TypeScript support. I've already created a proof of concept branch.", "start_time": 56, "end_time": 67},
        {"speaker": "Sarah Chen", "text": "Perfect. What's the estimated effort for the full dashboard redesign?", "start_time": 67, "end_time": 72},
        {"speaker": "Priya Patel", "text": "I'm estimating about 21 story points total. The metrics cards are about 5 points, the activity feed is 8 points because of the real-time updates, and the charts are another 8 points.", "start_time": 72, "end_time": 86},
        {"speaker": "Marcus Johnson", "text": "That sounds reasonable. For the backend, I need to build out the analytics API endpoints to support those new charts. That's probably another 5 points on our side.", "start_time": 86, "end_time": 97},
        {"speaker": "Sarah Chen", "text": "Okay, so we're looking at 26 points just for the dashboard. Our velocity last sprint was 34 points, so we need to be careful about what else we commit to.", "start_time": 97, "end_time": 109},
        {"speaker": "David Kim", "text": "I think we should also prioritize the search performance issues. Users have been complaining about slow search results, especially when filtering by date ranges.", "start_time": 109, "end_time": 120},
        {"speaker": "Marcus Johnson", "text": "Yeah, I've been looking into that. The main bottleneck is our database queries. We need to add proper indexing and maybe implement some query caching. I'd estimate about 8 points for the full optimization.", "start_time": 120, "end_time": 135},
        {"speaker": "Sarah Chen", "text": "Let's add that to the sprint. Search performance directly impacts user satisfaction. David, what about the mobile responsive issues?", "start_time": 135, "end_time": 145},
        {"speaker": "David Kim", "text": "There are about 12 tickets related to mobile layout issues. Most are quick fixes — maybe 3 points total. But there's one major issue with the navigation menu on tablets that might take 5 points.", "start_time": 145, "end_time": 160},
        {"speaker": "Priya Patel", "text": "I can help with the tablet navigation fix. I've been working on a new responsive nav component that should handle all breakpoints properly.", "start_time": 160, "end_time": 170},
        {"speaker": "Sarah Chen", "text": "Great, let's pair on that then. Marcus, let's circle back to the auth migration. What's the revised estimate?", "start_time": 170, "end_time": 180},
        {"speaker": "Marcus Johnson", "text": "So the original estimate was 13 points, but after digging into the codebase, I found that we have about 15 different services that depend on the current auth tokens. Each one needs to be updated and tested individually. I'm revising to 21 points.", "start_time": 180, "end_time": 200},
        {"speaker": "Sarah Chen", "text": "That's significant. Can we break it into phases? Maybe do the core services this sprint and the rest next sprint?", "start_time": 200, "end_time": 210},
        {"speaker": "Marcus Johnson", "text": "Absolutely. Phase one would cover the five critical services — user service, payment service, notification service, API gateway, and the admin panel. That's about 13 points.", "start_time": 210, "end_time": 225},
        {"speaker": "David Kim", "text": "Makes sense to me. We should also set up feature flags so we can gradually roll out the new auth system.", "start_time": 225, "end_time": 233},
        {"speaker": "Sarah Chen", "text": "Good thinking. Okay, let me tally this up. Dashboard redesign: 26 points. Search optimization: 8 points. Mobile fixes: 8 points. Auth migration phase one: 13 points. That's 55 points, which is over our velocity.", "start_time": 233, "end_time": 252},
        {"speaker": "Priya Patel", "text": "We could push the activity feed part of the dashboard to next sprint. That would save us 8 points and bring us down to 47, which is closer to our stretch goal.", "start_time": 252, "end_time": 264},
        {"speaker": "Sarah Chen", "text": "I like that compromise. Let's go with that plan. Marcus, can you write up the auth migration RFC by end of day tomorrow so the team can review it before we start?", "start_time": 264, "end_time": 278},
        {"speaker": "Marcus Johnson", "text": "Will do. I'll also set up the feature flag infrastructure as a prerequisite task.", "start_time": 278, "end_time": 285},
        {"speaker": "Sarah Chen", "text": "Perfect. Alright team, I think we have a solid sprint plan. Let me summarize: dashboard metrics and charts, search optimization, mobile fixes, and auth migration phase one. Any final questions?", "start_time": 285, "end_time": 300},
        {"speaker": "David Kim", "text": "Nope, looks good! Let's ship it.", "start_time": 300, "end_time": 304},
        {"speaker": "Sarah Chen", "text": "Great, meeting adjourned. I'll update the Jira board and send out the sprint plan to the wider team. Thanks everyone!", "start_time": 304, "end_time": 315},
    ]

    for i, seg in enumerate(m1_segments):
        db.add(TranscriptSegment(meeting_id=m1.id, order_index=i, **seg))

    db.add(Summary(
        meeting_id=m1.id,
        overview="The Platform Team conducted Q4 sprint planning, triaging backlog items and estimating effort for key initiatives. The team agreed on a 47-point sprint including dashboard redesign (metrics + charts), search performance optimization, mobile responsiveness fixes, and phase one of the authentication service migration. The activity feed component was deferred to the next sprint to stay within velocity limits.",
        key_topics=[
            {"title": "Dashboard Redesign", "description": "New dashboard with metrics cards and chart visualizations using Recharts. 18 points (activity feed deferred)."},
            {"title": "Search Performance", "description": "Database query optimization with proper indexing and caching to fix slow search results. 8 points."},
            {"title": "Auth Service Migration", "description": "Phase one covering 5 critical services (user, payment, notification, API gateway, admin). 13 points with feature flags."},
            {"title": "Mobile Responsiveness", "description": "12 mobile layout tickets plus tablet navigation fix. 8 points total."},
        ],
        chapters=[
            {"title": "Sprint Kickoff", "start_time": 0, "end_time": 30, "summary": "Sarah opened the meeting and set the agenda for triaging 47 backlog items."},
            {"title": "Frontend Priorities", "start_time": 30, "end_time": 109, "summary": "Priya presented the dashboard redesign plan with Recharts, estimating 21 story points."},
            {"title": "Search & Mobile Issues", "start_time": 109, "end_time": 180, "summary": "David and Marcus discussed search performance bottlenecks and mobile layout fixes."},
            {"title": "Auth Migration Planning", "start_time": 180, "end_time": 264, "summary": "Marcus revised the auth migration estimate and proposed a phased approach."},
            {"title": "Sprint Commitment", "start_time": 264, "end_time": 315, "summary": "Team finalized the 47-point sprint plan, deferring the activity feed to next sprint."},
        ],
        outline=[
            {"heading": "Sprint Velocity & Capacity", "points": ["Last sprint velocity: 34 points", "Stretch goal capacity considered", "Final commitment: 47 points"]},
            {"heading": "Technical Decisions", "points": ["Recharts chosen over D3 for charts", "Feature flags for auth migration rollout", "Phased auth migration approach"]},
        ],
    ))

    for ai in [
        {"text": "Write auth migration RFC document", "assignee": "Marcus Johnson", "is_completed": False},
        {"text": "Set up feature flag infrastructure", "assignee": "Marcus Johnson", "is_completed": False},
        {"text": "Create Recharts proof of concept for dashboard charts", "assignee": "Priya Patel", "is_completed": True},
        {"text": "Build analytics API endpoints for new dashboard", "assignee": "Marcus Johnson", "is_completed": False},
        {"text": "Fix tablet navigation responsive layout", "assignee": "Priya Patel", "is_completed": False},
        {"text": "Add database indexes for search optimization", "assignee": "Marcus Johnson", "is_completed": False},
        {"text": "Update Jira board with sprint plan", "assignee": "Sarah Chen", "is_completed": False},
    ]:
        db.add(ActionItem(meeting_id=m1.id, **ai))

    # ═══════════════════════════════════════════════════════════════
    # Meeting 2: Product Strategy Review
    # ═══════════════════════════════════════════════════════════════
    m2 = Meeting(
        title="Product Strategy Review — Q4 Roadmap",
        date=datetime.utcnow() - timedelta(days=3, hours=5),
        duration_seconds=3600,
        host="Emily Rodriguez",
        participants=["Emily Rodriguez", "James Wilson", "Aisha Okonkwo", "Tom Bradley"],
        status="completed",
        meeting_type="video",
    )
    db.add(m2)
    db.flush()
    m2.tags.append(tags["Product"])

    m2_segments = [
        {"speaker": "Emily Rodriguez", "text": "Welcome everyone to our Q4 product strategy review. We have some exciting updates to share and important decisions to make about our roadmap priorities.", "start_time": 0, "end_time": 10},
        {"speaker": "Emily Rodriguez", "text": "First, let me share some key metrics from Q3. Our monthly active users grew 23% to reach 1.2 million. Retention rate improved to 78%, up from 71% last quarter.", "start_time": 10, "end_time": 24},
        {"speaker": "James Wilson", "text": "That's fantastic growth. What's driving the retention improvement? Is it the onboarding flow changes we made?", "start_time": 24, "end_time": 31},
        {"speaker": "Emily Rodriguez", "text": "Partly, yes. The new onboarding reduced time-to-value by 40%. But the biggest driver was the collaborative features we launched — shared workspaces and real-time editing.", "start_time": 31, "end_time": 43},
        {"speaker": "Aisha Okonkwo", "text": "From a design perspective, we also saw a 35% reduction in support tickets related to navigation confusion after the sidebar redesign.", "start_time": 43, "end_time": 53},
        {"speaker": "Tom Bradley", "text": "Great numbers. Now, for Q4, I think we need to focus on enterprise features. We have three enterprise deals in the pipeline worth a combined $2.4 million ARR, but they all require SSO and advanced permissions.", "start_time": 53, "end_time": 70},
        {"speaker": "Emily Rodriguez", "text": "Absolutely. Enterprise is our top priority for Q4. I've outlined three main tracks: enterprise security features, API platform improvements, and the AI assistant launch.", "start_time": 70, "end_time": 83},
        {"speaker": "James Wilson", "text": "Can you tell us more about the AI assistant? What's the scope for the initial launch?", "start_time": 83, "end_time": 90},
        {"speaker": "Emily Rodriguez", "text": "The AI assistant will start with three core capabilities: smart summarization of documents, natural language search across workspaces, and automated task extraction from meeting notes.", "start_time": 90, "end_time": 105},
        {"speaker": "Aisha Okonkwo", "text": "I've been working on the AI assistant UX. The design concept is a conversational sidebar that users can invoke from anywhere in the app. Think of it like a copilot that understands context.", "start_time": 105, "end_time": 120},
        {"speaker": "Tom Bradley", "text": "That sounds compelling. What's the timeline for getting this to beta?", "start_time": 120, "end_time": 126},
        {"speaker": "Emily Rodriguez", "text": "We're targeting mid-November for a private beta with select customers, then a public launch in early December. The engineering team has already completed the initial LLM integration.", "start_time": 126, "end_time": 140},
        {"speaker": "James Wilson", "text": "What about pricing? Are we planning to include this in existing plans or create a new AI tier?", "start_time": 140, "end_time": 148},
        {"speaker": "Tom Bradley", "text": "My recommendation is a usage-based add-on. We charge per query after a free tier of 100 queries per month. This aligns with how other AI products are pricing and keeps the base product accessible.", "start_time": 148, "end_time": 165},
        {"speaker": "Emily Rodriguez", "text": "I agree with that approach. Let's also make sure we have proper cost monitoring in place — LLM API costs can scale quickly if we're not careful.", "start_time": 165, "end_time": 176},
        {"speaker": "Aisha Okonkwo", "text": "For the enterprise track, I've designed an admin dashboard concept that gives IT admins visibility into user activity, permissions, and compliance settings. Should I walk through it?", "start_time": 176, "end_time": 190},
        {"speaker": "Emily Rodriguez", "text": "Yes, please share your screen and walk us through the admin dashboard designs.", "start_time": 190, "end_time": 195},
        {"speaker": "Aisha Okonkwo", "text": "So here's the main admin view. On the left, you have a navigation panel for user management, security settings, audit logs, and billing. The central panel shows a usage overview with key metrics.", "start_time": 195, "end_time": 212},
        {"speaker": "James Wilson", "text": "This looks great. Can we also add a section for managing API keys and webhook configurations? Our enterprise customers have been asking for better API management tools.", "start_time": 212, "end_time": 224},
        {"speaker": "Aisha Okonkwo", "text": "Absolutely, I'll add an API management section. I'll have updated designs ready by Friday.", "start_time": 224, "end_time": 231},
        {"speaker": "Tom Bradley", "text": "One more thing — we should discuss the competitive landscape. Our main competitor just launched a similar AI feature set. We need to differentiate on the integration story.", "start_time": 231, "end_time": 245},
        {"speaker": "Emily Rodriguez", "text": "Good point, Tom. Our advantage is the depth of integrations — Slack, Jira, Google Workspace, Salesforce. Let's make sure the AI assistant can pull context from all these connected tools.", "start_time": 245, "end_time": 260},
        {"speaker": "Emily Rodriguez", "text": "Okay, let me summarize our Q4 priorities. Track one: enterprise security with SSO, SCIM, and advanced permissions by end of October. Track two: API platform v2 with better docs and webhook management by mid-November. Track three: AI assistant beta by mid-November, public launch in December.", "start_time": 260, "end_time": 285},
        {"speaker": "Tom Bradley", "text": "Sounds like a solid plan. Let's make Q4 count!", "start_time": 285, "end_time": 290},
        {"speaker": "Emily Rodriguez", "text": "Agreed. I'll send out the detailed roadmap document by end of day. Thanks everyone for a productive session!", "start_time": 290, "end_time": 300},
    ]

    for i, seg in enumerate(m2_segments):
        db.add(TranscriptSegment(meeting_id=m2.id, order_index=i, **seg))

    db.add(Summary(
        meeting_id=m2.id,
        overview="The product team reviewed Q3 performance metrics (23% MAU growth to 1.2M, 78% retention) and defined Q4 roadmap priorities across three tracks: enterprise security features (SSO, SCIM, permissions), API platform v2 improvements, and the AI assistant launch. The AI assistant will offer smart summarization, natural language search, and task extraction, with a private beta targeted for mid-November and public launch in December. Pricing will follow a usage-based add-on model.",
        key_topics=[
            {"title": "Q3 Performance Review", "description": "23% MAU growth, 78% retention, 40% reduction in time-to-value from new onboarding."},
            {"title": "Enterprise Features", "description": "SSO, SCIM, advanced permissions, admin dashboard for IT admins."},
            {"title": "AI Assistant Launch", "description": "Smart summarization, NL search, task extraction. Beta mid-November, launch December."},
            {"title": "Competitive Strategy", "description": "Differentiate through deep integrations (Slack, Jira, Google Workspace, Salesforce)."},
            {"title": "Pricing Strategy", "description": "Usage-based add-on for AI features with 100 free queries per month."},
        ],
        chapters=[
            {"title": "Q3 Metrics Review", "start_time": 0, "end_time": 53, "summary": "Team reviewed strong Q3 numbers including 23% MAU growth and improved retention."},
            {"title": "Q4 Enterprise Priority", "start_time": 53, "end_time": 83, "summary": "Enterprise features prioritized to close $2.4M pipeline deals."},
            {"title": "AI Assistant Scope", "start_time": 83, "end_time": 176, "summary": "Defined AI assistant capabilities, timeline, and pricing approach."},
            {"title": "Admin Dashboard Design", "start_time": 176, "end_time": 231, "summary": "Aisha walked through admin dashboard designs with API management additions."},
            {"title": "Competitive Positioning & Wrap-up", "start_time": 231, "end_time": 300, "summary": "Discussed differentiation through integrations and summarized Q4 tracks."},
        ],
        outline=[
            {"heading": "Key Decisions", "points": ["Enterprise features are top Q4 priority", "AI assistant using usage-based pricing", "Recharts selected for dashboard charts", "Phased rollout for AI assistant"]},
            {"heading": "Timeline Commitments", "points": ["Enterprise security: end of October", "API platform v2: mid-November", "AI assistant beta: mid-November", "AI assistant public launch: early December"]},
        ],
    ))

    for ai in [
        {"text": "Send detailed Q4 roadmap document", "assignee": "Emily Rodriguez", "is_completed": False},
        {"text": "Update admin dashboard designs with API management section", "assignee": "Aisha Okonkwo", "is_completed": False},
        {"text": "Set up LLM cost monitoring infrastructure", "assignee": "James Wilson", "is_completed": False},
        {"text": "Prepare enterprise SSO implementation plan", "assignee": "James Wilson", "is_completed": True},
        {"text": "Research competitor AI feature launches", "assignee": "Tom Bradley", "is_completed": False},
    ]:
        db.add(ActionItem(meeting_id=m2.id, **ai))

    # ═══════════════════════════════════════════════════════════════
    # Meeting 3: Design Review
    # ═══════════════════════════════════════════════════════════════
    m3 = Meeting(
        title="Design System Review — Component Library v2",
        date=datetime.utcnow() - timedelta(days=5, hours=2),
        duration_seconds=1980,
        host="Aisha Okonkwo",
        participants=["Aisha Okonkwo", "Priya Patel", "Lucas Martinez", "Sophie Wang"],
        status="completed",
        meeting_type="video",
    )
    db.add(m3)
    db.flush()
    m3.tags.append(tags["Design"])
    m3.tags.append(tags["Engineering"])

    m3_segments = [
        {"speaker": "Aisha Okonkwo", "text": "Hey team, thanks for joining. Today we're reviewing the component library v2 designs and the updated design tokens. I've shared the Figma link in the chat.", "start_time": 0, "end_time": 11},
        {"speaker": "Aisha Okonkwo", "text": "The main goals for v2 are: better accessibility across all components, consistent dark mode support, and improved animation patterns.", "start_time": 11, "end_time": 22},
        {"speaker": "Priya Patel", "text": "I love the new color tokens. The semantic naming convention — like surface-primary, surface-elevated, text-muted — makes so much more sense than the old numbered system.", "start_time": 22, "end_time": 35},
        {"speaker": "Lucas Martinez", "text": "Agreed. I've been implementing the new token system in our Storybook instance. One thing I noticed is that we have some inconsistencies between the border-radius tokens in Figma and what's currently in our CSS.", "start_time": 35, "end_time": 50},
        {"speaker": "Aisha Okonkwo", "text": "Good catch. Let me update the Figma file to match. We should use 4px for small, 8px for medium, 12px for large, and 16px for extra-large. Does that work for everyone?", "start_time": 50, "end_time": 63},
        {"speaker": "Sophie Wang", "text": "Can we also add a 'full' token for pill-shaped elements? We use full border-radius on tags and badges quite a bit.", "start_time": 63, "end_time": 72},
        {"speaker": "Aisha Okonkwo", "text": "Absolutely, I'll add a 'radius-full' token at 9999px. Now let's look at the button component updates.", "start_time": 72, "end_time": 80},
        {"speaker": "Aisha Okonkwo", "text": "I've redesigned the button system with five variants: primary, secondary, outline, ghost, and destructive. Each has three sizes — small, medium, and large — and proper focus and hover states.", "start_time": 80, "end_time": 96},
        {"speaker": "Priya Patel", "text": "The hover animations look really smooth. Are we using CSS transitions or Framer Motion for these?", "start_time": 96, "end_time": 103},
        {"speaker": "Lucas Martinez", "text": "I'd recommend CSS transitions for simple hover states and Framer Motion for more complex entrance and exit animations. It keeps the bundle size smaller for common interactions.", "start_time": 103, "end_time": 116},
        {"speaker": "Aisha Okonkwo", "text": "That's a good approach. Let's document that as a guideline in our contribution docs. Sophie, how are the accessibility audits going?", "start_time": 116, "end_time": 126},
        {"speaker": "Sophie Wang", "text": "I've completed the audit on 24 of our 38 components. We have 12 critical issues — mostly missing ARIA labels and keyboard navigation gaps. The biggest offenders are the dropdown menu, the modal dialog, and the date picker.", "start_time": 126, "end_time": 145},
        {"speaker": "Priya Patel", "text": "I can take the modal dialog fixes. I've been looking at the Radix UI primitives and they have excellent accessibility built in. We could adopt their dialog primitive as a base.", "start_time": 145, "end_time": 158},
        {"speaker": "Sophie Wang", "text": "That would be great. Radix also has a dropdown menu primitive that could solve our dropdown issues. Should we consider adopting Radix as our headless UI layer?", "start_time": 158, "end_time": 170},
        {"speaker": "Lucas Martinez", "text": "I'm all for it. Radix gives us unstyled, accessible primitives and we can apply our own design tokens on top. It would save us months of accessibility work.", "start_time": 170, "end_time": 182},
        {"speaker": "Aisha Okonkwo", "text": "Let's go with that approach. Lucas, can you create a migration plan for moving our existing components to Radix primitives? Prioritize the ones with accessibility issues.", "start_time": 182, "end_time": 195},
        {"speaker": "Lucas Martinez", "text": "Will do. I'll have a proposal ready by Monday. I'll also set up a comparison Storybook with the Radix-based versions so we can do a visual comparison.", "start_time": 195, "end_time": 207},
        {"speaker": "Aisha Okonkwo", "text": "Perfect. Last item — dark mode. I've created a complete dark mode palette that maintains WCAG AA contrast ratios across all surfaces. The key challenge was the elevation system — in dark mode, higher elevation means lighter, not darker.", "start_time": 207, "end_time": 228},
        {"speaker": "Sophie Wang", "text": "I tested the dark mode palette with our color blindness simulation tool and it passes all modes — deuteranopia, protanopia, and tritanopia.", "start_time": 228, "end_time": 240},
        {"speaker": "Aisha Okonkwo", "text": "Excellent work, Sophie. Okay team, great session. Let's sync again next Tuesday to review the Radix migration plan and the remaining accessibility fixes.", "start_time": 240, "end_time": 254},
    ]

    for i, seg in enumerate(m3_segments):
        db.add(TranscriptSegment(meeting_id=m3.id, order_index=i, **seg))

    db.add(Summary(
        meeting_id=m3.id,
        overview="The design and frontend teams reviewed the component library v2, covering updated design tokens with semantic naming, button system redesign with 5 variants, accessibility audit progress, and dark mode palette. Key decisions included adopting Radix UI primitives as the headless UI layer to resolve accessibility issues, and establishing CSS transitions vs Framer Motion guidelines for animations.",
        key_topics=[
            {"title": "Design Token System", "description": "Semantic naming convention (surface-primary, text-muted) with standardized border-radius tokens."},
            {"title": "Button Component Redesign", "description": "Five variants (primary, secondary, outline, ghost, destructive) with three sizes and proper states."},
            {"title": "Accessibility Audit", "description": "12 critical issues found across 24 audited components, mainly missing ARIA labels and keyboard nav."},
            {"title": "Radix UI Adoption", "description": "Team decided to adopt Radix primitives as headless UI layer for built-in accessibility."},
            {"title": "Dark Mode Design", "description": "Complete dark mode palette meeting WCAG AA contrast ratios, tested with color blindness simulations."},
        ],
        chapters=[
            {"title": "Design Token Updates", "start_time": 0, "end_time": 80, "summary": "Reviewed new semantic naming, border-radius tokens, and Figma-to-code consistency."},
            {"title": "Button System & Animations", "start_time": 80, "end_time": 126, "summary": "Presented 5-variant button system and established CSS vs Framer Motion animation guidelines."},
            {"title": "Accessibility Audit & Radix", "start_time": 126, "end_time": 207, "summary": "Sophie reported 12 critical accessibility issues; team decided to adopt Radix UI primitives."},
            {"title": "Dark Mode & Wrap-up", "start_time": 207, "end_time": 254, "summary": "Reviewed WCAG AA compliant dark mode palette and planned follow-up for next Tuesday."},
        ],
        outline=[
            {"heading": "Technical Decisions", "points": ["Adopt Radix UI primitives for accessibility", "CSS transitions for hover, Framer Motion for complex animations", "Semantic token naming convention"]},
        ],
    ))

    for ai in [
        {"text": "Update Figma border-radius tokens to match CSS", "assignee": "Aisha Okonkwo", "is_completed": False},
        {"text": "Create Radix UI migration plan", "assignee": "Lucas Martinez", "is_completed": False},
        {"text": "Fix modal dialog accessibility with Radix primitive", "assignee": "Priya Patel", "is_completed": False},
        {"text": "Complete accessibility audit on remaining 14 components", "assignee": "Sophie Wang", "is_completed": False},
        {"text": "Set up comparison Storybook with Radix components", "assignee": "Lucas Martinez", "is_completed": False},
        {"text": "Document animation guidelines in contribution docs", "assignee": "Aisha Okonkwo", "is_completed": False},
    ]:
        db.add(ActionItem(meeting_id=m3.id, **ai))

    # ═══════════════════════════════════════════════════════════════
    # Meeting 4: Client Onboarding Call
    # ═══════════════════════════════════════════════════════════════
    m4 = Meeting(
        title="Acme Corp — Enterprise Onboarding Kickoff",
        date=datetime.utcnow() - timedelta(days=7, hours=6),
        duration_seconds=2400,
        host="Tom Bradley",
        participants=["Tom Bradley", "Emily Rodriguez", "Rachel Green", "Michael Scott"],
        status="completed",
        meeting_type="video",
    )
    db.add(m4)
    db.flush()
    m4.tags.append(tags["Client"])

    m4_segments = [
        {"speaker": "Tom Bradley", "text": "Good morning Rachel and Michael! Welcome to the Fireflies platform. I'm Tom, your account manager, and Emily is our product lead. We're excited to help Acme Corp get set up.", "start_time": 0, "end_time": 14},
        {"speaker": "Rachel Green", "text": "Thanks Tom! We're really looking forward to this. We've been using manual meeting notes for years and it's been a huge pain point for our team of 150 people.", "start_time": 14, "end_time": 25},
        {"speaker": "Tom Bradley", "text": "I completely understand. Let me walk you through the onboarding process. We'll cover four main areas today: workspace setup, user provisioning, integration configuration, and training resources.", "start_time": 25, "end_time": 38},
        {"speaker": "Emily Rodriguez", "text": "Before we dive in, Rachel, can you tell us about your current workflow? What tools does your team use for meetings and collaboration?", "start_time": 38, "end_time": 48},
        {"speaker": "Rachel Green", "text": "We use Google Meet for most meetings, Slack for communication, and Jira for project management. We also have Salesforce for our sales team. Integration with these tools is really important for us.", "start_time": 48, "end_time": 62},
        {"speaker": "Emily Rodriguez", "text": "Perfect, we have native integrations with all of those. The Google Meet integration will automatically join your scheduled meetings and start transcribing.", "start_time": 62, "end_time": 73},
        {"speaker": "Michael Scott", "text": "That's exactly what we need. How does the Slack integration work? Can we get meeting summaries posted to specific channels?", "start_time": 73, "end_time": 82},
        {"speaker": "Emily Rodriguez", "text": "Yes! You can configure it per channel. After each meeting, a summary card is posted with key discussion points, action items, and a link to the full transcript. You can also set up keyword alerts.", "start_time": 82, "end_time": 97},
        {"speaker": "Tom Bradley", "text": "Now for user provisioning. Since you have 150 users, I'd recommend using our SCIM integration with your identity provider. Are you using Okta, Azure AD, or something else?", "start_time": 97, "end_time": 112},
        {"speaker": "Rachel Green", "text": "We use Okta for SSO. Having SCIM would be amazing — it would save our IT team hours of manual user management.", "start_time": 112, "end_time": 122},
        {"speaker": "Tom Bradley", "text": "Great, I'll share the SCIM setup guide after this call. The integration typically takes about 2-3 hours to configure. I can also hop on a call with your IT team if they need help.", "start_time": 122, "end_time": 136},
        {"speaker": "Michael Scott", "text": "What about data security? We're in a regulated industry, so we need to know about data retention policies and where our data is stored.", "start_time": 136, "end_time": 147},
        {"speaker": "Emily Rodriguez", "text": "All data is encrypted at rest and in transit. We're SOC 2 Type II certified and GDPR compliant. For enterprise plans, we offer custom data retention policies — you can set automatic deletion after 30, 60, 90 days, or keep data indefinitely.", "start_time": 147, "end_time": 167},
        {"speaker": "Rachel Green", "text": "That's reassuring. We'll need the 90-day retention policy for most meetings, but some compliance meetings need to be kept for 7 years.", "start_time": 167, "end_time": 178},
        {"speaker": "Tom Bradley", "text": "We can set up different retention policies per meeting type or tag. I'll work with you to configure that. Let's talk about the training plan next.", "start_time": 178, "end_time": 190},
        {"speaker": "Tom Bradley", "text": "We recommend a phased rollout. Week one: admin team setup and testing. Week two: pilot with 20-30 power users. Week three: company-wide rollout with training sessions.", "start_time": 190, "end_time": 205},
        {"speaker": "Rachel Green", "text": "That sounds like a solid plan. Can you provide training materials that we can share internally?", "start_time": 205, "end_time": 213},
        {"speaker": "Tom Bradley", "text": "Absolutely. We have video tutorials, quick-start guides, and we can do up to three live training sessions included in your enterprise plan. I'll also be available for ongoing support.", "start_time": 213, "end_time": 227},
        {"speaker": "Emily Rodriguez", "text": "One more thing — we're launching an AI assistant feature in December that I think will be a game-changer for your team. It can answer questions about past meetings and generate summaries across multiple meetings.", "start_time": 227, "end_time": 243},
        {"speaker": "Michael Scott", "text": "That sounds incredible! Will that be included in our enterprise plan?", "start_time": 243, "end_time": 249},
        {"speaker": "Emily Rodriguez", "text": "Enterprise plans will get 500 free AI queries per month. After that, it's a small per-query charge. We'll share detailed pricing before the launch.", "start_time": 249, "end_time": 261},
        {"speaker": "Tom Bradley", "text": "Alright, let me summarize our next steps. I'll send over the SCIM setup guide and schedule a call with your IT team for Thursday. Emily will share the integration docs for Google Meet, Slack, and Jira. And we'll aim to start the pilot week after next.", "start_time": 261, "end_time": 282},
        {"speaker": "Rachel Green", "text": "Sounds great! Thank you both so much. We're really excited to get started.", "start_time": 282, "end_time": 289},
        {"speaker": "Tom Bradley", "text": "Our pleasure! Looking forward to working with the Acme Corp team. Talk soon!", "start_time": 289, "end_time": 295},
    ]

    for i, seg in enumerate(m4_segments):
        db.add(TranscriptSegment(meeting_id=m4.id, order_index=i, **seg))

    db.add(Summary(
        meeting_id=m4.id,
        overview="Enterprise onboarding kickoff with Acme Corp (150 users). Covered workspace setup, user provisioning via Okta SCIM, integration configuration (Google Meet, Slack, Jira, Salesforce), data security (SOC 2, GDPR), custom retention policies, and a phased rollout plan. Key next steps include SCIM setup with IT team and a pilot program starting in two weeks.",
        key_topics=[
            {"title": "Integration Setup", "description": "Google Meet auto-join, Slack summary cards with keyword alerts, Jira and Salesforce connections."},
            {"title": "User Provisioning", "description": "SCIM integration with Okta for 150 users, estimated 2-3 hours to configure."},
            {"title": "Data Security & Compliance", "description": "SOC 2 Type II, GDPR compliant, custom retention policies (90-day default, 7-year for compliance meetings)."},
            {"title": "Rollout Plan", "description": "Three-phase rollout: admin setup (week 1), pilot with 20-30 users (week 2), company-wide (week 3)."},
        ],
        chapters=[
            {"title": "Welcome & Context", "start_time": 0, "end_time": 62, "summary": "Introductions and discussion of Acme Corp's current workflow and tool stack."},
            {"title": "Integration Overview", "start_time": 62, "end_time": 97, "summary": "Walkthrough of Google Meet, Slack, and Jira integration capabilities."},
            {"title": "User Provisioning & Security", "start_time": 97, "end_time": 178, "summary": "SCIM setup with Okta, data security certifications, and retention policies."},
            {"title": "Training & Rollout Plan", "start_time": 178, "end_time": 261, "summary": "Phased rollout plan and AI assistant preview."},
            {"title": "Next Steps", "start_time": 261, "end_time": 295, "summary": "Action items assigned and follow-up calls scheduled."},
        ],
        outline=[
            {"heading": "Client Requirements", "points": ["150 users", "Google Meet + Slack + Jira + Salesforce", "Okta SSO", "Regulated industry compliance needs"]},
        ],
    ))

    for ai in [
        {"text": "Send SCIM setup guide to Acme Corp IT team", "assignee": "Tom Bradley", "is_completed": True},
        {"text": "Schedule IT team call for Thursday", "assignee": "Tom Bradley", "is_completed": False},
        {"text": "Share Google Meet, Slack, and Jira integration docs", "assignee": "Emily Rodriguez", "is_completed": False},
        {"text": "Configure custom retention policies (90-day + 7-year)", "assignee": "Tom Bradley", "is_completed": False},
        {"text": "Prepare pilot program for 20-30 Acme power users", "assignee": "Tom Bradley", "is_completed": False},
    ]:
        db.add(ActionItem(meeting_id=m4.id, **ai))

    # ═══════════════════════════════════════════════════════════════
    # Meeting 5: Weekly Team Standup
    # ═══════════════════════════════════════════════════════════════
    m5 = Meeting(
        title="Engineering Weekly Standup",
        date=datetime.utcnow() - timedelta(hours=8),
        duration_seconds=1200,
        host="Sarah Chen",
        participants=["Sarah Chen", "Marcus Johnson", "Priya Patel", "David Kim", "Lucas Martinez"],
        status="completed",
        meeting_type="audio",
    )
    db.add(m5)
    db.flush()
    m5.tags.append(tags["Engineering"])

    m5_segments = [
        {"speaker": "Sarah Chen", "text": "Good morning team! Let's do our weekly standup. Quick updates from everyone. Marcus, you want to start?", "start_time": 0, "end_time": 8},
        {"speaker": "Marcus Johnson", "text": "Sure. This week I completed the auth migration RFC and got it approved. I also finished setting up the feature flag system using LaunchDarkly. Next week I'll start the actual migration of the first three services.", "start_time": 8, "end_time": 24},
        {"speaker": "Sarah Chen", "text": "Excellent progress on the auth migration. Any blockers?", "start_time": 24, "end_time": 28},
        {"speaker": "Marcus Johnson", "text": "One minor blocker — I need access to the staging environment for the payment service. Can you put in that request for me?", "start_time": 28, "end_time": 36},
        {"speaker": "Sarah Chen", "text": "Consider it done. I'll submit that today. Priya, you're up.", "start_time": 36, "end_time": 41},
        {"speaker": "Priya Patel", "text": "I've been focused on the dashboard metrics cards. The design is implemented and I've connected them to the analytics API. I also started on the Recharts integration for the trend graphs.", "start_time": 41, "end_time": 55},
        {"speaker": "Priya Patel", "text": "One thing I want to flag — the analytics API response times are a bit slow, averaging about 800 milliseconds. We might want Marcus to look at optimizing those queries before I finish the dashboard.", "start_time": 55, "end_time": 69},
        {"speaker": "Marcus Johnson", "text": "I can look at that. It's probably the aggregation queries. Let me add some materialized views and it should drop to under 200ms.", "start_time": 69, "end_time": 79},
        {"speaker": "Sarah Chen", "text": "Good, let's make that a priority. David, what's your update?", "start_time": 79, "end_time": 84},
        {"speaker": "David Kim", "text": "I knocked out 8 of the 12 mobile layout tickets this week. The remaining 4 are all related to the tablet navigation issue, which Priya and I are pairing on next week.", "start_time": 84, "end_time": 96},
        {"speaker": "David Kim", "text": "I also investigated the search performance issue and found that we're missing composite indexes on three tables. Adding those indexes improved search speed by 60% in my local tests.", "start_time": 96, "end_time": 111},
        {"speaker": "Sarah Chen", "text": "That's a huge improvement! Can you submit a PR for the index changes today?", "start_time": 111, "end_time": 116},
        {"speaker": "David Kim", "text": "Already done — PR 847. Just needs a review.", "start_time": 116, "end_time": 120},
        {"speaker": "Sarah Chen", "text": "Lucas, how about you?", "start_time": 120, "end_time": 123},
        {"speaker": "Lucas Martinez", "text": "I've been setting up the Radix UI migration. I've converted the Modal, Dropdown, and Tooltip components so far. The Storybook comparison is live and looking good. Next week I'll tackle the DatePicker and Select components.", "start_time": 123, "end_time": 142},
        {"speaker": "Lucas Martinez", "text": "Oh, and Sophie and I found a way to automate most of the accessibility testing using Playwright and axe-core. We have a CI pipeline that now catches accessibility regressions automatically.", "start_time": 142, "end_time": 157},
        {"speaker": "Sarah Chen", "text": "That's fantastic! Automated a11y testing is a game changer. Great work everyone. Sprint is looking really healthy at this point. Let's keep the momentum going!", "start_time": 157, "end_time": 168},
    ]

    for i, seg in enumerate(m5_segments):
        db.add(TranscriptSegment(meeting_id=m5.id, order_index=i, **seg))

    db.add(Summary(
        meeting_id=m5.id,
        overview="Weekly engineering standup covering progress on sprint items. Marcus completed the auth migration RFC and feature flag setup. Priya implemented dashboard metrics cards and started Recharts integration. David fixed 8/12 mobile tickets and improved search performance by 60% with composite indexes. Lucas converted 3 components to Radix UI and set up automated accessibility testing in CI.",
        key_topics=[
            {"title": "Auth Migration Progress", "description": "RFC approved, LaunchDarkly feature flags set up, migration of first 3 services starts next week."},
            {"title": "Dashboard Implementation", "description": "Metrics cards completed, Recharts integration in progress, analytics API needs optimization."},
            {"title": "Search Performance Win", "description": "60% search speed improvement from composite indexes, PR #847 ready for review."},
            {"title": "Radix UI Migration", "description": "Modal, Dropdown, and Tooltip converted, automated a11y testing pipeline created."},
        ],
        chapters=[
            {"title": "Marcus - Auth Migration Update", "start_time": 0, "end_time": 41, "summary": "Auth RFC approved, feature flags ready, needs staging access for payment service."},
            {"title": "Priya - Dashboard Progress", "start_time": 41, "end_time": 84, "summary": "Metrics cards done, Recharts started, analytics API response times need optimization."},
            {"title": "David - Mobile & Search Fixes", "start_time": 84, "end_time": 123, "summary": "8/12 mobile tickets done, search 60% faster with new indexes."},
            {"title": "Lucas - Component Library & Testing", "start_time": 123, "end_time": 168, "summary": "3 components migrated to Radix, automated a11y testing in CI pipeline."},
        ],
        outline=[
            {"heading": "Blockers", "points": ["Marcus needs staging access for payment service", "Analytics API response times (800ms) need optimization"]},
            {"heading": "Achievements", "points": ["Auth RFC approved", "8/12 mobile fixes done", "60% search speed improvement", "Automated a11y testing in CI"]},
        ],
    ))

    for ai in [
        {"text": "Submit staging access request for Marcus", "assignee": "Sarah Chen", "is_completed": False},
        {"text": "Optimize analytics API aggregation queries", "assignee": "Marcus Johnson", "is_completed": False},
        {"text": "Review PR #847 (composite index changes)", "assignee": "Sarah Chen", "is_completed": False},
        {"text": "Convert DatePicker and Select to Radix UI", "assignee": "Lucas Martinez", "is_completed": False},
    ]:
        db.add(ActionItem(meeting_id=m5.id, **ai))

    # ═══════════════════════════════════════════════════════════════
    # Meeting 6: Marketing Campaign Planning
    # ═══════════════════════════════════════════════════════════════
    m6 = Meeting(
        title="Q4 Marketing Campaign — AI Launch Strategy",
        date=datetime.utcnow() - timedelta(days=2, hours=4),
        duration_seconds=2100,
        host="Natasha Brooks",
        participants=["Natasha Brooks", "Derek Wang", "Lisa Park", "Tom Bradley"],
        status="completed",
        meeting_type="video",
    )
    db.add(m6)
    db.flush()
    m6.tags.append(tags["Marketing"])
    m6.tags.append(tags["Product"])

    m6_segments = [
        {"speaker": "Natasha Brooks", "text": "Alright team, let's plan our marketing campaign for the AI assistant launch. This is going to be our biggest product announcement this year, so we need to nail the messaging.", "start_time": 0, "end_time": 13},
        {"speaker": "Derek Wang", "text": "I've been analyzing our competitors' AI launch campaigns. The key themes that resonate with our audience are: time savings, accuracy, and seamless integration. We should lead with time savings.", "start_time": 13, "end_time": 27},
        {"speaker": "Lisa Park", "text": "I agree. Our early beta testers reported saving an average of 4 hours per week on meeting follow-ups. That's a powerful stat we should feature prominently.", "start_time": 27, "end_time": 39},
        {"speaker": "Natasha Brooks", "text": "Love that. Let's build our campaign around the headline: 'Reclaim 4 Hours Every Week.' Derek, can you draft three variations of the main campaign copy?", "start_time": 39, "end_time": 51},
        {"speaker": "Tom Bradley", "text": "From the sales perspective, our enterprise prospects are most interested in the cross-meeting intelligence feature — being able to search across all past meetings and find patterns.", "start_time": 51, "end_time": 64},
        {"speaker": "Natasha Brooks", "text": "Good point. We should have a separate enterprise-focused campaign track. Tom, can you provide 3-4 customer quotes we can use for the enterprise messaging?", "start_time": 64, "end_time": 76},
        {"speaker": "Derek Wang", "text": "For channels, I'm recommending a multi-touch approach: product launch blog post, email sequence to existing users, LinkedIn campaign targeting decision-makers, and a webinar demo.", "start_time": 76, "end_time": 92},
        {"speaker": "Lisa Park", "text": "Let's also plan a Product Hunt launch. Our last launch got us 2,000 sign-ups in the first week. With the AI angle, I think we could do even better.", "start_time": 92, "end_time": 104},
        {"speaker": "Natasha Brooks", "text": "Absolutely. Lisa, you'll lead the Product Hunt campaign. Let's target the first week of December for the launch. Derek, the blog post and email sequence. Tom, enterprise outreach.", "start_time": 104, "end_time": 120},
        {"speaker": "Derek Wang", "text": "What's our budget for this campaign? I'd like to allocate some spend on LinkedIn ads and potentially a sponsored newsletter placement.", "start_time": 120, "end_time": 130},
        {"speaker": "Natasha Brooks", "text": "We have $50,000 allocated for the Q4 product launch. I'd suggest 40% on LinkedIn ads, 25% on content and influencer partnerships, 20% on the webinar production, and 15% as a reserve.", "start_time": 130, "end_time": 148},
        {"speaker": "Lisa Park", "text": "Can we also create a short product demo video? Maybe 60-90 seconds showing the AI assistant in action. We could use it across all channels.", "start_time": 148, "end_time": 160},
        {"speaker": "Derek Wang", "text": "I'll coordinate with the product team to get screen recordings. We can produce the video in-house — I have experience with motion graphics.", "start_time": 160, "end_time": 171},
        {"speaker": "Natasha Brooks", "text": "Great. Let's set our milestones: Campaign assets ready by November 15th. Private beta outreach starts November 18th. Public launch December 1st. Post-launch analysis December 15th.", "start_time": 171, "end_time": 190},
        {"speaker": "Tom Bradley", "text": "One more idea — we should invite our top 10 enterprise prospects to an exclusive preview event the week before the public launch. It creates urgency and makes them feel valued.", "start_time": 190, "end_time": 205},
        {"speaker": "Natasha Brooks", "text": "Love that idea, Tom. Let's do a virtual preview event on November 25th. Alright team, we have a solid plan. Let's execute!", "start_time": 205, "end_time": 216},
    ]

    for i, seg in enumerate(m6_segments):
        db.add(TranscriptSegment(meeting_id=m6.id, order_index=i, **seg))

    db.add(Summary(
        meeting_id=m6.id,
        overview="Marketing team planned the AI assistant launch campaign with 'Reclaim 4 Hours Every Week' as the headline. Campaign includes a multi-channel approach: blog post, email sequence, LinkedIn ads, Product Hunt launch, webinar demo, and enterprise preview event. Budget of $50K allocated across LinkedIn ads (40%), content/influencer (25%), webinar (20%), and reserve (15%). Key milestones set from November 15 to December 15.",
        key_topics=[
            {"title": "Campaign Messaging", "description": "Lead with time savings (4 hours/week stat), separate enterprise track for cross-meeting intelligence."},
            {"title": "Channel Strategy", "description": "Blog post, email sequence, LinkedIn ads, Product Hunt, webinar demo, enterprise preview event."},
            {"title": "Budget Allocation", "description": "$50K total: LinkedIn 40%, content 25%, webinar 20%, reserve 15%."},
            {"title": "Timeline", "description": "Assets by Nov 15, beta outreach Nov 18, public launch Dec 1, analysis Dec 15."},
        ],
        chapters=[
            {"title": "Campaign Positioning", "start_time": 0, "end_time": 76, "summary": "Team aligned on 'Reclaim 4 Hours' messaging with separate enterprise track."},
            {"title": "Channel & Budget Planning", "start_time": 76, "end_time": 171, "summary": "Multi-channel approach with $50K budget allocation across LinkedIn, content, and webinar."},
            {"title": "Timeline & Milestones", "start_time": 171, "end_time": 216, "summary": "Key milestones set with exclusive enterprise preview event on November 25."},
        ],
        outline=[
            {"heading": "Campaign Assets Needed", "points": ["60-90 second demo video", "Blog post", "Email sequence", "LinkedIn ad creatives", "Product Hunt listing"]},
        ],
    ))

    for ai in [
        {"text": "Draft 3 variations of main campaign copy", "assignee": "Derek Wang", "is_completed": False},
        {"text": "Provide 3-4 enterprise customer quotes", "assignee": "Tom Bradley", "is_completed": False},
        {"text": "Lead Product Hunt launch campaign", "assignee": "Lisa Park", "is_completed": False},
        {"text": "Create 60-90 second product demo video", "assignee": "Derek Wang", "is_completed": False},
        {"text": "Plan enterprise preview event for November 25", "assignee": "Tom Bradley", "is_completed": False},
    ]:
        db.add(ActionItem(meeting_id=m6.id, **ai))

    db.commit()
    db.close()
    print("Database seeded with 6 meetings, transcripts, summaries, and action items!")


if __name__ == "__main__":
    seed_database()
