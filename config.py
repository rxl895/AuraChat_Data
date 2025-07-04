import os
from dotenv import load_dotenv

load_dotenv()

# Reddit API Configuration
REDDIT_CONFIG = {

    'client_id': os.getenv('REDDIT_CLIENT_ID'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
    'user_agent': os.getenv('REDDIT_USER_AGENT', 'AuraChat_Data_v1.0')
}

# 50 Empathetic Subreddits
EMPATHETIC_SUBREDDITS = [
    # Mental Health & Support (20)
    'therapy', 'depression', 'Anxiety', 'ADHD', 'autism',
    'BipolarReddit', 'SuicideWatch', 'PTSD', 'MentalHealth', 'askatherapist',
    'RedditorsInRecovery', 'StopDrinking', 'socialanxiety', 'OCD', 'BorderlinePDisorder',
    'eating_disorders', 'selfharm', 'BipolarSOs', 'mentalillness', 'getting_over_it',
    
    # Relationship & Life Support (15)
    'relationship_advice', 'breakups', 'dating_advice', 'AmItheAsshole', 'offmychest',
    'TrueOffMyChest', 'confessions', 'lonely', 'ForeverAlone', 'MomForAMinute',
    'DadForAMinute', 'internetparents', 'CasualConversation', 'KindVoice', 'FreeCompliments',
    
    # Specialized Support & Wholesome (15)
    'raisedbynarcissists', 'CPTSD', 'GriefSupport', 'cancer', 'ChronicPain',
    'disability', 'loseit', 'stopgaming', 'leaves', 'NoFap',
    'wholesomememes', 'MadeMeSmile', 'HumansBeingBros', 'GetMotivated', 'decidingtobebetter'
]

# Training Configuration
TRAINING_CONFIG = {
    'model_name': 'openchat/openchat-3.5-1210',
    'max_length': 512,
    'num_train_epochs': 2,
    'per_device_train_batch_size': 8,
    'gradient_accumulation_steps': 2,
    'learning_rate': 5e-5,
    'warmup_steps': 50,
    'logging_steps': 25,
    'save_steps': 1000,
    'output_dir': './aurachat_model',
    'fp16': True,
    'gradient_checkpointing': True
}

# Data Collection Settings
DATA_CONFIG = {
    'posts_per_subreddit': 200,
    'max_comments_per_post': 30,
    'min_comment_length': 30,
    'max_workers': 10,
    'rate_limit_delay': 0.1
}
