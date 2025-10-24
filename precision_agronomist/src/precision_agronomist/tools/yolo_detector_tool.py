from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import json
from pathlib import Path


class YOLODetectorInput(BaseModel):
    """Input schema for YOLODetector."""
    image_path: str = Field(..., description="Absolute path to the image for object detection")
    conf_threshold: float = Field(
        default=0.25, 
        description="Confidence threshold for detections (0-1)"
    )


class YOLODetectorTool(BaseTool):
    name: str = "YOLO Plant Disease Detector"
    description: str = (
        "Detects and localizes plant diseases in images using YOLOv8 object detection. "
        "Provide ONLY the image_path parameter. The model path is automatically configured. "
        "Returns bounding boxes, class labels, and confidence scores for all detected diseases."
    )
    args_schema: Type[BaseModel] = YOLODetectorInput

    def _run(
        self, 
        image_path: str, 
        conf_threshold: float = 0.25
    ) -> str:
        """
        Detect plant diseases using YOLOv8 via subprocess
        
        Args:
            image_path: Path to input image (absolute path)
            conf_threshold: Detection confidence threshold
            
        Returns:
            Detection results as JSON string
        """
        try:
            # Use fixed model path - don't let agent specify it
            model_path = "artifacts/yolo_detection/plant_disease_run1/weights/best.pt"
            
            # Get absolute paths
            project_root = Path(__file__).parent.parent.parent.parent.parent
            script_path = project_root / "predict_yolo.py"
            abs_model_path = project_root / model_path
            
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
                    "error": f"YOLO model not found: {abs_model_path}. Please check the model exists.",
                    "status": "failed"
                })
            
            # Run detection in subprocess using ML environment Python
            # Use ml_env with Python 3.12 (TensorFlow/YOLO compatible)
            ml_python = project_root / "ml_env" / "Scripts" / "python.exe"
            
            # Fallback to system python if ml_env doesn't exist
            if not ml_python.exists():
                import sys
                ml_python = Path(sys.executable)
                print(f"Warning: ml_env not found, using {ml_python}")
            
            result = subprocess.run(
                [str(ml_python), str(script_path), image_path, str(abs_model_path), str(conf_threshold)],
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
                    "error": result.stderr if result.stderr else "Detection failed",
                    "status": "failed"
                }
                return json.dumps(error_result, indent=2)
            
        except subprocess.TimeoutExpired:
            error_result = {
                "image": str(image_path),
                "error": "Detection timeout after 60 seconds",
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

