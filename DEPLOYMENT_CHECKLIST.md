# Pre-Deployment Checklist for Render

## ✅ Configuration Files
- [x] **Procfile** - Created ✓
- [x] **runtime.txt** - Created ✓
- [x] **requirements.txt** - Updated with gunicorn ✓
- [x] **.gitignore** - Exists ✓
- [x] **app.py** - Updated with dynamic port support ✓

## 📋 Before You Deploy

### Step 1: Verify Your .env File
Ensure these variables exist locally:
- [ ] `GOOGLE_API_KEY` - Your Google Places API key
- [ ] `GEMINI_API_KEY` - Your Gemini API key
- [ ] `FLASK_SECRET_KEY` - Your Flask secret key

**Note**: Never push `.env` to GitHub!

### Step 2: Test Locally
Run this command to test your app locally:
```bash
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:5000` to verify everything works.

### Step 3: Commit Your Code
```bash
git add .
git commit -m "Prepare for Render deployment"
```

### Step 4: Push to GitHub
```bash
git push origin main
```

## 🚀 Deploy on Render

1. Go to https://render.com
2. Sign up/Login
3. Click **New +** → **Web Service**
4. Connect your GitHub repository
5. Fill in deployment settings:
   - **Service Name**: documentation-pathway
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Add Environment Variables (from your `.env`):
   - GOOGLE_API_KEY
   - GEMINI_API_KEY
   - FLASK_SECRET_KEY
7. Click **Create Web Service**

## 📊 Deployment Status

| Item | Status |
|------|--------|
| Files created | ✅ |
| Code ready | ⏳ *Wait for user* |
| GitHub repo | ⏳ *Wait for user* |
| Render deployment | ⏳ *Wait for user* |

---

**Need help?** Refer to `RENDER_DEPLOYMENT.md` for detailed instructions!
