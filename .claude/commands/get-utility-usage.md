# Get Utility Usage

Fetch and display water usage statistics from the Thames Water monitoring service.

## Instructions

Query the Thames Water API at https://water.gavinslater.co.uk to retrieve usage data and present a summary.

### Steps

1. **Fetch Usage Summary** (30-day period):
   ```
   GET https://water.gavinslater.co.uk/api/usage/summary?days=30
   ```
   This returns:
   - Total usage (litres)
   - Average daily usage
   - Max/min daily usage
   - Days above threshold (800L)
   - Usage trend

2. **Fetch Recent Daily Data**:
   ```
   GET https://water.gavinslater.co.uk/api/usage/daily?limit=7
   ```
   Returns last 7 days of daily usage.

3. **Check for Alerts**:
   ```
   GET https://water.gavinslater.co.uk/api/alerts?status=unacknowledged
   ```
   Returns any active alerts.

4. **Format the Response**:
   Present the data in a clear, digestible format:

   ```
   ## Water Usage Summary (Last 30 Days)

   **Overview:**
   - Total: X,XXX litres
   - Daily Average: XXX litres
   - Trend: [up/down/stable]

   **Recent Usage (Last 7 Days):**
   | Date | Usage (L) | Status |
   |------|-----------|--------|
   | YYYY-MM-DD | XXX | Normal/High |
   ...

   **Alerts:**
   - [Any active alerts or "No active alerts"]

   **Dashboard:** https://water.gavinslater.co.uk
   ```

### Context

This integrates with the Thames Water monitoring service that:
- Automatically collects daily usage data at 6 AM
- Alerts when usage exceeds 800L threshold
- Tracks the gardener's fortnightly watering schedule (Thursdays)
- Helps monitor for potential leaks

### Response Format

Keep the response concise and actionable. Highlight any anomalies or concerns. If usage is approaching the threshold, suggest checking for issues.
