# ✅ Masumi Dashboard Checklist

## What to Do in Masumi Dashboard

### 1. ✅ Agent Registration (Already Done)
- [x] Agent registered: "RDM Goal Accountability Agent"
- [x] Linked wallet: Your selling wallet (ends in `j65x`)
- [ ] **Status**: Currently "Pending" → Need to fix below

### 2. 🔧 Fix Pending Status

**Option A: Use Public URL (Recommended for Transactions)**
- [ ] Go to: **AI Agents** → Your agent → **Edit**
- [ ] Change **API URL** from `http://127.0.0.1:8000` to:
  - `https://rdm-masumi-agent-production.up.railway.app` (Railway)
  - OR your deployed public URL
- [ ] **Save/Update**
- [ ] Wait 5-15 minutes for confirmation
- [ ] Status should change: **Pending** → **Active/Confirmed**

**Option B: Continue Local (No Masumi Transactions)**
- [ ] Keep `http://127.0.0.1:8000` (localhost)
- [ ] Use `/test_create_goal` endpoint for testing
- [ ] Agents work, but no transactions in Masumi dashboard

### 3. ✅ Verify Required Fields

- [ ] **Name**: RDM Goal Accountability Agent
- [ ] **Description**: AI-powered goal-setting and accountability system
- [ ] **API URL**: Public URL (not localhost) OR localhost for testing
- [ ] **Linked Wallet**: Your selling wallet address
- [ ] **Prices**: Set to `10` ADA (not 0.00)
- [ ] **Tags**: Add at least one tag:
  - `goal-setting`
  - `accountability`
  - `SDG`
  - `sustainability`
  - `tokens`

### 4. 📊 After Confirmation

Once status is **Active/Confirmed**:
- [ ] Go to: **Transactions** tab
- [ ] Create a goal via your web interface (`/start_job`)
- [ ] Payment request should appear in Transactions
- [ ] Complete payment in Masumi dashboard
- [ ] Goal will be created automatically

### 5. 🔍 Check Your Agent

- [ ] Go to: **AI Agents** → Your agent
- [ ] Verify all details are correct
- [ ] Check status is **Active** (not Pending)
- [ ] Verify API endpoints are accessible:
  - `/health` → Should return `{"status": "ok"}`
  - `/availability` → Should return availability status
  - `/input_schema` → Should return RDM schema

---

## Current Status

- ✅ Agent registered in Masumi
- ⏳ Status: **Pending** (waiting for API verification)
- 🔧 Action needed: Update API URL to public URL OR continue with localhost

---

## Quick Commands

**Check if Railway is running:**
```bash
curl https://rdm-masumi-agent-production.up.railway.app/health
```

**Check local API:**
```bash
curl http://127.0.0.1:8000/health
```

**Test agent endpoints:**
```bash
curl http://127.0.0.1:8000/availability
curl http://127.0.0.1:8000/input_schema
curl http://127.0.0.1:8000/agent_metadata
```

