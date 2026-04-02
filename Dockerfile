# Stage 1 — Build Tailwind CSS
FROM node:20-alpine AS tailwind-builder
WORKDIR /app

# Install npm deps first (cached layer)
COPY theme/static_src/package*.json theme/static_src/
RUN cd theme/static_src && npm ci

# Copy everything needed for Tailwind class scanning
COPY theme/static_src theme/static_src
COPY templates templates
COPY app app
COPY manage.py .

# Build minified CSS → theme/static/css/dist/styles.css
RUN cd theme/static_src && npm run build

# ─────────────────────────────────────────────────────────────────

# Stage 2 — Python runtime
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=event_management_system.settings.production

WORKDIR /app

# System deps required by psycopg and pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Overlay built CSS from Stage 1 (overwrites any stale local build)
COPY --from=tailwind-builder /app/theme/static/css/dist/styles.css theme/static/css/dist/styles.css

# Entrypoint
RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
