#!/bin/bash
#SBATCH --job-name=firehose_array
#SBATCH --output=logs/firehose_%A_%a.out
#SBATCH --error=logs/firehose_%A_%a.err
#SBATCH --array=0-287  # 288 days: 2025-01-01 to 2025-10-15
#SBATCH --time=00:15:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G

# Define start date
START_DATE="2025-01-01"

# Compute the date for this array task
TASK_DATE=$(date -d "$START_DATE +${SLURM_ARRAY_TASK_ID} days" +%Y-%m-%d)

# Path pattern with this task's date
INPUT_PATH="/m/cs/scratch/sinitaivas/bluesky_firehose/firehose_stream/${TASK_DATE}/*.ndjson.gz"

echo "Processing files in: $INPUT_PATH"


# Move to project directory
cd /scratch/cs/ecanet/polwell-mental-health/polwell_mh

# Activate conda environment
mamba activate /scratch/cs/ecanet/polwell-mental-health/polwell_mh/envs/polwell_mh

# Run the initial query script
# /scratch/cs/ecanet/polwell-mental-health/polwell_mh/polwell_mh/preprocess/initial_query.py

python polwell_mh.preprocess.initial_query.py --input "$INPUT_PATH"
echo "Completed processing for date: $TASK_DATE"