# 🚀 SIMPLE START GUIDE - RDM System

## ✅ YOUR CONFIGURATION IS COMPLETE!

Everything is ready. Here's how to start and test.

---

## 🎯 **METHOD 1: Double-Click to Start (Easiest)**

1. Go to folder: `C:\Users\Michael\Desktop\WorkSpace\crewai-masumi-quickstart-template`
2. **Double-click**: `start_server.bat`
3. Server starts automatically!
4. Keep window open while using

---

## 🎯 **METHOD 2: PowerShell Commands**

### Step 1: Open PowerShell

Right-click in the `crewai-masumi-quickstart-template` folder and select "Open in Terminal"

### Step 2: Run This EXACT Command:

```powershell
.\.venv311\Scripts\python.exe main.py api
```

**Server will start and show:**
```
======================================================================
Starting FastAPI server with Masumi integration...
======================================================================
API Documentation:        http://127.0.0.1:8000/docs
Availability Check:       http://127.0.0.1:8000/availability
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**DON'T CLOSE THIS WINDOW!** Server needs to stay running.

### Step 3: Open Browser

While server is running, open:
```
http://127.0.0.1:8000/docs
```

You'll see all your RDM API endpoints!

---

## 🧪 **METHOD 3: Test Without Starting Server**

Test your agents directly (no API server needed):

```powershell
.\.venv311\Scripts\python.exe rdm_agents.py full-flow
```

This runs Agent 1 + Agent 2 complete cycle!

---

## ✅ **WHAT'S CONFIGURED:**

```
✅ Lace Wallet: addr_test1qp2sp3z5g42whd...gnyst5ld8z
✅ Network: Preprod (1,000 tADA)
✅ Payment Service: Railway (Cloud)
✅ Blockfrost: Preprod key configured
✅ Agent 1: Goal-setting & Pledge
✅ Agent 2: Veritas (Verification & Distribution)
✅ Gemini 2.5 Flash: AI model
```

---

## 🎯 **RECOMMENDED: Test Agents First (No Server Needed)**

Run this command in PowerShell:

```powershell
cd C:\Users\Michael\Desktop\WorkSpace\crewai-masumi-quickstart-template
.\.venv311\Scripts\python.exe rdm_agents.py full-flow
```

**This will:**
1. ✅ Run Agent 1 (Goal creation + Pledge)
2. ✅ Run Agent 2 (Verification + Token distribution)
3. ✅ Show complete flow with results
4. ✅ Takes 2-3 minutes

**No server needed for this test!**

---

## 📊 **IF YOU WANT API SERVER:**

### Terminal 1 (Server):
```powershell
cd C:\Users\Michael\Desktop\WorkSpace\crewai-masumi-quickstart-template
.\.venv311\Scripts\python.exe main.py api
```
**Leave running!**

### Browser:
Open: `http://127.0.0.1:8000/docs`

### Terminal 2 (Testing):
Open NEW PowerShell window:
```powershell
cd C:\Users\Michael\Desktop\WorkSpace\crewai-masumi-quickstart-template
.\.venv311\Scripts\python.exe test_masumi_rdm_integration.py quick
```

---

## ✅ **QUICK START COMMANDS:**

Copy and paste these ONE AT A TIME:

```powershell
# 1. Go to project folder
cd C:\Users\Michael\Desktop\WorkSpace\crewai-masumi-quickstart-template

# 2. Test agents (standalone - no server needed)
.\.venv311\Scripts\python.exe rdm_agents.py full-flow

# 3. OR start API server
.\.venv311\Scripts\python.exe main.py api
```

---

**Which method do you want to try first?**
1. **Easiest**: Double-click `start_server.bat`
2. **Direct test**: Run agents without server
3. **Full API**: Start server + test endpoints

**Your system is 100% ready! Just choose how you want to run it! 🚀**


