#!/bin/bash
#SBATCH --job-name=reddit_gpu_extract
#SBATCH --account=rxf131
#SBATCH --partition=gpu
#SBATCH --output=logs/reddit_extraction_%j.out
#SBATCH --error=logs/reddit_extraction_%j.err
#SBATCH --time=6:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=rxl895@case.edu

# GPU-accelerated Reddit data extraction
set -e
set -x

echo "🚀 Starting GPU-Accelerated Reddit Data Extraction"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPU: $CUDA_VISIBLE_DEVICES"
echo "Start time: $(date)"

# Environment setup
echo "🔧 Setting up environment..."

# Load modules (if needed)
# module load python/3.9 cuda/11.8

# Check GPU availability
echo "🔍 GPU Information:"
nvidia-smi
echo "PyTorch GPU check:"
/home/rxl895/AuraChat_Data/.venv/bin/python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
/home/rxl895/AuraChat_Data/.venv/bin/python -c "import torch; print(f'GPU device: {torch.cuda.get_device_name() if torch.cuda.is_available() else \"None\"}')"

# Create necessary directories
mkdir -p logs data/raw data/processed data/checkpoints

# Environment variables for Reddit API
echo "🔑 Setting up Reddit API credentials..."
export REDDIT_CLIENT_ID="${REDDIT_CLIENT_ID:-your_client_id}"
export REDDIT_CLIENT_SECRET="${REDDIT_CLIENT_SECRET:-your_client_secret}"
export REDDIT_USERNAME="${REDDIT_USERNAME:-your_username}"
export REDDIT_PASSWORD="${REDDIT_PASSWORD:-your_password}"

# Check if credentials are set
if [[ "$REDDIT_CLIENT_ID" == "your_client_id" ]]; then
    echo "⚠️  Warning: Reddit API credentials not set!"
    echo "Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables"
    echo "You can set them in your .bashrc or pass them to sbatch:"
    echo "sbatch --export=REDDIT_CLIENT_ID=your_id,REDDIT_CLIENT_SECRET=your_secret extract_reddit_data.slurm"
    # exit 1  # Uncomment to fail if credentials not set
fi

# GPU optimization settings
export CUDA_LAUNCH_BLOCKING=0
export TORCH_CUDA_ARCH_LIST="7.0;7.5;8.0;8.6"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"

# Python settings for better performance
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=8
export PYTHONPATH=/home/rxl895/AuraChat_Data:$PYTHONPATH

echo "🚀 Starting Reddit data extraction..."

# Run the extraction
if /home/rxl895/AuraChat_Data/.venv/bin/python src/gpu_reddit_extractor.py; then
    echo "✅ Reddit data extraction completed successfully!"
    
    # Show results summary
    echo "📋 Extraction Results:"
    ls -la data/raw/ | tail -10
    
    # Count total files and size
    RAW_FILES=$(find data/raw/ -name "*.jsonl.gz" | wc -l)
    TOTAL_SIZE=$(du -sh data/raw/ | cut -f1)
    echo "📊 Summary:"
    echo "   Files created: $RAW_FILES"
    echo "   Total size: $TOTAL_SIZE"
    
    # Show latest summary if available
    LATEST_SUMMARY=$(ls -t data/raw/extraction_summary_*.json 2>/dev/null | head -1)
    if [[ -n "$LATEST_SUMMARY" && -f "$LATEST_SUMMARY" ]]; then
        echo "📈 Extraction Statistics:"
        /home/rxl895/AuraChat_Data/.venv/bin/python -c "
import json
with open('$LATEST_SUMMARY', 'r') as f:
    data = json.load(f)
    stats = data['extraction_stats']
    print(f'Posts processed: {stats[\"total_posts_processed\"]:,}')
    print(f'Comments extracted: {stats[\"total_comments_extracted\"]:,}')
    print(f'Empathy pairs found: {stats[\"empathy_pairs_found\"]:,}')
    print(f'Subreddits completed: {stats[\"subreddits_completed\"]}')
    print(f'Output files: {data[\"total_files\"]}')
"
    fi
    
else
    echo "❌ Reddit data extraction failed!"
    echo "📋 Recent error log:"
    tail -50 logs/reddit_extraction_${SLURM_JOB_ID}.err
    exit 1
fi

echo "🎉 Job completed at $(date)"
