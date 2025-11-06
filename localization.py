#!/usr/bin/env python3
"""
Localization Manager for Daily Brief Service
Handles all message localization in English, Spanish, and Slovak
"""

import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LocalizationManager:
    """Manages localized messages for all supported languages."""
    
    def __init__(self):
        self.messages = {}
        self.supported_languages = ['en', 'es', 'sk']
        self.load_all_languages()
    
    def load_all_languages(self):
        """Load messages for all supported languages."""
        for lang in self.supported_languages:
            self.load_language(lang)
    
    def load_language(self, language: str):
        """Load messages for a specific language."""
        messages_file = f"languages/{language}/messages.txt"
        
        if not os.path.exists(messages_file):
            logger.warning(f"Messages file not found for language {language}: {messages_file}")
            return
        
        self.messages[language] = {}
        
        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse message line: message_key|neutral|cute|brutal|emuska
                    parts = line.split('|')
                    if len(parts) < 4:
                        logger.warning(f"Invalid message format in {messages_file} line {line_num}: {line}")
                        continue
                    
                    message_key = parts[0]
                    
                    # Store all personality variants
                    self.messages[language][message_key] = {
                        'neutral': parts[1] if len(parts) > 1 else '',
                        'cute': parts[2] if len(parts) > 2 else '',
                        'brutal': parts[3] if len(parts) > 3 else '',
                        'emuska': parts[4] if len(parts) > 4 else ''  # Only available in Slovak
                    }
            
            logger.info(f"Loaded {len(self.messages[language])} messages for language: {language}")
            
        except Exception as e:
            logger.error(f"Error loading messages for language {language}: {e}")
    
    def get_message(self, key: str, personality: str = 'neutral', language: str = 'en', **kwargs) -> str:
        """Get a localized message with specified personality."""
        
        # Normalize inputs
        language = language.lower().strip()
        personality = personality.lower().strip()
        
        # Validate language
        if language not in self.supported_languages:
            logger.warning(f"Unsupported language {language}, falling back to English")
            language = 'en'
        
        # Validate personality
        if personality not in ['neutral', 'cute', 'brutal', 'emuska']:
            logger.warning(f"Invalid personality {personality}, falling back to neutral")
            personality = 'neutral'
        
        # Special handling for Emuska - only available in Slovak
        if personality == 'emuska' and language != 'sk':
            logger.warning(f"Emuska mode requested for {language}, falling back to cute")
            personality = 'cute'
        
        # Get message from loaded data
        lang_messages = self.messages.get(language, {})
        message_variants = lang_messages.get(key, {})
        
        # Get specific personality message
        message = message_variants.get(personality, '')
        
        # Fallback chain: requested personality -> neutral -> default message
        if not message:
            message = message_variants.get('neutral', '')
        
        if not message:
            logger.warning(f"No message found for key '{key}' in language '{language}'")
            # Ultimate fallback
            if language != 'en':
                return self.get_message(key, personality, 'en', **kwargs)
            else:
                message = f"Message not available ({key})"
        
        # Format message with provided parameters
        try:
            return message.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing format parameter {e} for message key '{key}'")
            return message
        except Exception as e:
            logger.error(f"Error formatting message '{key}': {e}")
            return message
    
    def get_weather_condition_message(self, condition: str, personality: str = 'neutral', language: str = 'en') -> str:
        """Get weather condition message (backwards compatibility)."""
        return self.get_message(condition, personality, language)
    
    def get_subject_line(self, subject_key: str, personality: str = 'neutral', language: str = 'en', **kwargs) -> str:
        """Get localized email subject line."""
        return self.get_message(subject_key, personality, language, **kwargs)

# Global instance
_localization_manager = None

def get_localization_manager() -> LocalizationManager:
    """Get global localization manager instance."""
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager

def get_localized_message(key: str, personality: str = 'neutral', language: str = 'en', **kwargs) -> str:
    """Convenience function to get localized message."""
    return get_localization_manager().get_message(key, personality, language, **kwargs)

def get_localized_subject(subject_key: str, personality: str = 'neutral', language: str = 'en', **kwargs) -> str:
    """Convenience function to get localized subject."""
    return get_localization_manager().get_subject_line(subject_key, personality, language, **kwargs)