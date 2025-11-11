#!/bin/bash
#SBATCH --job-name=duckdb_aggregate
#SBATCH --output=logs/duckdb_aggregate.out
#SBATCH --error=logs/duckdb_aggregate.err
#SBATCH --time=08:00:00
#SBATCH --cpus-per-task=24
#SBATCH --mem=300G

# Run the script
python post_aggregation.py