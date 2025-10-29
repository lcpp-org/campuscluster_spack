cd ..
module load python/3.13.2
git clone -c feature.manyFiles=true https://github.com/spack/spack.git
. spack/share/spack/setup-env.sh
cd -
cp spack_repo/spack_config/* ../spack/etc/spack/.
echo "repos:" > ../spack/etc/spack/repos.yaml
echo "- $PWD/spack_repo/lcpp_spack_repo" >> ../spack/etc/spack/repos.yaml
# Remove user-level configuration that might conflict
rm -f ~/.spack/packages.yaml
rm -f ~/.spack/linux/compilers.yaml
rm -f ~/.spack/compilers.yaml
rm -f ~/.spack/packages.yaml
#cp spack_repo/spack_config/compilers.yaml ~/.spack/bootstrap/config/linux/compilers.yaml
sh install_hpic2deps.sh
spack module tcl refresh --delete-tree -y
. ../spack/share/spack/setup-env.sh
module refresh

