#!/bin/bash
#SBATCH --job-name=DTRA_Campuscluster_Update
#SBATCH --output=/projects/illinois/grants/dtra_ura_msee/share/Outputs/output_update_spack_py_%x_output.txt
#SBATCH --time=4:00:00
#SBATCH --exclude=ccc0465
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
##SBATCH --mem=32G
#SBATCH --partition=IllinoisComputes,dtra,secondary,IllinoisComputes-GPU,eng-research-gpu,eng-instruction,ic-express
#SBATCH --account=dcurreli-npre-eng
#SBATCH --mail-type=END           # Type of email notifications to send

# Load required modules
module load python/3.13.2

# Set Python to unbuffered mode for real-time logging
export PYTHON_UNBUFFERED=1

# Run the campuscluster_update.py script
python3 -u campuscluster_update.py update
