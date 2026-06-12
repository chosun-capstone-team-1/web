# MalGuard Deployment Checklist

## Do not commit

- `node_modules/`, `dist/`, `.omx/`, `.playwright-mcp/`, screenshots, local `.env` files
- model files: `*.pth`, `*.pkl`

## Required backend files on the AWS server

The EXE model must be copied manually to:

```txt
backend/models/CNN_exe.pth
```

Do not create a dummy model and do not commit the `.pth` file to GitHub.

If PDF report/model support is used by backend internals, copy the existing PDF model manually to one of the supported model paths:

```txt
backend/models/Randomforest_pdf.pkl
# or legacy fallback
backend/app/assets/Randomforest_pdf.pkl
```

## Required backend environment variables

```bash
DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DBNAME'
REDIS_HOST='REDIS_HOST_OR_LOCALHOST'
REDIS_PORT='6379'
REDIS_DB='0'
CORS_ORIGINS='https://YOUR_FRONTEND_DOMAIN,https://YOUR_CLOUDFRONT_DOMAIN'
```

Run backend from `backend/`:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend API routing options

### Option A: Same domain reverse proxy (recommended)

Serve the built frontend and proxy `/api/*` to FastAPI. The frontend default API base is `/api`.

Example Nginx concept:

```nginx
location / {
  try_files $uri /index.html;
}

location /api/ {
  proxy_pass http://127.0.0.1:8000/;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
}
```

### Option B: Static frontend with absolute backend URL

Set the frontend build env before building:

```bash
VITE_API_BASE_URL='https://YOUR_BACKEND_DOMAIN' npm run build
```

For local dev proxy target override:

```bash
VITE_API_PROXY_TARGET='http://127.0.0.1:8000' npm run dev
```

## Frontend build

Run from `frontend/frontend/`:

```bash
npm run build
```

Deploy only `frontend/frontend/dist/` to static hosting if using S3/CloudFront.
