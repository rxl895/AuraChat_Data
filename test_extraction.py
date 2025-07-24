#!/usr/bin/env python3
"""
Test script for GPU Reddit Extractor
Verifies setup and runs a small test extraction
"""

import sys
import asyncio
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.gpu_reddit_extractor import GPURedditExtractor

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_extraction():
    """Run a small test extraction"""
    logger.info("🧪 Starting test extraction...")
    
    try:
        # Initialize extractor
        extractor = GPURedditExtractor()
        
        # Test with a small subset of subreddits
        test_subreddits = [
            'CasualConversation',
            'KindVoice',
            'MomForAMinute'
        ]
        
        logger.info(f"📋 Testing with {len(test_subreddits)} subreddits")
        
        # Override configuration for testing
        from config.settings import DATA_CONFIG
        original_posts = DATA_CONFIG['posts_per_subreddit']
        DATA_CONFIG['posts_per_subreddit'] = 10  # Small test
        
        # Run extraction
        summary_file = await extractor.extract_all_data(test_subreddits)
        
        # Restore original configuration
        DATA_CONFIG['posts_per_subreddit'] = original_posts
        
        logger.info(f"✅ Test extraction completed!")
        logger.info(f"📄 Summary file: {summary_file}")
        
        # Show test results
        stats = extractor.extraction_stats
        logger.info(f"📊 Test Results:")
        logger.info(f"   Posts processed: {stats['total_posts_processed']}")
        logger.info(f"   Comments extracted: {stats['total_comments_extracted']}")
        logger.info(f"   Empathy pairs found: {stats['empathy_pairs_found']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gpu_setup():
    """Test GPU setup"""
    try:
        import torch
        logger.info(f"🔧 PyTorch version: {torch.__version__}")
        logger.info(f"🔥 CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"💻 GPU device: {torch.cuda.get_device_name()}")
            logger.info(f"🔥 GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        else:
            logger.info("💻 Running in CPU mode")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ GPU setup test failed: {e}")
        return False

def test_reddit_config():
    """Test Reddit API configuration"""
    try:
        from config.settings import REDDIT_CONFIG, EMPATHETIC_SUBREDDITS
        
        logger.info("🔧 Reddit Configuration:")
        logger.info(f"   Client ID: {'Set' if REDDIT_CONFIG['client_id'] != 'your_client_id_here' else 'NOT SET'}")
        logger.info(f"   Client Secret: {'Set' if REDDIT_CONFIG['client_secret'] != 'your_client_secret_here' else 'NOT SET'}")
        logger.info(f"   User Agent: {REDDIT_CONFIG['user_agent']}")
        logger.info(f"   Target Subreddits: {len(EMPATHETIC_SUBREDDITS)}")
        
        if REDDIT_CONFIG['client_id'] == 'your_client_id_here':
            logger.warning("⚠️  Reddit API credentials not configured!")
            logger.info("Please update config/settings.py or set environment variables:")
            logger.info("   export REDDIT_CLIENT_ID='your_actual_client_id'")
            logger.info("   export REDDIT_CLIENT_SECRET='your_actual_client_secret'")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Reddit config test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 AuraChat GPU Reddit Extractor - Test Suite")
    logger.info("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: GPU Setup
    logger.info("\n📋 Test 1: GPU Setup")
    if test_gpu_setup():
        tests_passed += 1
        logger.info("✅ GPU setup test passed")
    else:
        logger.error("❌ GPU setup test failed")
    
    # Test 2: Reddit Configuration
    logger.info("\n📋 Test 2: Reddit Configuration")
    config_ok = test_reddit_config()
    if config_ok:
        tests_passed += 1
        logger.info("✅ Reddit config test passed")
    else:
        logger.error("❌ Reddit config test failed")
    
    # Test 3: Extraction (only if config is OK)
    logger.info("\n📋 Test 3: Small Test Extraction")
    if config_ok:
        if await test_extraction():
            tests_passed += 1
            logger.info("✅ Test extraction passed")
        else:
            logger.error("❌ Test extraction failed")
    else:
        logger.warning("⚠️  Skipping test extraction due to config issues")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        logger.info("🎉 All tests passed! Ready for full extraction.")
        logger.info("🚀 To run full extraction:")
        logger.info("   sbatch scripts/extract_reddit_data.slurm")
    elif tests_passed >= 2:
        logger.info("⚠️  Most tests passed. Check configuration and try again.")
    else:
        logger.error("❌ Multiple tests failed. Please check setup.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
