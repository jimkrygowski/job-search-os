Summarize a job search call transcript and save the notes to the right place.

## What to do

1. **Find the transcript.** The user will either paste it directly, provide a file path, or name a company. If it's not clear, ask: "Where's the transcript — paste it here, or give me a file path?"

2. **Extract the key facts:**
   - Who was on the call (names, titles, companies)
   - Date and duration
   - What they told the user about the company, role, opportunity, comp, team, roadmap, concerns
   - What the user said that landed well or poorly
   - Explicit next steps and who owns them
   - Any surprises, red flags, or things that shifted the user's stance

3. **Write the call notes file.** Resolve the opportunity folder via
   `python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` —
   never construct the path yourself from the Company/Role text — then
   write to `<resolved folder>/transcripts/<Contact>_Call_<YYYY-MM-DD>.md`
   using this structure:
   - Header: date, attendees, duration
   - Key takeaways (bullet list, most important things first)
   - What the user learned (about company, role, team, comp, process)
   - What landed well
   - Open questions / things to follow up on
   - Next steps (who does what by when)
   - Stance update (if the user's level of interest shifted, say so and why)

4. **Update the tracker:**
   ```
   python3 tools/tracker.py update-status "<Company>" "<Role>" \
     --stage "<stage>" --next-action "<next action>" \
     --next-action-date "<date, if known>"
   ```
   Add a one-line summary to the resolved opportunity folder's `notes.md`
   as well — the tracker row itself stays to short scalar fields.

5. **Ask the user** if there are follow-up emails to draft or prep docs to update based on what came out of the call.

## Style notes
- Be specific — names, numbers, quotes from the call where useful
- Flag anything that changed the user's read on the opportunity (positively or negatively)
- Keep the stance update honest — if it's unclear, say so
