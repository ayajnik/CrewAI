"""
Standalone YOLO detection script - runs independently of CrewAI
Avoids threading conflicts
"""
import sys
import json
from ultralytics import YOLO
from pathlib import Path


def detect_diseases(image_path, model_path, conf_threshold=0.25, save_output=True):
    """Detect diseases in image using YOLO"""
    try:
        # Load YOLO model
        model = YOLO(model_path)
        
        # Run detection
        results = model.predict(
            source=image_path,
            conf=conf_threshold,
            save=save_output,
            project='artifacts/yolo_detection/predictions',
            name='crew_results',
            exist_ok=True,
            verbose=False
        )
        
        # Parse detections
        detections = []
        for result in results:
            boxes = result.boxes
            
            for i in range(len(boxes)):
                detection = {
                    'class': result.names[int(boxes.cls[i])],
                    'class_id': int(boxes.cls[i]),
                    'confidence': float(boxes.conf[i]),
                    'bbox': {
                        'x1': float(boxes.xyxy[i][0]),
                        'y1': float(boxes.xyxy[i][1]),
                        'x2': float(boxes.xyxy[i][2]),
                        'y2': float(boxes.xyxy[i][3])
                    }
                }
                detections.append(detection)
        
        output_result = {
            "image": str(image_path),
            "num_detections": len(detections),
            "detections": detections,
            "model_type": "YOLOv8n",
            "confidence_threshold": conf_threshold,
            "status": "success"
        }
        
        if save_output:
            output_result["annotated_image"] = "artifacts/yolo_detection/predictions/crew_results/"
        
        return output_result
        
    except Exception as e:
        return {
            "image": str(image_path),
            "error": str(e),
            "status": "failed"
        }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python predict_yolo.py <image_path> <model_path> [conf_threshold]"}))
        sys.exit(1)
    
    image_path = sys.argv[1]
    model_path = sys.argv[2]
    conf_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
    
    result = detect_diseases(image_path, model_path, conf_threshold)
    print(json.dumps(result, indent=2))

