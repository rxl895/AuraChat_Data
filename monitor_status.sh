#!/bin/bash

# AuraChat Project Status Monitor
# Provides comprehensive status of extraction and processing

echo "📊 AURACHAT PROJECT STATUS MONITOR"
echo "=================================="
echo "🕐 $(date)"
echo ""

# Check SLURM job status
echo "🔍 REDDIT EXTRACTION STATUS:"
echo "----------------------------"
SLURM_JOBS=$(squeue -u rxl895 | tail -n +2)
if [ -z "$SLURM_JOBS" ]; then
    echo "❌ No active SLURM jobs found"
    echo "📋 Checking for completed jobs..."
    sacct -u rxl895 --starttime=today --format=JobID,JobName,State,ExitCode,Runtime | tail -5
else
    echo "✅ Active extraction job found:"
    echo "$SLURM_JOBS"
    
    # Get job details
    JOB_ID=$(echo "$SLURM_JOBS" | awk '{print $1}')
    echo ""
    echo "📈 Job Details:"
    echo "Job ID: $JOB_ID"
    echo "Runtime: $(echo "$SLURM_JOBS" | awk '{print $6}')"
    echo "Node: $(echo "$SLURM_JOBS" | awk '{print $8}')"
fi

echo ""

# Check extracted data
echo "💾 EXTRACTED DATA STATUS:"
echo "------------------------"
if [ -d "data/raw" ] && [ "$(ls -A data/raw 2>/dev/null)" ]; then
    echo "✅ Data directory exists with files:"
    ls -lah data/raw/ | tail -5
    
    echo ""
    echo "📊 Data Summary:"
    BATCH_FILES=$(ls data/raw/batch_*.jsonl.gz 2>/dev/null | wc -l)
    echo "Batch files: $BATCH_FILES"
    
    if [ $BATCH_FILES -gt 0 ]; then
        TOTAL_SIZE=$(du -sh data/raw/ | cut -f1)
        echo "Total size: $TOTAL_SIZE"
        
        # Count conversations if possible
        echo "📈 Estimated conversations:"
        for file in data/raw/batch_*.jsonl.gz; do
            if [ -f "$file" ]; then
                COUNT=$(zcat "$file" 2>/dev/null | wc -l)
                echo "  $(basename "$file"): $COUNT conversations"
                break  # Just show first file as example
            fi
        done
    fi
else
    echo "📝 No extracted data found yet (normal for early extraction)"
fi

echo ""

# Check processing status
echo "⚙️ PROCESSING PIPELINE STATUS:"
echo "------------------------------"
if [ -d "data/processed" ] && [ "$(ls -A data/processed 2>/dev/null)" ]; then
    echo "✅ Processed data found:"
    ls -lah data/processed/ | tail -5
else
    echo "⏳ Processing not yet started (waiting for extraction)"
fi

echo ""

# Check logs
echo "📋 RECENT LOG ACTIVITY:"
echo "----------------------"
if [ -d "logs" ]; then
    echo "Recent extraction logs:"
    ls -lt logs/*.out logs/*.err 2>/dev/null | head -3
    
    echo ""
    echo "Last 3 lines from latest extraction log:"
    LATEST_LOG=$(ls -t logs/reddit_extraction_*.out 2>/dev/null | head -1)
    if [ -f "$LATEST_LOG" ]; then
        tail -3 "$LATEST_LOG"
    else
        echo "No extraction logs found"
    fi
else
    echo "📝 No logs directory found"
fi

echo ""

# Project timeline
echo "⏰ PROJECT TIMELINE ESTIMATE:"
echo "-----------------------------"
if [ ! -z "$SLURM_JOBS" ]; then
    RUNTIME=$(echo "$SLURM_JOBS" | awk '{print $6}')
    echo "✅ Extraction: In progress ($RUNTIME elapsed)"
    echo "⏳ Processing: Waiting for extraction (~2-4 hours)"
    echo "⏳ Model Training: Waiting for processing (~4-8 hours)"
    echo "⏳ Total Remaining: ~6-12 hours"
else
    echo "🎯 Extraction: Complete or not started"
    echo "🎯 Next: Run processing pipeline"
fi

echo ""

# Resource usage
echo "💻 SYSTEM RESOURCES:"
echo "-------------------"
echo "Memory usage:"
free -h | head -2

echo ""
echo "Disk usage for project:"
du -sh . 2>/dev/null || echo "Unable to calculate disk usage"

echo ""

# GitHub status
echo "🏆 GITHUB REPOSITORY STATUS:"
echo "----------------------------"
echo "Repository: https://github.com/rxl895/AuraChat_Data"
echo "Commits: $(git rev-list --count HEAD 2>/dev/null || echo 'Unknown')"
echo "Last commit: $(git log -1 --pretty=format:'%h - %s (%cr)' 2>/dev/null || echo 'Git not available')"

echo ""

# Next steps
echo "🎯 RECOMMENDED NEXT STEPS:"
echo "-------------------------"
if [ ! -z "$SLURM_JOBS" ]; then
    echo "1. ⏳ Wait for extraction to complete"
    echo "2. 📊 Monitor progress: tail -f logs/reddit_extraction_*.out"
    echo "3. 🔧 Prepare processing environment: chmod +x setup_processing.sh && ./setup_processing.sh"
    echo "4. 🚀 Run processing when ready: python src/data_processing/run_pipeline.py"
else
    if [ -d "data/raw" ] && [ "$(ls -A data/raw 2>/dev/null)" ]; then
        echo "1. 🔧 Setup processing environment: ./setup_processing.sh"
        echo "2. 🚀 Run data processing: python src/data_processing/run_pipeline.py"
        echo "3. 📊 Review processing results"
        echo "4. 🤖 Begin model training"
    else
        echo "1. 🔍 Check extraction job status"
        echo "2. 📋 Review extraction logs for issues"
        echo "3. 🔄 Restart extraction if needed"
    fi
fi

echo ""
echo "================================================================"
