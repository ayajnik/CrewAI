from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import json
from pathlib import Path

class ImageClassifierInput(BaseModel):
    """Input schema for ImageClassifier."""
    image_path: str = Field(..., description="Absolute path to the image to classify")


class ImageClassifierTool(BaseTool):
    name: str = "Plant Disease Classifier"
    description: str = (
        "Classifies plant images using a trained ResNet50 model to detect diseases. "
        "Provide ONLY the image_path parameter. Model paths are automatically configured. "
        "Returns the predicted disease class and confidence score."
    )
    args_schema: Type[BaseModel] = ImageClassifierInput

    def _run(self, image_path: str) -> str:
        """
        Classify plant disease using ResNet50 via subprocess
        
        Args:
            image_path: Path to input image (absolute path)
            
        Returns:
            Classification results as JSON string
        """
        try:
            # Use fixed paths - don't let agent specify them
            model_path = "artifacts/model_training/model.h5"
            class_names_path = "artifacts/model_training/class_names.json"
            
            # Get absolute paths
            project_root = Path(__file__).parent.parent.parent.parent.parent
            script_path = project_root / "predict_classification.py"
            abs_model_path = project_root / model_path
            abs_class_names_path = project_root / class_names_path
            
            # Verify files exist
            if not script_path.exists():
                return json.dumps({
                    "image": str(image_path),
                    "error": f"Prediction script not found: {script_path}",
                    "status": "failed"
                })
            
            if not abs_model_path.exists():
                return json.dumps({
                    "image": str(image_path),
                    "error": f"Model file not found: {abs_model_path}. Please check the model exists.",
                    "status": "failed"
                })
            
            if not abs_class_names_path.exists():
                return json.dumps({
                    "image": str(image_path),
                    "error": f"Class names file not found: {abs_class_names_path}",
                    "status": "failed"
                })
            
            # Run classification in subprocess using ML environment Python
            # Use ml_env with Python 3.12 (TensorFlow compatible)
            ml_python = project_root / "ml_env" / "Scripts" / "python.exe"
            
            # Fallback to system python if ml_env doesn't exist
            if not ml_python.exists():
                import sys
                ml_python = Path(sys.executable)
                print(f"Warning: ml_env not found, using {ml_python}")
            
            result = subprocess.run(
                [str(ml_python), str(script_path), image_path, str(abs_model_path), str(abs_class_names_path)],
                capture_output=True,
                text=True,
                timeout=60,  # Increased timeout
                cwd=str(project_root)
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                error_result = {
                    "image": str(image_path),
                    "error": result.stderr if result.stderr else "Classification failed",
                    "status": "failed"
                }
                return json.dumps(error_result, indent=2)
            
        except subprocess.TimeoutExpired:
            error_result = {
                "image": str(image_path),
                "error": "Classification timeout after 60 seconds",
                "status": "failed"
            }
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {
                "image": str(image_path),
                "error": str(e),
                "status": "failed"
            }
            return json.dumps(error_result, indent=2)

