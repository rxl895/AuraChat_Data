#!/bin/bash

# AuraChat Project Status Monitor
# Quick status check for extraction and processing

echo "📊 AURACHAT STATUS - $(date)"
echo "==============================================="

# Check SLURM job
echo "🔍 Reddit Extraction:"
squeue -u rxl895 | tail -n +2 || echo "❌ No active jobs"

echo ""
echo "💾 Extracted Data:"
if [ -d "data/raw" ]; then
    ls -lah data/raw/ | grep batch || echo "📝 No batch files yet"
else
    echo "📝 Data directory not created yet"
fi

echo ""
echo "⏰ Next Steps:"
echo "1. Wait for extraction completion (~3-4 hours remaining)"
echo "2. Setup processing: ./setup_processing.sh"
echo "3. Run pipeline: python src/data_processing/run_pipeline.py"

echo ""
echo "🏆 GitHub Progress:"
echo "Commits: $(git rev-list --count HEAD)"
echo "Achievements: Pull Shark, Heart On Sleeve (processing)"
echo "==============================================="
