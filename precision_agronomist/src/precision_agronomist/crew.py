from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# Import custom tools
from precision_agronomist.tools.model_downloader_tool import ModelDownloaderTool
from precision_agronomist.tools.image_loader_tool import ImageLoaderTool
from precision_agronomist.tools.yolo_detector_tool import YOLODetectorTool
from precision_agronomist.tools.database_storage_tool import DatabaseStorageTool
from precision_agronomist.tools.trend_analysis_tool import TrendAnalysisTool
from precision_agronomist.tools.email_alert_tool import EmailAlertTool
from precision_agronomist.tools.chatbot_tool import FarmerChatbotTool
from precision_agronomist.tools.translation_tool import TranslationTool
# Note: ImageClassifierTool removed - using YOLO-only approach to avoid TensorFlow conflicts


@CrewBase
class PrecisionAgronomist():
    """PrecisionAgronomist crew for plant disease detection"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
    @agent
    def model_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['model_manager'],  # type: ignore[index]
            verbose=True,
            tools=[ModelDownloaderTool()]
        )

    @agent
    def image_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['image_analyst'],  # type: ignore[index]
            verbose=True,
            tools=[
                ImageLoaderTool(),
                YOLODetectorTool()
                # Note: Removed ImageClassifierTool to avoid TensorFlow compatibility issues
                # YOLO provides both classification and localization
            ]
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],  # type: ignore[index]
            verbose=True,
            tools=[EmailAlertTool()]
        )
    
    @agent
    def farmer_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['farmer_advisor'],  # type: ignore[index]
            verbose=True,
            tools=[FarmerChatbotTool(), TranslationTool()]
        )
    
    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analyst'],  # type: ignore[index]
            verbose=True,
            tools=[DatabaseStorageTool(), TrendAnalysisTool()]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    @task
    def download_models_task(self) -> Task:
        return Task(
            config=self.tasks_config['download_models_task'],  # type: ignore[index]
            agent=self.model_manager()
        )

    @task
    def load_test_images_task(self) -> Task:
        return Task(
            config=self.tasks_config['load_test_images_task'],  # type: ignore[index]
            agent=self.image_analyst()
        )

    @task
    def detect_diseases_task(self) -> Task:
        return Task(
            config=self.tasks_config['detect_diseases_task'],  # type: ignore[index]
            agent=self.image_analyst()
        )

    @task
    def store_detections_task(self) -> Task:
        return Task(
            config=self.tasks_config['store_detections_task'],  # type: ignore[index]
            agent=self.data_analyst()
        )
    
    @task
    def analyze_trends_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_trends_task'],  # type: ignore[index]
            agent=self.data_analyst()
        )
    
    @task
    def send_alert_task(self) -> Task:
        return Task(
            config=self.tasks_config['send_alert_task'],  # type: ignore[index]
            agent=self.report_generator()
        )
    
    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],  # type: ignore[index]
            agent=self.report_generator(),
            output_file='plant_disease_report.md'
        )
    
    @task
    def chatbot_assistance_task(self) -> Task:
        return Task(
            config=self.tasks_config['chatbot_assistance_task'],  # type: ignore[index]
            agent=self.farmer_advisor()
        )
    
    @task
    def translate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['translate_report_task'],  # type: ignore[index]
            agent=self.farmer_advisor()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PrecisionAgronomist crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
