#!/bin/bash

# AuraChat Environment Setup Script
# Sets up the environment for GPU-accelerated Reddit data extraction

set -e

echo "🚀 AuraChat Data Extraction v2.0 - Environment Setup"
echo "=============================================="

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the AuraChat_Data directory."
    exit 1
fi

# Install Python requirements
echo "📦 Installing Python requirements..."
pip install -r requirements.txt

# Check GPU availability
echo "🔥 Checking GPU availability..."
.venv/bin/python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU device: {torch.cuda.get_device_name()}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
else:
    print('Running in CPU mode')
"

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/raw data/processed data/checkpoints logs

# Check Reddit API configuration
echo "🔑 Checking Reddit API configuration..."
if [[ -n "$REDDIT_CLIENT_ID" && -n "$REDDIT_CLIENT_SECRET" ]]; then
    echo "✅ Reddit API credentials found in environment variables"
else
    echo "⚠️  Reddit API credentials not set as environment variables"
    echo "You can set them now or edit config/settings.py"
    echo ""
    echo "To set environment variables:"
    echo "export REDDIT_CLIENT_ID='your_client_id'"
    echo "export REDDIT_CLIENT_SECRET='your_client_secret'"
    echo ""
fi

# Test basic imports
echo "🧪 Testing imports..."
.venv/bin/python -c "
try:
    import praw
    import torch
    import pandas as pd
    import asyncio
    print('✅ All required packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Environment setup completed!"
echo ""
echo "Next steps:"
echo "1. Set Reddit API credentials (if not already done)"
echo "2. Run test: .venv/bin/python test_extraction.py"
echo "3. Start full extraction: sbatch scripts/extract_reddit_data.slurm"
echo ""
echo "For more information, see README.md"
