#!/bin/bash
#SBATCH --job-name=LIWCParse
#SBATCH --output=/scratch/cs/ecanet/polwell-mental-health/polwell_mh/jobs/features/logs/LIWCParse_%A_%a.out
#SBATCH --error=/scratch/cs/ecanet/polwell-mental-health/polwell_mh/jobs/features/logs/LIWCParse_%A_%a.err
#SBATCH --array=0-287  # 288 days: 2025-01-01 to 2025-10-15
#SBATCH --time=00:15:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G

# user list path
INPUT_PATH="/scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/interim/aggregates/aggregate-0001.parquet"

# Define start date
START_DATE="2025-01-01"

# Compute the date for this array task
TASK_DATE=$(date -d "$START_DATE +${SLURM_ARRAY_TASK_ID} days" +%Y-%m-%d)


# Path pattern with this task's date
INPUT_PATH="/scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/raw/filtered/users_posts_${TASK_DATE}.parquet"

echo "Processing files in: $INPUT_PATH"

# text column to analyze
TEXT_COLUMN="text"


# Move to project directory
cd /scratch/cs/ecanet/polwell-mental-health/polwell_mh

# Activate conda environment
module load mamba

source activate /scratch/cs/ecanet/polwell-mental-health/polwell_mh/envs/polwell_mh

python /scratch/cs/ecanet/polwell-mental-health/polwell_mh/polwell_mh/features/LIWCParse.py --input_path "$INPUT_PATH" --text_column "$TEXT_COLUMN" -

echo "Completed LIWC parsing"


