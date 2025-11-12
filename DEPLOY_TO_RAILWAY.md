# 🚂 Deploy RDM Agent System to Railway

This guide shows you how to deploy your RDM Agent System to Railway (or similar platforms).

---

## 📋 **Prerequisites**

Before deploying, make sure you have:

- ✅ **Gemini API Key** from https://aistudio.google.com/app/apikey
- ✅ **Lace Wallet Address** (Preprod testnet)
- ✅ **Blockfrost API Key** (Preprod) from https://blockfrost.io/dashboard
- ✅ **Masumi Payment Service URL** (Railway deployment)
- ✅ **GitHub Account** with your code pushed

---

## 🚀 **Step 1: Deploy to Railway**

### Option A: Deploy from GitHub

1. **Go to Railway**: https://railway.app
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your repository**: `mailidpwd/rdm-masumi-agent`
5. **Wait for initial deployment** (it will fail - that's expected!)

### Option B: Deploy with Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

---

## ⚙️ **Step 2: Configure Environment Variables**

Railway doesn't have access to your `.env` file. You need to add environment variables manually.

### In Railway Dashboard:

1. **Go to your project**: https://railway.app/project/[your-project-id]
2. **Click your service** (the one that's failing)
3. **Click "Variables" tab**
4. **Add each variable below** (click "+ New Variable" for each):

### Required Variables:

```bash
# ===== AI CONFIGURATION =====
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ===== WALLET CONFIGURATION =====
SELLER_VKEY=addr_test1qp2sp3z5g42whd0hzwkw2hy367ywt6n45j4yfjacmnkuy8e2swzfgw07e8tf33w70h8x76swtknfkzkgc80z50ytgnyst5ld8z

# ===== MASUMI PAYMENT SERVICE =====
PAYMENT_SERVICE_URL=https://masumi-payment-service-production-50ce.up.railway.app
PAYMENT_API_KEY=local-dev-key-CHANGE-IN-PRODUCTION

# ===== BLOCKFROST API =====
BLOCKFROST_PREPROD_KEY=preprodXXXXXXXXXXXXXXXXXXXXXXXXXXXX
BLOCKFROST_API_KEY=preprodXXXXXXXXXXXXXXXXXXXXXXXXXXXX
BLOCKFROST_NETWORK=preprod

# ===== AGENT CONFIGURATION =====
AGENT_IDENTIFIER=rdm-agent-001
NETWORK=preprod
PAYMENT_AMOUNT=1000000
PAYMENT_UNIT=lovelace
```

### How to Add Variables:

1. Copy the variable name (e.g., `GEMINI_API_KEY`)
2. Click "+ New Variable"
3. Paste the name in "Variable Name"
4. Paste your actual value in "Value" (not the placeholder!)
5. Click "Add"
6. Repeat for all variables

---

## 🔄 **Step 3: Redeploy**

After adding all variables:

1. **Click "Deploy"** button in Railway
2. **Wait for build to complete** (watch the logs)
3. **Check for success**: Look for:
   ```
   Starting server on 0.0.0.0:8000
   ```

---

## ✅ **Step 4: Test Your Deployment**

### Get Your Deployment URL:

Railway will give you a URL like:
```
https://rdm-masumi-agent-production-xxxx.up.railway.app
```

### Test Endpoints:

```bash
# Health check
curl https://your-railway-url.up.railway.app/health

# Availability
curl https://your-railway-url.up.railway.app/availability

# Input schema
curl https://your-railway-url.up.railway.app/input_schema

# Agent metadata
curl https://your-railway-url.up.railway.app/agent_metadata
```

---

## 🐛 **Troubleshooting**

### Error: "Missing required configuration parameters"

**Problem**: Environment variables not set

**Solution**:
- Go back to "Variables" tab
- Verify ALL variables are added
- Check for typos in variable names
- Redeploy

### Error: "Google Gen AI native provider not available"

**Problem**: Missing dependencies (we fixed this!)

**Solution**:
- Make sure you pulled latest code with updated `requirements.txt`
- Railway should auto-install `crewai[google-genai]`
- Check build logs for installation errors

### Error: "401 Unauthorized" or "Invalid API Key"

**Problem**: Wrong Gemini API key

**Solution**:
- Get a new key from https://aistudio.google.com/app/apikey
- Update `GEMINI_API_KEY` in Variables
- Redeploy

### Error: "Blockfrost API error"

**Problem**: Wrong Blockfrost key or wrong network

**Solution**:
- Make sure you're using **Preprod** key (not Mainnet)
- Verify `BLOCKFROST_NETWORK=preprod`
- Get new Preprod key from https://blockfrost.io/dashboard

---

## 📊 **Monitoring Your Deployment**

### View Logs:

1. Go to Railway dashboard
2. Click your service
3. Click "Logs" tab
4. Watch for errors or requests

### View Metrics:

1. Click "Metrics" tab
2. See CPU, Memory, Network usage

---

## 🎯 **What to Do After Deployment**

1. **Test all endpoints** with curl or Postman
2. **Register your agent** on Masumi Registry
3. **Update your documentation** with the live URL
4. **Share your agent** with users!

---

## 🔒 **Security Reminders**

- ✅ **NEVER commit `.env`** to GitHub (already protected by `.gitignore`)
- ✅ **Use strong API keys** for production
- ✅ **Change default `PAYMENT_API_KEY`** from `local-dev-key-CHANGE-IN-PRODUCTION`
- ✅ **Use Railway's secret management** for sensitive data
- ✅ **Enable HTTPS** (Railway does this automatically)

---

## 📖 **Additional Resources**

- **Railway Docs**: https://docs.railway.app
- **Masumi Docs**: https://docs.masumi.ai
- **RDM System README**: See `RDM_SYSTEM_README.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`

---

## 🎉 **Success!**

Your RDM Agent System should now be live on Railway!

**Next Steps**:
1. Test with real users
2. Monitor performance
3. Scale as needed

**Your agents are ready to help users achieve their goals! 🚀**

