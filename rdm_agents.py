import os
from crewai import Agent, Crew, Task, LLM
from logging_config import get_logger
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from datetime import datetime

# Load environment variables
load_dotenv()

class RDMAgentSystem:
    """RDM (Redemption) Agent System for goal-setting and pledge management"""
    
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        
        # Configure Gemini LLM
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
            self.llm = LLM(
                model="google/gemini-2.5-flash",
                api_key=gemini_api_key
            )
            self.logger.info("Configured Gemini 2.5 Flash LLM for RDM Agents")
        else:
            self.llm = None
            self.logger.warning("GEMINI_API_KEY not found, using default LLM")
        
        # Initialize Agent 1
        self.agent_1 = self._create_agent_1()
        self.logger.info("RDM Agent System initialized")

    def _create_agent_1(self) -> Agent:
        """
        Agent 1: Goal-Setting, Pledge Management & Reflection Assistant
        
        Role: Guides users through goal creation, manages RDM token pledges,
              facilitates daily/weekly reflections, and verifies goal completion
        """
        agent_1 = Agent(
            role='Goal-Setting and Pledge Management Specialist',
            goal="""Guide users in setting meaningful goals aligned with SDGs, ESGs, 
                    and personal values. Manage RDM token pledges, facilitate reflections, 
                    and verify goal completion status.""",
            backstory="""You are an expert life coach and commitment facilitator with deep 
                        knowledge of Sustainable Development Goals (SDGs), Environmental, 
                        Social, and Governance (ESG) principles. You understand human motivation, 
                        behavioral psychology, and the power of financial commitment through 
                        token pledges. Your mission is to help users set achievable goals, 
                        maintain accountability through reflection, and verify their progress 
                        using various verification methods (self-reporting, third-party apps, 
                        IoT devices, external confirmations). You are empathetic, encouraging, 
                        and data-driven.""",
            verbose=self.verbose,
            llm=self.llm,
            allow_delegation=False
        )
        
        self.logger.info("Created Agent 1: Goal-Setting and Pledge Management Specialist")
        return agent_1

    def guide_goal_selection(self, user_input: str) -> str:
        """
        Task: Guide user through selecting meaningful goals
        
        Args:
            user_input: User's initial goal description or interests
            
        Returns:
            Structured goal recommendations aligned with SDGs/ESGs/personal values
        """
        task = Task(
            description=f"""Guide the user in creating a meaningful goal based on their input: "{user_input}"
            
            Your guidance should include:
            1. Analyze the user's input and identify relevant SDGs (Sustainable Development Goals) and ESG principles
            2. Ask clarifying questions if needed to understand their motivation and constraints
            3. Suggest 2-3 specific, measurable, achievable, relevant, and time-bound (SMART) goals
            4. Explain how each goal aligns with SDGs, ESGs, or personal values
            5. Provide examples of success criteria and verification methods
            6. Recommend an appropriate RDM token pledge amount based on the goal's difficulty and duration
            
            Format your response as a structured JSON with:
            - goal_suggestions: list of goal options
            - sdg_alignment: relevant SDGs for each goal
            - esg_alignment: relevant ESG principles
            - verification_methods: suggested ways to verify completion
            - recommended_pledge: suggested RDM token amount and reasoning
            """,
            expected_output="""A structured JSON response containing goal suggestions, SDG/ESG alignments, 
                             verification methods, and recommended pledge amounts.""",
            agent=self.agent_1
        )
        
        crew = Crew(
            agents=[self.agent_1],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        return result.raw if hasattr(result, "raw") else str(result)

    def capture_pledge(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Capture and validate RDM token pledge for a goal
        
        Args:
            goal_data: Dictionary containing goal details and pledge amount
            
        Returns:
            Validated pledge details with confirmation
        """
        task = Task(
            description=f"""Process and validate the following goal and pledge:
            
            Goal: {goal_data.get('goal_description', 'Not provided')}
            Pledge Amount: {goal_data.get('pledge_amount', 0)} RDM tokens
            Duration: {goal_data.get('duration', 'Not specified')}
            Verification Method: {goal_data.get('verification_method', 'Not specified')}
            
            Your tasks:
            1. Validate that the pledge amount is appropriate for the goal's scope and duration
            2. Confirm the verification method is suitable and achievable
            3. Create a pledge commitment statement
            4. Suggest check-in frequency (daily/weekly) based on the goal
            5. Calculate key milestone dates
            6. Provide motivational messaging for the commitment
            
            Format as JSON with:
            - validation_status: "approved" or "needs_adjustment"
            - pledge_confirmation: commitment statement
            - check_in_schedule: recommended frequency
            - milestones: list of milestone dates
            - motivation_message: encouraging message
            - adjustment_recommendations: if validation_status is "needs_adjustment"
            """,
            expected_output="""JSON response with pledge validation, commitment statement, 
                             check-in schedule, and motivational content.""",
            agent=self.agent_1
        )
        
        crew = Crew(
            agents=[self.agent_1],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        pledge_result = {
            "goal_id": goal_data.get("goal_id", f"RDM-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "timestamp": datetime.now().isoformat(),
            "result": result.raw if hasattr(result, "raw") else str(result)
        }
        
        return pledge_result

    def conduct_reflection_checkin(self, goal_id: str, check_in_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Facilitate daily/weekly reflection check-in
        
        Args:
            goal_id: Unique identifier for the goal
            check_in_data: User's reflection input and progress data
            
        Returns:
            Reflection analysis and guidance
        """
        task = Task(
            description=f"""Conduct a reflection check-in for goal: {goal_id}
            
            Check-in Data:
            - User Status: {check_in_data.get('status', 'Not provided')}
            - Progress Notes: {check_in_data.get('notes', 'None')}
            - Challenges Faced: {check_in_data.get('challenges', 'None')}
            - Days Since Last Check-in: {check_in_data.get('days_since_last', 0)}
            
            Your tasks:
            1. Analyze the user's progress and self-reported status
            2. Identify patterns (consistency, struggles, progress)
            3. Provide constructive feedback and encouragement
            4. Ask reflective questions to deepen self-awareness
            5. Suggest adjustments if needed (goal modification, support resources)
            6. Determine if the user is on track (Done / Partially Done / Not Done)
            7. Flag any concerns that might require intervention
            
            Format as JSON with:
            - progress_status: "on_track", "needs_support", or "at_risk"
            - reflection_feedback: personalized feedback message
            - reflective_questions: list of questions for deeper reflection
            - recommendations: actionable suggestions
            - flags_for_agent_2: any data that should be passed to verification agent
            """,
            expected_output="""JSON response with progress analysis, feedback, reflective questions, 
                             and recommendations.""",
            agent=self.agent_1
        )
        
        crew = Crew(
            agents=[self.agent_1],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        
        reflection_result = {
            "goal_id": goal_id,
            "check_in_timestamp": datetime.now().isoformat(),
            "check_in_number": check_in_data.get("check_in_number", 1),
            "result": result.raw if hasattr(result, "raw") else str(result)
        }
        
        return reflection_result

    def initiate_goal_verification(self, goal_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Initiate goal completion verification process
        
        Args:
            goal_id: Unique identifier for the goal
            completion_data: Data related to goal completion claim
            
        Returns:
            Verification initiation details and flags for Agent 2
        """
        task = Task(
            description=f"""Initiate verification for goal completion: {goal_id}
            
            Completion Data:
            - User Claims Completion: {completion_data.get('user_claims_done', False)}
            - Completion Evidence: {completion_data.get('evidence', 'None provided')}
            - Verification Method: {completion_data.get('verification_method', 'Not specified')}
            - Self-Assessment: {completion_data.get('self_assessment', 'Done / Partially Done / Not Done')}
            
            Your tasks:
            1. Review the user's claim and evidence
            2. Assess the self-reported completion status
            3. Determine the appropriate verification method:
               - Self-verification (Y/N input)
               - Third-party app integration (fitness apps, habit trackers, etc.)
               - IoT device data (smart devices, sensors)
               - External confirmation (from other users, organizations)
            4. Prepare verification request with all necessary data
            5. Set verification expectations and timeline
            6. Flag comprehensive data for Agent 2 (Verification Agent)
            
            Format as JSON with:
            - verification_request_id: unique identifier
            - verification_method_selected: chosen verification approach
            - verification_criteria: what needs to be verified
            - evidence_summary: summary of provided evidence
            - verification_input_required: what input is needed (e.g., 'Y' for confirmed)
            - flag_for_agent_2: complete data package for verification agent
            - estimated_verification_time: expected time to complete verification
            """,
            expected_output="""JSON response with verification request details and complete 
                             data package for Agent 2.""",
            agent=self.agent_1
        )
        
        crew = Crew(
            agents=[self.agent_1],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        
        verification_initiation = {
            "goal_id": goal_id,
            "verification_request_id": f"VRF-{goal_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "initiated_at": datetime.now().isoformat(),
            "result": result.raw if hasattr(result, "raw") else str(result),
            "flagged_for_agent_2": True,
            "agent_2_data_package": {
                "goal_id": goal_id,
                "completion_data": completion_data,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return verification_initiation

    def get_agent_status(self) -> Dict[str, str]:
        """Get the current status of Agent 1"""
        return {
            "agent_name": "Agent 1: Goal-Setting and Pledge Management",
            "status": "active",
            "llm_model": "google/gemini-2.5-flash" if self.llm else "default",
            "capabilities": [
                "Goal selection guidance (SDG/ESG alignment)",
                "RDM token pledge management",
                "Daily/weekly reflection check-ins",
                "Goal completion verification initiation",
                "Data flagging for Agent 2"
            ]
        }


# Example usage functions for testing
def example_goal_selection():
    """Example: Guide user through goal selection"""
    rdm_system = RDMAgentSystem(verbose=True)
    
    user_input = "I want to reduce my carbon footprint and live more sustainably"
    result = rdm_system.guide_goal_selection(user_input)
    
    print("\n" + "="*70)
    print("GOAL SELECTION GUIDANCE")
    print("="*70)
    print(result)
    print("="*70 + "\n")
    
    return result


def example_pledge_capture():
    """Example: Capture pledge for a goal"""
    rdm_system = RDMAgentSystem(verbose=True)
    
    goal_data = {
        "goal_id": "RDM-001",
        "goal_description": "Reduce single-use plastic consumption by 80% over 30 days",
        "pledge_amount": 100,
        "duration": "30 days",
        "verification_method": "Daily photo log + weekly self-assessment"
    }
    
    result = rdm_system.capture_pledge(goal_data)
    
    print("\n" + "="*70)
    print("PLEDGE CAPTURE")
    print("="*70)
    print(result)
    print("="*70 + "\n")
    
    return result


def example_reflection_checkin():
    """Example: Conduct reflection check-in"""
    rdm_system = RDMAgentSystem(verbose=True)
    
    check_in_data = {
        "check_in_number": 7,
        "status": "Partially Done",
        "notes": "Successfully avoided plastic bags this week, but struggled with food packaging",
        "challenges": "Hard to find plastic-free alternatives for some products",
        "days_since_last": 7
    }
    
    result = rdm_system.conduct_reflection_checkin("RDM-001", check_in_data)
    
    print("\n" + "="*70)
    print("REFLECTION CHECK-IN")
    print("="*70)
    print(result)
    print("="*70 + "\n")
    
    return result


def example_verification_initiation():
    """Example: Initiate goal verification"""
    rdm_system = RDMAgentSystem(verbose=True)
    
    completion_data = {
        "user_claims_done": True,
        "evidence": "30-day photo log completed, reduced plastic use by 85%",
        "verification_method": "Self-verification + photo evidence review",
        "self_assessment": "Done"
    }
    
    result = rdm_system.initiate_goal_verification("RDM-001", completion_data)
    
    print("\n" + "="*70)
    print("VERIFICATION INITIATION")
    print("="*70)
    print(result)
    print("="*70 + "\n")
    
    return result


class VeritasAgent:
    """
    Agent 2: Veritas - Final Judgment and Token Distribution Agent
    
    Role: Analyzes goal outcomes, verifies completion, and distributes RDM tokens
          between Reward and Remorse buckets based on performance.
    """
    
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        
        # Configure Gemini LLM
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
            self.llm = LLM(
                model="google/gemini-2.5-flash",
                api_key=gemini_api_key
            )
            self.logger.info("Configured Gemini 2.5 Flash LLM for Veritas Agent")
        else:
            self.llm = None
            self.logger.warning("GEMINI_API_KEY not found, using default LLM")
        
        # Initialize Agent 2
        self.agent_2 = self._create_agent_2()
        self.logger.info("Veritas Agent initialized")

    def _create_agent_2(self) -> Agent:
        """
        Agent 2: Veritas - Final Judgment and Token Distribution
        
        Role: Impartial judge that analyzes goal completion, verifies evidence,
              and distributes tokens fairly based on outcome analysis
        """
        agent_2 = Agent(
            role='Veritas - Final Judgment and Token Distribution Specialist',
            goal="""Analyze goal outcomes with absolute fairness, verify completion evidence, 
                    determine success levels (Done/Partial/Not Done), and distribute RDM tokens 
                    between Reward and Remorse buckets. Trigger impact ledger updates and 
                    smart contract actions.""",
            backstory="""You are Veritas, the embodiment of truth and justice in the RDM ecosystem. 
                        With unwavering impartiality, you analyze evidence, verify claims, and make 
                        final judgments on goal completion. You understand behavioral psychology, 
                        evidence evaluation, and the importance of fair accountability. Your decisions 
                        determine whether pledged tokens go to the Reward Bucket (success), Remorse 
                        Bucket (failure), or are split (partial success). You consider self-reporting, 
                        peer verification, third-party data, and IoT evidence. You also award bonus 
                        tokens for exceptional efforts and assign impact badges. Your judgment is 
                        final, fair, and based solely on evidence and predefined criteria.""",
            verbose=self.verbose,
            llm=self.llm,
            allow_delegation=False
        )
        
        self.logger.info("Created Agent 2: Veritas - Final Judgment Specialist")
        return agent_2

    def retrieve_and_analyze_data(self, goal_id: str, flagged_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Retrieve reflection and verification data from Agent 1
        
        Args:
            goal_id: Unique identifier for the goal
            flagged_data: Data package flagged by Agent 1
            
        Returns:
            Structured analysis of all available data
        """
        task = Task(
            description=f"""Retrieve and analyze all data for goal: {goal_id}
            
            Flagged Data from Agent 1:
            {flagged_data}
            
            Your tasks:
            1. Review all reflection check-in data provided by Agent 1
            2. Examine the user's completion claim and self-assessment
            3. Analyze all provided evidence (photos, logs, receipts, IoT data)
            4. Review peer verification input (if applicable)
            5. Check third-party app data or external confirmations
            6. Identify any inconsistencies or gaps in evidence
            7. Assess the reliability and credibility of each evidence source
            8. Compile a comprehensive evidence summary
            
            Format as JSON with:
            - data_retrieved: confirmation of data sources accessed
            - evidence_quality: assessment of evidence strength
            - self_assessment: user's claimed completion status
            - peer_verification: peer validator input (if any)
            - third_party_data: external app/IoT verification (if any)
            - inconsistencies: any discrepancies found
            - reliability_score: 0-100 score for evidence credibility
            - preliminary_assessment: initial judgment before final analysis
            """,
            expected_output="""JSON response with comprehensive data analysis and evidence assessment.""",
            agent=self.agent_2
        )
        
        crew = Crew(
            agents=[self.agent_2],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        
        analysis_result = {
            "goal_id": goal_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "data_analysis": result.raw if hasattr(result, "raw") else str(result)
        }
        
        return analysis_result

    def determine_outcome(self, goal_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Analyze outcome and determine success level
        
        Args:
            goal_id: Unique identifier for the goal
            analysis_data: Comprehensive analysis from retrieve_and_analyze_data
            
        Returns:
            Final judgment with success percentage and outcome category
        """
        task = Task(
            description=f"""Determine the final outcome for goal: {goal_id}
            
            Analysis Data:
            {analysis_data}
            
            Your tasks:
            1. Evaluate the evidence against the original success criteria
            2. Consider all data sources and their reliability
            3. Determine the actual completion percentage (0-100%)
            4. Categorize the outcome:
               - ✅ SUCCESS (Done): 80-100% completion
               - 🔶 PARTIAL: 40-79% completion  
               - ❌ FAILURE (Not Done): 0-39% completion
            5. Provide detailed reasoning for your judgment
            6. Highlight what was achieved vs. what was promised
            7. Note any exceptional efforts or mitigating circumstances
            8. Determine if bonus tokens should be awarded
            9. Assign an appropriate impact badge level
            
            Format as JSON with:
            - outcome_category: "SUCCESS", "PARTIAL", or "FAILURE"
            - completion_percentage: 0-100 number
            - achievement_summary: what was accomplished
            - shortfall_summary: what was not achieved (if applicable)
            - judgment_reasoning: detailed explanation of the decision
            - exceptional_efforts: any noteworthy efforts beyond expectation
            - bonus_eligibility: whether bonus tokens should be awarded
            - impact_badge: recommended badge level and name
            - confidence_level: 0-100 confidence in this judgment
            """,
            expected_output="""JSON response with final outcome determination and detailed reasoning.""",
            agent=self.agent_2
        )
        
        crew = Crew(
            agents=[self.agent_2],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        
        outcome_result = {
            "goal_id": goal_id,
            "judgment_timestamp": datetime.now().isoformat(),
            "final_outcome": result.raw if hasattr(result, "raw") else str(result)
        }
        
        return outcome_result

    def distribute_tokens(self, goal_id: str, outcome_data: Dict[str, Any], pledge_amount: int) -> Dict[str, Any]:
        """
        Task: Allocate pledged tokens to Reward/Remorse buckets
        
        Args:
            goal_id: Unique identifier for the goal
            outcome_data: Final outcome determination from determine_outcome
            pledge_amount: Original RDM token pledge amount
            
        Returns:
            Token distribution details and bucket allocations
        """
        task = Task(
            description=f"""Distribute {pledge_amount} RDM tokens for goal: {goal_id}
            
            Outcome Data:
            {outcome_data}
            
            Your tasks:
            1. Review the final outcome category and completion percentage
            2. Calculate token distribution using these rules:
               
               SUCCESS (80-100%):
               - 100% → Reward Bucket
               - 0% → Remorse Bucket
               
               PARTIAL (40-79%):
               - Calculate proportional split based on completion %
               - Example: 60% completion = 60% to Reward, 40% to Remorse
               
               FAILURE (0-39%):
               - 0% → Reward Bucket
               - 100% → Remorse Bucket
            
            3. Calculate bonus tokens (if applicable):
               - Exceptional effort: +5% of pledge
               - Peer verification bonus: +5 tokens
               - Innovation bonus: +10 tokens
            
            4. Prepare distribution transaction details
            5. Generate visual representation data (pie chart percentages)
            6. Create distribution summary message
            
            Format as JSON with:
            - total_pledge: original pledge amount
            - reward_bucket_amount: tokens allocated to Reward
            - remorse_bucket_amount: tokens allocated to Remorse
            - reward_percentage: percentage to Reward
            - remorse_percentage: percentage to Remorse
            - bonus_tokens: any bonus tokens awarded
            - bonus_breakdown: explanation of bonus calculations
            - total_received: reward_bucket + bonus_tokens
            - distribution_visualization: pie chart data
            - distribution_message: user-friendly summary
            - transaction_hash: mock smart contract transaction ID
            """,
            expected_output="""JSON response with complete token distribution details.""",
            agent=self.agent_2
        )
        
        crew = Crew(
            agents=[self.agent_2],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        
        distribution_result = {
            "goal_id": goal_id,
            "distribution_timestamp": datetime.now().isoformat(),
            "pledge_amount": pledge_amount,
            "distribution_details": result.raw if hasattr(result, "raw") else str(result)
        }
        
        return distribution_result

    def trigger_impact_ledger(self, goal_id: str, outcome_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Update impact ledger and trigger smart contract actions
        
        Args:
            goal_id: Unique identifier for the goal
            outcome_summary: Complete outcome and distribution data
            
        Returns:
            Impact ledger update confirmation and smart contract details
        """
        task = Task(
            description=f"""Update impact ledger and execute smart contract for goal: {goal_id}
            
            Outcome Summary:
            {outcome_summary}
            
            Your tasks:
            1. Prepare impact ledger entry with:
               - Goal details and SDG alignment
               - Outcome category and completion percentage
               - Token distribution details
               - Environmental/social impact metrics
               - Timestamp and verification method
            
            2. Generate smart contract transaction data:
               - Contract address (mock)
               - Transaction hash
               - Token transfer details
               - Execution status
            
            3. Award impact badge:
               - Badge level (Bronze/Silver/Gold/Platinum)
               - Badge name based on goal type
               - Badge metadata
            
            4. Calculate impact metrics:
               - CO2 saved, waste reduced, etc. (if applicable)
               - SDG contribution score
               - Community impact rating
            
            5. Prepare notification data for user
            
            Format as JSON with:
            - ledger_entry_id: unique ledger entry identifier
            - smart_contract_hash: blockchain transaction hash
            - contract_address: smart contract address (mock)
            - execution_status: "completed" or "pending"
            - impact_badge: badge details (level, name, image_url)
            - impact_metrics: measurable impact achieved
            - sdg_contribution: SDG alignment and impact score
            - notification_data: user notification message
            - ledger_timestamp: timestamp of ledger update
            - verification_proof: immutable proof of outcome
            """,
            expected_output="""JSON response with ledger update and smart contract execution details.""",
            agent=self.agent_2
        )
        
        crew = Crew(
            agents=[self.agent_2],
            tasks=[task],
            verbose=self.verbose,
            llm=self.llm
        )
        
        result = crew.kickoff()
        
        ledger_result = {
            "goal_id": goal_id,
            "ledger_update_timestamp": datetime.now().isoformat(),
            "ledger_and_contract": result.raw if hasattr(result, "raw") else str(result)
        }
        
        return ledger_result

    def complete_verification_cycle(self, goal_id: str, flagged_data: Dict[str, Any], pledge_amount: int) -> Dict[str, Any]:
        """
        Complete verification cycle: Retrieve → Analyze → Distribute → Ledger Update
        
        Args:
            goal_id: Unique identifier for the goal
            flagged_data: Data package from Agent 1
            pledge_amount: Original RDM token pledge
            
        Returns:
            Complete verification outcome with all details
        """
        self.logger.info(f"Starting complete verification cycle for goal: {goal_id}")
        
        # Step 1: Retrieve and analyze data
        analysis = self.retrieve_and_analyze_data(goal_id, flagged_data)
        
        # Step 2: Determine outcome
        outcome = self.determine_outcome(goal_id, analysis)
        
        # Step 3: Distribute tokens
        distribution = self.distribute_tokens(goal_id, outcome, pledge_amount)
        
        # Step 4: Update impact ledger
        ledger = self.trigger_impact_ledger(goal_id, {
            "analysis": analysis,
            "outcome": outcome,
            "distribution": distribution
        })
        
        # Compile complete result
        complete_result = {
            "goal_id": goal_id,
            "verification_cycle_completed": datetime.now().isoformat(),
            "steps": {
                "1_data_analysis": analysis,
                "2_outcome_determination": outcome,
                "3_token_distribution": distribution,
                "4_ledger_update": ledger
            },
            "summary": {
                "pledge_amount": pledge_amount,
                "outcome_category": "extracted_from_outcome",  # Will be parsed from result
                "tokens_to_reward": "extracted_from_distribution",
                "tokens_to_remorse": "extracted_from_distribution",
                "impact_badge": "extracted_from_ledger",
                "smart_contract_hash": "extracted_from_ledger"
            }
        }
        
        self.logger.info(f"Verification cycle completed for goal: {goal_id}")
        return complete_result

    def get_agent_status(self) -> Dict[str, str]:
        """Get the current status of Agent 2"""
        return {
            "agent_name": "Agent 2: Veritas - Final Judgment and Token Distribution",
            "status": "active",
            "llm_model": "google/gemini-2.5-flash" if self.llm else "default",
            "capabilities": [
                "Evidence retrieval and analysis",
                "Outcome determination (Success/Partial/Failure)",
                "Token distribution (Reward/Remorse buckets)",
                "Bonus token allocation",
                "Impact ledger updates",
                "Smart contract execution",
                "Impact badge assignment",
                "Peer verification analysis"
            ]
        }


# Example usage functions for Agent 2
def example_verification_cycle():
    """Example: Complete verification cycle"""
    veritas = VeritasAgent(verbose=True)
    
    # Simulated data from Agent 1
    flagged_data = {
        "goal_description": "Run a school recycling drive for 2 weeks",
        "pledge_amount": 100,
        "duration": "14 days",
        "verification_method": "Photo evidence + peer verification",
        "reflection_data": {
            "check_ins_completed": 5,
            "last_check_in": "Day 14",
            "status": "Partial",
            "notes": "Completed 3 drives instead of 7, faced scheduling challenges"
        },
        "completion_claim": {
            "user_claims_done": True,
            "self_assessment": "Partially Done",
            "evidence": [
                "Photos of 3 recycling events",
                "Journal entries documenting process",
                "Weight measurements: 45kg plastic collected"
            ],
            "peer_verification": {
                "verified_by": "Teacher Sarah Johnson",
                "rating": "Moderate success (60%)",
                "comments": "Student showed dedication, drive was done 3 times with good impact"
            }
        }
    }
    
    result = veritas.complete_verification_cycle("RDM-001", flagged_data, 100)
    
    print("\n" + "="*70)
    print("COMPLETE VERIFICATION CYCLE - VERITAS AGENT 2")
    print("="*70)
    print(result)
    print("="*70 + "\n")
    
    return result


def example_token_distribution_only():
    """Example: Token distribution for different outcomes"""
    veritas = VeritasAgent(verbose=True)
    
    # SUCCESS example
    outcome_success = {
        "outcome_category": "SUCCESS",
        "completion_percentage": 95,
        "achievement_summary": "Completed all recycling drives with excellent participation"
    }
    
    # PARTIAL example
    outcome_partial = {
        "outcome_category": "PARTIAL",
        "completion_percentage": 60,
        "achievement_summary": "Completed 3 out of 7 planned drives, collected 45kg plastic"
    }
    
    # FAILURE example
    outcome_failure = {
        "outcome_category": "FAILURE",
        "completion_percentage": 25,
        "achievement_summary": "Only completed 1 drive, minimal impact"
    }
    
    print("\n" + "="*70)
    print("TOKEN DISTRIBUTION EXAMPLES")
    print("="*70 + "\n")
    
    for outcome_type, outcome_data in [("SUCCESS", outcome_success), 
                                        ("PARTIAL", outcome_partial), 
                                        ("FAILURE", outcome_failure)]:
        print(f"\n--- {outcome_type} Scenario ---")
        result = veritas.distribute_tokens(f"RDM-{outcome_type}", outcome_data, 100)
        print(result)
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("RDM AGENT SYSTEM: Agent 1 + Agent 2 (Veritas)")
    print("="*70 + "\n")
    
    # Check for command line arguments to run specific examples
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Agent 1 commands
        if command == "goal":
            example_goal_selection()
        elif command == "pledge":
            example_pledge_capture()
        elif command == "checkin":
            example_reflection_checkin()
        elif command == "verify-init":
            example_verification_initiation()
        
        # Agent 2 commands
        elif command == "veritas-cycle":
            example_verification_cycle()
        elif command == "token-distribution":
            example_token_distribution_only()
        
        # Combined commands
        elif command == "agent1":
            print("Running all Agent 1 examples...\n")
            example_goal_selection()
            example_pledge_capture()
            example_reflection_checkin()
            example_verification_initiation()
        elif command == "agent2":
            print("Running all Agent 2 examples...\n")
            example_verification_cycle()
            example_token_distribution_only()
        elif command == "all":
            print("Running all Agent 1 + Agent 2 examples...\n")
            example_goal_selection()
            example_pledge_capture()
            example_reflection_checkin()
            example_verification_initiation()
            example_verification_cycle()
            example_token_distribution_only()
        elif command == "full-flow":
            print("Running complete RDM flow: Agent 1 -> Agent 2...\n")
            print("\n" + "="*70)
            print("STEP 1: GOAL SELECTION (Agent 1)")
            print("="*70)
            example_goal_selection()
            
            print("\n" + "="*70)
            print("STEP 2: PLEDGE CAPTURE (Agent 1)")
            print("="*70)
            example_pledge_capture()
            
            print("\n" + "="*70)
            print("STEP 3: REFLECTION CHECK-IN (Agent 1)")
            print("="*70)
            example_reflection_checkin()
            
            print("\n" + "="*70)
            print("STEP 4: VERIFICATION INITIATION (Agent 1)")
            print("="*70)
            example_verification_initiation()
            
            print("\n" + "="*70)
            print("STEP 5: COMPLETE VERIFICATION CYCLE (Agent 2 - Veritas)")
            print("="*70)
            example_verification_cycle()
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("\n  Agent 1 Commands:")
            print("    goal          - Example goal selection guidance")
            print("    pledge        - Example pledge capture")
            print("    checkin       - Example reflection check-in")
            print("    verify-init   - Example verification initiation")
            print("    agent1        - Run all Agent 1 examples")
            print("\n  Agent 2 Commands:")
            print("    veritas-cycle - Complete verification cycle")
            print("    token-distribution - Token distribution examples")
            print("    agent2        - Run all Agent 2 examples")
            print("\n  Combined Commands:")
            print("    full-flow     - Complete RDM flow (Agent 1 -> Agent 2)")
            print("    all           - Run all examples")
    else:
        print("Usage: python rdm_agents.py [command]")
        print("\nAvailable commands:")
        print("\n  Agent 1 Commands:")
        print("    goal          - Example goal selection guidance")
        print("    pledge        - Example pledge capture")
        print("    checkin       - Example reflection check-in")
        print("    verify-init   - Example verification initiation")
        print("    agent1        - Run all Agent 1 examples")
        print("\n  Agent 2 Commands:")
        print("    veritas-cycle - Complete verification cycle")
        print("    token-distribution - Token distribution examples")
        print("    agent2        - Run all Agent 2 examples")
        print("\n  Combined Commands:")
        print("    full-flow     - Complete RDM flow (Agent 1 -> Agent 2)")
        print("    all           - Run all examples")
        print("\n" + "="*70)
        print("Running status check for both agents...")
        print("="*70 + "\n")
        
        # Agent 1 status
        rdm_system = RDMAgentSystem(verbose=False)
        status1 = rdm_system.get_agent_status()
        
        print("Agent 1 Status:")
        print(f"  Name: {status1['agent_name']}")
        print(f"  Status: {status1['status']}")
        print(f"  LLM Model: {status1['llm_model']}")
        print(f"  Capabilities:")
        for capability in status1['capabilities']:
            print(f"    - {capability}")
        
        # Agent 2 status
        print("\n" + "-"*70 + "\n")
        veritas = VeritasAgent(verbose=False)
        status2 = veritas.get_agent_status()
        
        print("Agent 2 Status:")
        print(f"  Name: {status2['agent_name']}")
        print(f"  Status: {status2['status']}")
        print(f"  LLM Model: {status2['llm_model']}")
        print(f"  Capabilities:")
        for capability in status2['capabilities']:
            print(f"    - {capability}")
        
        print("\n" + "="*70)

