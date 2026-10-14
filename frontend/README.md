# Vanavil frontend

Phase 2 milestone: **Students & Attendance — read-only**.

- Static Cloudflare-compatible frontend.
- Supabase Auth email/password sign-in for existing internal users.
- Browser client uses only the project URL and browser-safe publishable key.
- Students & Attendance reads live `students`, `student_grade_enrollments`, `grades`, `academic_years`, `attendance_months`, `attendance_days`, and `attendance_status_codes` data.
- Loading, empty, error, unauthenticated, expired-session, and signed-in states are handled.
- No student, attendance, or assessment writes are implemented.
- Assessment shared logic accepts numeric `0-10` and `A` (Absent). `A` stays `A`, contributes effective value `0`, and remains in the denominator. `77`, `87`, `89`, and `N` are not accepted as assessment scores.

## Local preview

Serve this directory with any static HTTP server. Opening via `file://` is not recommended because ES modules are used.

## Tests

```sh
node frontend/test_frontend.mjs
```

## Deployment

`frontend/wrangler.jsonc` deploys this directory as static assets. The Phase 2 feature-branch workflow provides a Cloudflare preview/deploy attempt when configured repository secrets are available.
