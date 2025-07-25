"""
Stage 1: Data Validation and Cleaning
Processes raw Reddit extraction data and prepares it for empathy scoring
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

import spacy
from langdetect import detect
import pandas as pd

class DataCleaner:
    """Handles data validation, cleaning, and normalization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize spaCy for text processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        self.quality_thresholds = config.get("quality_thresholds", {})
        self.text_processing = config.get("text_processing", {})
        
        # Compile regex patterns for cleaning
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.username_pattern = re.compile(r'/u/\w+|u/\w+|@\w+')
        self.subreddit_pattern = re.compile(r'/r/\w+|r/\w+')
        self.markdown_pattern = re.compile(r'\*{1,2}([^*]+)\*{1,2}|_{1,2}([^_]+)_{1,2}|\[([^\]]+)\]\([^)]+\)')
        
        # PII patterns (basic implementation)
        self.phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
    def clean_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean a batch of conversations"""
        cleaned_batch = []
        
        for conversation in batch:
            try:
                cleaned_conv = self.clean_conversation(conversation)
                if cleaned_conv:
                    cleaned_batch.append(cleaned_conv)
            except Exception as e:
                self.logger.error(f"Error cleaning conversation {conversation.get('conversation_id', 'unknown')}: {e}")
                
        return cleaned_batch
    
    def clean_conversation(self, conversation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and validate a single conversation"""
        
        # Basic validation
        if not self.validate_basic_structure(conversation):
            return None
            
        # Quality filtering
        if not self.meets_quality_thresholds(conversation):
            return None
            
        # Clean text content
        cleaned_conversation = self.clean_text_content(conversation)
        
        # Language detection
        if not self.is_english_content(cleaned_conversation):
            return None
            
        # Process empathy pairs
        cleaned_pairs = self.clean_empathy_pairs(cleaned_conversation.get("empathy_pairs", []))
        if not cleaned_pairs:
            return None
            
        # Create cleaned conversation object
        result = {
            "conversation_id": self.generate_clean_id(conversation),
            "subreddit": cleaned_conversation.get("subreddit", "").lower(),
            "context": self.clean_text(cleaned_conversation.get("post_content", "")),
            "post_title": self.clean_text(cleaned_conversation.get("post_title", "")),
            "empathy_pairs": cleaned_pairs,
            "metadata": {
                "source_subreddit": conversation.get("subreddit"),
                "original_score": conversation.get("metadata", {}).get("post_score", 0),
                "original_comment_count": conversation.get("metadata", {}).get("num_comments", 0),
                "extraction_timestamp": conversation.get("metadata", {}).get("extraction_timestamp"),
                "processing_timestamp": datetime.now().isoformat(),
                "quality_flags": []
            }
        }
        
        return result
    
    def validate_basic_structure(self, conversation: Dict[str, Any]) -> bool:
        """Validate basic conversation structure"""
        required_fields = ["conversation_id", "subreddit", "empathy_pairs"]
        
        for field in required_fields:
            if field not in conversation:
                self.logger.debug(f"Missing required field: {field}")
                return False
                
        if not isinstance(conversation["empathy_pairs"], list):
            self.logger.debug("empathy_pairs is not a list")
            return False
            
        if len(conversation["empathy_pairs"]) == 0:
            self.logger.debug("No empathy pairs found")
            return False
            
        return True
    
    def meets_quality_thresholds(self, conversation: Dict[str, Any]) -> bool:
        """Check if conversation meets quality thresholds"""
        thresholds = self.quality_thresholds
        
        # Check minimum empathy pairs
        min_pairs = thresholds.get("min_empathy_pairs", 2)
        if len(conversation.get("empathy_pairs", [])) < min_pairs:
            return False
            
        # Check post score
        min_score = thresholds.get("min_post_score", 10)
        post_score = conversation.get("metadata", {}).get("post_score", 0)
        if post_score < min_score:
            return False
            
        # Check post length
        max_length = thresholds.get("max_post_length", 2000)
        post_content = conversation.get("post_content", "")
        if len(post_content) > max_length:
            return False
            
        return True
    
    def clean_text_content(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Clean all text content in the conversation"""
        cleaned = conversation.copy()
        
        # Clean post content and title
        if "post_content" in cleaned:
            cleaned["post_content"] = self.clean_text(cleaned["post_content"])
        if "post_title" in cleaned:
            cleaned["post_title"] = self.clean_text(cleaned["post_title"])
            
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """Comprehensive text cleaning"""
        if not text or not isinstance(text, str):
            return ""
            
        # Remove URLs
        if self.text_processing.get("remove_urls", True):
            text = self.url_pattern.sub("", text)
            
        # Remove usernames
        if self.text_processing.get("remove_usernames", True):
            text = self.username_pattern.sub("", text)
            
        # Remove subreddit mentions
        if self.text_processing.get("remove_subreddit_mentions", True):
            text = self.subreddit_pattern.sub("", text)
            
        # Remove markdown formatting
        if self.text_processing.get("remove_markdown", True):
            text = self.markdown_pattern.sub(r'\1\2\3', text)
            
        # Remove PII
        if self.text_processing.get("remove_pii", True):
            text = self.remove_pii(text)
            
        # Normalize whitespace
        if self.text_processing.get("normalize_whitespace", True):
            text = re.sub(r'\s+', ' ', text).strip()
            
        return text
    
    def remove_pii(self, text: str) -> str:
        """Remove personally identifiable information"""
        # Remove phone numbers
        text = self.phone_pattern.sub("[PHONE]", text)
        
        # Remove email addresses
        text = self.email_pattern.sub("[EMAIL]", text)
        
        # Basic name anonymization (simple implementation)
        if self.text_processing.get("anonymize_names", True):
            # This is a basic implementation - could be enhanced with NER
            if self.nlp:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        text = text.replace(ent.text, "[NAME]")
                        
        return text
    
    def is_english_content(self, conversation: Dict[str, Any]) -> bool:
        """Detect if conversation content is in English"""
        text_to_check = ""
        
        # Combine post content and some empathy pairs for language detection
        if "post_content" in conversation:
            text_to_check += conversation["post_content"] + " "
            
        # Add first few empathy pairs
        empathy_pairs = conversation.get("empathy_pairs", [])
        for i, pair in enumerate(empathy_pairs[:3]):  # Check first 3 pairs
            if isinstance(pair, list) and len(pair) >= 2:
                text_to_check += pair[0] + " " + pair[1] + " "
                
        if not text_to_check.strip():
            return False
            
        try:
            detected_lang = detect(text_to_check)
            return detected_lang == "en"
        except:
            # If language detection fails, assume English
            return True
    
    def clean_empathy_pairs(self, empathy_pairs: List[Any]) -> List[Dict[str, Any]]:
        """Clean and structure empathy pairs"""
        cleaned_pairs = []
        
        for pair in empathy_pairs:
            cleaned_pair = self.clean_empathy_pair(pair)
            if cleaned_pair:
                cleaned_pairs.append(cleaned_pair)
                
        return cleaned_pairs
    
    def clean_empathy_pair(self, pair: Any) -> Optional[Dict[str, Any]]:
        """Clean a single empathy pair"""
        # Handle different input formats
        if isinstance(pair, list) and len(pair) >= 2:
            input_text = pair[0]
            response_text = pair[1]
        elif isinstance(pair, dict):
            input_text = pair.get("input") or pair.get("user_message") or pair.get("question")
            response_text = pair.get("response") or pair.get("assistant_message") or pair.get("answer")
        else:
            return None
            
        if not input_text or not response_text:
            return None
            
        # Clean both texts
        cleaned_input = self.clean_text(str(input_text))
        cleaned_response = self.clean_text(str(response_text))
        
        # Check minimum length
        min_length = self.quality_thresholds.get("min_comment_length", 20)
        if len(cleaned_input) < min_length or len(cleaned_response) < min_length:
            return None
            
        # Create structured pair
        return {
            "input": cleaned_input,
            "response": cleaned_response,
            "empathy_score": 0.0,  # Will be filled in Stage 2
            "quality_score": 0.0,  # Will be filled in Stage 2
            "pair_metadata": {
                "original_input_length": len(str(input_text)),
                "original_response_length": len(str(response_text)),
                "cleaned_input_length": len(cleaned_input),
                "cleaned_response_length": len(cleaned_response)
            }
        }
    
    def generate_clean_id(self, conversation: Dict[str, Any]) -> str:
        """Generate a clean, unique conversation ID"""
        original_id = conversation.get("conversation_id", "")
        subreddit = conversation.get("subreddit", "")
        
        # Create a hash-based ID if original is not suitable
        if not original_id or len(original_id) < 5:
            content_hash = hashlib.md5(
                (subreddit + str(conversation.get("post_content", "")[:100])).encode()
            ).hexdigest()[:12]
            return f"clean_{subreddit}_{content_hash}"
        else:
            # Clean the original ID
            clean_id = re.sub(r'[^a-zA-Z0-9_-]', '_', original_id)
            return f"clean_{clean_id}"

def main():
    """Test the data cleaner with sample data"""
    import yaml
    
    # Load configuration
    with open("config/processing_config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize cleaner
    cleaner = DataCleaner(config)
    
    # Sample conversation for testing
    sample_conversation = {
        "conversation_id": "test_123",
        "subreddit": "relationship_advice",
        "post_title": "Need advice on my relationship",
        "post_content": "I'm struggling with communication issues with my partner. It's really hard and I don't know what to do.",
        "empathy_pairs": [
            ["I feel overwhelmed", "I understand how difficult this must be for you"],
            ["Don't know what to do", "You're being so strong by reaching out for help"]
        ],
        "metadata": {
            "empathy_pairs_count": 2,
            "post_score": 25,
            "num_comments": 15
        }
    }
    
    # Test cleaning
    result = cleaner.clean_conversation(sample_conversation)
    
    if result:
        print("✅ Cleaning successful!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Cleaning failed")

if __name__ == "__main__":
    main()
