# Job Alert Sources

List the email senders that deliver job alerts, and what to filter for.
`morning-scan` reads this file to build its Tier 2 search.

## Example format

- **Source name:** Acme Job Alerts
  **Sender pattern:** `from:alerts@acmejobalerts.example`
  **Lookback:** `newer_than:2d`
  **Filter for:** title/company/location/comp matching
  `career/trajectory.md` must-haves

(Replace this example with real sources during setup.)
