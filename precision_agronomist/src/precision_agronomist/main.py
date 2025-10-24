#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from precision_agronomist.crew import PrecisionAgronomist

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the plant disease detection crew.
    """
    inputs = {
        # Google Drive URL for YOLO model (if you need to download it)
        # To skip downloading, set to 'None' (model should already exist)
        'yolo_model_url': 'None',  # Replace with your Google Drive URL or leave as 'None'
        
        # Prediction parameters
        'num_images': 5,  # Number of test images to analyze
        'detection_threshold': 0.25,  # YOLO confidence threshold (0-1)
        
        # Trend analysis
        'trend_analysis_days': 30,  # Days of historical data to analyze
        
        # Chatbot and translation
        'farmer_question_context': 'recent disease detections',  # Context for chatbot
        'preferred_language': 'en',  # Language code: 'en', 'es', 'hi', 'fr', etc.
        
        # Metadata
        'current_date': str(datetime.now().strftime('%Y-%m-%d'))
    }
    
    print("\n" + "="*60)
    print("🌱 PRECISION AGRONOMIST - Plant Disease Detection")
    print("="*60)
    print(f"Starting analysis on {inputs['current_date']}")
    print(f"Analyzing {inputs['num_images']} test images")
    print(f"Detection threshold: {inputs['detection_threshold']}")
    print("="*60 + "\n")
    
    try:
        result = PrecisionAgronomist().crew().kickoff(inputs=inputs)
        print("\n" + "="*60)
        print("✓ Plant Disease Detection Complete!")
        print("="*60)
        print(f"\nReport saved to: precision_agronomist/plant_disease_report.md")
        print("\nCheck the following locations for results:")
        print("  - Classification results: In the report")
        print("  - Detection visualizations: artifacts/yolo_detection/predictions/crew_results/")
        print("="*60 + "\n")
        return result
    except Exception as e:
        print("\n" + "="*60)
        print("✗ Error occurred during execution")
        print("="*60)
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'yolo_model_url': 'None',
        'num_images': 3,
        'detection_threshold': 0.25,
        'trend_analysis_days': 30,
        'farmer_question_context': 'recent disease detections',
        'preferred_language': 'en',
        'current_date': str(datetime.now().strftime('%Y-%m-%d'))
    }
    try:
        PrecisionAgronomist().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        PrecisionAgronomist().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'yolo_model_url': 'None',
        'num_images': 2,
        'detection_threshold': 0.25,
        'trend_analysis_days': 30,
        'farmer_question_context': 'recent disease detections',
        'preferred_language': 'en',
        'current_date': str(datetime.now().strftime('%Y-%m-%d'))
    }
    
    try:
        PrecisionAgronomist().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


# AMP API Endpoints
def detect_diseases_api(num_images: int = 5, detection_threshold: float = 0.25, preferred_language: str = "en"):
    """API endpoint for disease detection"""
    inputs = {
        'yolo_model_url': 'None',
        'num_images': num_images,
        'detection_threshold': detection_threshold,
        'trend_analysis_days': 30,
        'farmer_question_context': 'recent disease detections',
        'preferred_language': preferred_language,
        'current_date': str(datetime.now().strftime('%Y-%m-%d'))
    }
    
    try:
        result = PrecisionAgronomist().crew().kickoff(inputs=inputs)
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


def chatbot_api(question: str, language: str = "en"):
    """API endpoint for chatbot"""
    from precision_agronomist.tools.chatbot_tool import FarmerChatbotTool
    
    try:
        chatbot = FarmerChatbotTool()
        response = chatbot._run(
            farmer_question=question,
            language=language
        )
        return {
            "status": "success",
            "question": question,
            "answer": response,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


def trends_api(days: int = 30):
    """API endpoint for trend analysis"""
    from precision_agronomist.tools.trend_analysis_tool import TrendAnalysisTool
    
    try:
        analyzer = TrendAnalysisTool()
        trends = analyzer._run(time_period_days=days)
        return {
            "status": "success",
            "trends": trends,
            "period_days": days,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    run()
