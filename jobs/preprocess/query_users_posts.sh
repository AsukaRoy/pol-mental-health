#!/bin/bash
#SBATCH --job-name=firehose_array
#SBATCH --output=/scratch/cs/ecanet/polwell-mental-health/polwell_mh/jobs/preprocess/logs/firehose_%A_%a.out
#SBATCH --error=/scratch/cs/ecanet/polwell-mental-health/polwell_mh/jobs/preprocess/logs/firehose_%A_%a.err
#SBATCH --array=2-287  # 288 days: 2025-01-01 to 2025-10-15
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

# user list path
USERS_PATH="/scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/external/graph_data_AI.json"

# output path
OUTPUT_PATH="/scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/raw/filtered/users_posts_${TASK_DATE}.parquet"

# Move to project directory
cd /scratch/cs/ecanet/polwell-mental-health/polwell_mh

# Activate conda environment
module load mamba

source activate /scratch/cs/ecanet/polwell-mental-health/polwell_mh/envs/polwell_mh

# Run the initial query script
# /scratch/cs/ecanet/polwell-mental-health/polwell_mh/polwell_mh/preprocess/query_users_posts.py

python /scratch/cs/ecanet/polwell-mental-health/polwell_mh/polwell_mh/preprocess/query_users_posts.py --input "$INPUT_PATH" --users "$USERS_PATH" --output "$OUTPUT_PATH"

echo "Completed processing for date: $TASK_DATE"