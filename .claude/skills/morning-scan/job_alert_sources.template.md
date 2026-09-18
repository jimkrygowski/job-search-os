# Job Alert Sources

List the email senders that deliver job alerts, and what to filter for.
`morning-scan` reads this file (once copied to
`state/career/job_alert_sources.md` — see `morning-scan`'s Session Start)
to build its Tier 2 search.

## Example format

- **Source name:** Acme Job Alerts
  **Sender pattern:** `from:alerts@acmejobalerts.example`
  **Lookback:** `newer_than:1d`
  **Trashed digests:** hand-triaged (default) | auto-trashed
  **Filter for:** title/company/location/comp matching
  `state/career/trajectory.md` must-haves

**Trashed digests** decides whether Tier 2 reads Trash for this source:

- `hand-triaged` (default) — you trash a digest once you have read it and
  found nothing relevant. Tier 2 skips trashed digests, so it never
  re-surfaces a listing you already rejected.
- `auto-trashed` — a filter or cleanup rule moves these to Trash before
  you see them. Tier 2 passes `includeTrash: true` for this source so
  they are not silently missed.

(Replace this example with real sources during setup.)
