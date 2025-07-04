import praw
import pandas as pd
import json
import time
import concurrent.futures
from datetime import datetime
from tqdm import tqdm
import logging
from config import REDDIT_CONFIG, EMPATHETIC_SUBREDDITS, DATA_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditDataExtractor:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CONFIG['client_id'],
            client_secret=REDDIT_CONFIG['client_secret'],
            user_agent=REDDIT_CONFIG['user_agent']
        )
        logger.info("Reddit API initialized successfully")
    
    def extract_subreddit_conversations(self, subreddit_name, post_limit=200):
        """Extract conversations from a single subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            conversations = []
            
            logger.info(f"Extracting from r/{subreddit_name}...")
            
            for submission in subreddit.hot(limit=post_limit):
                if submission.num_comments < 2:
                    continue
                
                post_data = {
                    'subreddit': subreddit_name,
                    'post_id': submission.id,
                    'title': submission.title,
                    'selftext': submission.selftext,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'url': submission.url,
                    'comments': []
                }
                
                # Extract comments
                try:
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list()[:DATA_CONFIG['max_comments_per_post']]:
                        if (len(comment.body) >= DATA_CONFIG['min_comment_length'] and 
                            not comment.body.startswith('[deleted]') and 
                            not comment.body.startswith('[removed]')):
                            
                            post_data['comments'].append({
                                'comment_id': comment.id,
                                'body': comment.body,
                                'score': comment.score,
                                'created_utc': comment.created_utc,
                                'is_root': comment.is_root,
                                'parent_id': str(comment.parent_id) if comment.parent_id else None
                            })
                except Exception as e:
                    logger.warning(f"Error extracting comments from {submission.id}: {e}")
                    continue
                
                if post_data['comments']:  # Only add if has valid comments
                    conversations.append(post_data)
                
                time.sleep(DATA_CONFIG['rate_limit_delay'])
            
            logger.info(f"✓ r/{subreddit_name}: {len(conversations)} conversations extracted")
            return conversations
            
        except Exception as e:
            logger.error(f"✗ Failed to extract from r/{subreddit_name}: {e}")
            return []
    
    def extract_all_parallel(self, subreddit_list=None):
        """Extract from all subreddits in parallel"""
        if subreddit_list is None:
            subreddit_list = EMPATHETIC_SUBREDDITS
        
        all_conversations = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=DATA_CONFIG['max_workers']) as executor:
            # Submit all tasks
            futures = {
                executor.submit(
                    self.extract_subreddit_conversations, 
                    subreddit, 
                    DATA_CONFIG['posts_per_subreddit']
                ): subreddit 
                for subreddit in subreddit_list
            }
            
            # Collect results with progress bar
            for future in tqdm(concurrent.futures.as_completed(futures), 
                             total=len(futures), 
                             desc="Extracting subreddits"):
                subreddit = futures[future]
                try:
                    conversations = future.result()
                    all_conversations.extend(conversations)
                except Exception as e:
                    logger.error(f"Error processing {subreddit}: {e}")
        
        logger.info(f"🎉 Total conversations extracted: {len(all_conversations)}")
        return all_conversations
    
    def save_raw_data(self, conversations, filename='raw_reddit_data.json'):
        """Save raw extracted data"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
        logger.info(f"Raw data saved to {filename}")

if __name__ == "__main__":
    extractor = RedditDataExtractor()
    
    # Start extraction
    start_time = time.time()
    conversations = extractor.extract_all_parallel()
    
    # Save raw data
    extractor.save_raw_data(conversations)
    
    extraction_time = (time.time() - start_time) / 3600
    logger.info(f"🚀 Data extraction completed in {extraction_time:.2f} hours")
    logger.info(f"📊 Total conversations: {len(conversations)}")
