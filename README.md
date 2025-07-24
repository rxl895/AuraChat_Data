# AuraChat Data Extraction v2.0

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/rxl895/AuraChat_Data/blob/main/LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![Security Policy](https://img.shields.io/badge/Security-Policy-blueviolet)](SECURITY.md)

**GPU-Accelerated Reddit Data Extraction for Empathy Research**

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- CUDA-capable GPU (recommended)
- Reddit API credentials
- 64GB+ RAM for large-scale extraction

### Installation

1. **Clone and setup environment:**
```bash
cd /home/rxl895/AuraChat_Data
pip install -r requirements.txt
```

2. **Configure Reddit API:**
```bash
# Option 1: Environment variables (recommended)
export REDDIT_CLIENT_ID="your_actual_client_id"
export REDDIT_CLIENT_SECRET="your_actual_client_secret"
export REDDIT_USERNAME="your_reddit_username"  # optional
export REDDIT_PASSWORD="your_reddit_password"  # optional

# Option 2: Edit config/settings.py
# Update REDDIT_CONFIG dictionary with your credentials
```

3. **Test setup:**
```bash
python test_extraction.py
```

4. **Run full extraction:**
```bash
sbatch scripts/extract_reddit_data.slurm
```

## 📊 Project Structure

```
AuraChat_Data/
├── src/
│   └── gpu_reddit_extractor.py    # Main extraction engine
├── config/
│   └── settings.py                # Configuration settings
├── scripts/
│   └── extract_reddit_data.slurm  # SLURM deployment script
├── data/
│   ├── raw/                       # Raw extracted data
│   ├── processed/                 # Processed datasets
│   └── checkpoints/               # Extraction checkpoints
├── logs/                          # Extraction logs
├── test_extraction.py             # Test and validation script
└── requirements.txt               # Python dependencies
```

## 🔧 Features

### GPU Acceleration
- **Batch Processing**: Process 50 subreddits simultaneously
- **Memory Optimization**: Automatic cleanup and GPU memory management
- **Parallel Processing**: 8 concurrent API requests
- **Compression**: Gzip-compressed JSONL output

### Data Quality
- **Empathy Detection**: Advanced keyword-based empathy scoring
- **Content Filtering**: Remove deleted/removed content
- **Quality Thresholds**: Configurable minimum scores and lengths
- **Conversation Pairing**: Automatic empathy conversation pair extraction

### Scalability
- **Checkpoint System**: Resume from interruptions
- **Batch Saves**: Automatic intermediate saves every 1000 conversations
- **Progress Tracking**: Real-time statistics and ETA
- **Error Recovery**: Robust error handling and retry mechanisms

## 📋 Configuration

### Target Subreddits (45 communities)
- Support: `relationship_advice`, `offmychest`, `depression`, `Anxiety`
- Mental Health: `mentalhealth`, `SuicideWatch`, `ADHD`, `bipolar`
- Life Advice: `internetparents`, `MomForAMinute`, `DadForAMinute`
- And 35 more empathetic communities...

### Data Extraction Settings
- **Posts per subreddit**: 500 (25,000 total posts)
- **Comments per post**: 20 (up to 500,000 comments)
- **Minimum comment length**: 20 characters
- **Minimum empathy keywords**: 2 per response
- **Batch size**: 50 subreddits per batch

### GPU Settings
- **Device**: Auto-detect CUDA/CPU
- **Mixed precision**: Enabled for speed
- **Batch processing**: 128 sequences at once
- **Memory management**: Automatic cleanup

## 🎯 Expected Output

### Data Volume (Estimated)
- **Raw conversations**: 15,000-25,000
- **Empathy pairs**: 50,000-100,000
- **Total comments**: 300,000-500,000
- **File size**: 2-5GB compressed

### Output Format
```json
{
  "conversation_id": "abc123...",
  "subreddit": "relationship_advice",
  "post_title": "Need advice on...",
  "post_content": "I'm going through...",
  "empathy_pairs": [
    ["I'm feeling overwhelmed...", "I understand how difficult this must be..."],
    ["I don't know what to do...", "You're being so strong right now..."]
  ],
  "metadata": {
    "empathy_pairs_count": 2,
    "post_score": 45,
    "num_comments": 12
  }
}
```

## 🚀 Running the Extraction

### Local Test (3 subreddits, ~30 posts)
```bash
python test_extraction.py
```

### Full Production Extraction
```bash
# With environment variables
sbatch --export=REDDIT_CLIENT_ID=your_id,REDDIT_CLIENT_SECRET=your_secret scripts/extract_reddit_data.slurm

# Or edit credentials in config/settings.py first
sbatch scripts/extract_reddit_data.slurm
```

### Monitoring Progress
```bash
# Check job status
squeue -u $USER

# Monitor logs
tail -f logs/reddit_extraction_JOBID.out

# Check GPU usage
watch nvidia-smi
```

## 📈 Performance Expectations

### With GPU Acceleration
- **Processing speed**: ~100 posts/minute
- **Total time**: 4-6 hours for full extraction
- **Memory usage**: 8-16GB GPU, 32-64GB RAM
- **Network**: 1-2 requests/second (respects Reddit limits)

### Checkpoints and Recovery
- **Auto-checkpoint**: Every 3 batches (~150 subreddits)
- **Resume capability**: Start from any batch number
- **Error recovery**: Automatic retry with exponential backoff
- **Progress persistence**: All statistics saved to checkpoints

## 🔍 Quality Assurance

### Empathy Detection
- **Keyword matching**: 24 empathy categories
- **Minimum threshold**: 2+ empathy keywords per response
- **Context aware**: Post-comment and comment-reply pairs
- **Quality filtering**: Score thresholds and length requirements

### Data Validation
- **Content filtering**: Remove deleted/removed posts
- **Language detection**: English language posts only
- **Spam filtering**: Score-based quality thresholds
- **Duplicate detection**: Unique conversation IDs

## 🛠️ Troubleshooting

### Common Issues
1. **Reddit API Rate Limits**: Automatic handling with delays
2. **GPU Memory**: Automatic cleanup and batch size adjustment
3. **Network Timeouts**: Retry mechanism with backoff
4. **Disk Space**: Monitor `data/raw/` directory size

### Error Recovery
```bash
# Resume from checkpoint
python src/gpu_reddit_extractor.py --resume-from-checkpoint data/checkpoints/latest.pkl

# Process specific subreddits only
python src/gpu_reddit_extractor.py --subreddit-list "depression,anxiety,mentalhealth"

# Debug mode with detailed logging
PYTHONPATH=. python -m pdb src/gpu_reddit_extractor.py
```

## 📊 Monitoring Commands

```bash
# Check extraction progress
ls -la data/raw/ | tail -10

# Count extracted conversations
zcat data/raw/*.jsonl.gz | wc -l

# Check empathy pairs
zcat data/raw/*.jsonl.gz | jq '.empathy_pairs | length' | awk '{sum+=$1} END {print sum}'

# Monitor system resources
htop
nvidia-smi
df -h data/
```

## 🎯 Next Steps

After successful extraction:

1. **Data Processing**: Clean and format data for training
2. **Model Training**: Fine-tune empathy models
3. **Evaluation**: Benchmark empathy performance
4. **Publication**: Academic paper preparation

## 🏆 GitHub Achievements Progress

We're actively working to unlock GitHub achievements through quality development practices:

### 🌟 Repository Health
- ✅ **MIT License** - Open source licensing
- ✅ **Code of Conduct** - Community guidelines established
- ✅ **Security Policy** - Vulnerability reporting process
- ✅ **Contributing Guidelines** - Clear contribution instructions

### 🚀 Development Milestones
- ✅ **Initial Repository** - Project foundation established
- ✅ **Pull Request Workflow** - Collaborative development achieved
- ✅ **Community Building** - Welcoming contributors
- ✅ **Documentation Excellence** - Comprehensive project docs

### 📊 Current Stats
- **Commits**: Growing commit history with meaningful messages
- **Branches**: Feature branch workflow implementation  
- **Pull Requests**: 2+ merged PRs (Pull Shark achievement target)
- **Documentation**: Complete README, contributing guidelines, and security policy
- **Community Files**: All GitHub recommended files present

### 🤝 Collaboration Features
- **Co-authored Commits**: Pair programming support enabled
- **Issue Templates**: Coming soon for better bug reports
- **Discussion Forum**: Ready for community Q&A
- **Wiki**: Available for extended documentation

---

**Status**: Fresh setup ready for large-scale GPU-accelerated data extraction  
**Last Updated**: July 24, 2025  
**Version**: 2.0 (Complete rewrite)