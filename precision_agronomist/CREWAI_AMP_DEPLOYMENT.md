# 🚀 CrewAI AMP Deployment Guide

## What is CrewAI AMP?

**CrewAI AMP (Agent Management Platform)** is a cloud deployment platform that allows you to:
- Deploy your CrewAI crews to the cloud
- Create web APIs from your agents
- Monitor agent performance and costs
- Scale your AI applications globally
- Share your crews with others

This guide shows you how to deploy the **Precision Agronomist** plant disease detection system to CrewAI AMP.

---

## 📋 Prerequisites

1. **CrewAI Account**
   - Sign up at [https://amp.crewai.com](https://amp.crewai.com)
   - Get your API key from the dashboard

2. **Project Ready**
   - Ensure all agents, tasks, and tools are working locally
   - Test with `crewai run` before deploying

3. **Environment Variables Configured**
   - Set up API keys (OpenAI, Groq, etc.)
   - Configure email credentials (for alerts)

---

## 🔧 Step 1: Install AMP CLI

First, ensure you have the latest CrewAI with AMP support:

```bash
pip install 'crewai[tools]' --upgrade
```

Verify AMP CLI is available:

```bash
crewai amp --help
```

---

## 🔐 Step 2: Authenticate with AMP

Login to your CrewAI AMP account:

```bash
crewai amp login
```

This will:
- Open your browser for authentication
- Store credentials securely
- Enable deployment commands

Verify authentication:

```bash
crewai amp whoami
```

---

## 📦 Step 3: Prepare for Deployment

### 3.1 Create Environment Configuration

Create a `.env` file with required credentials:

```bash
# precision_agronomist/.env
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Email alert configuration (optional)
ALERT_SENDER_EMAIL=alerts@yourdomain.com
ALERT_SENDER_PASSWORD=your_email_password
FARMER_EMAIL=farmer@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3.2 Create AMP Configuration

Create `amp.yaml` in the `precision_agronomist` folder:

```yaml
name: precision-agronomist
description: AI-powered plant disease detection system with YOLO, trend analysis, and farmer chatbot
version: 1.0.0

# Runtime configuration
runtime:
  python_version: "3.10"
  max_execution_time: 600  # 10 minutes
  memory: 2048  # 2GB RAM

# Environment variables (do NOT include secrets here)
environment:
  PREFERRED_LANGUAGE: "en"
  TREND_ANALYSIS_DAYS: "30"
  NUM_IMAGES: "5"
  DETECTION_THRESHOLD: "0.25"

# API endpoints
api:
  enabled: true
  endpoints:
    - path: /detect
      method: POST
      description: "Detect plant diseases in uploaded images"
      parameters:
        - name: num_images
          type: integer
          default: 5
        - name: detection_threshold
          type: float
          default: 0.25
        - name: preferred_language
          type: string
          default: "en"
    
    - path: /chatbot
      method: POST
      description: "Ask the agricultural advisor chatbot"
      parameters:
        - name: question
          type: string
          required: true
        - name: language
          type: string
          default: "en"
    
    - path: /trends
      method: GET
      description: "Get disease trend analysis"
      parameters:
        - name: days
          type: integer
          default: 30

# Storage configuration
storage:
  - type: sqlite
    path: disease_tracking.db
    description: "Historical disease detection database"
  
  - type: file
    path: artifacts/
    description: "Model weights and detection results"

# External dependencies (installed in ml_env)
external_services:
  - name: ml_environment
    type: subprocess
    python_path: ml_env/Scripts/python.exe
    description: "Separate Python 3.12 environment for TensorFlow/YOLO"

# Monitoring
monitoring:
  enabled: true
  metrics:
    - detections_per_session
    - alert_frequency
    - chatbot_interactions
    - translation_requests
```

---

## 🚢 Step 4: Deploy to AMP

### 4.1 Validate Configuration

Check for any issues before deploying:

```bash
cd precision_agronomist
crewai amp validate
```

### 4.2 Deploy

Deploy your crew to AMP:

```bash
crewai amp deploy
```

This will:
- Package your crew code
- Upload to CrewAI cloud
- Create API endpoints
- Generate deployment URL

### 4.3 Check Deployment Status

Monitor deployment progress:

```bash
crewai amp status
```

---

## 🌐 Step 5: Access Your Deployed Crew

### Web Interface

Access the web dashboard:
- URL: `https://amp.crewai.com/crews/[your-crew-id]`
- Features:
  - Run crew manually
  - View execution history
  - Monitor costs and performance
  - Configure environment variables

### API Endpoints

Your crew will have REST API endpoints:

```bash
# Disease Detection
curl -X POST https://api.amp.crewai.com/crews/[your-crew-id]/detect \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "num_images": 5,
    "detection_threshold": 0.25,
    "preferred_language": "en"
  }'

# Chatbot
curl -X POST https://api.amp.crewai.com/crews/[your-crew-id]/chatbot \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I treat apple scab?",
    "language": "en"
  }'

# Trend Analysis
curl -X GET https://api.amp.crewai.com/crews/[your-crew-id]/trends?days=30 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 🔄 Step 6: Update Deployment

When you make changes to your crew:

```bash
# Make your code changes
# Test locally first
crewai run

# Deploy update
crewai amp deploy --update
```

---

## 📊 Step 7: Monitor Performance

### View Logs

```bash
crewai amp logs --tail 100
```

### Monitor Metrics

```bash
crewai amp metrics --last 24h
```

### Cost Tracking

```bash
crewai amp costs --month current
```

---

## 🌍 Frontend Integration

### React Example

```javascript
// Example: Call your deployed crew from React frontend

const detectDiseases = async (numImages, language) => {
  const response = await fetch('https://api.amp.crewai.com/crews/[your-crew-id]/detect', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.REACT_APP_CREWAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      num_images: numImages,
      detection_threshold: 0.25,
      preferred_language: language
    })
  });
  
  const result = await response.json();
  return result;
};

