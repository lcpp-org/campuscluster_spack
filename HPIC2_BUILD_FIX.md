# hpic2 Build Fix

## Problem

The hpic2 build was failing with compilation errors due to missing `#include <iterator>` in several source files:
- `core/magnetic_field/BFromFile.cpp`
- `core/utils/hpic_utils.cpp`
- `core/species/FullOrbitICFromFile.cpp`
- `core/species/FullOrbitVolumetricSourceMinimumMassFromFile.cpp`

## Error Message

```
error: 'istream_iterator' is not a member of 'std'
note: 'std::istream_iterator' is defined in header '<iterator>'; did you forget to '#include <iterator>'?
```

## Root Cause

The hpic2 source code uses `std::istream_iterator` but does not include the `<iterator>` header. With newer versions of GCC (13.3.0), this header is no longer implicitly included by other standard library headers like `<fstream>`.

## Solution

All update scripts now patch the hpic2 source code after cloning to add the missing `#include <iterator>` directive:

```bash
cd hpic2
sed -i '2a #include <iterator>' core/magnetic_field/BFromFile.cpp
sed -i '2a #include <iterator>' core/utils/hpic_utils.cpp
sed -i '2a #include <iterator>' core/species/FullOrbitICFromFile.cpp
sed -i '2a #include <iterator>' core/species/FullOrbitVolumetricSourceMinimumMassFromFile.cpp
cd ..
```

This adds `#include <iterator>` after line 2 (after the existing `#include <fstream>` or similar) in each file.

## Files Modified

The following update scripts have been patched:
- `campuscluster_update.py`
- `campus_cluster_update_2.py`
- `campus_cluster_update_3_fixing_mpi_errors.py`
- `campus_cluster_update_3_hypre_cuda.py`

## Impact

This fix allows hpic2 to build successfully on the Illinois Campus Cluster with GCC 13.3.0. The patch is applied automatically during the build process, so no manual intervention is required.

## Future Work

This is a temporary workaround. The proper solution is to submit a pull request to the upstream hpic2 repository to add the missing includes directly in the source code.
