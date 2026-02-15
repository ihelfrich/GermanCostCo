# Consulting Portal (React + GitHub Pages)

## Local development
```bash
pnpm install --dir webapp
python3 scripts/build_presentation_data.py
pnpm --dir webapp run prepare:data
pnpm --dir webapp run dev
```

Open `http://localhost:5173`.

## Production build
```bash
python3 scripts/build_presentation_data.py
pnpm --dir webapp run prepare:data
pnpm --dir webapp run build
pnpm --dir webapp run preview
```

## Deployment
Deployment is automated by `.github/workflows/deploy-pages.yml` on pushes to `main`.

Important repository setting:
- `Settings -> Pages -> Build and deployment -> Source = GitHub Actions`
