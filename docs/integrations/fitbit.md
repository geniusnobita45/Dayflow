# Fitbit automatic activity sync

DayFlow supports Fitbit OAuth 2.0 for automatic daily steps, distance, calories, and active-minute tracking.

## One-time Fitbit developer setup

1. Sign in at [dev.fitbit.com](https://dev.fitbit.com/) and register a server/web application.
2. Set the OAuth callback URL to your deployed DayFlow URL followed by `/auth/fitbit/callback`.
   Example: `https://dayflow.onrender.com/auth/fitbit/callback`
3. In Render, add these environment variables:
   - `FITBIT_CLIENT_ID`
   - `FITBIT_CLIENT_SECRET`
   - `FITBIT_REDIRECT_URI` (the exact callback URL registered above)
4. Redeploy DayFlow after saving the environment variables.

## User flow

A signed-in user selects **Connect Fitbit** on the Activity tracker, approves the `activity` permission, and returns to DayFlow. DayFlow then:

- encrypts the OAuth access and refresh tokens before database storage;
- syncs today's Fitbit summary immediately;
- refreshes expired access tokens automatically;
- refreshes dashboard activity data at most once every five minutes;
- lets the user force a refresh with **Sync Fitbit**;
- deletes the connection and imported metrics when the user disconnects.

Manual tracking remains available as a fallback. To avoid duplicate totals when an activity exists in both places, DayFlow uses the larger of the Fitbit and manual daily totals for each headline metric.

## API endpoints

- `GET /auth/fitbit` — begin OAuth connection
- `GET /auth/fitbit/callback` — complete OAuth connection
- `GET /api/fitbit/status` — connection status
- `POST /api/fitbit/sync` — force a daily sync
- `DELETE /api/fitbit/disconnect` — remove the connection and synced metrics