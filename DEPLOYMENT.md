# Deployment Guide

This project is a Django application called **FitNutriBuddy** that integrates with IBM Watsonx.ai models (`ibm/granite-3-8b-instruct` and `meta-llama/llama-3-2-11b-vision-instruct`).

## Local Setup & Testing

Before deploying, ensure the application runs successfully in your local environment.

1. **Activate Virtual Environment**:
   ```powershell
   # On Windows:
   .venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Verify Watsonx Credentials**:
   Run the quick integration test script:
   ```powershell
   python test_watsonx.py
   ```
4. **Run Server Locally**:
   ```powershell
   python manage.py runserver
   ```
   Access the app at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Deployment to IBM Cloud (IBM Code Engine)

> **Notice**: IBM Cloud Foundry is deprecated. The recommended path is **IBM Code Engine**, which is a managed serverless container service.

### Option A: Build and Deploy from Github (Recommended - No local Docker required)

If your project is pushed to a Github repository, you can build and run it directly in Code Engine:

1. Log in to the [IBM Cloud Console](https://cloud.ibm.com/).
2. Go to **Code Engine** and create a **Project**.
3. Under the project page, go to **Applications** -> click **Create**.
4. Configure application details:
   - **Name**: `fitnutribuddy`
   - **Choose how to run your code**: Select **Source code**.
   - **Repository URL**: Paste your GitHub repository URL.
   - **Build Strategy**: Select **Dockerfile**.
5. Add the environment variables from your `.env` file under **Environment variables (optional)**:
   - `WATSONX_APIKEY` = *[Your Watsonx API Key]*
   - `WATSONX_PROJECT_ID` = *[Your Watsonx Project ID]*
   - `WATSONX_URL` = `https://au-syd.ml.cloud.ibm.com` (or other appropriate region URL)
   - `DJANGO_SECRET_KEY` = *[A unique Django secret key]*
   - `DEBUG` = `False`
6. Click **Create** to compile and launch. Code Engine will deploy your application and expose a secure HTTPS endpoint.

### Option B: Deploy using Docker CLI (Local Build)

If you prefer building the image locally and pushing it to IBM Container Registry (ICR):

1. **Log in to IBM Cloud CLI**:
   ```powershell
   ibmcloud login
   ibmcloud target -g Default
   ```
2. **Log in to Container Registry**:
   ```powershell
   ibmcloud cr login
   ```
3. **Build the container image**:
   ```powershell
   docker build -t fitnutribuddy .
   ```
4. **Tag & Push to ICR Namespace**:
   ```powershell
   # Replace <your_namespace> with your registry namespace
   docker tag fitnutribuddy us.icr.io/<your_namespace>/fitnutribuddy:latest
   docker push us.icr.io/<your_namespace>/fitnutribuddy:latest
   ```
5. **Launch in Code Engine**:
   ```powershell
   ibmcloud ce app create --name fitnutribuddy --image us.icr.io/<your_namespace>/fitnutribuddy:latest --env WATSONX_APIKEY=<api_key> --env WATSONX_PROJECT_ID=<project_id> --env WATSONX_URL=https://au-syd.ml.cloud.ibm.com --env DJANGO_SECRET_KEY=<secret_key> --env DEBUG=False
   ```
