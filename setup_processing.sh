#!/bin/bash

# AuraChat Data Processing Setup Script
# Prepares environment for data processing pipeline

echo "🚀 Setting up AuraChat Data Processing Environment"
echo "=================================================="

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/temp
mkdir -p data/checkpoints
mkdir -p logs/processing
mkdir -p src/data_processing
mkdir -p models
mkdir -p docs

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install data processing dependencies
echo "📦 Installing data processing dependencies..."
pip install --upgrade pip

# Core dependencies
pip install pandas numpy scipy
pip install scikit-learn
pip install tqdm
pip install pyyaml

# NLP dependencies
pip install spacy
pip install langdetect
pip install nltk
pip install textblob

# ML/DL dependencies  
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers
pip install datasets
pip install accelerate

# Download spaCy English model
echo "📥 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo "📥 Downloading NLTK data..."
python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('wordnet')
"

# Create processing requirements file
echo "📝 Creating processing requirements.txt..."
cat > requirements_processing.txt << EOF
# AuraChat Data Processing Dependencies

# Core data processing
pandas>=1.5.0
numpy>=1.21.0
scipy>=1.9.0
scikit-learn>=1.1.0
tqdm>=4.64.0
pyyaml>=6.0

# Natural Language Processing
spacy>=3.4.0
langdetect>=1.0.9
nltk>=3.7
textblob>=0.17.1

# Machine Learning & Deep Learning
torch>=1.12.0
torchvision>=0.13.0
torchaudio>=0.12.0
transformers>=4.21.0
datasets>=2.4.0
accelerate>=0.12.0

# Text processing and cleaning
beautifulsoup4>=4.11.0
html2text>=2020.1.16
regex>=2022.7.9

# Utilities
psutil>=5.9.0
memory-profiler>=0.60.0
joblib>=1.1.0

# Optional dependencies for advanced features
# Uncomment if needed:
# torch-audio>=0.12.0  # For audio processing
# sentence-transformers>=2.2.0  # For semantic similarity
# faiss-cpu>=1.7.2  # For efficient similarity search
# wandb>=0.13.0  # For experiment tracking
EOF

echo "✅ Processing environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate environment: source .venv/bin/activate"
echo "2. Wait for Reddit extraction to complete"
echo "3. Run processing pipeline: python src/data_processing/run_pipeline.py"
echo ""
echo "📊 Expected timeline:"
echo "- Reddit extraction: 4-6 hours (currently running)"
echo "- Data processing: 2-4 hours"
echo "- Total time to training-ready data: 6-10 hours"
echo ""
echo "🔍 Monitor extraction progress:"
echo "squeue -u \$USER"
echo "tail -f logs/reddit_extraction_*.out"
