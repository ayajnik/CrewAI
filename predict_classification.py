"""
Standalone classification script - runs independently of CrewAI
Avoids threading conflicts with TensorFlow
"""
import sys
import json
import tensorflow as tf
import numpy as np
from pathlib import Path
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.applications.resnet50 import preprocess_input


def classify_image(image_path, model_path, class_names_path):
    """Classify a single image"""
    try:
        # Load class names
        with open(class_names_path, 'r') as f:
            class_names = json.load(f)
        
        # Load model
        model = tf.keras.models.load_model(model_path)
        
        # Load and preprocess image
        img = keras_image.load_img(image_path, target_size=(224, 224))
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # Get class name
        predicted_class = class_names[predicted_class_idx]
        
        # Get top 3 predictions
        top_3_idx = np.argsort(predictions[0])[-3:][::-1]
        top_3_results = [
            {
                "class": class_names[idx],
                "confidence": float(predictions[0][idx])
            }
            for idx in top_3_idx
        ]
        
        result = {
            "image": str(image_path),
            "predicted_class": predicted_class,
            "confidence": confidence,
            "top_3_predictions": top_3_results,
            "model_type": "ResNet50",
            "status": "success"
        }
        
        return result
        
    except Exception as e:
        return {
            "image": str(image_path),
            "error": str(e),
            "status": "failed"
        }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(json.dumps({"error": "Usage: python predict_classification.py <image_path> <model_path> <class_names_path>"}))
        sys.exit(1)
    
    image_path = sys.argv[1]
    model_path = sys.argv[2]
    class_names_path = sys.argv[3]
    
    result = classify_image(image_path, model_path, class_names_path)
    print(json.dumps(result, indent=2))

