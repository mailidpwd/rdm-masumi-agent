import os
import uvicorn
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from masumi.config import Config
from masumi.payment import Payment, Amount
from crew_definition import ResearchCrew
from logging_config import setup_logging
# RDM Agent Integration
from rdm_masumi_integration import (
    execute_goal_creation,
    execute_reflection_checkin,
    execute_goal_verification,
    get_rdm_input_schema,
    get_agent_metadata_for_registration,
    get_goal_status
)

# Configure logging
logger = setup_logging()

# Load environment variables
load_dotenv(override=True)

# Retrieve API Keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
NETWORK = os.getenv("NETWORK")

logger.info("Starting application with configuration:")
logger.info(f"PAYMENT_SERVICE_URL: {PAYMENT_SERVICE_URL}")

# Initialize FastAPI
app = FastAPI(
    title="API following the Masumi API Standard",
    description="API for running Agentic Services tasks with Masumi payment integration",
    version="1.0.0"
)

# ─────────────────────────────────────────────────────────────────────────────
# Temporary in-memory job store (DO NOT USE IN PRODUCTION)
# ─────────────────────────────────────────────────────────────────────────────
jobs = {}
payment_instances = {}

# ─────────────────────────────────────────────────────────────────────────────
# Initialize Masumi Payment Config
# ─────────────────────────────────────────────────────────────────────────────
config = Config(
    payment_service_url=PAYMENT_SERVICE_URL,
    payment_api_key=PAYMENT_API_KEY
)

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────────────────
class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: dict[str, str]
    
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
    crew = ResearchCrew(logger=logger)
    inputs = {"text": input_data}
    result = crew.crew.kickoff(inputs)
    logger.info("CrewAI task completed successfully")
    return result

# ─────────────────────────────────────────────────────────────────────────────
# RDM Agent Task Execution
# ─────────────────────────────────────────────────────────────────────────────
async def execute_rdm_goal_creation(input_data: dict) -> str:
    """ Execute RDM Agent 1: Goal Creation and Pledge """
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
        
        # Log the input text (truncate if too long)
        input_text = data.input_data["text"]
        truncated_input = input_text[:100] + "..." if len(input_text) > 100 else input_text
        logger.info(f"Received job request with input: '{truncated_input}'")
        logger.info(f"Starting job {job_id} with agent {agent_identifier}")

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
            detail="Bad Request: If input_data or identifier_from_purchaser is missing, invalid, or does not adhere to the schema."
        )
    except Exception as e:
        logger.error(f"Error in start_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Input_data or identifier_from_purchaser is missing, invalid, or does not adhere to the schema."
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
    return get_rdm_input_schema()

# ─────────────────────────────────────────────────────────────────────────────
# 6) Health Check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """
    Returns the health of the server.
    """
    return {
        "status": "healthy"
    }

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
        
        result = await execute_reflection_checkin(data.goal_id, reflection_data)
        
        # Store reflection in job
        if "reflections" not in jobs[data.job_id]:
            jobs[data.job_id]["reflections"] = []
        
        jobs[data.job_id]["reflections"].append({
            "timestamp": datetime.now().isoformat(),
            "check_in_number": data.check_in_number,
            "status": data.status,
            "result": result
        })
        
        return {
            "status": "success",
            "job_id": data.job_id,
            "goal_id": data.goal_id,
            "reflection_number": data.check_in_number,
            "feedback": result
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
        if data.job_id not in jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get pledge amount from job
        pledge_amount = jobs[data.job_id].get("pledge_amount", 100)
        
        # Execute verification with Agent 2 (Veritas)
        completion_data = {
            "user_claims_done": data.user_claims_done,
            "evidence": data.evidence,
            "self_assessment": data.self_assessment,
            "verification_method": data.verification_method,
            "goal_description": jobs[data.job_id].get("goal_description", "")
        }
        
        verification_result = await execute_goal_verification(
            data.goal_id,
            completion_data,
            pledge_amount
        )
        
        # Update job status
        jobs[data.job_id]["status"] = "completed"
        jobs[data.job_id]["verification_result"] = verification_result
        jobs[data.job_id]["result"] = verification_result
        
        return {
            "status": "success",
            "job_id": data.job_id,
            "goal_id": data.goal_id,
            "verification_result": verification_result,
            "message": "Agent 2 (Veritas) has completed verification and token distribution"
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
    return get_agent_metadata_for_registration()

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
    crew = ResearchCrew(verbose=True)
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
