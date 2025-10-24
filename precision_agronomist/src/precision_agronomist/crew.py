from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# Import custom tools
from precision_agronomist.tools.model_downloader_tool import ModelDownloaderTool
from precision_agronomist.tools.image_loader_tool import ImageLoaderTool
from precision_agronomist.tools.image_classifier_tool import ImageClassifierTool
from precision_agronomist.tools.yolo_detector_tool import YOLODetectorTool


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
                ImageClassifierTool(),
                YOLODetectorTool()
            ]
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],  # type: ignore[index]
            verbose=True
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
    def classify_images_task(self) -> Task:
        return Task(
            config=self.tasks_config['classify_images_task'],  # type: ignore[index]
            agent=self.image_analyst()
        )

    @task
    def detect_diseases_task(self) -> Task:
        return Task(
            config=self.tasks_config['detect_diseases_task'],  # type: ignore[index]
            agent=self.image_analyst()
        )

    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],  # type: ignore[index]
            agent=self.report_generator(),
            output_file='plant_disease_report.md'
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
