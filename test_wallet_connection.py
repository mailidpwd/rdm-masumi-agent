"""
Wallet Connection Test Script for RDM Agent System

This script helps you verify that your wallet is properly configured
and connected to the RDM agent system.
"""

import os
import sys
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()


def check_environment_variables() -> Dict[str, Any]:
    """Check if all required environment variables are set"""
    
    required_vars = {
        "GEMINI_API_KEY": "AI model API key",
        "SELLER_VKEY": "Your wallet verification key",
        "PAYMENT_SERVICE_URL": "Masumi payment service URL",
        "PAYMENT_API_KEY": "Payment service API key",
        "AGENT_IDENTIFIER": "Your registered agent ID",
        "NETWORK": "Blockchain network (Preprod/Mainnet)",
        "PAYMENT_AMOUNT": "Default pledge amount",
        "PAYMENT_UNIT": "Token unit (lovelace)"
    }
    
    results = {}
    all_set = True
    
    print("\n" + "="*70)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("="*70 + "\n")
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        is_set = bool(value and value.strip())
        
        results[var] = {
            "set": is_set,
            "value": value if is_set else None,
            "description": description
        }
        
        status = "✓" if is_set else "✗"
        display_value = ""
        
        if is_set:
            # Mask sensitive values
            if "KEY" in var or "VKEY" in var:
                if len(value) > 20:
                    display_value = f" = {value[:10]}...{value[-10:]}"
                else:
                    display_value = f" = {value[:5]}...{value[-5:]}"
            else:
                display_value = f" = {value}"
        else:
            all_set = False
            display_value = " = ❌ NOT SET"
        
        print(f"  [{status}] {var:<25} {display_value}")
        print(f"      {description}")
        print()
    
    results["all_set"] = all_set
    return results


def test_wallet_configuration(env_results: Dict[str, Any]) -> bool:
    """Test wallet-specific configuration"""
    
    print("\n" + "="*70)
    print("WALLET CONFIGURATION TEST")
    print("="*70 + "\n")
    
    wallet_config_ok = True
    
    # Check SELLER_VKEY
    seller_vkey = os.getenv("SELLER_VKEY")
    if seller_vkey and seller_vkey.strip():
        print("✓ Wallet Verification Key (SELLER_VKEY):")
        print(f"    Length: {len(seller_vkey)} characters")
        print(f"    Preview: {seller_vkey[:20]}...")
        
        # Basic validation
        if len(seller_vkey) < 20:
            print("  ⚠️  Warning: VKey seems too short. Verify it's correct.")
            wallet_config_ok = False
        else:
            print("  ✓ VKey length looks valid")
    else:
        print("✗ Wallet Verification Key NOT SET")
        print("  You need to add your wallet's verification key to .env")
        wallet_config_ok = False
    
    print()
    
    # Check AGENT_IDENTIFIER
    agent_id = os.getenv("AGENT_IDENTIFIER")
    if agent_id and agent_id.strip() and agent_id != "your_agent_identifier_from_registration":
        print("✓ Agent Identifier:")
        print(f"    {agent_id}")
    else:
        print("✗ Agent Identifier NOT SET or still using default value")
        print("  You need to register your agent and add the identifier to .env")
        wallet_config_ok = False
    
    print()
    
    # Check network
    network = os.getenv("NETWORK", "").upper()
    if network in ["PREPROD", "MAINNET"]:
        print(f"✓ Network: {network}")
        if network == "PREPROD":
            print("  Good: Using testnet for development")
        else:
            print("  ⚠️  Warning: Using MAINNET - ensure you have real ADA")
    else:
        print("✗ Network not properly set")
        print(f"  Current value: {network}")
        print("  Should be: PREPROD (for testing) or MAINNET")
        wallet_config_ok = False
    
    print()
    
    # Check payment amount
    payment_amount = os.getenv("PAYMENT_AMOUNT")
    if payment_amount:
        try:
            amount_int = int(payment_amount)
            amount_ada = amount_int / 1000000  # Convert lovelace to ADA
            print(f"✓ Default Pledge Amount: {amount_ada} ADA ({payment_amount} lovelace)")
            
            if amount_ada < 1:
                print(f"  ⚠️  Low amount: {amount_ada} ADA")
            elif amount_ada > 100:
                print(f"  ⚠️  High amount: {amount_ada} ADA")
            else:
                print(f"  ✓ Reasonable amount for testing")
        except ValueError:
            print(f"✗ Invalid payment amount: {payment_amount}")
            wallet_config_ok = False
    else:
        print("✗ Payment amount not set")
        wallet_config_ok = False
    
    return wallet_config_ok


