# Complete Guide: How to Host & Make the AI-SGC System Live

This guide provides **three simple, 100% free methods** to host and make your project accessible over the internet for college reviews, viva presentations, or live demonstrations.

---

## Method 1: Instant 2-Minute Public URL (Zero Cloud Accounts Needed)
> **Best for**: Live presentation in college, viva review, or showing your project to professors on their mobile phones/laptops immediately.

You can expose your running local project to the internet using **Cloudflare Tunnel** (recommended) or **LocalTunnel**.

### Steps Using Cloudflare Tunnel (Free & No Signup Required)

1. **Start the backend and frontend locally** (Terminal 1 & Terminal 2 or using `run_backend.bat` and `run_frontend.bat`).
2. Open a new Command Prompt (`cmd.exe`) and run:
   ```cmd
   npx cloudflared tunnel --url http://localhost:5173
   ```
3. Cloudflare will immediately generate a public HTTPS URL like:
   ```text
   https://random-words-college.trycloudflare.com
   ```
4. **Anyone in the world** can open that URL in their browser or smartphone to use your full live application!

---

## Method 2: Permanent Free Cloud Hosting (Render + Vercel)
> **Best for**: Keeping the project permanently live on the internet with public URLs (e.g. on your resume or portfolio).

### Part A: Deploy the Backend on Render.com (100% Free)

1. Push your project code to a **GitHub repository** (e.g., `github.com/your-username/AI-SGC-system`).
2. Sign up or log into [Render.com](https://render.com/) with GitHub.
3. Click **New +** $\to$ **Web Service**.
4. Select your GitHub repository.
5. Configure the following settings:
   - **Name**: `ai-sgc-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python -m app.ml.train && python scripts/seed_demo_data.py
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`
6. Click **Create Web Service**.
7. Render will build the environment, train the model, seed the database, and provide your public backend URL:
   ```text
   https://ai-sgc-backend.onrender.com
   ```
   (Verify by opening `https://ai-sgc-backend.onrender.com/docs` in your browser).

---

### Part B: Deploy the Frontend on Vercel (100% Free)

1. Sign up or log into [Vercel.com](https://vercel.com/) with GitHub.
2. Click **Add New...** $\to$ **Project**.
3. Import your GitHub repository.
4. Configure the settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click "Edit" and choose `frontend`.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Under **Environment Variables**, add:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://ai-sgc-backend.onrender.com` *(Replace with your Render backend URL from Part A)*
6. Click **Deploy**.
7. In ~30 seconds, Vercel will give you a live production URL:
   ```text
   https://ai-sgc-system.vercel.app
   ```

Now your frontend and backend are both live in the cloud 24/7!

---

## Method 3: Deploy on Railway.app

1. Sign up on [Railway.app](https://railway.app/).
2. Click **New Project** $\to$ **Deploy from GitHub Repo**.
3. Select your repository.
4. Set the Root Directory to `/backend`.
5. Railway will automatically detect the [Procfile](file:///c:/Users/koneAjay/OneDrive/Desktop/AI-SGC-system/backend/Procfile) and launch the FastAPI server.
6. Generate a domain in Railway project settings, then deploy the frontend on Vercel pointing to that Railway domain.

---

## Pre-Configured Deployment Files Included in the Project

The following configuration files have already been created and prepared in your project:

1. [`render.yaml`](file:///c:/Users/koneAjay/OneDrive/Desktop/AI-SGC-system/render.yaml): Render blueprint for automated deployment.
2. [`frontend/vercel.json`](file:///c:/Users/koneAjay/OneDrive/Desktop/AI-SGC-system/frontend/vercel.json): Vercel configuration ensuring client-side single-page routing works smoothly.
3. [`backend/Procfile`](file:///c:/Users/koneAjay/OneDrive/Desktop/AI-SGC-system/backend/Procfile): Procfile for Railway and Heroku.
4. [`frontend/src/services/api.ts`](file:///c:/Users/koneAjay/OneDrive/Desktop/AI-SGC-system/frontend/src/services/api.ts): Updated to support `VITE_API_BASE_URL` environment variable dynamically.
