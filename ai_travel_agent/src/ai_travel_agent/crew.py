from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff, llm
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from langchain_openai import ChatOpenAI  # ✅ modern import


@CrewBase
class TripPlannerCrew():
    """Trip planning multi-agent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @llm
    def llm(self):
        """Centralized LLM definition for all agents and tasks"""
        return ChatOpenAI(
            model="gpt-4o-mini",  # or "gpt-4o" if you prefer
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    @before_kickoff
    def before_crew(self, inputs):
        print("Running before kickoff with inputs:", inputs)
        if "cities" in inputs and isinstance(inputs["cities"], str):
            inputs["cities"] = [city.strip() for city in inputs["cities"].split(",")]
        return inputs

    @after_kickoff
    def after_crew(self, output):
        print("Crew execution complete. Processing output...")
        output.raw += "\n\n---\nTrip planning completed by TripPlannerCrew."
        return output

    @agent
    def destination_selector(self) -> Agent:
        return Agent(
            config=self.agents_config['destination_selector'],  # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()],
            llm=self.llm()
        )

    @agent
    def local_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['local_expert'],  # type: ignore[index]
            verbose=True,
            llm=self.llm()
        )

    @agent
    def itinerary_builder(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_builder'],  # type: ignore[index]
            verbose=True,
            llm=self.llm()
        )

    @agent
    def budget_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['budget_advisor'],  # type: ignore[index]
            verbose=True,
            llm=self.llm()
        )

    @agent
    def booking_assistant(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_assistant'],  # type: ignore[index]
            verbose=True,
            llm=self.llm()
        )

    @task
    def select_destination_task(self) -> Task:
        return Task(
            config=self.tasks_config['select_destination_task'],  # type: ignore[index]
        )

    @task
    def gather_local_info_task(self) -> Task:
        return Task(
            config=self.tasks_config['gather_local_info_task'],  # type: ignore[index]
        )

    @task
    def build_itinerary_task(self) -> Task:
        return Task(
            config=self.tasks_config['build_itinerary_task'],  # type: ignore[index]
        )

    @task
    def optimize_budget_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_budget_task'],  # type: ignore[index]
        )

    @task
    def find_booking_options_task(self) -> Task:
        return Task(
            config=self.tasks_config['find_booking_options_task'],  # type: ignore[index]
            output_file='output/trip_plan.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TripPlanner crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            llm=self.llm()
        )


# # ✅ Usage example:
# if __name__ == "__main__":
#     TripPlannerCrew().crew().kickoff(inputs={
#         "origin": "Jersey City",
#         "cities": "Paris, Barcelona, Rome",
#         "date_range": "2026-06-01 to 2026-06-10",
#         "interests": "food, art, culture"
#     })
