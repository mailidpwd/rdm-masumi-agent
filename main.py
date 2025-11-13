import os
import uvicorn
import uuid
from datetime import datetime
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from masumi.config import Config
from masumi.payment import Payment, Amount
# Import ResearchCrew lazily to avoid initialization errors
# from crew_definition import ResearchCrew
from logging_config import setup_logging
# RDM Agent Integration - Import only when needed to avoid agent initialization
# from rdm_masumi_integration import (
#     execute_goal_creation,
#     execute_reflection_checkin,
#     execute_goal_verification,
#     get_rdm_input_schema,
#     get_agent_metadata_for_registration,
#     get_goal_status,
#     build_goal_creation_fallback,
#     USE_GEMINI
# )

# Configure logging
logger = setup_logging()

# Load environment variables
load_dotenv(override=True)

# Retrieve API Keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
NETWORK = os.getenv("NETWORK", "Preprod")  # Default to Preprod if not set

logger.info("Starting application with configuration:")
logger.info(f"PAYMENT_SERVICE_URL: {PAYMENT_SERVICE_URL}")
logger.info(f"NETWORK: {NETWORK}")

# Warn if critical env vars are missing (but don't crash)
if not PAYMENT_SERVICE_URL:
    logger.warning("PAYMENT_SERVICE_URL not set - payment features will not work")
if not PAYMENT_API_KEY:
    logger.warning("PAYMENT_API_KEY not set - payment features will not work")

# Initialize FastAPI with error handling
app = FastAPI(
    title="API following the Masumi API Standard",
    description="API for running Agentic Services tasks with Masumi payment integration",
    version="1.0.0"
)

# Add global exception handler to catch all errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions"""
    try:
        # Try to log, but don't fail if logger is broken
        if logger:
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    except:
        pass  # Ignore logger errors
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

# Add CORS middleware to allow browser requests
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (use specific domains in production)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
except Exception as e:
    logger.error(f"Failed to add CORS middleware: {str(e)}", exc_info=True)

# ─────────────────────────────────────────────────────────────────────────────
# Temporary in-memory job store (DO NOT USE IN PRODUCTION)
# ─────────────────────────────────────────────────────────────────────────────
jobs = {}
payment_instances = {}

# ─────────────────────────────────────────────────────────────────────────────
# Initialize Masumi Payment Config
# ─────────────────────────────────────────────────────────────────────────────
# Use defaults if env vars not set (prevents crashes on Railway)
try:
    config = Config(
        payment_service_url=PAYMENT_SERVICE_URL or "https://masumi-payment-service-production-50ce.up.railway.app/api/v1",
        payment_api_key=PAYMENT_API_KEY or ""
    )
except Exception as e:
    logger.error(f"Failed to initialize Config: {str(e)}", exc_info=True)
    # Create a minimal config to prevent crashes
    config = None

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────────────────
class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: dict[str, Any]  # Allow any type (string, number, etc.)
    
    class Config:
        json_schema_extra = {
            "example": {
                "identifier_from_purchaser": "example_purchaser_123",
                "input_data": {
                    "text": "Write a story about a robot learning to paint"
                }
            }
        }

class ProvideInputRequest(BaseModel):
    job_id: str

# RDM-specific models
class ReflectionRequest(BaseModel):
    job_id: str
    goal_id: str
    status: str  # "Done", "Partially Done", "Not Done", "In Progress"
    notes: str = ""
    challenges: str = ""
    check_in_number: int = 1

class CompleteGoalRequest(BaseModel):
    job_id: str
    goal_id: str
    user_claims_done: bool
    evidence: str
    self_assessment: str  # "Done", "Partially Done", "Not Done"
    verification_method: str = "Self-verification"

# ─────────────────────────────────────────────────────────────────────────────
# CrewAI Task Execution
# ─────────────────────────────────────────────────────────────────────────────
async def execute_crew_task(input_data: str) -> str:
    """ Execute a CrewAI task with Research and Writing Agents """
    logger.info(f"Starting CrewAI task with input: {input_data}")
    try:
        from crew_definition import ResearchCrew
        crew = ResearchCrew(logger=logger)
    except Exception as e:
        logger.error(f"Failed to import ResearchCrew: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Research crew initialization failed: {str(e)}")
    inputs = {"text": input_data}
    result = crew.crew.kickoff(inputs)
    logger.info("CrewAI task completed successfully")
    return result

