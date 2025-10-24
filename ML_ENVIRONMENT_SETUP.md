# 🔧 ML Environment Setup (Python 3.12)

## Problem
TensorFlow and Ultralytics don't support Python 3.13 yet. Your CrewAI is running on Python 3.13, but ML models need Python 3.12.

## Solution
Use a separate Python 3.12 virtual environment (`ml_env`) for ML model predictions.

---

## 📋 Step 1: Install Python 3.12

If you don't have Python 3.12 installed:

1. Download from: https://www.python.org/downloads/release/python-3120/
2. Install **alongside** your Python 3.13 (don't uninstall 3.13!)
3. During installation, **DO NOT** check "Add to PATH" (to avoid conflicts)

---

## 🚀 Step 2: Run Setup Script

```powershell
.\setup_ml_env.ps1
```

This script will:
- ✅ Find Python 3.12 on your system
- ✅ Create `ml_env\` virtual environment
- ✅ Install TensorFlow 2.17.0 (Python 3.12 compatible)
- ✅ Install Ultralytics (YOLO)
- ✅ Install OpenCV and other ML dependencies

---

## ✅ Step 3: Install CrewAI (Python 3.13 - Current Environment)

```powershell
cd precision_agronomist
pip install -e .
```

This installs **only CrewAI** dependencies (no TensorFlow conflicts!).

---

## 🎯 Step 4: Run Your Crew

```powershell
cd precision_agronomist
crewai run
```

**How it works:**
- 🤖 CrewAI runs in Python 3.13 environment
- 🔧 When ML prediction needed, tools call `ml_env\Scripts\python.exe` (Python 3.12)
- 🌱 Subprocess isolation = No conflicts!

---

## 📁 Project Structure After Setup

```
CrewAI/
├── ml_env/                          ← Python 3.12 environment (TensorFlow, YOLO)
│   └── Scripts/
│       └── python.exe               ← Used for predictions
│
├── precision_agronomist/
│   └── .venv/                       ← Python 3.13 environment (CrewAI)
│
├── predict_classification.py        ← Runs in ml_env
├── predict_yolo.py                  ← Runs in ml_env
└── setup_ml_env.ps1                 ← Setup script
```

---

## 🔍 Verification

Test that everything works:

```powershell
# Test ML environment
.\ml_env\Scripts\python.exe -c "import tensorflow; import ultralytics; print('✅ ML env OK!')"

# Test CrewAI environment
cd precision_agronomist
python -c "import crewai; print('✅ CrewAI OK!')"

# Run the crew
crewai run
```

---

## 🐛 Troubleshooting

### "Python 3.12 not found"
- Install Python 3.12 from python.org
- You can have multiple Python versions installed
- Try: `py -3.12 --version` to verify

### "ml_env not found" warning
- Run `.\setup_ml_env.ps1` from the project root
- Verify `ml_env\Scripts\python.exe` exists

### Models still not working
- Verify models exist:
  - `artifacts/model_training/model.h5`
  - `artifacts/yolo_detection/plant_disease_run1/weights/best.pt`
- Test prediction manually:
  ```powershell
  .\ml_env\Scripts\python.exe predict_classification.py "data/test/image.jpg" "artifacts/model_training/model.h5" "artifacts/model_training/class_names.json"
  ```

---

## 💡 Why This Approach?

| Alternative | Issue |
|-------------|-------|
| Downgrade to Python 3.12 everywhere | Lose Python 3.13 features, affects other projects |
| Wait for TensorFlow 3.13 support | Could take months |
| **Use separate ml_env (Python 3.12)** | ✅ **Works now, no conflicts, best of both worlds** |

---

## 🎓 How It Works Internally

```
CrewAI (Python 3.13)
    ↓
Tool: ImageClassifierTool
    ↓
Subprocess: ml_env\Scripts\python.exe predict_classification.py
    ↓
TensorFlow (Python 3.12) → Returns JSON
    ↓
Tool parses result → Agent gets prediction
```

**Complete isolation = Zero conflicts!**

---

**Status**: ✅ Ready to use after running `setup_ml_env.ps1`

