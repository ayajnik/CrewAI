from crewai.tools import BaseTool
from typing import Type, ClassVar, Dict
from pydantic import BaseModel, Field
from deep_translator import GoogleTranslator
import json


class TranslationInput(BaseModel):
    """Input schema for translation."""
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language code (e.g., 'es' for Spanish, 'hi' for Hindi, 'fr' for French)")
    source_language: str = Field(default='auto', description="Source language code (default: auto-detect)")


class TranslationTool(BaseTool):
    name: str = "Multi-Language Translator"
    description: str = (
        "Translates agricultural reports, disease descriptions, and recommendations "
        "into multiple languages for farmers worldwide. Supports major agricultural "
        "languages including Spanish, Hindi, French, Portuguese, Chinese, and many more."
    )
    args_schema: Type[BaseModel] = TranslationInput
    
    # Language codes and names for reference (ClassVar to prevent Pydantic field creation)
    SUPPORTED_LANGUAGES: ClassVar[Dict[str, str]] = {
        'es': 'Spanish',
        'hi': 'Hindi',
        'fr': 'French',
        'pt': 'Portuguese',
        'zh-CN': 'Chinese (Simplified)',
        'ar': 'Arabic',
        'bn': 'Bengali',
        'de': 'German',
        'ja': 'Japanese',
        'pa': 'Punjabi',
        'te': 'Telugu',
        'mr': 'Marathi',
        'ta': 'Tamil',
        'ur': 'Urdu',
        'vi': 'Vietnamese',
        'it': 'Italian',
        'th': 'Thai',
        'ko': 'Korean',
        'ru': 'Russian',
        'sw': 'Swahili'
    }

    def _run(
        self, 
        text: str,
        target_language: str,
        source_language: str = 'auto'
    ) -> str:
        """
        Translate text to target language using deep-translator
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language (auto-detect if not specified)
            
        Returns:
            Translated text as JSON with metadata
        """
        try:
            # Handle Chinese language code (convert zh-cn to zh-CN)
            if target_language.lower() in ['zh-cn', 'zh_cn']:
                target_language = 'zh-CN'
            
            # Perform translation using GoogleTranslator from deep-translator
            translator = GoogleTranslator(source=source_language, target=target_language)
            translated_text = translator.translate(text)
            
            # Get language names
            target_lang_name = self.SUPPORTED_LANGUAGES.get(
                target_language, 
                target_language.upper()
            )
            
            result = {
                "status": "success",
                "original_text": text[:100] + "..." if len(text) > 100 else text,
                "translated_text": translated_text,
                "source_language": source_language if source_language != 'auto' else 'auto-detected',
                "target_language": target_lang_name,
                "confidence": "high"
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Translation failed: {str(e)}",
                "original_text": text[:100] + "..." if len(text) > 100 else text,
                "suggestion": "Check target language code or internet connection. Supported codes: es, hi, fr, pt, zh-CN, ar, bn, de, ja, etc."
            }
            return json.dumps(error_result, indent=2)
    
    @staticmethod
    def get_supported_languages():
        """Get list of supported languages"""
        return TranslationTool.SUPPORTED_LANGUAGES

