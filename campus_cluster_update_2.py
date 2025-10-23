'''
Created on Sep 19, 2024

@author: Stephen Armstrong
'''
import datetime
import sys
import subprocess
import itertools
import os
import shutil
import glob
import numpy as np
import multiprocessing
top_level_dir = os.getcwd() #f"/projects/illinois/eng/npre/dcurreli" #
os.chdir(top_level_dir)

# Only support one compiler/MPI/CUDA combo at a time.
# This is mostly because only one combo works on ICC at a time...
''' #Old modules for RHL 7.2 keeping around for reference
compiler_module = "gcc/8.2.0"
mpi_module = "openmpi/4.1.4-gcc-8.2.0"
cuda_module = "cuda/11.8" #11.6
python_module = "anaconda/3"
'''

#New modules
#Intel compiler may not be needed, but in the event that cmake doesn't work, the intel compiler can generate an basic +omp-cuda build.
compiler_module = "gcc/13.3.0"# intel/tbb intel/compiler-rt intel/umf intel/compiler/2025.0.4"
mpi_module = "openmpi/5.0.1-gcc-13.3.0"
cuda_module = "cuda/12.8" #11.6
python_module = "python/3.13.2"

# ICC currently restricts compiling to a certain number of cores
num_build_cores = len(os.sched_getaffinity(0)) #4
# Delete old versions of builds if the number exceeds this
num_versions_kept = 3
#Module Compile options for OpenMP and CUDA
openmp_options = [True, False] # [True, False]
cuda_arch_options = [None, 70, 80, 86, 90]

#Don't edit the following lines for normal operations
#WHO SHOULD BE EDITING THE FOLLOWING LINES:
#     Stephen Armstrong
#     Andrew Liu
#     Logan Meredith
#Edit anything after this comment at your own risk.
build_types_arr = ["Release", "Debug"]