# ─────────────────────────────────────────────────────────────────────────────
# RDM Agent Task Execution
# ─────────────────────────────────────────────────────────────────────────────
async def execute_rdm_goal_creation(input_data: dict) -> str:
    """ Execute RDM Agent 1: Goal Creation and Pledge """
    from rdm_masumi_integration import execute_goal_creation
    logger.info(f"Starting RDM Goal Creation with input: {input_data}")
    result = await execute_goal_creation(input_data)
    logger.info("RDM Goal Creation completed successfully")
    return result

# ─────────────────────────────────────────────────────────────────────────────
# 1) Start Job (MIP-003: /start_job)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/start_job")
async def start_job(data: StartJobRequest):
    """ Initiates a job and creates a payment request """
    print(f"Received data: {data}")
    print(f"Received data.input_data: {data.input_data}")
    try:
        job_id = str(uuid.uuid4())
        agent_identifier = os.getenv("AGENT_IDENTIFIER")
        
        # Validate agent identifier (Masumi requires 57+ characters - Cardano address)
        if not agent_identifier or len(agent_identifier) < 57:
            error_msg = f"AGENT_IDENTIFIER must be at least 57 characters (Cardano address). Current: {len(agent_identifier) if agent_identifier else 0} characters. Please update your .env file with a valid Cardano address (e.g., addr_test1...)"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Log the input text (truncate if too long)
        # Handle both RDM goals (goal_description) and research tasks (text)
        input_text = data.input_data.get("text") or data.input_data.get("goal_description", "")
        truncated_input = input_text[:100] + "..." if len(input_text) > 100 else input_text
        logger.info(f"Received job request with input: '{truncated_input}'")
        logger.info(f"Starting job {job_id} with agent {agent_identifier[:20]}...")

        # Define payment amounts
        payment_amount = os.getenv("PAYMENT_AMOUNT", "10000000")  # Default 10 ADA
        payment_unit = os.getenv("PAYMENT_UNIT", "lovelace") # Default lovelace

        amounts = [Amount(amount=payment_amount, unit=payment_unit)]
        logger.info(f"Using payment amount: {payment_amount} {payment_unit}")
        
        # Create a payment request using Masumi
        payment = Payment(
            agent_identifier=agent_identifier,
            #amounts=amounts,
            config=config,
            identifier_from_purchaser=data.identifier_from_purchaser,
            input_data=data.input_data,
            network=NETWORK
        )
        
        logger.info("Creating payment request...")
        payment_request = await payment.create_payment_request()
        blockchain_identifier = payment_request["data"]["blockchainIdentifier"]
        payment.payment_ids.add(blockchain_identifier)
        logger.info(f"Created payment request with blockchain identifier: {blockchain_identifier}")

        # Store job info (Awaiting payment)
        jobs[job_id] = {
            "status": "awaiting_payment",
            "payment_status": "pending",
            "blockchain_identifier": blockchain_identifier,
            "input_data": data.input_data,
            "result": None,
            "identifier_from_purchaser": data.identifier_from_purchaser
        }

        async def payment_callback(blockchain_identifier: str):
            await handle_payment_status(job_id, blockchain_identifier)

        # Start monitoring the payment status
        payment_instances[job_id] = payment
        logger.info(f"Starting payment status monitoring for job {job_id}")
        await payment.start_status_monitoring(payment_callback)

        # Return the response in the required format
        return {
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": blockchain_identifier,
            "submitResultTime": payment_request["data"]["submitResultTime"],
            "unlockTime": payment_request["data"]["unlockTime"],
            "externalDisputeUnlockTime": payment_request["data"]["externalDisputeUnlockTime"],
            "agentIdentifier": agent_identifier,
            "sellerVKey": os.getenv("SELLER_VKEY"),
            "identifierFromPurchaser": data.identifier_from_purchaser,
            "amounts": amounts,
            "input_hash": payment.input_hash,
            "payByTime": payment_request["data"]["payByTime"],
        }
    except KeyError as e:
        logger.error(f"Missing required field in request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Bad Request: Missing required field - {str(e)}"
        )
    except ValueError as e:
        # Masumi payment service validation errors
        error_msg = str(e)
        logger.error(f"Payment validation error: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    except Exception as e:
        # Other errors - return the actual error message
        error_msg = str(e)
        logger.error(f"Error in start_job: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=error_msg if error_msg else "An unexpected error occurred. Please check the server logs."
        )

# ─────────────────────────────────────────────────────────────────────────────
# 2) Process Payment and Execute AI Task
# ─────────────────────────────────────────────────────────────────────────────
async def handle_payment_status(job_id: str, payment_id: str) -> None:
    """ Executes CrewAI task after payment confirmation """
    try:
        logger.info(f"Payment {payment_id} completed for job {job_id}, executing task...")
        
        # Update job status to running
        jobs[job_id]["status"] = "running"
        logger.info(f"Input data: {jobs[job_id]['input_data']}")

        # Determine which execution path: RDM or Research Crew
        input_data = jobs[job_id]["input_data"]
        
        # If input contains goal_description, use RDM agents
        if "goal_description" in input_data:
            logger.info("Using RDM Agent execution path")
            result = await execute_rdm_goal_creation(input_data)
            
            # Store goal-specific data
            jobs[job_id]["goal_description"] = input_data.get("goal_description", "")
            jobs[job_id]["pledge_amount"] = input_data.get("pledge_amount", 100)
            jobs[job_id]["duration"] = input_data.get("duration", "30 days")
            jobs[job_id]["reflections"] = []
        else:
            # Default: use original research crew
            logger.info("Using Research Crew execution path")
            result = await execute_crew_task(input_data)
        
        print(f"Result: {result}")
        logger.info(f"Task completed for job {job_id}")
        
        # Convert result to string for payment completion
        # Check if result has .raw attribute (CrewOutput), otherwise convert to string
        result_string = result.raw if hasattr(result, "raw") else str(result)
        
        # Mark payment as completed on Masumi
        # Use a shorter string for the result hash
        await payment_instances[job_id].complete_payment(payment_id, result_string)
        logger.info(f"Payment completed for job {job_id}")

        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["payment_status"] = "completed"
        jobs[job_id]["result"] = result

        # Stop monitoring payment status
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]
    except Exception as e:
        print(f"Error processing payment {payment_id} for job {job_id}: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        
        # Still stop monitoring to prevent repeated failures
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]

