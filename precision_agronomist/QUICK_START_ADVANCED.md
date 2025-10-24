# 🚀 Quick Start - Advanced Features

## ⚡ Installation (2 minutes)

```powershell
# Navigate to project
cd precision_agronomist

# Remove old translation package (if you installed it before)
pip uninstall googletrans -y

# Install new translation dependency (no conflicts!)
pip install deep-translator --upgrade

# Fix any httpx conflicts
pip install httpx --upgrade

# Done! ✅
```

---

## 🎯 Run Detection with All Features

```powershell
crewai run
```

This will:
1. ✅ Detect plant diseases with YOLO
2. ✅ Store results in database
3. ✅ Analyze historical trends
4. ✅ Send email alert (if high-severity)
5. ✅ Generate chatbot responses
6. ✅ Translate report to preferred language

---

## 📧 Email Alerts (Optional)

**Quick Setup:**
```powershell
$env:ALERT_SENDER_EMAIL = "your_email@gmail.com"
$env:ALERT_SENDER_PASSWORD = "your_app_password"
$env:FARMER_EMAIL = "recipient@example.com"
```

**Without Setup:** Alerts display in console (demo mode)

---

## 🌍 Change Language

Edit `main.py`:
```python
inputs = {
    'preferred_language': 'es',  # Spanish
    # OR: 'hi' (Hindi), 'fr' (French), etc.
}
```

**Supported:** English, Spanish, Hindi, French, Portuguese, Chinese, Arabic, Bengali, German, Japanese, Punjabi, Telugu, Marathi, Tamil, Urdu, Vietnamese, Italian, Thai, Korean, Russian, Swahili

---

## 💬 Test Chatbot

```python
from precision_agronomist.tools.chatbot_tool import FarmerChatbotTool

chatbot = FarmerChatbotTool()
response = chatbot._run(
    farmer_question="How do I treat apple scab?",
    language="en"
)
print(response)
```

---

## 📊 View Trend Analysis

```python
from precision_agronomist.tools.trend_analysis_tool import TrendAnalysisTool

analyzer = TrendAnalysisTool()
trends = analyzer._run(
    time_period_days=30,
    disease_focus="all"
)
print(trends)
```

Or check the database:
```powershell
sqlite3 disease_tracking.db "SELECT * FROM sessions ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🎨 Frontend Demo

1. Open `FRONTEND_EXAMPLE.html` in your browser
2. See the beautiful UI
3. Configure API endpoints (when deployed)
4. Test language selector
5. Try chatbot interface

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `ADVANCED_FEATURES_GUIDE.md` | Complete feature documentation |
| `CREWAI_AMP_DEPLOYMENT.md` | Deploy to production |
| `FRONTEND_EXAMPLE.html` | UI template for web app |
| `COMPETITION_READY_SUMMARY.md` | Competition strategy |

---

## 🏆 For Competition Demo

```powershell
# 1. Start detection
crewai run

# 2. Show output:
#    - Console logs (5 agents working)
#    - plant_disease_report.md
#    - Email alert (console)
#    - Database updates

# 3. Query trends:
sqlite3 disease_tracking.db "SELECT disease_class, COUNT(*) as count FROM detections GROUP BY disease_class ORDER BY count DESC;"

# 4. Show frontend:
# Open FRONTEND_EXAMPLE.html

# 5. Explain architecture:
# - 5 AI agents
# - Email alerts
# - Trend analysis
# - Chatbot
# - Multi-language
# - Deployment-ready
```

---

## ⚙️ Configuration

Edit `main.py` to customize:

```python
inputs = {
    'yolo_model_url': 'None',            # Or Google Drive URL
    'num_images': 5,                      # Images to analyze
    'detection_threshold': 0.25,          # Confidence threshold
    'trend_analysis_days': 30,            # Historical period
    'farmer_question_context': 'recent',  # Chatbot context
    'preferred_language': 'en',           # Output language
}
```

---

## 🐛 Troubleshooting

### Translation not working?
```powershell
pip install deep-translator --upgrade
pip install httpx --upgrade
```

### Database not found?
```powershell
# It's created automatically on first run
# Location: precision_agronomist/disease_tracking.db
```

### Email not sending?
- Check credentials are set
- Use Gmail App Password (not regular password)
- Without credentials, alerts show in console (normal!)

---

## 🎉 You're Ready!

**Everything is set up and ready to go!**

Run `crewai run` and watch the magic happen! 🚀🌱

Questions? Check the guides in this folder.

**Good luck! 🏆**

