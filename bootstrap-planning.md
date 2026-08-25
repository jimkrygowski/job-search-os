# Job Search Agent — Bootstrap Planning

Fill in each section below. Bullet points, fragments, or rambling paragraphs
are all fine — this is raw material, not a finished spec. Leave a section
blank if you're not sure yet; that's what "Open Questions" is for.

---

## 1. High-Level Purpose

This agent assists job seekers as they plan and execute a job search. The core job-to-be-done is to 
assist the job seeken in identifying the career objective they want to fulfill, understand their
career to date, develop a resume that reflects that career and accompanying stories, identify job 
opportunities and score them, manage an application workflow (identified, cover letter & resume tweak, 
network connection identificqation, resume submission, interview process stage management, offer negotiation).

This is for anyone. 
---

## 2. What to Preserve

Skills like /morning-scan and /career-coach are to be preserved and we'll add more. The organization
of the company folder (subdir per company) is good. the archiving function for closed opps is also good. 
the status csv is a good start but needs improving. keep the tools and build on them.

---

## 3. What to Fix / Leave Behind

00_Admin as a dumping ground is bad. that needs improving. career and opportunity scorecard are also 
needing improving. resume management needs improving.
Specific pain points, friction, or things that went unused or felt wrong.
What did you keep working around instead of using as designed?

---

## 4. Scope

What should this system actually do? Sort into buckets.

**Must-have:**
1. initial workflow to build the candidate profile. either start from an existing resume or guide the user through creation of one.
2. conversation about the career to date. why you're where you're at and what you want to head towards. ask questions about best job and why. worst job and why. best boss and why worst boss and why.
3. conversation about where the career is headed. what is a great next role. what experience supports that trajectory. what's must have. what's nice to have. also frank discussion about how much of a stretch the next step could be based on past experience and some coaching on how to position past experience or find ways to fill in gaps.
4. status list of active opportunities (application tracker)
5. company sub-folder for each opportunity with doc repository: jd, meeting transcripts, custom resumes & cover letters
6. daily email inbox review of job listings, correspondence with recruiters and potential employers
7. daily calndar review of events planned for the week w/ persistence of events into the application tracker
8. review of job descriptions pasted into chat
9. company research
9. ranking of opportunity against "great role"
10. interview prep briefings
11. interview transcript reviews and feedback

**Nice-to-have:**
-

**Explicitly out of scope:**
- automation

---

## 5. Data & Sources of Truth

Inputs that feed the system: resume, target roles, applications tracker,
email, calendar, call transcripts, company notes.

The current folder layout should change. i'd suggest
career/
opportunity/<Company>/<Role>
tools/

place the "application tracker" as a peer to the career, opportunity and toolls directories. 

keep the resume and the outputs of the career conversation. 

---

## 6. Interaction Model

There's one persistent agent persona and slash commands. Everything is chat interaction based.

---

## 7. Persona & Voice

Tone/character for the agent is career-coach "a peer and thought partner, not a cheerleader". The voice
is clear and direct. It does not oversell things or confidently pass judgement. It only states facts
known to it and provides references for the source of its facts. 

---

## 8. Automation & Triggers

Automation and triggers are out of scope. 


---

## 9. Memory & State

the application tracker file is the central state file that contains the state of the job search (aka pipeline state). 
for each opportunity create a file containing the contacts and their roles. also keep a record of meeting outcomes and
new opportunity information that helps to either make the next interview stage more succesful or refines the thinking
about the opportunity. 

preferences of the user of the agent are stored as memories.

the application tracker is mainted by the agent using a tool. we'll need to build this tool. i want
to avoid the problem with the current system where the tracker file is corrupted by the agent when it misformats information.
the tool will expose an API that the agent calls to update application status.

---

## 10. Guardrails / Non-negotiables

1. never invent experience on a resume
2. never assert "opinions" about things without referencing an underlying fact
3. never send correspondence on your own

---

## 11. Success Criteria

The new system will be considered successul if i have to exert less labor in operating it. 

---

## 12. Open Questions

None currently.