# campuscluster_spack

Scripts for installing modules useful for LCPP codes and developers on the Illinois Campus Cluster with Spack.

Usage:
```bash
mkdir share && cd share
git clone https://github.com/Stephen-Armstrong/campuscluster_spack.git 
cd campuscluster_spack
python3 campus_cluster_update_2.py # Or whichever one is actually working now # This might actually need to go in the setup.sh script before the call to install_hpic2deps. 
. setup.sh
```

Alternative Git Clone command:
```bash
git clone git@github.com:Stephen-Armstrong/campuscluster_spack.git
```

This will download Spack and then use Spack to install a bunch of packages,
which are then added to the module list.

After running, it is useful to add the Spack source command to your `.bashrc`:

`. /path/to/share/spack/share/spack/setup-env.sh`

Also suggest making the `share` directory at least read-accessible by the group.

## Installing h5py

The hpic2deps module provides an HDF5 installation that is compatible with h5py. 
After loading the module, you can install h5py with:

```bash
module load hpic2deps/~openmp-cuda-arch-None/Release/latest
pip install h5py
```

The module sets the necessary environment variables (`HDF5_DIR`, `HDF5_LIBDIR`, `HDF5_INCLUDEDIR`, `HDF5_MPI`, and `PKG_CONFIG_PATH`) for h5py to discover and build against the HDF5 installation. See `FIXING_H5PY_COMPATIBILITY.md` for more details.
