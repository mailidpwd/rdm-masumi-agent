# 🚀 Deploy to Railway - Step by Step Guide

## Prerequisites
- GitHub account
- Railway account (free tier available)
- Your code pushed to GitHub

---

## Step 1: Push Code to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - RDM Masumi Agent"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Create a new repository (e.g., `rdm-masumi-agent`)
   - **Don't** initialize with README

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/rdm-masumi-agent.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 2: Deploy to Railway

### Option A: Deploy via Railway Dashboard (Easiest)

1. **Go to Railway**: https://railway.app
2. **Sign in** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Select your repository** (`rdm-masumi-agent`)
6. **Railway will auto-detect** Python and deploy

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Initialize Railway**:
   ```bash
   railway init
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

---

## Step 3: Configure Environment Variables

**In Railway Dashboard:**

1. Go to your project → **Variables** tab
2. **Add these environment variables**:

```
NETWORK=Preprod
PAYMENT_SERVICE_URL=https://masumi-payment-service-production-50ce.up.railway.app/api/v1
PAYMENT_API_KEY=masumi-payment-c3dhwdu6s88108ndrr2hq30p
AGENT_IDENTIFIER=addr_test1qzqk05tzfae6lsc7g7rgzqyk75lj5ngjtddfxjk6u0d30lke3xg47jd76hw5d92w2p05dxw0wyj5djvwr3krjcfr05gswlj65x
PAYMENT_AMOUNT=10000000
PAYMENT_UNIT=lovelace
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here (optional)
BLOCKFROST_PREPROD_KEY=your_blockfrost_key_here (optional)
```

3. **Click "Deploy"** or Railway will auto-deploy

---

## Step 4: Get Your Railway URL

1. **Go to your project** in Railway dashboard
2. **Click on your service**
3. **Go to "Settings"** tab
4. **Find "Generate Domain"** or check **"Public URL"**
5. **Copy the URL** (e.g., `https://rdm-masumi-agent-production.up.railway.app`)

---

## Step 5: Update Masumi Dashboard

1. **Go to Masumi Dashboard** → **AI Agents**
2. **Click on your agent** → **Edit**
3. **Update API URL** to your Railway URL:
   - Example: `https://rdm-masumi-agent-production.up.railway.app`
4. **Save/Update**
5. **Wait 5-15 minutes** for status to change: **Pending** → **Active**

---

## Step 6: Verify Deployment

**Test your Railway deployment:**

```bash
# Health check
curl https://YOUR_RAILWAY_URL/health

# Should return: {"status": "ok"}

# Availability check
curl https://YOUR_RAILWAY_URL/availability

# Input schema
curl https://YOUR_RAILWAY_URL/input_schema
```

---

## Step 7: Test Transactions

1. **Create a goal** via your web interface
2. **Use Railway URL** in `rdm_web_interface.html`:
   ```javascript
   const API_BASE_URL = "https://YOUR_RAILWAY_URL";
   ```
3. **Go to Masumi Dashboard** → **Transactions**
4. **Payment request should appear** there!

---

## Troubleshooting

### Deployment Fails
- Check **Build Logs** in Railway dashboard
- Verify all **environment variables** are set
- Check **requirements.txt** has all dependencies

### Health Check Fails
- Check **Deployment Logs** in Railway
- Verify **PORT** environment variable (Railway sets this automatically)
- Check if **uvicorn** is starting correctly

### API Not Accessible
- Verify **Public URL** is generated in Railway Settings
- Check **Deployment Status** is "Active"
- Try accessing `/health` endpoint

### Masumi Still Shows Pending
- Verify Railway URL is **publicly accessible**
- Check Railway deployment is **running**
- Wait 5-15 minutes after updating API URL
- Verify all **environment variables** are set correctly

---

## Quick Commands

**Check Railway deployment:**
```bash
railway status
railway logs
```

**View environment variables:**
```bash
railway variables
```

**Redeploy:**
```bash
railway up
```

---

## Cost

**Railway Free Tier:**
- $5 free credit per month
- Perfect for testing and development
- Auto-sleeps after inactivity (wakes on request)

**For Production:**
- Consider Railway Pro ($20/month) for always-on
- Or use other platforms (Render, Fly.io, etc.)

---

## Next Steps

After deployment:
1. ✅ Update Masumi API URL
2. ✅ Wait for confirmation (5-15 min)
3. ✅ Test creating goals
4. ✅ Check Transactions in Masumi dashboard
5. ✅ Complete payments and see tokens flow!

