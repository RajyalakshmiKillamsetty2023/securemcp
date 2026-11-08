# Dashboard

React + Vite front end for SecureMCP. It shows agent calls as they happen.

```bash
npm install
npm run dev      # http://127.0.0.1:5173
npm run build
```

The dev server forwards `/api` to the Node API on `127.0.0.1:3001`, so start that first
(see the root README). Live updates arrive over server-sent events from `/api/events`.
