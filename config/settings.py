"""
Configuration file for Reddit Data Extraction with GPU acceleration
"""

import os

# Reddit API Configuration
REDDIT_CONFIG = {
    'client_id': os.getenv('REDDIT_CLIENT_ID', 'your_client_id_here'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET', 'your_client_secret_here'),
    'user_agent': 'AuraChat:v2.0:empathy_research (by u/your_username)',
    'username': os.getenv('REDDIT_USERNAME', ''),  # Optional for read-only
    'password': os.getenv('REDDIT_PASSWORD', '')   # Optional for read-only
}

# Empathetic Subreddits for extraction
EMPATHETIC_SUBREDDITS = [
    # Support and advice communities
    'relationship_advice',
    'offmychest',
    'TrueOffMyChest',
    'relationships',
    'AmItheAsshole',
    'unpopularopinion',
    'confession',
    'self',
    'socialskills',
    'depression',
    'Anxiety',
    'mentalhealth',
    'SuicideWatch',
    'internetparents',
    'raisedbynarcissists',
    'JustNoMIL',
    'BreakUps',
    'grief',
    'CasualConversation',
    'MomForAMinute',
    'DadForAMinute',
    'KindVoice',
    'toastme',
    'FreeCompliments',
    'GetMotivated',
    'decidingtobebetter',
    'getoutofbed',
    'progresspics',
    'loseit',
    'stopdrinking',
    'leaves',
    'ADHD',
    'autism',
    'bipolar',
    'BPD',
    'ptsd',
    'OCD',
    'eating_disorders',
    'selfharm',
    'TwoXChromosomes',
    'MensLib',
    'teenagers',
    'college',
    'jobs',
    'careerguidance',
    'personalfinance',
    'povertyfinance',
    'homeless',
    'assistance',
    'RandomKindness'
]

# GPU-Accelerated Data Processing Configuration
DATA_CONFIG = {
    # Extraction parameters
    'posts_per_subreddit': 500,        # Increased for larger dataset
    'max_comments_per_post': 20,       # More comments per post
    'min_comment_length': 20,          # Minimum comment length
    'max_comment_length': 2000,        # Maximum comment length
    'min_post_score': 5,               # Minimum post score
    'min_comment_score': 1,            # Minimum comment score
    
    # Batch processing for GPU acceleration
    'batch_size': 50,                  # Process 50 subreddits at once
    'parallel_workers': 8,             # Parallel API requests
    'gpu_batch_size': 128,             # GPU processing batch size
    'max_sequence_length': 512,        # Max tokens per sequence
    
    # Rate limiting
    'rate_limit_delay': 1.0,           # Delay between requests (seconds)
    'api_timeout': 30,                 # API request timeout
    'retry_attempts': 3,               # Retry failed requests
    'backoff_factor': 2,               # Exponential backoff
    
    # Data quality filters
    'empathy_keywords': [
        'sorry', 'understand', 'feel', 'support', 'here for you',
        'care', 'comfort', 'listen', 'strength', 'brave',
        'difficult', 'hard time', 'going through', 'experience',
        'valid', 'normal', 'okay to', 'makes sense'
    ],
    
    # Output configuration
    'output_format': 'jsonl',          # jsonl for large datasets
    'save_interval': 1000,             # Save every N conversations
    'compression': True,               # Compress output files
    'checkpoint_interval': 5000,       # Checkpoint every N records
}

# GPU Processing Configuration
GPU_CONFIG = {
    'device': 'cuda',                  # Use CUDA if available
    'mixed_precision': True,           # Use mixed precision for speed
    'dataloader_workers': 4,           # DataLoader workers
    'pin_memory': True,                # Pin memory for faster GPU transfer
    'prefetch_factor': 2,              # Prefetch batches
    'persistent_workers': True,        # Keep workers alive between epochs
}

# File paths
PATHS = {
    'raw_data': 'data/raw/',
    'processed_data': 'data/processed/',
    'checkpoints': 'data/checkpoints/',
    'logs': 'logs/',
    'models': 'models/',
    'results': 'results/'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_handler': True,
    'console_handler': True,
    'log_file': 'logs/reddit_extraction.log'
}

# Quality thresholds for empathy detection
QUALITY_THRESHOLDS = {
    'min_empathy_score': 0.3,          # Minimum empathy score to include
    'min_response_relevance': 0.5,     # Minimum response relevance
    'max_toxicity_score': 0.2,         # Maximum allowed toxicity
    'min_conversation_length': 2,      # Minimum conversation turns
    'max_conversation_length': 10,     # Maximum conversation turns
}

# Validation settings
VALIDATION_CONFIG = {
    'validation_split': 0.1,           # 10% for validation
    'test_split': 0.1,                 # 10% for testing
    'random_seed': 42,                 # For reproducibility
    'stratify_by_subreddit': True,     # Ensure balanced subreddit representation
}
