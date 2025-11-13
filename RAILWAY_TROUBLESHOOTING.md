# 🔧 Railway 502 Error Troubleshooting

## Current Issue: 502 Bad Gateway

Your Railway deployment is returning **502 Bad Gateway**, which means the app is crashing on startup.

---

## Step 1: Check Railway Logs

**In Railway Dashboard:**
1. Go to your project → **Deployments** tab
2. Click on the **latest deployment**
3. Check **"Logs"** tab
4. Look for **error messages** (usually in red)

**Common errors you might see:**
- `ModuleNotFoundError` → Missing dependency
- `ValueError` → Missing environment variable
- `ImportError` → Import issue
- `Port already in use` → Port configuration issue

---

## Step 2: Verify Environment Variables

**In Railway Dashboard:**
1. Go to your project → **Variables** tab
2. **Verify these are set:**

```
NETWORK=Preprod
PAYMENT_SERVICE_URL=https://masumi-payment-service-production-50ce.up.railway.app/api/v1
PAYMENT_API_KEY=masumi-payment-c3dhwdu6s88108ndrr2hq30p
AGENT_IDENTIFIER=addr_test1qzqk05tzfae6lsc7g7rgzqyk75lj5ngjtddfxjk6u0d30lke3xg47jd76hw5d92w2p05dxw0wyj5djvwr3krjcfr05gswlj65x
PAYMENT_AMOUNT=10000000
PAYMENT_UNIT=lovelace
OPENAI_API_KEY=your_actual_openai_key
```

**Important:** Railway sets `PORT` automatically - **don't add it manually**

---

## Step 3: Check Build Logs

**In Railway Dashboard:**
1. Go to **Deployments** → Latest deployment
2. Check **"Build Logs"**
3. Look for:
   - ✅ `Successfully installed...` → Dependencies installed
   - ❌ `ERROR: Could not find...` → Missing dependency
   - ❌ `ModuleNotFoundError` → Package not in requirements.txt

---

## Step 4: Common Fixes

### Fix 1: Missing Dependencies
**If you see `ModuleNotFoundError`:**
```bash
# Add missing package to requirements.txt
# Then commit and push:
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

### Fix 2: Missing Environment Variables
**If you see `ValueError` or `KeyError`:**
- Add missing variables in Railway → Variables tab
- Redeploy (Railway auto-redeploys when vars change)

### Fix 3: Port Configuration
**If you see port errors:**
- Railway sets `PORT` automatically
- Don't add `PORT` to environment variables
- Procfile should use `$PORT` (already correct)

### Fix 4: Python Version
**If build fails:**
- Check `runtime.txt` has correct Python version
- Should be: `python-3.11`

---

## Step 5: Test Locally First

**Before deploying, test locally:**
```bash
# Set environment variables
export PORT=8000
export NETWORK=Preprod
export PAYMENT_SERVICE_URL=https://masumi-payment-service-production-50ce.up.railway.app/api/v1
# ... etc

# Run the app
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

**If it works locally but not on Railway:**
- Check environment variables are set correctly
- Check Railway logs for specific errors

---

## Step 6: Redeploy

**After fixing issues:**
1. **Commit fixes:**
   ```bash
   git add .
   git commit -m "Fix Railway deployment issues"
   git push
   ```

2. **Railway will auto-redeploy** (or manually trigger redeploy)

3. **Check logs again** to verify it's working

---

## Quick Diagnostic Commands

**Check if Railway URL is accessible:**
```bash
curl https://rdm-masumi-agent-production.up.railway.app/health
```

**Expected response:**
```json
{"status": "ok"}
```

**If you get 502:**
- Check Railway logs (most important!)
- Verify environment variables
- Check build logs for errors

---

## Still Not Working?

1. **Share Railway logs** (from Deployments → Logs)
2. **Check these common issues:**
   - Missing `requirements.txt` dependencies
   - Incorrect environment variable names
   - Python version mismatch
   - Import errors in code

3. **Try redeploying from scratch:**
   - Delete Railway project
   - Create new project
   - Connect GitHub repo
   - Add environment variables
   - Deploy

---

## Success Checklist

- [ ] Railway deployment shows "Active" (not "Failed")
- [ ] Logs show "Application startup complete"
- [ ] `/health` endpoint returns `{"status": "ok"}`
- [ ] No errors in Railway logs
- [ ] Environment variables are all set