def test_payment_service_connection() -> bool:
    """Test connection to Masumi payment service"""
    
    print("\n" + "="*70)
    print("PAYMENT SERVICE CONNECTION TEST")
    print("="*70 + "\n")
    
    payment_url = os.getenv("PAYMENT_SERVICE_URL")
    payment_key = os.getenv("PAYMENT_API_KEY")
    
    if not payment_url:
        print("✗ Payment service URL not configured")
        return False
    
    print(f"Payment Service URL: {payment_url}")
    
    if not payment_key:
        print("✗ Payment API key not configured")
        return False
    
    print(f"API Key: {payment_key[:10]}..." if len(payment_key) > 10 else "API Key: Set")
    
    # Try to test the connection
    try:
        import requests
        health_url = payment_url.replace('/api/v1', '') + '/api/v1/health/'
        
        print(f"\nTesting connection to: {health_url}")
        print("Sending request...")
        
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print("✓ Payment service is reachable!")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Payment service returned status: {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  'requests' library not installed - skipping connection test")
        print("  Install with: pip install requests")
        return True  # Don't fail if requests not installed
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to payment service")
        print("  Make sure the Masumi Payment Service is running")
        print(f"  Expected at: {payment_url}")
        return False
    except Exception as e:
        print(f"⚠️  Connection test failed: {str(e)}")
        return False


def print_next_steps(all_ok: bool):
    """Print next steps based on configuration status"""
    
    print("\n" + "="*70)
    print("SUMMARY & NEXT STEPS")
    print("="*70 + "\n")
    
    if all_ok:
        print("✅ CONFIGURATION COMPLETE!")
        print("\nYour wallet is ready to use with the RDM Agent System.")
        print("\nNext steps:")
        print("  1. Test Agent 1: python rdm_agents.py goal")
        print("  2. Test pledge:  python rdm_agents.py pledge")
        print("  3. Full flow:    python rdm_agents.py full-flow")
        print("\nYour RDM tokens will be managed through your configured wallet.")
    else:
        print("⚠️  CONFIGURATION INCOMPLETE")
        print("\nPlease complete the following:")
        print("\n1. Update your .env file with missing values:")
        print("   - Get your wallet's verification key (SELLER_VKEY)")
        print("   - Register as an agent and get AGENT_IDENTIFIER")
        print("   - Ensure payment service is configured")
        print("\n2. See WALLET_INTEGRATION_GUIDE.md for detailed instructions")
        print("\n3. Run this test again: python test_wallet_connection.py")


def print_wallet_info():
    """Print helpful wallet information"""
    
    print("\n" + "="*70)
    print("WALLET INFORMATION")
    print("="*70 + "\n")
    
    print("Common Cardano Wallets:")
    print("  • Nami:     https://namiwallet.io/")
    print("  • Eternl:   https://eternl.io/")
    print("  • Yoroi:    https://yoroi-wallet.com/")
    print("  • Flint:    https://flint-wallet.com/")
    
    print("\nTestnet Faucets:")
    print("  • Cardano:  https://docs.cardano.org/cardano-testnets/tools/faucet")
    print("  • Masumi:   https://dispenser.masumi.network/")
    
    print("\nUseful Links:")
    print("  • Wallet Integration Guide: ./WALLET_INTEGRATION_GUIDE.md")
    print("  • RDM Documentation: ./RDM_COMPLETE_SYSTEM_README.md")


def main():
    """Main test function"""
    
    print("\n" + "="*70)
    print("🔐 RDM WALLET CONNECTION TEST")
    print("="*70)
    
    # Step 1: Check environment variables
    env_results = check_environment_variables()
    env_ok = env_results["all_set"]
    
    # Step 2: Test wallet configuration
    wallet_ok = test_wallet_configuration(env_results)
    
    # Step 3: Test payment service
    payment_ok = test_payment_service_connection()
    
    # Step 4: Print wallet info
    print_wallet_info()
    
    # Step 5: Print next steps
    all_ok = env_ok and wallet_ok and payment_ok
    print_next_steps(all_ok)
    
    print("\n" + "="*70 + "\n")
    
    # Return exit code
    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


