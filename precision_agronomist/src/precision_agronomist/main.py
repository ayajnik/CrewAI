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
        # Google Drive URLs for your models (replace with actual URLs or set to None if models exist)
        # To skip downloading, set these to 'None' or provide empty strings
        'classification_model_url': 'None',  # Replace with your Google Drive URL or leave as 'None'
        'yolo_model_url': 'None',  # Replace with your Google Drive URL or leave as 'None'
        'class_names_url': 'None',  # Replace with your Google Drive URL or leave as 'None'
        
        # Prediction parameters
        'num_images': 5,  # Number of test images to analyze
        'detection_threshold': 0.25,  # YOLO confidence threshold (0-1)
        
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
        'classification_model_url': 'None',
        'yolo_model_url': 'None',
        'class_names_url': 'None',
        'num_images': 3,
        'detection_threshold': 0.25,
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
        'classification_model_url': 'None',
        'yolo_model_url': 'None',
        'class_names_url': 'None',
        'num_images': 2,
        'detection_threshold': 0.25,
        'current_date': str(datetime.now().strftime('%Y-%m-%d'))
    }
    
    try:
        PrecisionAgronomist().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    run()