const askChatbot = async (question, language) => {
  const response = await fetch('https://api.amp.crewai.com/crews/[your-crew-id]/chatbot', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.REACT_APP_CREWAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question: question,
      language: language
    })
  });
  
  const result = await response.json();
  return result;
};
```

### HTML/JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Precision Agronomist</title>
</head>
<body>
    <h1>Plant Disease Detection</h1>
    
    <!-- Language Selector -->
    <select id="language">
        <option value="en">English</option>
        <option value="es">Español</option>
        <option value="hi">हिन्दी</option>
        <option value="fr">Français</option>
    </select>
    
    <!-- Detection Button -->
    <button onclick="detectDiseases()">Detect Diseases</button>
    
    <!-- Chatbot -->
    <div id="chatbot">
        <input type="text" id="question" placeholder="Ask a question...">
        <button onclick="askQuestion()">Ask</button>
        <div id="chatResponse"></div>
    </div>
    
    <script>
        const API_KEY = 'your_api_key_here';
        const CREW_ID = 'your_crew_id_here';
        
        async function detectDiseases() {
            const language = document.getElementById('language').value;
            
            const response = await fetch(`https://api.amp.crewai.com/crews/${CREW_ID}/detect`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${API_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    num_images: 5,
                    detection_threshold: 0.25,
                    preferred_language: language
                })
            });
            
            const result = await response.json();
            console.log('Detection results:', result);
            // Display results in your UI
        }
        
        async function askQuestion() {
            const question = document.getElementById('question').value;
            const language = document.getElementById('language').value;
            
            const response = await fetch(`https://api.amp.crewai.com/crews/${CREW_ID}/chatbot`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${API_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    language: language
                })
            });
            
            const result = await response.json();
            document.getElementById('chatResponse').innerText = result.answer;
        }
    </script>
</body>
</html>
```

---

## 🎯 Advanced Features

### Scheduled Runs

Set up automatic daily disease detection:

```yaml
# In amp.yaml
schedules:
  - name: daily_monitoring
    cron: "0 8 * * *"  # Every day at 8 AM
    endpoint: /detect
    parameters:
      num_images: 10
      detection_threshold: 0.25
```

### Webhooks

Get notified when high-severity diseases are detected:

```yaml
# In amp.yaml
webhooks:
  - event: alert_sent
    url: https://yourdomain.com/webhook/disease-alert
    method: POST
```

### Custom Domains

Map your own domain:

```bash
crewai amp domain add disease-detection.yourdomain.com
```

---

## 🔒 Security Best Practices

1. **Never commit secrets** to version control
2. Use **environment variables** for sensitive data
3. **Rotate API keys** regularly
4. Enable **rate limiting** in AMP dashboard
5. Use **HTTPS only** for API calls
6. Implement **authentication** in your frontend

---

## 💰 Cost Optimization

1. **Cache results** when possible
2. Use **smaller models** for non-critical tasks
3. Set **execution timeouts** to prevent runaway costs
4. Monitor **token usage** in dashboard
5. Use **batch processing** for multiple images

---

## 🐛 Troubleshooting

### Deployment Failed

```bash
# Check validation errors
crewai amp validate

# View detailed logs
crewai amp logs --level error

# Redeploy with verbose output
crewai amp deploy --verbose
```

### ML Environment Issues

Since your project uses a separate `ml_env` for TensorFlow/YOLO:

1. **Option 1**: Include ml_env in deployment (larger package)
2. **Option 2**: Use containerized deployment with Dockerfile
3. **Option 3**: Switch to cloud-based inference APIs

### Performance Issues

```bash
# Increase memory allocation
# Edit amp.yaml:
runtime:
  memory: 4096  # 4GB

# Increase timeout
runtime:
  max_execution_time: 1200  # 20 minutes
```

---

## 📚 Additional Resources

- **CrewAI AMP Documentation**: https://docs.crewai.com/amp
- **API Reference**: https://docs.crewai.com/amp/api
- **Community Forum**: https://community.crewai.com
- **Example Projects**: https://github.com/crewai/examples

---

## 🎉 Next Steps

1. **Deploy your crew** to AMP
2. **Build a frontend** (React, Vue, or simple HTML)
3. **Add authentication** for your users
4. **Monitor usage** and optimize costs
5. **Scale** as your user base grows
6. **Submit to challenges** and share with the community!

---

## 📞 Support

- **Email**: support@crewai.com
- **Discord**: https://discord.gg/crewai
- **GitHub Issues**: https://github.com/crewai/crewai/issues

---

**Good luck with your deployment! 🚀🌱**

