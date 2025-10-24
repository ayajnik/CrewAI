# 🚀 CrewAI AMP Deployment Guide

## Overview

Your Precision Agronomist project is now **CrewAI AMP ready**! This guide will walk you through deploying your multi-agent plant disease detection system to the cloud.

---

## 📋 Prerequisites

1. **CrewAI AMP Account**
   - Sign up at [https://amp.crewai.com](https://amp.crewai.com)
   - Get your API key from the dashboard

2. **Project Ready**
   - All agents, tasks, and tools are working locally
   - Test with `crewai run` before deploying

3. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your API keys and credentials

---

## 🔧 Step 1: Install AMP CLI

```powershell
# Install/upgrade CrewAI with AMP support
pip install 'crewai[tools]' --upgrade

# Verify AMP CLI is available
crewai amp --help
```

---

## 🔐 Step 2: Configure Environment

1. **Copy environment template:**
   ```powershell
   copy .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```env
   # Required API Keys
   OPENAI_API_KEY=your_openai_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   
   # Optional: Email alerts
   ALERT_SENDER_EMAIL=alerts@yourdomain.com
   ALERT_SENDER_PASSWORD=your_app_password
   FARMER_EMAIL=farmer@example.com
   
   # AMP Configuration
   CREWAI_AMP_API_KEY=your_amp_api_key_here
   ```

---

## 🚀 Step 3: Deploy to AMP

### Option A: Use the Deployment Script (Recommended)

```powershell
# Navigate to project
cd precision_agronomist

# Run deployment script
.\deploy_amp.ps1
```

### Option B: Manual Deployment

```powershell
# 1. Login to AMP
crewai amp login

# 2. Validate configuration
crewai amp validate

# 3. Deploy
crewai amp deploy

# 4. Check status
crewai amp status
```

---

## 🌐 Step 4: Access Your Deployed Crew

### Web Dashboard
- URL: `https://amp.crewai.com/crews/[your-crew-id]`
- Monitor agent performance
- View execution history
- Configure environment variables

### API Endpoints

Your crew will have these REST API endpoints:

#### 1. **Disease Detection** - `POST /detect`
```bash
curl -X POST https://api.amp.crewai.com/crews/[your-crew-id]/detect \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "num_images": 5,
    "detection_threshold": 0.25,
    "preferred_language": "en"
  }'
```

#### 2. **Chatbot** - `POST /chatbot`
```bash
curl -X POST https://api.amp.crewai.com/crews/[your-crew-id]/chatbot \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I treat apple scab?",
    "language": "en"
  }'
```

#### 3. **Trend Analysis** - `GET /trends`
```bash
curl -X GET https://api.amp.crewai.com/crews/[your-crew-id]/trends?days=30 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 🧪 Step 5: Test Your API

### Using the Test Script

```powershell
# Edit test_amp_api.py with your credentials
python test_amp_api.py
```

### Manual Testing

1. **Get your crew ID** from the AMP dashboard
2. **Get your API key** from the dashboard
3. **Update the test script** with your credentials
4. **Run the tests**

---

## 📊 Step 6: Monitor Performance

### View Logs
```powershell
crewai amp logs --tail 100
```

### Monitor Metrics
```powershell
crewai amp metrics --last 24h
```

### Cost Tracking
```powershell
crewai amp costs --month current
```

---

## 🔄 Step 7: Update Deployment

When you make changes to your crew:

```powershell
# Make your code changes
# Test locally first
crewai run

# Deploy update
crewai amp deploy --update
```

---

## 🌍 Frontend Integration

### React Example

```javascript
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
  
  return await response.json();
};
```

### HTML/JavaScript Example

```html
<script>
const API_KEY = 'your_api_key_here';
const CREW_ID = 'your_crew_id_here';

async function detectDiseases() {
  const response = await fetch(`https://api.amp.crewai.com/crews/${CREW_ID}/detect`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      num_images: 5,
      detection_threshold: 0.25,
      preferred_language: 'en'
    })
  });
  
  const result = await response.json();
  console.log('Detection results:', result);
}
</script>
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

```powershell
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

```powershell
# Check validation errors
crewai amp validate

# View detailed logs
crewai amp logs --level error

# Redeploy with verbose output
crewai amp deploy --verbose
```

### API Not Working

1. **Check API key** is correct
2. **Verify crew ID** in URL
3. **Check rate limits** in dashboard
4. **Review logs** for errors

### Performance Issues

```yaml
# Edit amp.yaml to increase resources
runtime:
  memory: 4096  # 4GB
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
2. **Test the API endpoints**
3. **Build a frontend** (React, Vue, or simple HTML)
4. **Add authentication** for your users
5. **Monitor usage** and optimize costs
6. **Scale** as your user base grows
7. **Submit to challenges** and share with the community!

---

## 📞 Support

- **Email**: support@crewai.com
- **Discord**: https://discord.gg/crewai
- **GitHub Issues**: https://github.com/crewai/crewai/issues

---

**Your Precision Agronomist is now AMP-ready! 🚀🌱**

Deploy it and start helping farmers worldwide! 🌍
