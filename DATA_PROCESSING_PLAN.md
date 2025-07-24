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

## 🚀 Implementation Plan

When Reddit extraction completes, we will:

1. **Setup Processing Environment**
   ```bash
   chmod +x setup_processing.sh
   ./setup_processing.sh
   ```

2. **Run Data Processing Pipeline**
   ```bash
   python src/data_processing/run_pipeline.py \
     --input-dir data/raw/ \
     --output-dir data/processed/ \
     --parallel
   ```

3. **Expected Timeline**
   - Stage 1 (Cleaning): 30 minutes
   - Stage 2 (Empathy Scoring): 1-2 hours  
   - Stage 3 (Dataset Generation): 20 minutes
   - Stage 4 (Model Preparation): 15 minutes
   - **Total**: 2-4 hours

## 📈 Expected Results

### Dataset Characteristics
- **Total conversations**: 15,000-25,000
- **Empathy pairs**: 50,000-100,000
- **High-quality pairs**: 35,000-70,000
- **Training examples**: 24,500-49,000
- **Validation examples**: 5,250-10,500  
- **Test examples**: 5,250-10,500

### Output Formats
1. **Hugging Face Datasets**: For transformer fine-tuning
2. **OpenAI Fine-tuning**: JSONL format for GPT models
3. **Conversational Format**: Multi-turn dialogues
4. **Instruction Format**: Supervised fine-tuning

## 🎯 Next Steps

1. **Complete Reddit Extraction** (currently running)
2. **Setup Processing Environment**
3. **Run Data Processing Pipeline** 
4. **Begin Model Training**
5. **Evaluate Empathy Performance**

---

**Status**: Ready to process when Reddit extraction completes
**Dependencies**: Reddit extraction completion (~3-4 more hours)
**Success Criteria**: High-quality empathy conversation datasets for model training
