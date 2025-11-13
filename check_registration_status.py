#!/usr/bin/env python3
"""
Check Masumi Agent Registration Status
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def check_registration_status():
    """Check if agent is registered with Masumi"""
    payment_service_url = os.getenv("PAYMENT_SERVICE_URL")
    payment_api_key = os.getenv("PAYMENT_API_KEY")
    agent_identifier = os.getenv("AGENT_IDENTIFIER")
    
    print("=" * 70)
    print("Checking Masumi Agent Registration Status")
    print("=" * 70)
    print(f"Agent Identifier: {agent_identifier[:30]}...{agent_identifier[-10:]}")
    print(f"Payment Service: {payment_service_url}")
    print()
    
    # Note: This requires the wallet vkey, not the address
    # The registration status check needs the wallet verification key
    print("⚠️  Note: Registration status check requires wallet vkey")
    print("   Check your Masumi dashboard for registration status")
    print()
    print("If status is 'pending', possible reasons:")
    print("  1. Waiting for blockchain confirmation (wait 5-10 minutes)")
    print("  2. API URL not accessible (localhost won't work)")
    print("  3. Need to update API URL to public URL (Railway)")
    print()
    print("To fix:")
    print("  1. Update agent registration in Masumi dashboard")
    print("  2. Change API URL to: https://rdm-masumi-agent-production.up.railway.app")
    print("  3. Save and wait for confirmation")

if __name__ == "__main__":
    asyncio.run(check_registration_status())