# ─────────────────────────────────────────────────────────────────────────────
# 3) Check Job and Payment Status (MIP-003: /status)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status")
async def get_status(job_id: str):
    """ Retrieves the current status of a specific job """
    logger.info(f"Checking status for job {job_id}")
    if job_id not in jobs:
        logger.warning(f"Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    # Check latest payment status if payment instance exists
    if job_id in payment_instances:
        try:
            status = await payment_instances[job_id].check_payment_status()
            job["payment_status"] = status.get("data", {}).get("status")
            logger.info(f"Updated payment status for job {job_id}: {job['payment_status']}")
        except ValueError as e:
            logger.warning(f"Error checking payment status: {str(e)}")
            job["payment_status"] = "unknown"
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}", exc_info=True)
            job["payment_status"] = "error"


    result_data = job.get("result")
    logger.info(f"Result data: {result_data}")
    result = result_data.raw if result_data and hasattr(result_data, "raw") else None



    return {
        "job_id": job_id,
        "status": job["status"],
        "payment_status": job["payment_status"],
        "result": result
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Check Server Availability (MIP-003: /availability)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/availability")
async def check_availability():
    """ Checks if the server is operational """

    return {"status": "available", "type": "masumi-agent", "message": "Server operational."}
    # Commented out for simplicity sake but its recommended to include the agentIdentifier
    #return {"status": "available","agentIdentifier": os.getenv("AGENT_IDENTIFIER"), "message": "The server is running smoothly."}

# ─────────────────────────────────────────────────────────────────────────────
# 5) Retrieve Input Schema (MIP-003: /input_schema)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/input_schema")
async def input_schema():
    """
    Returns the expected input schema for the /start_job endpoint.
    Fulfills MIP-003 /input_schema endpoint.
    Now returns RDM Agent schema for goal-setting and pledge management.
    """
    from rdm_masumi_integration import get_rdm_input_schema
    return get_rdm_input_schema()

# ─────────────────────────────────────────────────────────────────────────────
# 6) Health Check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    """ Root endpoint - API information - Minimal implementation """
    return JSONResponse(content={
        "service": "RDM Masumi Agent API",
        "status": "running",
        "version": "1.0.0"
    })

@app.get("/health")
async def health():
    """
    Returns the health of the server - Minimal implementation
    """
    return JSONResponse(content={"status": "healthy"})

@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404/502 errors"""
    from fastapi.responses import Response
    return Response(status_code=204)  # No content

# ─────────────────────────────────────────────────────────────────────────────
# 7) RDM Agent: Submit Reflection Check-in
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/submit_reflection")
async def submit_reflection(data: ReflectionRequest):
    """
    Submit a reflection check-in for a goal (Agent 1)
    Allows users to log their progress and receive feedback
    """
    logger.info(f"Reflection submitted for goal {data.goal_id}")
    
    try:
        if data.job_id not in jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Execute reflection with Agent 1
        reflection_data = {
            "check_in_number": data.check_in_number,
            "status": data.status,
            "notes": data.notes,
            "challenges": data.challenges,
            "days_since_last": 7  # Calculate based on last check-in
        }
        
        # Hardcoded fallback - NO GEMINI CALLS
        logger.info("SUBMIT_REFLECTION CALLED - Returning hardcoded response, NO GEMINI")
        
        fallback_result = {
            "goal_id": data.goal_id,
            "check_in_timestamp": datetime.now().isoformat(),
            "check_in_number": data.check_in_number,
            "result": {
                "progress_status": "on_track" if data.status.lower() in ["done", "completed"] else "in_progress",
                "reflection_feedback": f"Great progress on your goal! Your status '{data.status}' shows commitment. Keep logging reflections to track your journey.",
                "reflective_questions": [
                    "What specific actions contributed to your progress?",
                    "What challenges did you overcome?",
                    "What will you focus on next?"
                ],
                "recommendations": [
                    "Continue logging regular reflections",
                    "Celebrate your progress",
                    "Stay consistent with your goal"
                ],
                "mode": "fallback"
            }
        }
        
        # Store reflection in job
        if "reflections" not in jobs[data.job_id]:
            jobs[data.job_id]["reflections"] = []
        
        jobs[data.job_id]["reflections"].append({
            "timestamp": datetime.now().isoformat(),
            "check_in_number": data.check_in_number,
            "status": data.status,
            "result": str(fallback_result)
        })
        
        return {
            "status": "success",
            "job_id": data.job_id,
            "goal_id": data.goal_id,
            "reflection_number": data.check_in_number,
            "feedback": fallback_result
        }
    except Exception as e:
        logger.error(f"Error in submit_reflection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 8) RDM Agent: Complete Goal and Trigger Verification
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/complete_goal")
async def complete_goal(data: CompleteGoalRequest):
    """
    Submit goal completion claim and trigger Agent 2 (Veritas) verification
    Returns token distribution and final judgment
    """
    logger.info(f"Goal completion submitted for goal {data.goal_id}")
    
    try:
        # Handle case where job doesn't exist (server restart cleared memory)
        if data.job_id not in jobs:
            logger.warning(f"Job {data.job_id} not found in memory (server may have restarted). Using default values.")
            # Create a temporary job entry with default values
            jobs[data.job_id] = {
                "status": "completed",
                "pledge_amount": 100,  # Default pledge
                "goal_description": "Goal (job data lost on server restart)",
                "duration": "14 days"
            }
        
        # Get pledge amount from job
        pledge_amount = jobs[data.job_id].get("pledge_amount", 100)
        
        # Hardcoded fallback - NO GEMINI CALLS
        logger.info("COMPLETE_GOAL CALLED - Returning hardcoded verification response, NO GEMINI")
        
        import json
        
        # Determine success rate based on verification status
        is_verified = data.verification_method.lower().startswith("peer") and "verified" in data.self_assessment.lower()
        success_rate = 100 if (data.user_claims_done and is_verified) else 75 if data.user_claims_done else 50
        
        # Calculate token distribution
        reward_tokens = int((pledge_amount * success_rate) / 100)
        remorse_tokens = pledge_amount - reward_tokens
        
        # Create fallback verification result matching expected structure
        verification_result = {
            "goal_id": data.goal_id,
            "verification_cycle_completed": datetime.now().isoformat(),
            "steps": {
                "2_outcome_determination": {
                    "final_outcome": json.dumps({
                        "outcome_category": "SUCCESS" if success_rate >= 75 else "PARTIAL",
                        "completion_percentage": success_rate,
                        "achievement_summary": f"Goal verified with {success_rate}% completion rate",
                        "judgment_reasoning": "Fallback verification completed for local testing"
                    })
                },
                "3_token_distribution": {
                    "distribution_details": json.dumps({
                        "total_pledge": pledge_amount,
                        "reward_bucket_amount": reward_tokens,
                        "remorse_bucket_amount": remorse_tokens,
                        "reward_percentage": success_rate,
                        "remorse_percentage": 100 - success_rate,
                        "bonus_tokens": 0,
                        "transaction_hash": f"0xfallback_{data.goal_id.replace('-', '')}"
                    })
                },
                "4_ledger_update": {
                    "ledger_and_contract": json.dumps({
                        "smart_contract_hash": f"0xfallback_{data.goal_id.replace('-', '')}",
                        "impact_badge": {
                            "level": 2 if success_rate >= 75 else 1,
                            "name": "Silver Achiever" if success_rate >= 75 else "Bronze Achiever"
                        }
                    })
                }
            },
            "summary": {
                "pledge_amount": pledge_amount,
                "outcome_category": "SUCCESS" if success_rate >= 75 else "PARTIAL",
                "tokens_to_reward": reward_tokens,
                "tokens_to_remorse": remorse_tokens,
                "impact_badge": "Silver Achiever" if success_rate >= 75 else "Bronze Achiever",
                "smart_contract_hash": f"0xfallback_{data.goal_id.replace('-', '')}"
            }
        }
        
        # Update job status
        jobs[data.job_id]["status"] = "completed"
        jobs[data.job_id]["verification_result"] = str(verification_result)
        jobs[data.job_id]["result"] = str(verification_result)
        
        return {
            "status": "success",
            "job_id": data.job_id,
            "goal_id": data.goal_id,
            "verification_result": str(verification_result),
            "message": "Agent 2 (Veritas) has completed verification and token distribution (Fallback mode)"
        }
    except Exception as e:
        logger.error(f"Error in complete_goal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 9) RDM Agent: Get Goal Status
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/goal_status")
async def goal_status(goal_id: str):
    """
    Get detailed status of a specific goal
    """
    logger.info(f"Checking status for goal {goal_id}")
    
    try:
        from rdm_masumi_integration import get_goal_status
        result = await get_goal_status(goal_id, jobs)
        return result
    except Exception as e:
        logger.error(f"Error in goal_status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=404, detail="Goal not found")

# ─────────────────────────────────────────────────────────────────────────────
# 10) RDM Agent: Get Registration Metadata
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/agent_metadata")
async def agent_metadata():
    """
    Returns agent metadata for Masumi on-chain registration
    Follows Masumi metadata standard for agent registry
    """
    from rdm_masumi_integration import get_agent_metadata_for_registration
    return get_agent_metadata_for_registration()

# ─────────────────────────────────────────────────────────────────────────────
# TEST ENDPOINTS - BYPASS PAYMENT FOR LOCAL TESTING
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/test_create_goal")
async def test_create_goal(data: dict):
    """
    TEST ENDPOINT - Create goal without payment (local testing only)
    Returns hardcoded response - NO GEMINI, NO AGENTS, NO IMPORTS
    """
    import json
    
    logger.info("TEST_CREATE_GOAL CALLED - Returning hardcoded response, NO GEMINI")
    
    job_id = str(uuid.uuid4())
    goal_description = data.get("goal_description", "")
    pledge_amount = data.get("pledge_amount", 100)
    duration = data.get("duration", "Flexible timeframe")
    
    # Hardcoded fallback - NO GEMINI CALLS AT ALL
    fallback_goal_id = f"RDM-{uuid.uuid4().hex[:8]}"
    fallback_result = {
        "goal_guidance": {
            "mode": "fallback",
            "goal_summary": goal_description or "Sustainable impact goal",
            "goal_suggestions": [
                {
                    "title": "Clarify your objective",
                    "description": "Write down the exact outcome you want in 1-2 sentences.",
                    "verification": "Self-reflection journal or peer confirmation"
                },
                {
                    "title": "Break into milestones",
                    "description": "List three small actions you can complete this week toward the goal.",
                    "verification": "Checklist with completed dates"
                }
            ],
            "recommended_pledge": {
                "amount": pledge_amount,
                "reason": "Default pledge used while primary AI is offline"
            },
            "notes": "Temporary fallback guidance - Gemini bypassed for local testing."
        },
        "pledge_confirmation": {
            "goal_id": fallback_goal_id,
            "pledge_amount": pledge_amount,
            "duration": duration,
            "verification_method": "Self-verification",
            "confirmation": "Temporary fallback confirmation generated for local testing.",
            "mode": "fallback"
        },
        "goal_id": fallback_goal_id,
        "status": "goal_created",
        "next_steps": "Submit daily/weekly reflections via /submit_reflection endpoint",
        "fallback_used": True
    }
    
    jobs[job_id] = {
        "status": "completed",
        "payment_status": "bypassed_for_testing",
        "input_data": data,
        "result": json.dumps(fallback_result),
        "goal_description": goal_description,
        "pledge_amount": pledge_amount,
        "duration": duration,
        "reflections": [],
        "fallback_used": True,
        "goal_id": fallback_goal_id
    }
    
    return {
        "job_id": job_id,
        "status": "completed",
        "result": json.dumps(fallback_result),
        "message": "Temporary local fallback response (Gemini completely bypassed)",
        "fallback_used": True
    }

# ─────────────────────────────────────────────────────────────────────────────
# Main Logic if Called as a Script
# ─────────────────────────────────────────────────────────────────────────────
def main():
    """Run the standalone agent flow without the API"""
    import os
    import sys
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    # Disable execution traces to avoid terminal issues
    os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
    
    print("\n" + "=" * 70)
    print("Running CrewAI agents locally (standalone mode)...")
    print("=" * 70 + "\n")
    
    # Define test input
    input_data = {"text": "The impact of AI on the job market"}
    
    print(f"Input: {input_data['text']}")
    print("\nProcessing with CrewAI agents...\n")
    
    # Initialize and run the crew
    try:
        from crew_definition import ResearchCrew
        crew = ResearchCrew(verbose=True)
    except Exception as e:
        print(f"Error: Failed to import ResearchCrew: {str(e)}")
        raise
    result = crew.crew.kickoff(inputs=input_data)
    
    # Display the result
    print("\n" + "=" * 70)
    print("Crew Output:")
    print("=" * 70 + "\n")
    print(result)
    print("\n" + "=" * 70 + "\n")
    
    # Ensure terminal is properly reset after CrewAI execution
    sys.stdout.flush()
    sys.stderr.flush()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Run API mode
        port = int(os.environ.get("API_PORT", 8000))
        # Set host from environment variable, default to localhost for security.
        # Use host=0.0.0.0 to allow external connections (e.g., in Docker or production).
        host = os.environ.get("API_HOST", "127.0.0.1")

        print("\n" + "=" * 70)
        print("Starting FastAPI server with Masumi integration...")
        print("=" * 70)
        print(f"API Documentation:        http://{host}:{port}/docs")
        print(f"Availability Check:       http://{host}:{port}/availability")
        print(f"Status Check:             http://{host}:{port}/status")
        print(f"Input Schema:             http://{host}:{port}/input_schema\n")
        print("=" * 70 + "\n")

        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        # Run standalone mode
        main()
