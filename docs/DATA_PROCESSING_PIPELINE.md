# AuraChat Data Processing Pipeline

## 🎯 Overview

This pipeline processes raw Reddit empathy conversation data into training-ready datasets for empathy-enhanced chatbot models.

## 📊 Pipeline Stages

### Stage 1: Data Validation & Cleaning
- **Input**: Raw JSONL.gz files from Reddit extraction
- **Output**: Validated, cleaned conversation data
- **Duration**: ~30 minutes

### Stage 2: Empathy Enhancement & Scoring
- **Input**: Cleaned conversations
- **Output**: Empathy-scored conversation pairs
- **Duration**: ~1-2 hours

### Stage 3: Dataset Generation
- **Input**: Empathy-scored pairs
- **Output**: Training/validation/test splits
- **Duration**: ~20 minutes

### Stage 4: Model Preparation
- **Input**: Split datasets
- **Output**: Model-ready formats (Hugging Face, OpenAI fine-tuning)
- **Duration**: ~15 minutes

## 🔄 Processing Flow

```
Raw Reddit Data (2-5GB)
        ↓
[Stage 1] Data Validation & Cleaning
        ↓
Clean Conversations (~1-3GB)
        ↓
[Stage 2] Empathy Enhancement & Scoring
        ↓
Empathy-Scored Pairs (~800MB-1.5GB)
        ↓
[Stage 3] Dataset Generation
        ↓
Train/Val/Test Splits (~600MB-1GB)
        ↓
[Stage 4] Model Preparation
        ↓
Model-Ready Datasets (~400MB-800MB)
```

## 🛠️ Implementation Plan

### Technologies
- **Processing**: Python 3.9+, Pandas, NumPy
- **NLP**: spaCy, NLTK, Transformers
- **ML**: scikit-learn, PyTorch
- **Empathy Scoring**: Custom models + rule-based
- **Parallel Processing**: multiprocessing, Dask (optional)

### Hardware Requirements
- **CPU**: 8+ cores recommended
- **RAM**: 32GB+ for large datasets
- **Storage**: 20GB free space
- **GPU**: Optional for empathy scoring models

## 📋 Detailed Stage Breakdown

### Stage 1: Data Validation & Cleaning

#### Input Processing
```python
# Expected input format from Reddit extraction
{
    "conversation_id": "unique_id",
    "subreddit": "relationship_advice", 
    "post_title": "Need advice...",
    "post_content": "I'm struggling with...",
    "empathy_pairs": [
        ["I feel overwhelmed", "I understand how difficult this must be"],
        ["Don't know what to do", "You're being so strong right now"]
    ],
    "metadata": {
        "empathy_pairs_count": 2,
        "post_score": 45,
        "num_comments": 12,
        "extraction_timestamp": "2025-07-24T17:59:01"
    }
}
```

#### Cleaning Operations
1. **Remove duplicates** based on conversation_id
2. **Filter by quality**:
   - Minimum empathy_pairs_count: 2
   - Minimum post_score: 10
   - Maximum post length: 2000 characters
   - Language detection: English only
3. **Content sanitization**:
   - Remove personally identifiable information
   - Remove harmful/toxic content
   - Normalize text formatting
4. **Validation checks**:
   - Ensure empathy_pairs are valid
   - Check for missing required fields
   - Verify data integrity

#### Output Format
```python
{
    "conversation_id": "clean_unique_id",
    "subreddit": "relationship_advice",
    "context": "Cleaned and normalized post content",
    "empathy_pairs": [
        {
            "input": "Normalized user message",
            "response": "Normalized empathetic response",
            "empathy_score": 0.85,
            "quality_score": 0.92
        }
    ],
    "metadata": {
        "source_subreddit": "relationship_advice",
        "original_score": 45,
        "processing_timestamp": "2025-07-24T18:30:00",
        "quality_flags": []
    }
}
```

### Stage 2: Empathy Enhancement & Scoring

#### Empathy Scoring System
1. **Rule-based scoring**:
   - Emotional validation phrases
   - Supportive language patterns
   - Active listening indicators
   - Solution-oriented responses

2. **ML-based scoring**:
   - Pre-trained empathy detection models
   - Sentiment analysis integration
   - Emotional intelligence metrics
   - Context-aware scoring

