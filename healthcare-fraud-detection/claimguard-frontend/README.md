# ClaimGuard — Frontend

React frontend for the AI-Powered Healthcare Insurance Claim Fraud Detection System, built from the project PRD (Login → Dashboard → Submit Claim → Investigation → Reports → Notifications, three roles: Claims Officer, Fraud Investigator, Admin).

## Stack

- React 19 + Vite
- MUI (Material UI) v6 — theming, layout, tables, forms
- React Router v6 — routing + role-based route guards
- Recharts — dashboard/report charts
- Axios — API layer with JWT refresh interceptor

## Getting started

```bash
npm install
npm run dev
```

The app runs fully standalone out of the box in **mock mode** — no backend required. Use the demo account buttons on the Login page (or any of these, password `demo1234`):

| Role | Email |
|---|---|
| Claims Officer | officer@claimguard.ai |
| Fraud Investigator | investigator@claimguard.ai |
| Admin | admin@claimguard.ai |

## Connecting to the real backend

Everything runs through `src/services/*.js`. Each function already calls the exact endpoint listed in the PRD — it just short-circuits to mock data while `VITE_USE_MOCK=true`.

1. Copy `.env.example` to `.env`.
2. Set `VITE_API_BASE_URL` to your Flask/FastAPI base URL (e.g. `http://localhost:8000/api`).
3. Set `VITE_USE_MOCK=false`.
4. Make sure your backend's `/auth/login` response matches `{ accessToken, refreshToken, user: { id, name, email, role } }`, and that `role` is exactly one of `"Claims Officer"`, `"Fraud Investigator"`, `"Admin"` (see `src/context/AuthContext.jsx`).

No component code needs to change — the pages only ever call the service layer.

## Folder structure

```
src/
  theme/theme.js          Design tokens (blue/white enterprise healthcare palette), MUI theme
  context/AuthContext.jsx JWT session state + role helpers (ROLES.OFFICER/INVESTIGATOR/ADMIN)
  services/                api.js (axios + refresh), authService, claimsService,
                            dashboardService, notificationsService, mockData.js
  components/
    layout/                Sidebar (role-filtered nav), Topbar, DashboardLayout
    common/                KpiCard, RiskGauge (SVG), RiskChip/StatusChip, EmptyState, ProtectedRoute
  pages/                   Login, Dashboard, SubmitClaim, ClaimHistory, ClaimDetails,
                            Investigation, Reports, Notifications, Profile
```

## Role-based access

Defined once in `App.jsx` via `<ProtectedRoute roles={[...]}>`, and mirrored in `Sidebar.jsx` so nav items only render for roles that can access them:

- **Claims Officer** — Dashboard, Submit Claim, Claim History, Notifications
- **Fraud Investigator** — Dashboard, Claim History, Investigation, Reports, Notifications
- **Admin** — everything except Submit Claim

## Notes

- Claim amounts, KPIs, and chart data are never hardcoded into components — they always come from the service layer (mocked today, live once the backend is connected), matching the PRD's "no fake/static data" requirement.
- `RiskGauge` is a hand-built SVG arc (no chart library) so it can sit cleanly inside cards at any size.
- Reports → Export CSV downloads the monthly trend as a `.csv`; Export PDF uses the browser print dialog (`window.print()`) with the current filtered view.
- `USE_MOCK` also gates the demo-account helper on the Login page, so it disappears automatically once you point at the real backend.
