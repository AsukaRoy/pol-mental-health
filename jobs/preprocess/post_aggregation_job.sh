#!/bin/bash
#SBATCH --job-name=duckdb_aggregate
#SBATCH --output=/scratch/cs/ecanet/polwell-mental-health/polwell_mh/jobs/preprocess/logs/duckdb_aggregate.out
#SBATCH --error=/scratch/cs/ecanet/polwell-mental-health/polwell_mh/jobs/preprocess/logs/duckdb_aggregate.err
#SBATCH --time=08:00:00
#SBATCH --cpus-per-task=24
#SBATCH --mem=300G

# Run the script

# Move to project directory
cd /scratch/cs/ecanet/polwell-mental-health/polwell_mh

# Activate conda environment
module load mamba

source activate /scratch/cs/ecanet/polwell-mental-health/polwell_mh/envs/polwell_mh

python /scratch/cs/ecanet/polwell-mental-health/polwell_mh/polwell_mh/preprocess/post_aggregation.py

echo "Completed post_aggregation"