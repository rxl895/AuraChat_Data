"""
AuraChat Data Processing Pipeline - Main Orchestrator
Processes raw Reddit extraction data into training-ready empathy datasets
"""

import json
import gzip
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
import numpy as np
from tqdm import tqdm

# Import pipeline stages
from stage1_cleaning import DataCleaner
from stage2_empathy import EmpathyScorer
from stage3_datasets import DatasetGenerator
from stage4_model_prep import ModelPreparator

class DataProcessingPipeline:
    """Main data processing pipeline orchestrator"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load processing configuration"""
        default_config = {
            "input_dir": "data/raw/",
            "output_dir": "data/processed/",
            "temp_dir": "data/temp/",
            "parallel_workers": mp.cpu_count() - 1,
            "batch_size": 1000,
            "quality_thresholds": {
                "min_empathy_pairs": 2,
                "min_post_score": 10,
                "max_post_length": 2000,
                "min_empathy_score": 0.4
            },
            "dataset_splits": {
                "train": 0.7,
                "validation": 0.15,
                "test": 0.15
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs/processing/")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"data_processing_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_raw_data(self) -> List[Dict[str, Any]]:
        """Load all raw Reddit extraction files"""
        input_dir = Path(self.config["input_dir"])
        raw_files = list(input_dir.glob("batch_*.jsonl.gz"))
        
        if not raw_files:
            raise FileNotFoundError(f"No batch files found in {input_dir}")
            
        self.logger.info(f"Found {len(raw_files)} raw data files")
        
        all_conversations = []
        for file_path in tqdm(raw_files, desc="Loading raw data"):
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            conversation = json.loads(line)
                            all_conversations.append(conversation)
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
                
        self.logger.info(f"Loaded {len(all_conversations)} raw conversations")
        return all_conversations
    
    def run_stage1_cleaning(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stage 1: Data validation and cleaning"""
        self.logger.info("🧹 Starting Stage 1: Data Cleaning")
        
        cleaner = DataCleaner(self.config)
        
        # Process in parallel batches
        batch_size = self.config["batch_size"]
        batches = [raw_data[i:i + batch_size] for i in range(0, len(raw_data), batch_size)]
        
        cleaned_conversations = []
        with ProcessPoolExecutor(max_workers=self.config["parallel_workers"]) as executor:
            futures = [executor.submit(cleaner.clean_batch, batch) for batch in batches]
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Cleaning batches"):
                try:
                    batch_result = future.result()
                    cleaned_conversations.extend(batch_result)
                except Exception as e:
                    self.logger.error(f"Error in cleaning batch: {e}")
        
        # Save intermediate results
        stage1_output = Path(self.config["temp_dir"]) / "stage1_cleaned.jsonl.gz"
        stage1_output.parent.mkdir(parents=True, exist_ok=True)
        
        with gzip.open(stage1_output, 'wt', encoding='utf-8') as f:
            for conv in cleaned_conversations:
                f.write(json.dumps(conv) + '\n')
                
        self.logger.info(f"✅ Stage 1 complete: {len(cleaned_conversations)} clean conversations")
        return cleaned_conversations
    
    def run_stage2_empathy(self, clean_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stage 2: Empathy enhancement and scoring"""
        self.logger.info("💝 Starting Stage 2: Empathy Scoring")
        
        scorer = EmpathyScorer(self.config)
        
        # Process conversations for empathy scoring
        empathy_scored = []
        for conversation in tqdm(clean_data, desc="Scoring empathy"):
            try:
                scored_conv = scorer.score_conversation(conversation)
                if scored_conv:  # Only keep high-quality empathy conversations
                    empathy_scored.append(scored_conv)
            except Exception as e:
                self.logger.error(f"Error scoring conversation {conversation.get('conversation_id', 'unknown')}: {e}")
        
        # Save intermediate results
        stage2_output = Path(self.config["temp_dir"]) / "stage2_empathy_scored.jsonl.gz"
        with gzip.open(stage2_output, 'wt', encoding='utf-8') as f:
            for conv in empathy_scored:
                f.write(json.dumps(conv) + '\n')
                
        self.logger.info(f"✅ Stage 2 complete: {len(empathy_scored)} empathy-scored conversations")
        return empathy_scored
    
    def run_stage3_datasets(self, empathy_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Stage 3: Dataset generation and splitting"""
        self.logger.info("📊 Starting Stage 3: Dataset Generation")
        
        generator = DatasetGenerator(self.config)
        
        # Generate train/validation/test splits
        datasets = generator.create_splits(empathy_data)
        
        # Save datasets
        output_dir = Path(self.config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for split_name, split_data in datasets.items():
            split_file = output_dir / f"{split_name}_dataset.jsonl.gz"
            with gzip.open(split_file, 'wt', encoding='utf-8') as f:
                for item in split_data:
                    f.write(json.dumps(item) + '\n')
            
            self.logger.info(f"💾 Saved {split_name}: {len(split_data)} examples")
        
        self.logger.info("✅ Stage 3 complete: Datasets generated")
        return datasets
    
    def run_stage4_model_prep(self, datasets: Dict[str, List[Dict[str, Any]]]):
        """Stage 4: Model preparation and format conversion"""
        self.logger.info("🚀 Starting Stage 4: Model Preparation")
        
        preparator = ModelPreparator(self.config)
        
        # Generate multiple model formats
        formats = ['huggingface', 'openai', 'conversational', 'instruction']
        
        for format_name in formats:
            self.logger.info(f"📝 Preparing {format_name} format")
            preparator.prepare_format(datasets, format_name)
        
        self.logger.info("✅ Stage 4 complete: All model formats prepared")
    
    def generate_processing_report(self, datasets: Dict[str, List[Dict[str, Any]]]):
        """Generate comprehensive processing report"""
        report = {
            "processing_timestamp": datetime.now().isoformat(),
            "pipeline_config": self.config,
            "dataset_statistics": {},
            "quality_metrics": {},
            "empathy_distribution": {}
        }
        
        # Calculate statistics for each split
        for split_name, split_data in datasets.items():
            empathy_scores = []
            for item in split_data:
                if 'empathy_pairs' in item:
                    for pair in item['empathy_pairs']:
                        if 'empathy_score' in pair:
                            empathy_scores.append(pair['empathy_score'])
            
            report["dataset_statistics"][split_name] = {
                "total_examples": len(split_data),
                "avg_empathy_score": np.mean(empathy_scores) if empathy_scores else 0,
                "empathy_std": np.std(empathy_scores) if empathy_scores else 0,
                "high_empathy_count": sum(1 for s in empathy_scores if s >= 0.8),
                "medium_empathy_count": sum(1 for s in empathy_scores if 0.6 <= s < 0.8),
                "low_empathy_count": sum(1 for s in empathy_scores if s < 0.6)
            }
        
        # Save report
        report_file = Path(self.config["output_dir"]) / "processing_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📋 Processing report saved to {report_file}")
        return report
    
    def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run the complete data processing pipeline"""
        start_time = datetime.now()
        self.logger.info("🚀 Starting AuraChat Data Processing Pipeline")
        
        try:
            # Stage 1: Load and clean raw data
            raw_data = self.load_raw_data()
            clean_data = self.run_stage1_cleaning(raw_data)
            
            # Stage 2: Empathy scoring
            empathy_data = self.run_stage2_empathy(clean_data)
            
            # Stage 3: Dataset generation
            datasets = self.run_stage3_datasets(empathy_data)
            
            # Stage 4: Model preparation
            self.run_stage4_model_prep(datasets)
            
            # Generate final report
            report = self.generate_processing_report(datasets)
            
            end_time = datetime.now()
            processing_time = end_time - start_time
            
            self.logger.info(f"🎉 Pipeline completed successfully in {processing_time}")
            self.logger.info(f"📊 Total datasets: {sum(len(d) for d in datasets.values())} examples")
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description="AuraChat Data Processing Pipeline")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--input-dir", type=str, help="Input directory override")
    parser.add_argument("--output-dir", type=str, help="Output directory override")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing")
    
    args = parser.parse_args()
    
    # Override config with command line arguments
    config_overrides = {}
    if args.input_dir:
        config_overrides["input_dir"] = args.input_dir
    if args.output_dir:
        config_overrides["output_dir"] = args.output_dir
    if not args.parallel:
        config_overrides["parallel_workers"] = 1
    
    # Initialize and run pipeline
    pipeline = DataProcessingPipeline(args.config)
    
    # Apply command line overrides
    pipeline.config.update(config_overrides)
    
    # Run the complete pipeline
    report = pipeline.run_complete_pipeline()
    
    print("\n🎉 Data Processing Complete!")
    print(f"📊 Final Report: {pipeline.config['output_dir']}/processing_report.json")

if __name__ == "__main__":
    main()
