# 🚀 How to Host masterSchetan CCIE Online 100% Free (Permanent URL)

## 📌 Why Streamlit Community Cloud (NOT Firebase)?

1. **Firebase Hosting is ONLY for static websites (HTML/JS) or Node.js.**
   - Firebase **cannot** run Python code, `yfinance`, or pandas natively.
   - Firebase free tier has strict transfer limits (360 MB/day).
2. **Streamlit Community Cloud is 100% FREE & built specifically for Python apps.**
   - Hosted directly by Streamlit on Google Cloud infrastructure.
   - **Cost:** ₹0 / Month forever.
   - **Persistence:** Runs 24/7 online even when your PC is turned off.
   - **URL:** Gives you a permanent clean URL like `https://masterschetan-ccie.streamlit.app`.

---

## ⚡ 3-Step Deployment Instructions (Takes 3 Minutes)

### Step 1: Push Code to GitHub
1. Go to [github.com/new](https://github.com/new) and log into your GitHub account.
2. Create a new repository named `masterSchetan-CCIE` (set it to Public or Private).
3. Open your terminal in `C:\Users\HP\Desktop\MF Analyiser\masterSchetan_CCIE` and run:
   ```bash
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/masterSchetan-CCIE.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Connect to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **"New App"** (or **"Deploy an app"**).
3. Select your repository: `masterSchetan-CCIE`
4. Set Main file path: `app.py`

---

### Step 3: Add API Keys to Streamlit Secrets
1. Before clicking Deploy, click **"Advanced Settings..."** (or **Secrets** in app settings).
2. Add your Gemini API key:
   ```toml
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   ```
3. Click **"Deploy!"**

🎉 **Done! Your app will be live 24/7 at `https://masterschetan-ccie.streamlit.app` accessible to anyone on the internet!**
