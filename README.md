<<<<<<< HEAD
# FitNutriBuddy 🏋️‍♂️🥗
**AI-powered personalized fitness and nutrition assistant**
Built with Django + Anthropic Claude, deployable on IBM Cloud.

---

## Project Structure
```
fitnutribuddy/
├── fitnutribuddy/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/                  # REST API app
│   ├── views.py          # All AI endpoints
│   └── urls.py
├── templates/
│   └── index.html        # Full frontend UI
├── static/               # Static assets (CSS/JS if separated)
├── requirements.txt
├── manage.py
├── Procfile              # IBM Cloud Foundry
├── manifest.yml          # IBM Cloud Foundry config
├── runtime.txt           # Python version
└── .env.example          # Environment variables template
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | Conversational AI with profile context |
| POST | `/api/generate-plan/` | Generate one plan section |
| POST | `/api/generate-all/` | Generate all 6 plans at once |
| GET  | `/api/health/` | Health check |

---

## Local Setup

### 1. Clone and install dependencies
```bash
cd fitnutribuddy
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY and DJANGO_SECRET_KEY
```

### 3. Collect static files
```bash
python manage.py collectstatic --noinput
```

### 4. Run locally
```bash
python manage.py runserver
# Open http://localhost:8000
```

---

## Deploy to IBM Cloud (Cloud Foundry)

### 1. Install IBM Cloud CLI
```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
ibmcloud login
ibmcloud target --cf
```

### 2. Edit manifest.yml
Replace the placeholder values:
- `ANTHROPIC_API_KEY` → your actual Anthropic key
- `DJANGO_SECRET_KEY` → a random 50-char secret string

### 3. Collect static files first
```bash
python manage.py collectstatic --noinput
```

### 4. Deploy
```bash
ibmcloud cf push
```

Your app will be live at:
`https://fitnutribuddy.mybluemix.net`

---

## Deploy to IBM Code Engine (Container)

### 1. Build Docker image
```bash
docker build -t fitnutribuddy .
docker tag fitnutribuddy us.icr.io/YOUR_NAMESPACE/fitnutribuddy
docker push us.icr.io/YOUR_NAMESPACE/fitnutribuddy
```

### 2. Deploy via IBM Cloud console
- Go to Code Engine → Create Application
- Point to your container image
- Set environment variables (ANTHROPIC_API_KEY, DJANGO_SECRET_KEY)

---

## Generate a Django Secret Key
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
=======
# FitNutriBuddy-
>>>>>>> d5b96aeca39b58b3a29d7f5c20e0ef83de192147