#### Scoring Categories
```python
empathy_categories = {
    "emotional_validation": 0.0-1.0,
    "active_listening": 0.0-1.0, 
    "supportive_language": 0.0-1.0,
    "solution_oriented": 0.0-1.0,
    "emotional_intelligence": 0.0-1.0,
    "overall_empathy": 0.0-1.0
}
```

#### Enhancement Operations
1. **Pair quality assessment**
2. **Empathy score calculation**
3. **Response appropriateness evaluation**
4. **Context relevance scoring**
5. **Toxicity filtering**

### Stage 3: Dataset Generation

#### Dataset Splits
- **Training**: 70% (empathy conversation pairs)
- **Validation**: 15% (model tuning)
- **Test**: 15% (final evaluation)

#### Stratification
- Balanced across subreddits
- Empathy score distribution maintained
- Conversation length variety preserved

#### Output Formats
1. **Hugging Face Datasets**: For transformer fine-tuning
2. **OpenAI Fine-tuning**: JSONL format for GPT models
3. **Custom PyTorch**: For specialized architectures
4. **Evaluation Sets**: Human evaluation subsets

### Stage 4: Model Preparation

#### Format Conversions
1. **Conversational Format**:
```json
{
    "messages": [
        {"role": "user", "content": "I'm feeling overwhelmed..."},
        {"role": "assistant", "content": "I understand how difficult this must be..."}
    ],
    "empathy_score": 0.85
}
```

2. **Instruction Format**:
```json
{
    "instruction": "Respond with empathy to the following message:",
    "input": "I'm feeling overwhelmed...",
    "output": "I understand how difficult this must be...",
    "empathy_metrics": {...}
}
```

## 🚀 Automation Scripts

### Main Processing Script
```bash
# Run complete pipeline
python src/data_processing/run_pipeline.py \
    --input-dir data/raw/ \
    --output-dir data/processed/ \
    --config config/processing_config.yaml \
    --parallel --gpu-acceleration
```

### Individual Stage Scripts
```bash
# Stage 1: Cleaning
python src/data_processing/stage1_cleaning.py

# Stage 2: Empathy scoring  
python src/data_processing/stage2_empathy.py

# Stage 3: Dataset generation
python src/data_processing/stage3_datasets.py

# Stage 4: Model preparation
python src/data_processing/stage4_model_prep.py
```

## 📊 Quality Metrics

### Data Quality Indicators
- **Duplicate rate**: < 1%
- **Clean conversation rate**: > 95%
- **Empathy score distribution**: Normal distribution
- **Language quality**: > 90% high-quality English

### Processing Performance
- **Throughput**: 1000-5000 conversations/minute
- **Memory usage**: < 16GB peak
- **Processing time**: < 3 hours total
- **Error rate**: < 0.1%

## 🔍 Monitoring & Logging

### Progress Tracking
- Real-time processing statistics
- Quality metric monitoring
- Error logging and handling
- Resource usage tracking

### Output Validation
- Schema validation for each stage
- Data integrity checks
- Quality threshold verification
- Final dataset validation

## 📈 Expected Results

### Dataset Characteristics
- **Total conversations**: 15,000-25,000
- **Empathy pairs**: 50,000-100,000
- **High-quality pairs**: 35,000-70,000
- **Training examples**: 24,500-49,000
- **Validation examples**: 5,250-10,500  
- **Test examples**: 5,250-10,500

### Quality Distribution
- **High empathy (0.8+)**: 30-40%
- **Medium empathy (0.6-0.8)**: 40-50%
- **Lower empathy (0.4-0.6)**: 10-20%
- **Filtered out (<0.4)**: 5-10%

## 🎯 Next Steps After Processing

1. **Model Training**: Fine-tune empathy models
2. **Evaluation**: Benchmark against existing chatbots
3. **Human Evaluation**: Quality assessment by humans
4. **Deployment**: Production chatbot deployment
5. **Research**: Academic paper preparation

---

**Timeline**: Complete pipeline execution in 2-4 hours after Reddit extraction finishes.
**Dependencies**: Reddit extraction completion, processing environment setup.
**Success Criteria**: High-quality empathy conversation datasets ready for model training.
