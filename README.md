# GitLab DevSecOps Pipeline

This repository contains a reusable GitLab CI pipeline for DevSecOps workflows. It is designed to be safe as a starting point for a new project and to activate deeper checks when application, container, infrastructure, or deployment files are added.

## What It Covers

- CI validation for the pipeline file
- Secret detection with Gitleaks
- SAST with Semgrep
- Dependency, secret, and misconfiguration scanning with Trivy
- Infrastructure-as-code scanning with Checkov
- Container build and push when a `Dockerfile` exists
- Container image scanning before promotion
- SBOM generation in CycloneDX and SPDX formats
- Optional OWASP ZAP baseline DAST scan
- Manual production deployment gate

## Quick Start

1. Push this repo to GitLab.
2. Confirm GitLab Container Registry is enabled if you plan to build images.
3. Add your application code and, if needed, a `Dockerfile`.
4. Add deployment commands to `deploy:review`, `deploy:review:stop`, and `deploy:production` in [.gitlab-ci.yml](.gitlab-ci.yml).
5. Configure CI/CD variables in GitLab as needed.

## Run Locally

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Open the interactive API docs at `http://127.0.0.1:8000/docs`.

Available endpoints:

- `GET /health`
- `GET /api/v1/customers/cust-001`
- `GET /api/v1/customers/cust-002`

Run tests:

```powershell
pytest
```

The test command also writes `coverage.xml`, which is consumed by SonarQube.

Build and run with Docker:

```powershell
docker build -t devsecops-demo-api .
docker run --rm -p 8000:8000 devsecops-demo-api
```

## Production Dockerfile

Build the image:

```powershell
docker build -t devsecops-demo-api:latest .
```

Run the container:

```powershell
docker run --rm --name devsecops-demo-api -p 8000:8000 devsecops-demo-api:latest
```

Check the API:

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/customers/cust-001
```

Dockerfile instruction notes:

- `FROM python:3.13-slim AS builder` uses a small Debian-based Python image for dependency installation and names it `builder`.
- `ENV PYTHONDONTWRITEBYTECODE=1` prevents Python from writing `.pyc` files into the image.
- `ENV PYTHONUNBUFFERED=1` sends logs directly to stdout and stderr, which is best for containers.
- `ENV VIRTUAL_ENV=/opt/venv` defines the virtual environment location used by both stages.
- `ENV PATH="$VIRTUAL_ENV/bin:$PATH"` makes the virtual environment Python and console scripts the default.
- `WORKDIR /app` sets the application working directory.
- `RUN python -m venv "$VIRTUAL_ENV"` creates an isolated dependency environment in the builder stage.
- `COPY requirements.txt .` copies only runtime dependency metadata before source code to improve Docker layer caching.
- `RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt` installs runtime dependencies without retaining pip cache.
- `FROM python:3.13-slim AS runtime` starts a clean final image, excluding builder-only layers.
- `RUN addgroup --system app && adduser --system --ingroup app --home /app --no-create-home app` creates a restricted non-root user.
- `COPY --from=builder /opt/venv /opt/venv` copies only installed runtime dependencies from the builder stage.
- `COPY --chown=app:app app ./app` copies only application source code and gives ownership to the non-root user.
- `USER app` runs the API process without root privileges.
- `EXPOSE 8000` documents the port the service listens on.
- `HEALTHCHECK ...` asks Docker to verify `/health` regularly using Python standard library HTTP calls.
- `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` starts the FastAPI app with Uvicorn.

## Useful CI/CD Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `REVIEW_APP_URL` | Optional | Enables review environment deployment jobs for merge requests. |
| `ZAP_TARGET_URL` | Optional | Enables OWASP ZAP baseline DAST against a running app. |
| `SEMGREP_RULES` | Optional | Defaults to `p/ci`; change to a Semgrep ruleset or local config. |
| `SONAR_HOST_URL` | Optional | Enables the GitLab SonarQube scanner job, for example `http://sonarqube.example.com:9000`. |
| `SONAR_TOKEN` | Optional | SonarQube token used by the GitLab scanner job. Store this as a masked CI/CD variable. |
| `CI_REGISTRY_*` | Built in | Used by GitLab to authenticate image build, push, and scan jobs. |

## SonarQube

The project is configured for SonarQube in [sonar-project.properties](sonar-project.properties):

- Project key: `devsecops-demo-api`
- Project name: `DevSecOps Demo API`
- Source folder: `app`
- Test folder: `tests`
- Coverage report path: `coverage.xml`

Run SonarQube locally with Docker Compose:

```powershell
docker compose -f docker-compose.sonarqube.yml up -d
```

Open SonarQube at `http://localhost:9000`. The default local login for a fresh SonarQube instance is usually `admin` / `admin`; SonarQube will prompt you to change it. Create a project token from SonarQube before running the scanner.

If SonarQube fails to start on Linux, set the host virtual memory limit first:

```bash
sudo sysctl -w vm.max_map_count=524288
sudo sysctl -w fs.file-max=131072
```

Generate the coverage report:

```powershell
pip install -r requirements-dev.txt
pytest
```

Run `sonar-scanner` manually from the repository root:

```powershell
sonar-scanner `
  -Dsonar.host.url=http://localhost:9000 `
  -Dsonar.token=<your-sonarqube-token>
```

Stop the local SonarQube stack:

```powershell
docker compose -f docker-compose.sonarqube.yml down
```

Suggested Quality Gate:

- Blocker issues: `0`
- Critical issues: `0`
- Coverage: greater than `80%`
- Duplicated lines: less than `3%`
- Maintainability rating: `A`
- Reliability rating: `A`
- Security rating: `A`

In GitLab CI, set `SONAR_HOST_URL` and `SONAR_TOKEN` as CI/CD variables to enable the `quality:sonarqube` job. The `test:pytest` job publishes `coverage.xml`, and the SonarQube job imports it during analysis.

## Recommended Branch Protection

- Require merge request pipelines to pass before merge.
- Protect the default branch.
- Require approvals for production deployment changes.
- Keep `deploy:production` as a manual job unless your release process is fully automated.

## Reports

Pipeline artifacts are retained for security review:

- `gl-secret-detection-report.json`
- `semgrep-report.json`
- `trivy-fs-report.json`
- `checkov-report.json`
- `trivy-container-report.json`
- `sbom.cdx.json`
- `sbom.spdx.json`
- `zap-report.json`
- `zap-report.html`
