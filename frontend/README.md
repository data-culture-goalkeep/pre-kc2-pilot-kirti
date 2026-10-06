# Vanavil frontend prototype

This folder contains the static frontend prototype currently deployed manually to Cloudflare.

## Current status
- Sample-data prototype only.
- Not connected to Supabase yet.
- Assessment score entry follows the PM-approved integer 1-10 rule.
- Attendance options expose P, A, H, and NA. Raw source code N remains unresolved and is not exposed as a selectable UI value.
- BMI analysis remains explicitly provisional.
- Follow-up/risk thresholds are illustrative pending final business-rule approval.

## Local preview
Open `frontend/index.html` in a browser.

## Deployment
The current prototype can be deployed as static assets to Cloudflare. Automatic GitHub-to-Cloudflare deployment can be added separately.

Cloudflare auto-deploy is enabled for this branch via GitHub Actions.
