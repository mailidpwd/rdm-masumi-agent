# 🎯 RDM SYSTEM - QUICK REFERENCE CARD

## 📖 **What You Built**

**Two AI Agents for Goal Accountability:**

### **Agent 1**: Goal-Setting & Pledge Manager
- Sets meaningful goals (SDG/ESG aligned)
- Manages 100 RDM token pledges
- Tracks daily/weekly reflections
- Prepares data for Agent 2

### **Agent 2**: Veritas - The Judge
- Verifies goal completion
- Distributes tokens fairly:
  - SUCCESS (80-100%): 100% to Reward
  - PARTIAL (60%): 60% Reward, 40% Remorse
  - FAILURE (0-39%): 100% to Remorse
- Awards bonus tokens
- Assigns achievement badges

---

## 🔌 **Your Connected Systems**

```
Your Lace Wallet (1,000 tADA) 
         ↓
Blockfrost API (Blockchain data)
         ↓
Masumi Payment (Railway cloud)
         ↓
Your RDM API Server (Port 8000)
         ↓
Agent 1 → Agent 2
         ↓
Tokens back to your wallet!
```

---

## 🚀 **Start Commands**

### Test Agents (No server needed):
```powershell
cd C:\Users\Michael\Desktop\WorkSpace\crewai-masumi-quickstart-template
.\test_agents_only.ps1
```

### Start API Server:
```powershell
cd C:\Users\Michael\Desktop\WorkSpace\crewai-masumi-quickstart-template
.\start_rdm_server.ps1
```

### Test Wallet:
```powershell
.\.venv311\Scripts\python.exe test_wallet_connection.py
```

---

## 📝 **Your Setup**

```
✅ Agent 1: rdm_agents.py (RDMAgentSystem)
✅ Agent 2: rdm_agents.py (VeritasAgent)
✅ API: main.py (8 endpoints)
✅ Wallet: Lace Preprod (1,000 tADA)
✅ Blockchain: Cardano Preprod
✅ AI: Gemini 2.5 Flash
✅ Payment: Masumi Railway
```

---

## 🎯 **Token Example**

**Goal**: Reduce plastic 80% (100 RDM pledge)  
**Result**: 85% achieved (SUCCESS)

**Distribution:**
- Reward: 100 RDM → Your wallet ✅
- Remorse: 0 RDM
- Bonus: +5 RDM
- **Total: 105 RDM received! 🎉**

---

## 📚 **Documentation**

- **`RDM_SYSTEM_README.md`** - Complete system guide
- **`QUICK_REFERENCE.md`** - This file
- **`SIMPLE_START_GUIDE.md`** - How to start
- **`MASUMI_RDM_INTEGRATION.md`** - Masumi details

---

**Everything is ready! Just waiting for Gemini API to be less busy!** 🚀

