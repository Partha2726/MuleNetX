# MuleNetX dashboard

React 18 + TypeScript + Vite + D3 + Zustand, plain CSS modules (PLAN §2).

```
npm ci
npm run dev        # http://localhost:5173, proxies /api to MULENETX_BACKEND (default http://localhost:8000)
npm run lint       # eslint + tsc
npm test           # Vitest + MSW
npm run build
make gen-types     # (repo root) regenerate src/api/schema.d.ts from docs/openapi.json
```

Only `src/api/client.ts` performs HTTP (SRS §20.2; enforced by eslint). The session token lives in memory only.
Design context: `PRODUCT.md`, `DESIGN.md` and `.impeccable/` at the repository root.
