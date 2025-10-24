# 🌱 Precision Agronomist - Plant Disease Detection with CrewAI

A CrewAI-powered system that uses ResNet50 classification and YOLOv8 object detection to analyze plant diseases.

## 📋 Prerequisites

Make sure you have the following installed in your main environment:
- Python 3.10+
- TensorFlow (for ResNet50 classification)
- Ultralytics (for YOLO detection)
- OpenCV

These should already be installed from your root `requirements.txt`.

## 🚀 Installation

1. Navigate to the precision_agronomist directory:
```bash
cd precision_agronomist
```

2. Install the package in editable mode:
```bash
pip install -e .
```

This will install all CrewAI-specific dependencies without TensorFlow (to avoid conflicts).

## 📁 Project Structure

```
CrewAI/
├── predict_classification.py          # Standalone ResNet50 classifier (subprocess)
├── predict_yolo.py                    # Standalone YOLO detector (subprocess)
├── data/test/                         # Test images directory
├── artifacts/
│   ├── model_training/
│   │   ├── model.h5                   # ResNet50 model
│   │   └── class_names.json           # Class names
│   └── yolo_detection/
│       └── plant_disease_run1/weights/
│           └── best.pt                # YOLO model
└── precision_agronomist/
    ├── pyproject.toml
    └── src/precision_agronomist/
        ├── main.py                    # Entry point
        ├── crew.py                    # Crew definition
        ├── config/
        │   ├── agents.yaml            # Agent configurations
        │   └── tasks.yaml             # Task definitions
        └── tools/
            ├── model_downloader_tool.py
            ├── image_loader_tool.py
            ├── image_classifier_tool.py
            └── yolo_detector_tool.py
```

## 🔧 Configuration

### Option 1: Use Existing Models (Recommended)

If your models are already in place (which they are), edit `main.py`:

```python
inputs = {
    'classification_model_url': 'None',  # Keep as 'None'
    'yolo_model_url': 'None',           # Keep as 'None'
    'class_names_url': 'None',          # Keep as 'None'
    'num_images': 5,                    # Adjust number of images
    'detection_threshold': 0.25,        # Adjust YOLO confidence
}
```

### Option 2: Download from Google Drive

If you need to download models, replace the URLs:

```python
inputs = {
    'classification_model_url': 'https://drive.google.com/file/d/YOUR_FILE_ID/view',
    'yolo_model_url': 'https://drive.google.com/file/d/YOUR_FILE_ID/view',
    'class_names_url': 'https://drive.google.com/file/d/YOUR_FILE_ID/view',
    'num_images': 5,
    'detection_threshold': 0.25,
}
```

## ▶️ Running the System

### Method 1: Using Python Directly

```bash
cd precision_agronomist
python src/precision_agronomist/main.py
```

### Method 2: Using Installed Script

```bash
cd precision_agronomist
run_crew
```

## 🎯 What the System Does

The CrewAI workflow consists of 5 sequential tasks:

### 1. **Download Models** (Model Manager Agent)
   - Downloads model artifacts from Google Drive (if URLs provided)
   - Or verifies existing models are in place
   - Checks: `model.h5`, `best.pt`, `class_names.json`

### 2. **Load Test Images** (Image Analyst Agent)
   - Randomly selects N images from `data/test/`
   - Returns absolute paths to selected images

### 3. **Classify Images** (Image Analyst Agent)
   - Runs ResNet50 classification on each image
   - Returns predicted disease class and confidence
   - Provides top 3 predictions
   - **Runs in isolated subprocess** (no TensorFlow conflicts!)

### 4. **Detect Diseases** (Image Analyst Agent)
   - Runs YOLO object detection on same images
   - Localizes disease regions with bounding boxes
   - Saves annotated images to `artifacts/yolo_detection/predictions/`
   - **Runs in isolated subprocess**

### 5. **Generate Report** (Report Generator Agent)
   - Combines results from classification and detection
   - Creates comprehensive markdown report
   - Saves to `plant_disease_report.md`

## 📊 Output

After running, you'll find:

1. **Console Output**: Real-time progress and results
2. **Report**: `precision_agronomist/plant_disease_report.md`
3. **Annotated Images**: `artifacts/yolo_detection/predictions/crew_results/`

## 🔍 Example Output Structure

```markdown
# Plant Disease Diagnostic Report

## Executive Summary
- Images Analyzed: 5
- Most Common Disease: Apple Scab
- Average Confidence: 87.3%

## Image Analysis

### Image 1: 0001aa74-bbd7-433b-a900-1dccab39d521.jpg

**Classification Results:**
- Predicted Class: apple_scab
- Confidence: 0.89
- Top 3: apple_scab (0.89), apple_black_rot (0.07), apple_healthy (0.03)

**Detection Results:**
- Detections Found: 3
- Regions: [bbox coordinates]
- Average Detection Confidence: 0.85

**Analysis:**
Classification and detection agree on apple_scab diagnosis...
```

## 🛠️ Troubleshooting

### Error: "Model file not found"
- Ensure models are in correct locations:
  - `artifacts/model_training/model.h5`
  - `artifacts/yolo_detection/plant_disease_run1/weights/best.pt`
  - `artifacts/model_training/class_names.json`

### Error: "No images found"
- Check that `data/test/` contains image files
- Supported formats: `.jpg`, `.jpeg`, `.png`

### Error: "Subprocess timeout"
- Increase timeout in tool files (default: 30 seconds)
- Or use GPU for faster inference

### CrewAI/TensorFlow Conflict
- The subprocess isolation should prevent this
- If issues persist, ensure you're using the standalone scripts

## 🎨 Customization

### Change Number of Images
Edit `main.py`:
```python
'num_images': 10,  # Analyze 10 images instead of 5
```

### Adjust YOLO Confidence
Edit `main.py`:
```python
'detection_threshold': 0.5,  # Higher = fewer but more confident detections
```

### Modify Agent Behavior
Edit `config/agents.yaml` and `config/tasks.yaml`

## 📝 Advanced Usage

### Training Mode
```bash
crewai train -n 5 -f training_output.json
```

### Testing Mode
```bash
crewai test -n 3 -m gpt-4
```

### Replay Task
```bash
crewai replay <task_id>
```

## 🔑 Key Features

✅ **No TensorFlow Conflicts**: Uses subprocess isolation  
✅ **Dual Model Analysis**: Both classification and detection  
✅ **Automated Workflow**: CrewAI handles task orchestration  
✅ **Professional Reports**: Markdown-formatted, ready to share  
✅ **Flexible Configuration**: Easy to customize via YAML  

## 📧 Support

For issues or questions, contact: ayushyajnik1@outlook.com

---

**Built with CrewAI** 🤖 | **Powered by ResNet50 & YOLOv8** 🌱

