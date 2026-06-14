# MalGuard EC2 Deployment Guide

## 프로젝트 실행 구조

- Backend: FastAPI + Uvicorn, `backend/Dockerfile` 기반 컨테이너로 실행
- DB: PostgreSQL 13, `backend/docker-compose.yml`의 `db` 서비스로 실행
- Redis: 업로드 제한 카운터 저장용, `backend/docker-compose.yml`의 `redis` 서비스로 실행
- Frontend: Vite React 앱, Docker Compose의 frontend 컨테이너 또는 Nginx로 서빙
- 모델 파일: `Model/CNN_exe.pth`를 backend 컨테이너의 `/app/models/CNN_exe.pth`로 마운트

## EC2 Ubuntu 설치 항목

Docker Compose로 backend, DB, Redis를 실행하는 기준입니다.

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release git nginx

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

docker --version
docker compose version
nginx -v
```

Frontend를 EC2에서 빌드하려면 Node.js 20도 설치합니다.

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

## backend 환경 변수

`backend/.env.example`을 복사해서 `backend/.env`로 사용합니다.

```bash
cp .env.example .env
```

기본 예시는 Docker Compose 기준입니다.

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/mld-backend-db
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
SECRET_KEY=change-this-to-a-long-random-string
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://YOUR_EC2_PUBLIC_IP:4173,https://YOUR_FRONTEND_DOMAIN
OPENAI_API_KEY=
```

## Docker Compose 실행

프로젝트 루트에서 한 번에 backend, DB, Redis, frontend를 빌드하고 실행하려면 아래를 사용합니다.

```bash
cd /home/ubuntu/web
cp backend/.env.example backend/.env
docker compose up -d --build
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

backend만 따로 올릴 때는 기존처럼 `backend/`에서 `docker compose up -d --build`를 사용해도 됩니다.

컨테이너 포트는 외부에 공개하지 않고 로컬에만 바인딩합니다.

```bash
127.0.0.1:3000 -> frontend container
127.0.0.1:8000 -> backend container
```

중지할 때는 아래를 사용합니다.

```bash
cd /home/ubuntu/web/backend
docker compose down
```

## Frontend 빌드와 API 연결

현재 프론트엔드는 `frontend/frontend/src/utils/analysis.js`에서 `VITE_API_BASE_URL`을 읽고, 기본값이 `/api`입니다.

EC2에서 backend를 직접 호출할 때도 프론트 코드는 `/api`를 사용합니다. 배포 빌드에서는 이미 기본값이 `/api`라서 별도 주소를 넣지 않아도 됩니다.

```bash
cd /home/ubuntu/web/frontend/frontend
npm install
npm run build
```

로컬 확인용으로 정적 미리보기 서버를 띄우려면 아래를 사용합니다.

```bash
npm run preview -- --host 0.0.0.0 --port 4173
```

같은 도메인에서 Nginx를 쓸 경우에는 프론트 기본값인 `/api`를 유지하고, Nginx에서 `/`는 `http://127.0.0.1:3000`으로, `/api/`는 `http://127.0.0.1:8000/`으로 프록시하면 됩니다.

Nginx 설정 예시는 [`nginx/ec2.conf`](nginx/ec2.conf) 입니다.

## AWS 실행 순서

1. EC2 Ubuntu에 Docker, Docker Compose plugin, Nginx, Node.js 20을 설치합니다.
2. 저장소를 `/home/ubuntu/web`에 배포합니다.
3. `backend/.env.example`을 `backend/.env`로 복사한 뒤 `SECRET_KEY`, `CORS_ORIGINS`, 필요하면 `OPENAI_API_KEY`를 수정합니다.
4. `cd /home/ubuntu/web && docker compose up -d --build`로 backend, DB, Redis, frontend를 올립니다.
5. `sudo cp /home/ubuntu/web/nginx/ec2.conf /etc/nginx/sites-available/malguard.conf`
6. `sudo ln -sf /etc/nginx/sites-available/malguard.conf /etc/nginx/sites-enabled/malguard.conf`
7. `sudo nginx -t && sudo systemctl reload nginx`로 Nginx를 반영합니다.

## 접속 확인

```bash
curl http://127.0.0.1/api/robots.txt
curl http://127.0.0.1/api/docs
docker compose ps
docker compose logs --tail=50 backend
```

브라우저에서는 아래를 확인합니다.

- `http://YOUR_EC2_PUBLIC_IP/`
- `http://YOUR_EC2_PUBLIC_IP/api/docs`
- `http://YOUR_EC2_PUBLIC_IP/api/robots.txt`

## 자주 발생하는 오류

- `DATABASE_URL 환경변수가 없습니다!`: `backend/.env`가 없거나 `DATABASE_URL` 값이 빠졌습니다. `cp .env.example .env` 후 다시 실행합니다.
- `psycopg2` 연결 실패: `db` 컨테이너가 아직 올라오지 않았거나 `DATABASE_URL`의 호스트가 `db`가 아닙니다.
- `Redis` 연결 실패: `REDIS_HOST`가 `redis`가 아닌지 확인합니다.
- CORS 에러: `CORS_ORIGINS`에 `http://YOUR_EC2_PUBLIC_IP`가 빠졌는지 확인합니다.
- 프론트에서 API 호출이 실패함: 프론트가 `/api`를 쓰고 있는지 확인하고, Nginx에서 `/api/`가 `http://127.0.0.1:8000/`로 프록시되는지 확인합니다.
- 로그인 후 토큰 오류: `SECRET_KEY`를 자주 바꾸면 기존 토큰이 무효화됩니다. 배포 후에는 고정된 값으로 유지합니다.
- Nginx 502 오류: backend 컨테이너가 `Up` 상태인지, 그리고 `127.0.0.1:8000` 바인딩이 살아 있는지 확인합니다.
- 업로드 실패: `client_max_body_size`가 너무 작으면 Nginx에서 413이 납니다. 예시 설정의 `100m`로 유지합니다.

## 참고

- `backend/.env.example`은 샘플이며, 실제 운영값은 따로 관리합니다.
- `*.pth`, `*.pkl`, 로컬 `.env` 파일은 저장소에 커밋하지 않습니다.
