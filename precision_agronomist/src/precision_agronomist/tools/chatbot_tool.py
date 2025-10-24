from crewai.tools import BaseTool
from typing import Type, ClassVar, Dict, Any
from pydantic import BaseModel, Field
import json


class ChatbotInput(BaseModel):
    """Input schema for farmer chatbot."""
    farmer_question: str = Field(..., description="Question or query from the farmer")
    context: str = Field(default="", description="Additional context like recent detection results")
    language: str = Field(default="en", description="Preferred language for response")


class FarmerChatbotTool(BaseTool):
    name: str = "Agricultural Advisor Chatbot"
    description: str = (
        "An intelligent chatbot that answers farmer questions about plant diseases, "
        "treatments, prevention strategies, and agricultural best practices. "
        "Provides context-aware advice based on recent disease detections. "
        "Supports multiple languages for global accessibility."
    )
    args_schema: Type[BaseModel] = ChatbotInput
    
    # Knowledge base for common questions (ClassVar to prevent Pydantic field creation)
    KNOWLEDGE_BASE: ClassVar[Dict[str, Any]] = {
        "apple_scab": {
            "description": "Fungal disease causing dark, scabby spots on leaves and fruit",
            "treatment": [
                "Apply fungicides (captan or mancozeb) during early season",
                "Remove and destroy infected leaves and fruit",
                "Prune trees to improve air circulation",
                "Choose resistant apple varieties"
            ],
            "prevention": [
                "Apply dormant oil spray in spring",
                "Rake and remove fallen leaves",
                "Maintain proper tree spacing",
                "Monitor weather conditions (wet weather favors disease)"
            ]
        },
        "grape_black_rot": {
            "description": "Fungal disease causing rotted grapes and leaf spots",
            "treatment": [
                "Apply fungicides (mancozeb, myclobutanil) at first sign",
                "Remove infected berries and mummified fruit",
                "Prune out infected canes",
                "Improve vineyard sanitation"
            ],
            "prevention": [
                "Remove mummified berries from vines and ground",
                "Prune for better air circulation",
                "Apply protective fungicides before rain",
                "Use resistant grape varieties"
            ]
        },
        "general": {
            "best_practices": [
                "Regular monitoring and early detection",
                "Proper irrigation management",
                "Crop rotation when applicable",
                "Maintain good soil health",
                "Use disease-resistant varieties",
                "Practice integrated pest management (IPM)"
            ],
            "organic_options": [
                "Neem oil for fungal diseases",
                "Copper-based fungicides",
                "Biological controls (beneficial microbes)",
                "Cultural practices (spacing, pruning, sanitation)"
            ]
        }
    }

    def _run(
        self, 
        farmer_question: str,
        context: str = "",
        language: str = "en"
    ) -> str:
        """
        Answer farmer questions with agricultural expertise
        
        Args:
            farmer_question: The farmer's question
            context: Additional context (e.g., recent detections)
            language: Preferred language for response
            
        Returns:
            Expert advice as formatted text
        """
        try:
            # Normalize question
            question_lower = farmer_question.lower()
            
            # Determine response based on question content
            response = self._generate_response(question_lower, context)
            
            # Format response
            formatted_response = {
                "question": farmer_question,
                "answer": response,
                "language": language,
                "confidence": "high",
                "additional_resources": [
                    "Consult local agricultural extension office",
                    "Check university agricultural programs",
                    "Join local farming communities"
                ]
            }
            
            # Note: In production, integrate with Translation API for non-English
            if language != "en":
                formatted_response["note"] = f"Response in English. Use Translation Tool to convert to {language}"
            
            return self._format_chat_response(formatted_response)
            
        except Exception as e:
            return f"⚠️ Error processing question: {str(e)}\nPlease rephrase or contact support."
    
    def _generate_response(self, question_lower, context):
        """Generate appropriate response based on question"""
        
        # Treatment questions
        if any(word in question_lower for word in ['treat', 'cure', 'fix', 'remedy']):
            if 'apple_scab' in question_lower or ('apple' in question_lower and 'scab' in question_lower):
                return self._format_treatment_advice('apple_scab')
            elif 'grape' in question_lower and 'black' in question_lower:
                return self._format_treatment_advice('grape_black_rot')
            else:
                return self._format_general_treatment_advice()
        
        # Prevention questions
        elif any(word in question_lower for word in ['prevent', 'avoid', 'stop', 'protect']):
            if 'apple_scab' in question_lower:
                return self._format_prevention_advice('apple_scab')
            elif 'grape' in question_lower:
                return self._format_prevention_advice('grape_black_rot')
            else:
                return self._format_general_prevention_advice()
        
        # Organic farming questions
        elif 'organic' in question_lower or 'natural' in question_lower:
            return self._format_organic_advice()
        
        # Identification questions
        elif any(word in question_lower for word in ['what is', 'identify', 'recognize']):
            if context:
                return f"Based on recent detections: {context}\n\nUse the YOLO detection system to automatically identify diseases in your crop images."
            else:
                return "I can help identify diseases! Upload images of your plants and I'll use AI to detect diseases with high accuracy."
        
        # General advice
        elif any(word in question_lower for word in ['best practice', 'advice', 'recommendation', 'suggest']):
            return self._format_best_practices()
        
        # Cost/economic questions
        elif any(word in question_lower for word in ['cost', 'price', 'expensive', 'cheap']):
            return self._format_economic_advice()
        
        # Timing questions
        elif any(word in question_lower for word in ['when', 'timing', 'season']):
            return self._format_timing_advice()
        
        # Default response
        else:
            return self._format_default_response(question_lower)
    
    def _format_treatment_advice(self, disease):
        """Format treatment advice for specific disease"""
        info = self.KNOWLEDGE_BASE.get(disease, {})
        treatments = info.get('treatment', [])
        
        response = f"**Treatment for {disease.replace('_', ' ').title()}:**\n\n"
        response += f"*Description:* {info.get('description', 'Fungal disease')}\n\n"
        response += "**Recommended Actions:**\n"
        for i, treatment in enumerate(treatments, 1):
            response += f"{i}. {treatment}\n"
        
        response += "\n⏰ **Timing:** Start treatment immediately upon detection"
        response += "\n📋 **Follow-up:** Monitor treated areas daily for 1-2 weeks"
        
        return response
    
    def _format_prevention_advice(self, disease):
        """Format prevention advice"""
        info = self.KNOWLEDGE_BASE.get(disease, {})
        prevention = info.get('prevention', [])
        
        response = f"**Prevention Strategies for {disease.replace('_', ' ').title()}:**\n\n"
        for i, tip in enumerate(prevention, 1):
            response += f"{i}. {tip}\n"
        
        response += "\n💡 **Key Tip:** Prevention is always better than cure!"
        return response
    
    def _format_general_treatment_advice(self):
        """General treatment advice"""
        return """**General Disease Treatment Guide:**

1. **Immediate Actions:**
   - Isolate infected plants if possible
   - Remove and destroy severely infected plant parts
   - Improve air circulation around plants

2. **Chemical Control:**
   - Choose appropriate fungicide for the specific disease
   - Follow label instructions carefully
   - Apply during cool, dry weather when possible

3. **Cultural Practices:**
   - Adjust watering to avoid leaf wetness
   - Remove crop debris
   - Sanitize tools between plants

4. **Monitoring:**
   - Check plants daily during treatment
   - Document progress with photos
   - Adjust strategy if no improvement after 7-10 days

📞 **Consult a professional agronomist for severe infections**
        """
    
    def _format_general_prevention_advice(self):
        """General prevention advice"""
        best_practices = self.KNOWLEDGE_BASE['general']['best_practices']
        
        response = "**General Disease Prevention Best Practices:**\n\n"
        for i, practice in enumerate(best_practices, 1):
            response += f"{i}. {practice}\n"
        
        response += "\n🌱 **Remember:** Healthy plants are more resistant to diseases!"
        return response
    
    def _format_organic_advice(self):
        """Organic farming advice"""
        organic_options = self.KNOWLEDGE_BASE['general']['organic_options']
        
        response = "**Organic Disease Management Options:**\n\n"
        for i, option in enumerate(organic_options, 1):
            response += f"{i}. {option}\n"
        
        response += "\n✅ **Certified organic:** Check labels for OMRI certification"
        response += "\n🌍 **Sustainable:** Better for environment and beneficial insects"
        return response
    
    def _format_best_practices(self):
        """General best practices"""
        return """**Agricultural Best Practices for Disease Management:**

**🔍 Monitoring & Detection:**
- Weekly field inspections
- Use AI detection tools for early identification
- Keep records of disease occurrences

**💧 Water Management:**
- Water early morning (leaves dry during day)
- Avoid overhead watering when possible
- Ensure proper drainage

**🌿 Plant Health:**
- Balanced fertilization (avoid excess nitrogen)
- Proper spacing for air circulation
- Choose disease-resistant varieties

**🧹 Sanitation:**
- Clean tools between plants
- Remove plant debris promptly
- Rotate crops annually

**📊 Record Keeping:**
- Document disease occurrences
- Track treatment effectiveness
- Monitor weather patterns

**👥 Community Support:**
- Share information with neighboring farmers
- Join local agricultural groups
- Attend extension workshops
        """
    
    def _format_economic_advice(self):
        """Economic considerations"""
        return """**Economic Considerations for Disease Management:**

**💰 Cost-Effective Strategies:**
1. Prevention is cheaper than treatment
2. Early detection saves money on advanced treatments
3. AI monitoring reduces labor costs
4. Resistant varieties may cost more upfront but save long-term

**📊 Cost-Benefit Analysis:**
- Calculate potential crop loss value
- Compare treatment costs vs. expected yield protection
- Consider labor time in total cost

**🎯 Priority Investments:**
1. Disease monitoring system (like this AI tool)
2. Quality preventive sprays
3. Resistant seed varieties
4. Proper irrigation system

**💡 Money-Saving Tips:**
- Buy fungicides in bulk when on sale
- Use integrated pest management (IPM)
- Share equipment with neighboring farms
- Apply treatments at optimal times (avoid waste)

📈 **ROI:** Preventive measures typically return $3-5 for every $1 spent
        """
    
    def _format_timing_advice(self):
        """Timing and seasonal advice"""
        return """**Timing Guidelines for Disease Management:**

**🌸 Spring (Bud Break to Flowering):**
- Apply preventive fungicides
- Monitor for early disease signs
- Prune for air circulation

**☀️ Summer (Growing Season):**
- Weekly monitoring essential
- Treat at first sign of disease
- Manage irrigation carefully
- Watch for weather-related outbreaks

**🍂 Fall (Harvest to Dormancy):**
- Remove infected plant material
- Apply dormant sprays
- Plan crop rotation
- Clean and sanitize tools

**❄️ Winter (Dormant Season):**
- Order resistant varieties for spring
- Plan disease management strategy
- Review previous season records
- Attend agricultural training

**⚡ Critical Timing Tips:**
- Spray fungicides BEFORE rain, not after
- Treat early morning or evening (avoid heat)
- Don't spray during bloom (protect pollinators)
- Allow proper re-entry time after chemical applications

**📅 Disease-Specific Timing:**
- Apple scab: Start at green tip stage
- Black rot: Begin at bud break
- Downy mildew: Pre-bloom to fruit set
        """
    
    def _format_default_response(self, question):
        """Default helpful response"""
        return """**I'm here to help with plant disease questions!**

**I can assist with:**
- 🔬 Disease identification and diagnosis
- 💊 Treatment recommendations
- 🛡️ Prevention strategies
- 🌱 Organic farming options
- 💰 Cost-effective solutions
- ⏰ Timing and seasonal advice
- 📊 Best agricultural practices

**Popular Questions:**
- "How do I treat apple scab?"
- "What are organic options for fungal diseases?"
- "When should I apply fungicides?"
- "How can I prevent grape black rot?"

**Need specific help?** Please ask about:
- Specific disease treatment or prevention
- Organic vs. conventional methods
- Timing of applications
- Cost considerations
- Best practices for your crop

🤝 **Tip:** The more specific your question, the better advice I can provide!
        """
    
    def _format_chat_response(self, response_data):
        """Format final chat response"""
        output = f"**Question:** {response_data['question']}\n\n"
        output += f"{response_data['answer']}\n\n"
        output += "---\n"
        output += "**Additional Resources:**\n"
        for resource in response_data['additional_resources']:
            output += f"• {resource}\n"
        
        if 'note' in response_data:
            output += f"\n📝 {response_data['note']}"
        
        output += "\n\n💬 **Need more help?** Ask another question anytime!"
        
        return output

