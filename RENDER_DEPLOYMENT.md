# Render Deployment Guide for Documentation Pathway

## Prerequisites
- GitHub account (to host your code)
- Render account (https://render.com - free tier available)
- Git installed on your machine

---

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit - prepare for Render deployment"
```

### 1.2 Create/Update .gitignore
Ensure your `.gitignore` includes:
```
.env
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
venv/
```

**Important**: Never commit `.env` file to GitHub! Your API keys must be added to Render's environment variables.

---

## Step 2: Push to GitHub

1. Create a new repository on GitHub (https://github.com/new)
2. Add remote and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/documentation-pathway.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy on Render

### 3.1 Connect GitHub to Render
1. Go to https://render.com
2. Sign up or log in
3. Click **New +** and select **Web Service**
4. Click **Connect** and authorize GitHub
5. Search for and select your `documentation-pathway` repository
6. Click **Connect**

### 3.2 Configure Your Service

Fill in the following details:

| Field | Value |
|-------|-------|
| **Name** | documentation-pathway |
| **Environment** | Python 3 |
| **Region** | Choose closest to you |
| **Branch** | main |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

### 3.3 Add Environment Variables

1. Scroll down to **Environment** section
2. Add the following variables (from your `.env` file):

| Key | Value |
|-----|-------|
| `GOOGLE_API_KEY` | Your Google Places API Key |
| `GEMINI_API_KEY` | Your Gemini API Key |
| `FLASK_SECRET_KEY` | Your Flask secret key |

3. Click **Create Web Service**

---

## Step 4: Monitor Deployment

- Render will automatically:
  - Build your Python environment
  - Install dependencies from `requirements.txt`
  - Start your app with the command in `Procfile`
  
- Check the **Logs** tab to monitor progress
- Your app will be live at: `https://documentation-pathway.onrender.com` (URL shown on dashboard)

---

## Step 5: Update Your App in Future

1. Make changes locally
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Update feature XYZ"
git push origin main
```

3. Render will **automatically redeploy** when you push to GitHub!

---

## Troubleshooting

### Build Fails
- Check **Build Logs** for errors
- Ensure `requirements.txt` is correct
- Verify `Procfile` has correct format

### App Crashes After Deployment
- Check **Runtime Logs**
- Verify all environment variables are set
- Ensure API keys are valid
- Check that `app.py` runs locally first

### "Port Already in Use" Error
- Render automatically assigns ports
- Your app should use: `PORT = os.getenv('PORT', 5000)`
- Update your `app.py` if needed

### Still Having Issues?
```python
# Add this to your app.py to handle dynamic port:
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

---

## Files Created for Deployment

✅ `Procfile` - Tells Render how to start your app
✅ `runtime.txt` - Specifies Python version
✅ Updated `requirements.txt` - Added gunicorn (web server)

---

## Free Tier Limitations (Render)

- **Auto-sleep**: App sleeps after 15 min of inactivity (wake up on request)
- **Bandwidth**: 100 GB/month
- **Upgrade available**: For persistent hosting without sleep

---

## Next Steps

1. Push code to GitHub
2. Create Render account and connect GitHub
3. Deploy following **Step 3** above
4. Test your live application
5. Share your deployed URL!

**Happy Deploying! 🚀**
