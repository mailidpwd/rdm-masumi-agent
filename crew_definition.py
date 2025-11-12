import os
from crewai import Agent, Crew, Task, LLM
from logging_config import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResearchCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        
        # Configure Gemini LLM
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            # Set the API key as environment variable for CrewAI to pick up
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
            # Use CrewAI's LLM with Google Gemini 2.5 Flash model
            self.llm = LLM(
                model="google/gemini-2.5-flash",
                api_key=gemini_api_key
            )
            self.logger.info("Configured Gemini 2.5 Flash LLM using CrewAI LLM")
        else:
            self.llm = None
            self.logger.warning("GEMINI_API_KEY not found, using default LLM")
        
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")
        
        researcher = Agent(
            role='Research Analyst',
            goal='Find and analyze key information',
            backstory='Expert at extracting information',
            verbose=self.verbose,
            llm=self.llm
        )

        writer = Agent(
            role='Content Summarizer',
            goal='Create clear summaries from research',
            backstory='Skilled at transforming complex information',
            verbose=self.verbose,
            llm=self.llm
        )

        self.logger.info("Created research and writer agents")

        crew = Crew(
            agents=[researcher, writer],
            tasks=[
                Task(
                    description='Research: {text}',
                    expected_output='Detailed research findings about the topic',
                    agent=researcher
                ),
                Task(
                    description='Write summary',
                    expected_output='Clear and concise summary of the research findings',
                    agent=writer
                )
            ],
            llm=self.llm
        )
        self.logger.info("Crew setup completed")
        return crew