module load python/3.13.2
export PYTHON_UNBUFFERED=1
(sh -c "python3 -u campuscluster_update.py update" &> output_update_spack_py.log) & echo $! > output_update_spack_py.pid & disown # Or whichever one is actually working now