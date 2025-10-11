# src/ai_travel_agent/run.py

import os
from dotenv import load_dotenv
from src.ai_travel_agent.crew import TripPlannerCrew

load_dotenv()

if __name__ == '__main__':
    origin = input("Enter your origin city: ")
    cities = input("Enter destination cities (comma separated): ")
    date_range = input("Enter your travel date range: ")
    interests = input("Enter your interests: ")

    inputs = {
        "origin": origin,
        "cities": cities,
        "date_range": date_range,
        "interests": interests,
    }

    result = TripPlannerCrew().crew().kickoff(inputs)
    print("\nGenerated Trip Plan:\n")
    print(result.raw)
