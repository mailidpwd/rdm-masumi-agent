# 🔥 Connect Your Lace Wallet - SIMPLE GUIDE

## What You Have Right Now ✅
- ✅ Lace Wallet installed
- ✅ 1,000 tADA on Preprod testnet
- ✅ 1,000 tUSDM tokens
- ✅ Payment service running

## What We Need to Do (3 Steps - 5 Minutes)

---

## STEP 1: Get Your Wallet Address (2 minutes)

### Method 1: From Lace Wallet (Easiest)
1. Open your Lace wallet
2. Click the **"Receive"** button (top right, red outline)
3. You'll see your wallet address starting with `addr_test1...`
4. **COPY THIS ADDRESS** - this is your SELLER_VKEY!

### Method 2: Using Browser Console
1. Open your browser with Lace wallet
2. Press **F12** (opens developer tools)
3. Click **Console** tab
4. Copy and paste this code:

```javascript
async function getLaceAddress() {
    const api = await window.cardano.lace.enable();
    const addresses = await api.getUsedAddresses();
    console.log("YOUR WALLET ADDRESS:");
    console.log(addresses[0]);
    return addresses[0];
}

getLaceAddress();
```

5. Press **Enter**
6. **COPY the address that appears**

---

## STEP 2: Update Your .env File (1 minute)

1. Open the `.env` file in your project folder
2. Find this line:
   ```
   SELLER_VKEY=your_selling_wallet_vkey
   ```

3. Replace it with your actual address:
   ```
   SELLER_VKEY=addr_test1qz...YOUR_ACTUAL_ADDRESS_HERE
   ```

4. **SAVE the file** (Ctrl+S)

**Example:**
```ini
# Before:
SELLER_VKEY=your_selling_wallet_vkey

# After (yours will be different):
SELLER_VKEY=addr_test1qz6r9z8c3alyzm7vj9sqnpr5e5n46r9jkmhwu3l4sd8wdq0g5hsxy
```

---

## STEP 3: Register Your Agent (2 minutes)

Now we need to register your wallet as an "agent" on the network.

### Open PowerShell and Run This:

```powershell
# Copy your wallet address from Step 1
$walletAddress = "addr_test1qz...YOUR_ADDRESS_HERE"

# Register the agent
$body = @{
    agentName = "My RDM Agent"
    agentDescription = "Goal tracking with my Lace wallet"
    network = "PREPROD"
    sellingWalletVkey = $walletAddress
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:3001/api/v1/registry" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"; "token"="abcdef_this_should_be_very_secure"} `
    -Body $body

Write-Host "SUCCESS! Your Agent ID:"
Write-Host $response.agentIdentifier
```

**COPY the Agent ID that appears!**

### Update .env Again:

1. Open `.env` file
2. Find this line:
   ```
   AGENT_IDENTIFIER=your_agent_identifier_from_registration
   ```

3. Replace with your Agent ID:
   ```
   AGENT_IDENTIFIER=agent_1234567890abcdef
   ```

4. **SAVE the file** (Ctrl+S)

---

## STEP 4: Test Everything (1 minute)

Run this command:

```bash
python test_wallet_connection.py
```

### You Should See:
```
✅ CONFIGURATION COMPLETE!

Your wallet is ready to use with the RDM Agent System.
```

If you see this, **YOU'RE DONE! 🎉**

---

## NOW USE IT! 🚀

### Try Setting a Goal:
```bash
python rdm_agents.py goal
```

### Test Pledge System:
```bash
python rdm_agents.py pledge
```

### Complete Flow (Agent 1 → Agent 2):
```bash
python rdm_agents.py full-flow
```

---

## Your Final .env Should Look Like This:

```ini
# Payment Service
PAYMENT_SERVICE_URL=http://localhost:3001/api/v1
PAYMENT_API_KEY=abcdef_this_should_be_very_secure

# ⭐ YOUR LACE WALLET
SELLER_VKEY=addr_test1qz...your_actual_address
AGENT_IDENTIFIER=agent_...your_agent_id

# Token Settings
PAYMENT_AMOUNT=100000000
PAYMENT_UNIT=lovelace

# Network
NETWORK=Preprod

# AI
GEMINI_API_KEY=AIzaSyBL_Mw0uwvrv285BnWoQ334XGQZtekB_pE
```

---

## How It Works:

1. **You set a goal** → Pledge 100 RDM tokens (from your 1,000 tADA)
2. **Agent 1 tracks** → Daily check-ins and progress
3. **You complete goal** → Provide evidence
4. **Agent 2 (Veritas) judges** → Fair distribution:
   - ✅ Success (80-100%): 100% to Reward → **You get 100 RDM!**
   - 🔶 Partial (40-79%): Split → **You get 60 RDM, 40 to Remorse**
   - ❌ Failure (0-39%): 100% to Remorse → **You get 0 RDM**
5. **Tokens go to your Lace wallet** → Real blockchain transaction!

---

## Quick Troubleshooting:

❌ **"Wallet not detected"**
→ Make sure Lace wallet is unlocked and on Preprod

❌ **"Agent registration failed"**
→ Check payment service is running: http://localhost:3001/health

❌ **"Wrong network"**
→ Your Lace is already on Preprod ✅ You're good!

---

## That's It! 🎉

**3 Steps:**
1. ✅ Get wallet address from Lace
2. ✅ Update .env with address + agent ID
3. ✅ Test connection

**Then start using:**
```bash
python rdm_agents.py full-flow
```

Your 1,000 tADA on Lace wallet is now connected to the RDM Agent System!

---

**Need help? The test will tell you exactly what's wrong:**
```bash
python test_wallet_connection.py
```

**Ready to go? Start here:**
```bash
python rdm_agents.py goal
```


