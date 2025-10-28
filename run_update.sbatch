#!/bin/bash
#SBATCH --job-name=campuscluster_update
#SBATCH --output=output_update_spack_py_%j.log
#SBATCH --error=output_update_spack_py_%j.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=secondary

# Load required modules
module load python/3.13.2

# Set Python to unbuffered mode for real-time logging
export PYTHON_UNBUFFERED=1

# Run the campuscluster_update.py script
python3 -u campuscluster_update.py update
