"""
RDM Agent Integration with Masumi Protocol
Connects Agent 1 and Agent 2 to Masumi payment system
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any
from rdm_agents import RDMAgentSystem, VeritasAgent
from logging_config import get_logger

logger = get_logger(__name__)

# Initialize RDM Agents (singleton pattern)
_rdm_agent_1 = None
_veritas_agent_2 = None


def get_agent_1():
    """Get or create Agent 1 instance"""
    global _rdm_agent_1
    if _rdm_agent_1 is None:
        _rdm_agent_1 = RDMAgentSystem(verbose=False, logger=logger)
        logger.info("Agent 1 (RDM System) initialized")
    return _rdm_agent_1


def get_agent_2():
    """Get or create Agent 2 instance"""
    global _veritas_agent_2
    if _veritas_agent_2 is None:
        _veritas_agent_2 = VeritasAgent(verbose=False, logger=logger)
        logger.info("Agent 2 (Veritas) initialized")
    return _veritas_agent_2


async def execute_goal_creation(input_data: Dict[str, Any]) -> str:
    """
    Execute Agent 1: Goal Selection and Pledge Capture
    
    Args:
        input_data: Dictionary containing goal parameters
        
    Returns:
        Goal creation result with pledge details
    """
    logger.info(f"Executing Agent 1 - Goal Creation with input: {input_data}")
    
    agent_1 = get_agent_1()
    
    # Extract user's goal input
    user_goal_input = input_data.get("goal_description", "")
    
    # Step 1: Guide goal selection
    goal_guidance = agent_1.guide_goal_selection(user_goal_input)
    logger.info("Agent 1 completed goal selection guidance")
    
    # Step 2: Capture pledge (if provided)
    pledge_amount = input_data.get("pledge_amount", 100)
    duration = input_data.get("duration", "30 days")
    verification_method = input_data.get("verification_method", "Self-verification")
    
    goal_data = {
        "goal_id": f"RDM-{uuid.uuid4().hex[:8]}",
        "goal_description": user_goal_input,
        "pledge_amount": pledge_amount,
        "duration": duration,
        "verification_method": verification_method
    }
    
    pledge_result = agent_1.capture_pledge(goal_data)
    logger.info("Agent 1 completed pledge capture")
    
    # Combine results
    result = {
        "goal_guidance": goal_guidance,
        "pledge_confirmation": pledge_result,
        "goal_id": goal_data["goal_id"],
        "status": "goal_created",
        "next_steps": "Submit daily/weekly reflections via /submit_reflection endpoint"
    }
    
    return str(result)


async def execute_reflection_checkin(goal_id: str, reflection_data: Dict[str, Any]) -> str:
    """
    Execute Agent 1: Reflection Check-in
    
    Args:
        goal_id: Goal identifier
        reflection_data: User's reflection input
        
    Returns:
        Reflection analysis and feedback
    """
    logger.info(f"Executing Agent 1 - Reflection Check-in for goal: {goal_id}")
    
    agent_1 = get_agent_1()
    
    check_in_data = {
        "check_in_number": reflection_data.get("check_in_number", 1),
        "status": reflection_data.get("status", "In Progress"),
        "notes": reflection_data.get("notes", ""),
        "challenges": reflection_data.get("challenges", ""),
        "days_since_last": reflection_data.get("days_since_last", 7)
    }
    
    result = agent_1.conduct_reflection_checkin(goal_id, check_in_data)
    logger.info("Agent 1 completed reflection check-in")
    
    return str(result)


async def execute_goal_verification(goal_id: str, completion_data: Dict[str, Any], pledge_amount: int) -> str:
    """
    Execute Agent 2: Veritas - Complete Verification and Token Distribution
    
    Args:
        goal_id: Goal identifier
        completion_data: Completion claim and evidence
        pledge_amount: Original pledge amount
        
    Returns:
        Complete verification result with token distribution
    """
    logger.info(f"Executing Agent 2 - Veritas Verification for goal: {goal_id}")
    
    agent_1 = get_agent_1()
    agent_2 = get_agent_2()
    
    # Agent 1: Initiate verification (flag data for Agent 2)
    verification_init = agent_1.initiate_goal_verification(goal_id, completion_data)
    logger.info("Agent 1 flagged data for Agent 2")
    
    # Agent 2: Complete verification cycle
    flagged_data = verification_init.get("agent_2_data_package", {})
    flagged_data.update({
        "goal_description": completion_data.get("goal_description", ""),
        "pledge_amount": pledge_amount,
        "verification_method": completion_data.get("verification_method", ""),
        "completion_claim": completion_data
    })
    
    verification_result = agent_2.complete_verification_cycle(goal_id, flagged_data, pledge_amount)
    logger.info("Agent 2 completed verification cycle")
    
    return str(verification_result)


def get_rdm_input_schema() -> Dict[str, Any]:
    """
    Get input schema for RDM agent system
    Masumi requires this for /input_schema endpoint
    
    Returns:
        Structured input schema for goal creation
    """
    return {
        "input_data": [
            {
                "id": "goal_description",
                "type": "string",
                "name": "Goal Description",
                "data": {
                    "description": "Describe your sustainability or personal development goal",
                    "placeholder": "E.g., Reduce single-use plastic by 80% over 30 days",
                    "required": True
                }
            },
            {
                "id": "pledge_amount",
                "type": "number",
                "name": "RDM Token Pledge Amount",
                "data": {
                    "description": "How many RDM tokens do you want to pledge? (75-175 recommended)",
                    "placeholder": "100",
                    "min": 50,
                    "max": 500,
                    "default": 100,
                    "required": True
                }
            },
            {
                "id": "duration",
                "type": "string",
                "name": "Goal Duration",
                "data": {
                    "description": "How long will you work on this goal?",
                    "placeholder": "30 days",
                    "examples": ["7 days", "30 days", "2 months", "90 days"],
                    "required": True
                }
            },
            {
                "id": "verification_method",
                "type": "string",
                "name": "Verification Method",
                "data": {
                    "description": "How will you verify completion?",
                    "placeholder": "Daily photo log + weekly self-assessment",
                    "options": [
                        "Self-verification (Y/N)",
                        "Photo/video evidence",
                        "Third-party app (fitness, habit tracker)",
                        "IoT device data",
                        "Peer verification",
                        "Combined methods"
                    ],
                    "required": True
                }
            },
            {
                "id": "goal_category",
                "type": "string",
                "name": "Goal Category",
                "data": {
                    "description": "What type of goal is this?",
                    "options": [
                        "Environmental Sustainability",
                        "Health & Fitness",
                        "Learning & Education",
                        "Community Service",
                        "Personal Development",
                        "Financial Wellness"
                    ],
                    "required": False
                }
            }
        ],
        "metadata": {
            "service_name": "RDM Goal Accountability Agent",
            "version": "1.0.0",
            "capabilities": [
                "Goal setting with SDG/ESG alignment",
                "Token pledge management",
                "Daily/weekly reflection check-ins",
                "AI-powered verification and judgment",
                "Token distribution (Reward/Remorse buckets)",
                "Impact badge assignment",
                "Smart contract integration"
            ]
        }
    }


def get_agent_metadata_for_registration() -> Dict[str, Any]:
    """
    Get agent metadata for Masumi on-chain registration
    Follows Masumi metadata standard
    
    Returns:
        JSON metadata for agent registration
    """
    return {
        "name": ["RDM Goal Accountability Agent"],
        "description": [
            "AI-powered goal-setting and accountability system with token-based commitment. "
            "Uses two specialized agents: (1) Goal-Setting & Pledge Management for guidance "
            "and reflections, and (2) Veritas for impartial verification and token distribution. "
            "Supports SDG/ESG alignment, multiple verification methods, and impact tracking."
        ],
        "api_url": [os.getenv("API_URL", "http://localhost:8000")],
        "example_output": [
            "Goal created with 100 RDM pledge, daily reflections tracked, "
            "60% completion verified by Veritas, 60 RDM to Reward bucket + 10 bonus tokens, "
            "Eco Champion (Bronze) badge awarded, impact: 150kg waste diverted, 300kg CO2 saved"
        ],
        "capability": {
            "name": [
                "Goal Setting with SDG/ESG Alignment",
                "RDM Token Pledge Management",
                "Daily/Weekly Reflection Facilitation",
                "AI-Powered Verification (Veritas)",
                "Token Distribution (Reward/Remorse)",
                "Impact Badge Assignment",
                "Smart Contract Integration"
            ],
            "version": ["1.0.0"]
        },
        "requests_per_hour": ["100"],
        "author": {
            "name": ["RDM Development Team"],
            "contact": ["rdm-support@example.com"],
            "organization": ["RDM Accountability Systems"]
        },
        "legal": {
            "privacy_policy": ["https://rdm.example.com/privacy"],
            "terms": ["https://rdm.example.com/terms"],
            "other": ["Agent judgments are AI-powered and should be used as guidance. Users maintain final responsibility for their goals."]
        },
        "tags": [
            "goal-setting",
            "accountability",
            "sustainability",
            "SDG",
            "ESG",
            "token-economy",
            "behavioral-psychology",
            "impact-tracking"
        ],
        "pricing": [
            {
                "quantity": int(os.getenv("PAYMENT_AMOUNT", "10000000")),
                "unit": [os.getenv("PAYMENT_UNIT", "lovelace")]
            }
        ],
        "image": ["https://rdm.example.com/agent-logo.png"],
        "metadata_version": 1
    }


async def get_goal_status(goal_id: str, jobs_db: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed status of a goal
    
    Args:
        goal_id: Goal identifier
        jobs_db: Jobs database
        
    Returns:
        Detailed goal status
    """
    if goal_id not in jobs_db:
        return {"error": "Goal not found", "goal_id": goal_id}
    
    goal_data = jobs_db[goal_id]
    
    return {
        "goal_id": goal_id,
        "status": goal_data.get("status", "unknown"),
        "payment_status": goal_data.get("payment_status", "unknown"),
        "pledge_amount": goal_data.get("pledge_amount", 0),
        "reflections_count": len(goal_data.get("reflections", [])),
        "last_reflection": goal_data.get("reflections", [])[-1] if goal_data.get("reflections") else None,
        "result": goal_data.get("result"),
        "created_at": goal_data.get("created_at"),
        "updated_at": datetime.now().isoformat()
    }

