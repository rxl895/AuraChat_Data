"""
GPU-Accelerated Reddit Data Extractor
High-performance batch processing for large-scale empathy data collection
"""

import praw
import asyncio
import aiohttp
import json
import time
import torch
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path
import gc
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm.asyncio import tqdm as atqdm
from tqdm import tqdm
import pandas as pd
import pickle
import gzip
import hashlib

from config.settings import (
    REDDIT_CONFIG, EMPATHETIC_SUBREDDITS, DATA_CONFIG, 
    GPU_CONFIG, PATHS, LOGGING_CONFIG, QUALITY_THRESHOLDS
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ConversationData:
    """Structured conversation data for GPU processing"""
    subreddit: str
    post_id: str
    post_title: str
    post_content: str
    post_score: int
    comments: List[Dict[str, Any]]
    extracted_at: str
    conversation_id: str
    empathy_pairs: List[Tuple[str, str]]
    metadata: Dict[str, Any]

class GPURedditExtractor:
    """High-performance Reddit data extractor with GPU acceleration"""
    
    def __init__(self):
        self.device = torch.device(GPU_CONFIG['device'] if torch.cuda.is_available() else 'cpu')
        self.setup_reddit_api()
        self.setup_directories()
        self.checkpoint_data = {}
        self.extraction_stats = {
            'total_posts_processed': 0,
            'total_comments_extracted': 0,
            'empathy_pairs_found': 0,
            'subreddits_completed': 0,
            'start_time': None,
            'last_checkpoint': None
        }
        
        logger.info(f"🚀 GPU Reddit Extractor initialized")
        logger.info(f"💻 Device: {self.device}")
        logger.info(f"🔥 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB" if torch.cuda.is_available() else "CPU Mode")
        
    def setup_reddit_api(self):
        """Initialize Reddit API with error handling"""
        try:
            # Use read-only authentication (no username/password needed)
            self.reddit = praw.Reddit(
                client_id=REDDIT_CONFIG['client_id'],
                client_secret=REDDIT_CONFIG['client_secret'],
                user_agent=REDDIT_CONFIG['user_agent']
            )
            
            # Test API connection with a simple read-only request
            test_subreddit = self.reddit.subreddit('test')
            list(test_subreddit.hot(limit=1))  # Simple test
            logger.info("✅ Reddit API authenticated successfully")
            
        except Exception as e:
            logger.error(f"❌ Reddit API authentication failed: {e}")
            raise
    
    def setup_directories(self):
        """Create necessary directories"""
        for path in PATHS.values():
            Path(path).mkdir(parents=True, exist_ok=True)
        logger.info("📁 Directory structure created")
    
    def generate_conversation_id(self, subreddit: str, post_id: str) -> str:
        """Generate unique conversation ID"""
        timestamp = datetime.now().isoformat()
        data = f"{subreddit}_{post_id}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def extract_empathy_pairs(self, post_content: str, comments: List[Dict]) -> List[Tuple[str, str]]:
        """Extract potential empathy conversation pairs"""
        pairs = []
        
        # Post-to-comment pairs (user seeking help -> empathetic response)
        for comment in comments[:5]:  # Top 5 comments
            if (len(comment['body']) >= DATA_CONFIG['min_comment_length'] and
                self.is_empathetic_response(comment['body'])):
                pairs.append((post_content, comment['body']))
        
        # Comment-to-reply pairs
        comment_dict = {c['comment_id']: c for c in comments}
        for comment in comments:
            if comment.get('parent_id') and comment['parent_id'].startswith('t1_'):
                parent_id = comment['parent_id'][3:]  # Remove 't1_' prefix
                if parent_id in comment_dict:
                    parent_comment = comment_dict[parent_id]
                    if (self.is_empathetic_response(comment['body']) and
                        len(parent_comment['body']) >= DATA_CONFIG['min_comment_length']):
                        pairs.append((parent_comment['body'], comment['body']))
        
        return pairs
    
    def is_empathetic_response(self, text: str) -> bool:
        """Check if text contains empathetic language"""
        text_lower = text.lower()
        empathy_count = sum(1 for keyword in DATA_CONFIG['empathy_keywords'] 
                          if keyword in text_lower)
        return empathy_count >= 2  # At least 2 empathy keywords
    
    async def extract_subreddit_batch(self, subreddit_names: List[str]) -> List[ConversationData]:
        """Extract data from a batch of subreddits asynchronously"""
        conversations = []
        
        with ThreadPoolExecutor(max_workers=DATA_CONFIG['parallel_workers']) as executor:
            # Submit extraction tasks
            futures = {
                executor.submit(self.extract_single_subreddit, name): name 
                for name in subreddit_names
            }
            
            # Collect results with progress tracking
            for future in tqdm(as_completed(futures), 
                             total=len(futures), 
                             desc=f"Processing batch"):
                subreddit_name = futures[future]
                try:
                    subreddit_conversations = future.result()
                    conversations.extend(subreddit_conversations)
                    self.extraction_stats['subreddits_completed'] += 1
                    logger.info(f"✅ {subreddit_name}: {len(subreddit_conversations)} conversations")
                except Exception as e:
                    logger.error(f"❌ Failed to extract {subreddit_name}: {e}")
        
        return conversations
    
    def extract_single_subreddit(self, subreddit_name: str) -> List[ConversationData]:
        """Extract conversations from a single subreddit"""
        conversations = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            post_count = 0
            
            # Extract from hot posts
            for submission in subreddit.hot(limit=DATA_CONFIG['posts_per_subreddit']):
                if (submission.num_comments < 2 or 
                    submission.score < DATA_CONFIG['min_post_score']):
                    continue
                
                # Extract post data
                post_content = f"{submission.title}\n\n{submission.selftext}".strip()
                if len(post_content) < DATA_CONFIG['min_comment_length']:
                    continue
                
                # Extract comments
                comments_data = self.extract_comments(submission)
                if len(comments_data) < 2:  # Need at least 2 comments for conversation
                    continue
                
                # Extract empathy pairs
                empathy_pairs = self.extract_empathy_pairs(post_content, comments_data)
                if not empathy_pairs:  # Skip if no empathy detected
                    continue
                
                # Create conversation object
                conversation = ConversationData(
                    subreddit=subreddit_name,
                    post_id=submission.id,
                    post_title=submission.title,
                    post_content=post_content,
                    post_score=submission.score,
                    comments=comments_data,
                    extracted_at=datetime.now(timezone.utc).isoformat(),
                    conversation_id=self.generate_conversation_id(subreddit_name, submission.id),
                    empathy_pairs=empathy_pairs,
                    metadata={
                        'num_comments': len(comments_data),
                        'empathy_pairs_count': len(empathy_pairs),
                        'post_created_utc': submission.created_utc,
                        'post_url': submission.url,
                        'submission_type': 'self' if submission.is_self else 'link'
                    }
                )
                
                conversations.append(conversation)
                post_count += 1
                self.extraction_stats['total_posts_processed'] += 1
                self.extraction_stats['empathy_pairs_found'] += len(empathy_pairs)
                
                # Rate limiting
                time.sleep(DATA_CONFIG['rate_limit_delay'])
                
                # Progress update
                if post_count % 50 == 0:
                    logger.info(f"🔄 {subreddit_name}: {post_count} posts processed")
        
        except Exception as e:
            logger.error(f"❌ Error extracting from r/{subreddit_name}: {e}")
        
        return conversations
    
    def extract_comments(self, submission) -> List[Dict[str, Any]]:
        """Extract and filter comments from a submission"""
        comments_data = []
        
        try:
            submission.comments.replace_more(limit=0)
            
            for comment in submission.comments.list()[:DATA_CONFIG['max_comments_per_post']]:
                if (hasattr(comment, 'body') and 
                    not comment.body.startswith(('[deleted]', '[removed]')) and
                    len(comment.body) >= DATA_CONFIG['min_comment_length'] and
                    len(comment.body) <= DATA_CONFIG['max_comment_length'] and
                    comment.score >= DATA_CONFIG['min_comment_score']):
                    
                    comments_data.append({
                        'comment_id': comment.id,
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'is_root': comment.is_root,
                        'parent_id': str(comment.parent_id) if hasattr(comment, 'parent_id') else None,
                        'depth': getattr(comment, 'depth', 0),
                        'author': str(comment.author) if comment.author else '[deleted]'
                    })
            
            self.extraction_stats['total_comments_extracted'] += len(comments_data)
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting comments: {e}")
        
        return comments_data
    
    def save_batch_data(self, conversations: List[ConversationData], batch_num: int):
        """Save batch data with compression"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to dictionary format for JSON serialization
        batch_data = []
        for conv in conversations:
            conv_dict = {
                'conversation_id': conv.conversation_id,
                'subreddit': conv.subreddit,
                'post_id': conv.post_id,
                'post_title': conv.post_title,
                'post_content': conv.post_content,
                'post_score': conv.post_score,
                'comments': conv.comments,
                'extracted_at': conv.extracted_at,
                'empathy_pairs': conv.empathy_pairs,
                'metadata': conv.metadata
            }
            batch_data.append(conv_dict)
        
        # Save as compressed JSONL
        output_file = Path(PATHS['raw_data']) / f"batch_{batch_num:03d}_{timestamp}.jsonl.gz"
        
        with gzip.open(output_file, 'wt', encoding='utf-8') as f:
            for conv_dict in batch_data:
                f.write(json.dumps(conv_dict, ensure_ascii=False) + '\n')
        
        logger.info(f"💾 Batch {batch_num} saved: {len(batch_data)} conversations → {output_file}")
        return output_file
    
    def save_checkpoint(self):
        """Save extraction checkpoint"""
        checkpoint = {
            'extraction_stats': self.extraction_stats,
            'timestamp': datetime.now().isoformat(),
            'device': str(self.device),
            'completed_subreddits': self.extraction_stats['subreddits_completed']
        }
        
        checkpoint_file = Path(PATHS['checkpoints']) / f"extraction_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint, f)
        
        self.extraction_stats['last_checkpoint'] = checkpoint_file
        logger.info(f"💾 Checkpoint saved: {checkpoint_file}")
    
    async def extract_all_data(self, subreddit_list: Optional[List[str]] = None) -> str:
        """Main extraction pipeline with GPU acceleration"""
        if subreddit_list is None:
            subreddit_list = EMPATHETIC_SUBREDDITS
        
        self.extraction_stats['start_time'] = datetime.now()
        logger.info(f"🚀 Starting large-scale extraction from {len(subreddit_list)} subreddits")
        
        # Process in batches for memory efficiency
        batch_size = DATA_CONFIG['batch_size']
        all_output_files = []
        
        for i in range(0, len(subreddit_list), batch_size):
            batch_num = i // batch_size + 1
            batch_subreddits = subreddit_list[i:i + batch_size]
            
            logger.info(f"📦 Processing batch {batch_num}/{(len(subreddit_list) + batch_size - 1) // batch_size}")
            logger.info(f"📋 Subreddits: {', '.join(batch_subreddits)}")
            
            try:
                # Extract batch data
                batch_conversations = await self.extract_subreddit_batch(batch_subreddits)
                
                if batch_conversations:
                    # Save batch
                    output_file = self.save_batch_data(batch_conversations, batch_num)
                    all_output_files.append(output_file)
                    
                    # Memory cleanup
                    del batch_conversations
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                
                # Save checkpoint every few batches
                if batch_num % 3 == 0:
                    self.save_checkpoint()
                
                # Progress update
                progress = (batch_num * batch_size) / len(subreddit_list) * 100
                logger.info(f"📈 Overall progress: {progress:.1f}% complete")
                
            except Exception as e:
                logger.error(f"❌ Batch {batch_num} failed: {e}")
                continue
        
        # Final summary
        total_time = datetime.now() - self.extraction_stats['start_time']
        logger.info(f"🎉 Extraction completed!")
        logger.info(f"⏱️ Total time: {total_time}")
        logger.info(f"📊 Statistics:")
        logger.info(f"   - Posts processed: {self.extraction_stats['total_posts_processed']:,}")
        logger.info(f"   - Comments extracted: {self.extraction_stats['total_comments_extracted']:,}")
        logger.info(f"   - Empathy pairs found: {self.extraction_stats['empathy_pairs_found']:,}")
        logger.info(f"   - Subreddits completed: {self.extraction_stats['subreddits_completed']}")
        logger.info(f"   - Output files: {len(all_output_files)}")
        
        # Save final summary
        summary_file = self.save_extraction_summary(all_output_files)
        return summary_file
    
    def save_extraction_summary(self, output_files: List[Path]) -> str:
        """Save final extraction summary"""
        summary = {
            'extraction_stats': self.extraction_stats,
            'output_files': [str(f) for f in output_files],
            'total_files': len(output_files),
            'extraction_completed_at': datetime.now().isoformat(),
            'config_used': {
                'subreddits_targeted': len(EMPATHETIC_SUBREDDITS),
                'posts_per_subreddit': DATA_CONFIG['posts_per_subreddit'],
                'batch_size': DATA_CONFIG['batch_size'],
                'parallel_workers': DATA_CONFIG['parallel_workers']
            }
        }
        
        summary_file = Path(PATHS['raw_data']) / f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"📋 Extraction summary saved: {summary_file}")
        return str(summary_file)

async def main():
    """Main execution function"""
    extractor = GPURedditExtractor()
    
    try:
        summary_file = await extractor.extract_all_data()
        logger.info(f"✅ Data extraction pipeline completed successfully!")
        logger.info(f"📄 Summary: {summary_file}")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Extraction interrupted by user")
        extractor.save_checkpoint()
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        extractor.save_checkpoint()
        raise

if __name__ == "__main__":
    asyncio.run(main())
