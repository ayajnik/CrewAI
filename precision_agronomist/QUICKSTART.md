# 🚀 Quick Start Guide

## Step 1: Install Dependencies

```bash
cd precision_agronomist
pip install -e .
```

## Step 2: Verify Models Exist

Check that these files are present:
- ✅ `../artifacts/model_training/model.h5`
- ✅ `../artifacts/yolo_detection/plant_disease_run1/weights/best.pt`
- ✅ `../artifacts/model_training/class_names.json`

## Step 3: Run the Crew

```bash
python src/precision_agronomist/main.py
```

## Step 4: View Results

Results will be saved to:
- 📄 Report: `precision_agronomist/plant_disease_report.md`
- 🖼️ Annotated Images: `../artifacts/yolo_detection/predictions/crew_results/`

---

## 🎛️ Quick Configuration

Edit `src/precision_agronomist/main.py`:

```python
inputs = {
    'num_images': 5,              # Change number of images to analyze
    'detection_threshold': 0.25,  # Change YOLO confidence threshold
}
```

---

## 🔄 Workflow Overview

```
Model Manager → Image Analyst → Report Generator
     ↓              ↓                  ↓
  Download      Classify           Generate
   Models       + Detect           Report
```

**Sequential Tasks:**
1. ✅ Verify/Download Models
2. ✅ Load Test Images
3. ✅ Classify with ResNet50
4. ✅ Detect with YOLOv8
5. ✅ Generate Report

---

## 💡 Tips

- Start with 3-5 images for testing
- Use confidence threshold 0.25 for more detections
- Use confidence threshold 0.5+ for high-confidence only
- Check `plant_disease_report.md` for comprehensive analysis

---

## ❗ Troubleshooting

**Issue**: Models not found  
**Fix**: Ensure you're running from the CrewAI directory and models exist

**Issue**: No images in test folder  
**Fix**: Check `../data/test/` contains `.jpg` or `.png` files

**Issue**: Subprocess timeout  
**Fix**: Normal on first run (model loading), subsequent runs are faster

---

**Ready to go!** 🌱