def update():
    if not os.path.isdir("builds"):
        os.mkdir("builds")
    if not os.path.isdir("modulefiles"):
        os.mkdir("modulefiles")

    #cmake_module = f"{top_level_dir}/modulefiles/cmake"
    cmake_module = f"cmake"
    #cmake_module = "intel/tbb intel/compiler-rt intel/umf intel/compiler/2025.0.4" #Overwriting cmake to what is already installed on the cluster so the following install script isn't necessary but still runs.
    
    # ICC's cmake modules are broken and stupid so build our own.
    if not os.path.isdir("cmake"):
        cmake_build_script = f"""
mkdir cmake && cd cmake
mkdir install
wget https://github.com/Kitware/CMake/releases/download/v3.26.5/cmake-3.26.5-linux-x86_64.sh
sh cmake-3.26.5-linux-x86_64.sh --skip-license --exclude-subdir --prefix=install
cd ..
        """
        subprocess.run(cmake_build_script, shell=True)

        cmake_modulefile_contents = f"""#%Module1.0

module-whatis {{A cross-platform, open-source build system. CMake is a family of tools designed to build, test and package software. }}

proc ModulesHelp {{ }} {{
    puts stderr {{Name   : cmake}}
    puts stderr {{}}
    puts stderr {{A cross-platform, open-source build system. CMake is a family of tools}}
    puts stderr {{designed to build, test and package software.}}
}}
conflict cmake

prepend-path --delim {{:}} PATH {{{top_level_dir}/cmake/install/bin}}
prepend-path --delim {{:}} ACLOCAL_PATH {{{top_level_dir}/cmake/install/share/aclocal}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{top_level_dir}/cmake/install/.}}

        """

        with open(f"{top_level_dir}/modulefiles/cmake", 'w') as cmake_modulefile:
            cmake_modulefile.write(cmake_modulefile_contents)
    
    current_datetime = datetime.datetime.now()
    datetime_format = '%Y-%m-%d'
    datetime_format_length = 10
    current_datetime = current_datetime.strftime(datetime_format)
    
    #assert 1==2
    
    dir_name = f"build_once_modules"
    build_once_dir_path = f"{top_level_dir}/builds/build_once_modules"
    build_type = f"build_once"
    
    build_once_modules_script = f"""
module purge
module use {top_level_dir}/modulefiles
module --ignore_cache load {compiler_module} {mpi_module} {cmake_module}
""" 
    build_once_files = f"""
cd builds
mkdir {dir_name}
cd {dir_name}
"""
    build_once_rust = f"""
# install rust
# set up directories for rust install files
mkdir cargo
mkdir multirust
# setting these env variables installs rust locally,
# rather than in home directory
export CARGO_HOME=$PWD/cargo
export RUSTUP_HOME=$PWD/multirust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
source $CARGO_HOME/env
cd {top_level_dir}/builds/{dir_name}
"""
    build_once_hypre = f"""
# install hypre
# TODO build cuda-aware hypre when cuda enabled
mkdir hypre_dev
cd hypre_dev
git clone https://github.com/hypre-space/hypre.git #git@github.com:hypre-space/hypre.git
cd hypre/src
./configure
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}
"""

    build_once_spdlog = f"""
# install spdlog
mkdir spdlog_dev && cd spdlog_dev
git clone https://github.com/gabime/spdlog.git #git@github.com:gabime/spdlog.git
mkdir build && cd build
cmake ../spdlog -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE={build_type}
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}
"""

    build_once_metis = f"""
# install metis 5
wget https://github.com/mfem/tpls/raw/gh-pages/metis-5.1.0.tar.gz
tar -xvf metis-5.1.0.tar.gz
cd metis-5.1.0
make config prefix=install
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}
"""
    build_once_rustbca = f"""
# install rustbca
git clone https://github.com/lcpp-org/RustBCA.git #git@github.com:lcpp-org/RustBCA.git
cd RustBCA
cargo build --release --lib -j {num_build_cores}
mkdir include && cd include
ln -s ../RustBCA.h .
cd ..
mkdir lib && cd lib
ln -s ../target/release/liblibRustBCA.so .
cd {top_level_dir}/builds/{dir_name}
""" 
    #build_once_script = build_once_modules_script + build_once_files + build_once_rust + build_once_hypre + build_once_spdlog + build_once_metis + build_once_rustbca + build_once_hdf5
    build_once_script = build_once_modules_script + build_once_files + build_once_rust + build_once_hypre + build_once_spdlog + build_once_metis + build_once_rustbca
    subprocess.run(build_once_script, shell=True)
    
    #assert 1==2
    
    for openmp_option, cuda_arch_option in itertools.product(openmp_options, cuda_arch_options):
        option_spec_string = f"{'+' if openmp_option else '~'}openmp-cuda-arch-{str(cuda_arch_option)}"
        # Want to build both Debug and Release versions of hpic2deps,
        # but only the Release version of hpic2 itself.
        # First, hpic2deps
        for build_type in build_types_arr:
            dir_name = f"hpic2deps-{option_spec_string}-{build_type}-{current_datetime}"
            
            build_dependent_dir_path = f"{top_level_dir}/builds/{dir_name}"

            # Remove the build directories for this datetime if it already
            # exists, i.e. if we have already updated today.
            if os.path.exists(f"builds/{dir_name}"):
                shutil.rmtree(f"builds/{dir_name}")

            cuda_enabled = cuda_arch_option != None
            # May want to enable Broadwell optimizations, but not sure
            # if that can be used on all of ICC.
            kokkos_cmake_cmd = f"cmake ../kokkos -DKokkos_ENABLE_SERIAL=ON -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE={build_type} -DKokkos_ENABLE_SHARED=OFF"
            if build_type == "Debug":
                kokkos_cmake_cmd += " -DKokkos_ENABLE_DEBUG=ON -DKokkos_ENABLE_DEBUG_BOUNDS_CHECK=ON -DKokkos_ENABLE_DEBUG_DUALVIEW_MODIFY_CHECK=ON"
            if cuda_enabled:
                kokkos_cmake_cmd += f" -DKokkos_ENABLE_CUDA=ON -DKokkos_ENABLE_CUDA_LAMBDA=ON"
                if cuda_arch_option==70 or cuda_arch_option==72:
                    kokkos_cmake_cmd += f" -DKokkos_ARCH_VOLTA{cuda_arch_option}=ON"
                elif cuda_arch_option==80 or cuda_arch_option==86:
                    kokkos_cmake_cmd += f" -DKokkos_ARCH_AMPERE{cuda_arch_option}=ON"
                elif cuda_arch_option==90:
                    kokkos_cmake_cmd += f" -DKokkos_ARCH_HOPPER{cuda_arch_option}=ON"
            kokkos_cmake_cmd += f" -DKokkos_ENABLE_OPENMP={'ON' if openmp_option else 'OFF'}"
            
            hypre_configure_cmd = f"./configure --enable-shared --prefix={build_dependent_dir_path}/hypre_dev/install"
            if build_type == "Debug":
                hypre_configure_cmd += f" --enable-debug"
            if openmp_option:
                hypre_configure_cmd += f" --with-openmp"
            if cuda_enabled:
                hypre_configure_cmd += f" --with-kokkos --with-cuda --with-gpu-arch={cuda_arch_option}"
                """
            hypre_cmake_cmd = f"cmake ../hypre/src/ -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE={build_type} -DKokkos_DIR={build_dependent_dir_path}/kokkos_dev/install -DHYPRE_BUILD_EXAMPLES=ON -DHYPRE_ENABLE_SHARED=ON"
            if openmp_option:
                hypre_cmake_cmd += f" -DHYPRE_WITH_OPENMP=ON"
            if cuda_enabled:
                hypre_cmake_cmd += f" -DHYPRE_WITH_KOKKOS=ON \
-DKokkos_ROOT={build_dependent_dir_path}/kokkos_dev/install \
-DHYPRE_WITH_CUDA=ON \
-DHYPRE_CUDA_SM={cuda_arch_option} \
-DHYPRE_ENABLE_GPU_PROFILING=ON \
-DHYPRE_ENABLE_CUSPARSE=ON \
-DHYPRE_ENABLE_CUBLAS=ON \
-DHYPRE_ENABLE_CURAND=ON \
-DHYPRE_ENABLE_DEVICE_POOL=ON \
-DHYPRE_ENABLE_UNIFIED_MEMORY=ON"
            """
            mfem_cmake_cmd = f"cmake ../mfem -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE={build_type} -DMETIS_DIR={build_once_dir_path}/metis-5.1.0/build/Linux-x86_64/install -DHYPRE_DIR={build_once_dir_path}/hypre_dev/hypre/src/hypre -DMFEM_USE_MPI=YES"
            if cuda_enabled:
                mfem_cmake_cmd += f" -DMFEM_USE_CUDA=YES -DCUDA_ARCH=sm_{cuda_arch_option}"
            elif openmp_option:
                mfem_cmake_cmd += f" -DMFEM_USE_OPENMP=YES"
            
            module_load_script = f"""
module purge
module use {top_level_dir}/modulefiles
module --ignore_cache load {compiler_module} {mpi_module} {cmake_module} {cuda_module if cuda_enabled else ''}

"""
            subprocess.run(module_load_script, shell=True)
            
            if openmp_options:
                build_dependent_hdf5_mpicc = module_load_script + f"""
# install hdf5
cd {top_level_dir}/builds/{dir_name}
mkdir hdf5_dev && cd hdf5_dev
git clone https://github.com/HDFGroup/hdf5.git #git@github.com:HDFGroup/hdf5.git
mkdir build && cd build
export CC=mpicc
export HDF5_MPI="ON"
mpicc ./configure --enable-parallel --enable-shared
cmake ../hdf5 -DCMAKE_BUILD_TYPE={build_type} -DHDF5_BUILD_EXAMPLES=OFF -DHDF5_ENABLE_PARALLEL=ON -DHDF5_BUILD_CPP_LIB=ON -DHDF5_ALLOW_UNSUPPORTED=ON -DCMAKE_INSTALL_PREFIX=../install -DBUILD_TESTING=OFF
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}
"""
            else:
                build_dependent_hdf5_mpicc = module_load_script + f"""
# install hdf5
cd {top_level_dir}/builds/{dir_name}
mkdir hdf5_dev && cd hdf5_dev
git clone https://github.com/HDFGroup/hdf5.git #git@github.com:HDFGroup/hdf5.git
mkdir build && cd build
cmake ../hdf5 -DCMAKE_BUILD_TYPE={build_type} -DHDF5_BUILD_EXAMPLES=OFF -DHDF5_ENABLE_PARALLEL=ON -DHDF5_BUILD_CPP_LIB=ON -DHDF5_ALLOW_UNSUPPORTED=ON -DCMAKE_INSTALL_PREFIX=../install -DBUILD_TESTING=OFF
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}
"""
            
            build_dependent_script_kokkos = module_load_script + f"""
cd builds
mkdir {dir_name}
cd {dir_name}

# install kokkos
mkdir kokkos_dev && cd kokkos_dev
git clone https://github.com/kokkos/kokkos.git #git@github.com:kokkos/kokkos.git
mkdir build && cd build
{kokkos_cmake_cmd}
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}

"""
            build_dependent_script_hypre = module_load_script + f"""
module load kokkos
cd {top_level_dir}/builds/{dir_name}
# install hypre
# TODO build cuda-aware hypre when cuda enabled
mkdir hypre_dev
cd hypre_dev
git clone https://github.com/hypre-space/hypre.git #git@github.com:hypre-space/hypre.git
cd hypre/src
#mkdir build && cd build
#./configure
{hypre_configure_cmd}
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}
"""
            build_dependent_script_pumimbbl = module_load_script + f"""
cd {top_level_dir}/builds/{dir_name}
# install pumimbbl
mkdir pumiMBBL_dev && cd pumiMBBL_dev
git clone https://github.com/SCOREC/pumiMBBL.git #git@github.com:SCOREC/pumiMBBL.git
mkdir build && cd build
cmake ../pumiMBBL -DCMAKE_INSTALL_PREFIX=../install -DKokkos_ROOT=../../kokkos_dev/install -DCMAKE_BUILD_TYPE={build_type}
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}
"""

            build_dependent_script_mfem = module_load_script + f"""
cd {top_level_dir}/builds/{dir_name}
# install mfem
mkdir mfem_dev && cd mfem_dev
git clone https://github.com/mfem/mfem.git #git@github.com:mfem/mfem.git
mkdir build && cd build
{mfem_cmake_cmd}
make -j{num_build_cores}
make install
cd {top_level_dir}/builds/{dir_name}

"""
            subprocess.run(build_dependent_script_kokkos, shell=True)
            subprocess.run(build_dependent_hdf5_mpicc, shell=True)
            #assert 1==2
            #subprocess.run(build_dependent_script_hypre, shell=True) #Tried to make hypre cuda aware. It didn't work before APS-DPP.
            #assert 1==2
            subprocess.run(build_dependent_script_pumimbbl, shell=True)
            subprocess.run(build_dependent_script_mfem, shell=True)
            #assert 1 == 2 
            
            

            # I wrote this modulefile based on the modulefiles generated by
            # spack for each of these packages.
            modulefile_contents = f"""#%Module1.0

module-whatis {{Dependencies for hPIC2 building. }}

proc ModulesHelp {{ }} {{
    puts stderr {{Name   : hpic2deps}}
}}

conflict hpic2deps
conflict cmake
conflict gcc
conflict openmpi
conflict cuda
if {{![info exists ::env(LMOD_VERSION_MAJOR)]}} {{
    module load {mpi_module}
    module load {compiler_module}
    module load {cmake_module}
    module load {python_module}
    {'module load ' + cuda_module if cuda_enabled else ''}
}} else {{
    depends-on {mpi_module}
    depends-on {compiler_module}
    depends-on {cmake_module}
    depends-on {python_module}
    {'depends-on ' + cuda_module if cuda_enabled else ''}
}}


prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_once_dir_path}/hypre_dev/hypre/src/hypre/.}}
setenv HYPRE_ROOT {{{build_once_dir_path}/hypre_dev/hypre/src/hypre}}
#append-path --delim {{:}} LD_LIBRARY_PATH {{{build_once_dir_path}/hypre_dev/install/lib64}}
#setenv HYPRE_DIR {{{build_once_dir_path}/hypre_dev/install}}
#setenv HYPRE_INCLUDE_DIRS {{{build_once_dir_path}/hypre_dev/install/include}}
#setenv HYPRE_LIBRARY_DIRS {{{build_once_dir_path}/hypre_dev/install/lib64}}

prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_once_dir_path}/spdlog_dev/install/.}}
prepend-path --delim {{:}} PATH {{{build_dependent_dir_path}/kokkos_dev/install/bin}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dependent_dir_path}/kokkos_dev/install/.}}
setenv KOKKOS_ROOT {{{build_dependent_dir_path}/kokkos_dev/install}}
prepend-path --delim {{:}} PATH {{{build_once_dir_path}/metis-5.1.0/build/Linux-x86_64/install/bin}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_once_dir_path}/metis-5.1.0/build/Linux-x86_64/install/.}}
setenv METIS_ROOT {{{build_once_dir_path}/metis-5.1.0/build/Linux-x86_64/install}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dependent_dir_path}/mfem_dev/install/.}}
setenv MFEM_ROOT {{{build_dependent_dir_path}/mfem_dev/install}}
setenv PUMIMBBL_ROOT {{{build_dependent_dir_path}/pumiMBBL_dev/install}}
setenv RUSTBCA_ROOT {{{build_once_dir_path}/RustBCA}}
prepend-path --delim {{:}} PATH {{{build_once_dir_path}/hdf5_dev/install/bin}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_once_dir_path}/hdf5_dev/install/.}}
append-path --delim {{:}} LD_LIBRARY_PATH {{{build_once_dir_path}/hdf5_dev/install/lib}}
setenv HDF5_ROOT {{{build_dependent_dir_path}/hdf5_dev/install}}
setenv HDF5_DIR {{{build_dependent_dir_path}/hdf5_dev/install}}
setenv HDF5_MPI ON

            """
            
            modulefile_dir = f"{top_level_dir}/modulefiles/hpic2deps/{option_spec_string}/{build_type}"
            if not os.path.exists(modulefile_dir):
                os.makedirs(modulefile_dir)
            with open(f"{modulefile_dir}/{current_datetime}", 'w') as modulefile:
                modulefile.write(modulefile_contents)

            # Remove the "latest" modulefile
            if os.path.exists(f"{modulefile_dir}/latest"):
                os.unlink(f"{modulefile_dir}/latest")

            # Delete old builds, if necessary.
            old_builds = glob.glob(f"{top_level_dir}/builds/hpic2deps-{option_spec_string}-{build_type}-*")
            build_dates = [old_build[-datetime_format_length:] for old_build in old_builds]
            # Convert date strings to datetime objects, for comparisons
            build_dates = np.array([datetime.datetime.strptime(build_date, datetime_format) for build_date in build_dates])
            sorted_build_date_indices = np.argsort(build_dates)
            for old_build_index in sorted_build_date_indices[:-num_versions_kept]:
                old_build = old_builds[old_build_index]
                shutil.rmtree(old_build)

            # Delete old modulefiles, if necessary.
            old_mfs = glob.glob(f"{modulefile_dir}/*")
            # The modulefile names are their build dates.
            # Convert date strings to datetime objects, for comparisons.
            build_dates = np.array([datetime.datetime.strptime(build_date[-datetime_format_length:], datetime_format) for build_date in old_mfs])
            sorted_build_date_indices = np.argsort(build_dates)
            for old_mf_index in sorted_build_date_indices[:-num_versions_kept]:
                old_mf = old_mfs[old_mf_index]
                os.remove(old_mf)

            # Update the "latest" modulefile
            os.link(f"{modulefile_dir}/{current_datetime}", f"{modulefile_dir}/latest")

        # Now build Release version of hpic2 itself
        dir_name = f"hpic2-{option_spec_string}-{current_datetime}"

        # Remove the build directories for this datetime if it already
        # exists, i.e. if we have already updated today.
        if os.path.exists(f"builds/{dir_name}"):
            shutil.rmtree(f"builds/{dir_name}")

        deps_module = f"hpic2deps/{option_spec_string}/Release/latest"

        build_script = f"""
module purge
module use {top_level_dir}/modulefiles
module load {deps_module}

cd builds
mkdir {dir_name}
cd {dir_name}

git clone --recurse-submodules https://github.com/lcpp-org/hpic2.git #git@github.com:lcpp-org/hpic2.git
mkdir build && cd build
#cmake ../hpic2 -DWITH_RUSTBCA=ON -DWITH_PUMIMBBL=ON -DWITH_MFEM=ON
cmake ../hpic2 -DWITH_RUSTBCA=ON -DWITH_PUMIMBBL=ON
make -j{num_build_cores}

        """

        subprocess.run(build_script, shell=True)


        # I wrote this modulefile based on the modulefiles generated by
        # spack for each of these packages.
        modulefile_contents = f"""#%Module1.0

module-whatis {{hPIC2 }}

proc ModulesHelp {{ }} {{
    puts stderr {{Name   : hpic2}}
}}

conflict hpic2
if {{![info exists ::env(LMOD_VERSION_MAJOR)]}} {{
    module load {deps_module}
}} else {{
    depends-on {deps_module}
}}

prepend-path --delim {{:}} PATH {{{top_level_dir}/builds/{dir_name}/build}}

        """

        modulefile_dir = f"{top_level_dir}/modulefiles/hpic2/{option_spec_string}"
        if not os.path.exists(modulefile_dir):
            os.makedirs(modulefile_dir)
        with open(f"{modulefile_dir}/{current_datetime}", 'w') as modulefile:
            modulefile.write(modulefile_contents)

        # Remove the "latest" modulefile
        if os.path.exists(f"{modulefile_dir}/latest"):
            os.unlink(f"{modulefile_dir}/latest")

        # Delete old builds, if necessary.
        old_builds = glob.glob(f"{top_level_dir}/builds/hpic2-{option_spec_string}-*")
        build_dates = [old_build[-datetime_format_length:] for old_build in old_builds]
        # Convert date strings to datetime objects, for comparisons
        build_dates = np.array([datetime.datetime.strptime(build_date, datetime_format) for build_date in build_dates])
        sorted_build_date_indices = np.argsort(build_dates)
        for old_build_index in sorted_build_date_indices[:-num_versions_kept]:
            old_build = old_builds[old_build_index]
            shutil.rmtree(old_build)

        # Delete old modulefiles, if necessary.
        old_mfs = glob.glob(f"{modulefile_dir}/*")
        # The modulefile names are their build dates.
        # Convert date strings to datetime objects, for comparisons.
        build_dates = np.array([datetime.datetime.strptime(build_date[-datetime_format_length:], datetime_format) for build_date in old_mfs])
        sorted_build_date_indices = np.argsort(build_dates)
        for old_mf_index in sorted_build_date_indices[:-num_versions_kept]:
            old_mf = old_mfs[old_mf_index]
            os.remove(old_mf)

        # Update the "latest" modulefile
        os.link(f"{modulefile_dir}/{current_datetime}", f"{modulefile_dir}/latest")

    print(f"""
Done! If you haven't already, update your module search path with

module use {top_level_dir}/modulefiles
    """)
    return True


if __name__ == "__main__":
    help_message = f"""
Hi! This is a script to update hpic2 and dependencies on ICC.

You probably wanna

module purge
module load anaconda/3

before using this. This script will build the most recent versions of hpic2
and its dependencies, creating modulefiles for all of them, and deleting old
versions. Currently, you can update once per day; if you run this more than once
in a day, it will delete the builds from earlier in the day and proceed with
a fresh build. You may run this for the first time in an empty directory.
Afterward, update by running from inside the same directory.
Usage:

python3 {os.path.basename(__file__)} update
    """

    if len(sys.argv) == 2 and sys.argv[1] == "update":
        update()
    else:
        print(help_message)
