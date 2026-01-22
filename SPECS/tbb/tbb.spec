%global giturl https://github.com/oneapi-src/oneTBB

Name:    tbb
Summary: The Threading Building Blocks library abstracts low-level threading details
Version: 2021.13.0
Release: 2%{?dist}
License: Apache-2.0 AND BSD-3-Clause
URL:     http://threadingbuildingblocks.org/

Source0: %{giturl}/archive/v%{version}/%{name}-%{version}.tar.gz
# These two are downstream sources.
Source7: tbbmalloc.pc
Source8: tbbmalloc_proxy.pc

# TBB tries to remove -Werror from the compiler flags, which turns
# -Werror=format-security into =format-security
Patch0: tbb-2021-Werror.patch

BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: hwloc
BuildRequires: hwloc-devel
BuildRequires: make
BuildRequires: python3-devel
BuildRequires: python3-pip
BuildRequires: %{py3_dist setuptools}
BuildRequires: %{py3_dist wheel}
BuildRequires: %{py3_dist sphinx}
BuildRequires: %{py3_dist sphinx-rtd-theme}
BuildRequires: swig

%description
Threading Building Blocks (TBB) is a C++ runtime library that
abstracts the low-level threading details necessary for optimal
multi-core performance.  It uses common C++ templates and coding style
to eliminate tedious threading implementation work.

TBB requires fewer lines of code to achieve parallelism than other
threading models.  The applications you write are portable across
platforms.  Since the library is also inherently scalable, no code
maintenance is required as more processor cores become available.


%package bind
Summary: NUMA support library for TBB
Requires: %{name}%{?_isa} = %{version}-%{release}

%description bind
NUMA support library for TBB, allowing the binding of tasks to selected
CPU cores.


%package devel
Summary: The Threading Building Blocks C++ headers and shared development libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-bind%{?_isa} = %{version}-%{release}

%description devel
Header files and shared object symlinks for the Threading Building
Blocks (TBB) C++ libraries.


%package doc
Summary: The Threading Building Blocks documentation
%ifarch %{ix86}
# https://bugzilla.redhat.com/show_bug.cgi?id=2174300
Conflicts: %{name}-doc.x86_64
%endif

%description doc
PDF documentation for the user of the Threading Building Block (TBB)
C++ library.


%package -n python3-%{name}
Summary: Python 3 TBB module
Requires: %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}
Python 3 TBB module.


%prep
%autosetup -p1 -n oneTBB-%{version}

# Invoke the right python binary directly
for fil in $(grep -Frl %{_bindir}/env python); do
    sed -i.orig 's,env python3,python3,' $fil
    touch -r $fil.orig $fil
    rm $fil.orig
done

%generate_buildrequires
cd python
%pyproject_buildrequires

%build
export TBBROOT=$PWD
export PYTHONPATH=$(sed "s,%{_prefix},$PWD/%{_vpath_builddir}/python/build," <<< %{python3_sitearch})
%cmake \
    -DCMAKE_CXX_STANDARD=17 \
    -DTBB4PY_BUILD:BOOL=ON \
    -DTBB_STRICT:BOOL=OFF \
    -DCMAKE_HWLOC_2_4_LIBRARY_PATH=%{_libdir}/libhwloc.so \
    -DCMAKE_HWLOC_2_4_INCLUDE_PATH=%{_includedir}/hwloc \
%cmake_build

# The python package is not built the Fedora way.  Do it over.
unset PYTHONPATH
export LD_LIBRARY_PATH=$(ls -1d $PWD/*relwithdebinfo)
export LDFLAGS="-L $LD_LIBRARY_PATH %{build_ldflags}"
cd python
%pyproject_wheel
cd -

# Build documentation
export BUILD_TYPE=oneapi
sphinx-build doc/GSG getting-started
sphinx-build doc/main html

%install
%cmake_install

# The python package is not installed the Fedora way.  Do it over.
rm -fr %{buildroot}%{python3_sitearch}
cd python
%pyproject_install
cd -

mkdir -p %{buildroot}/%{_libdir}/pkgconfig
for file in %{SOURCE7} %{SOURCE8}; do
    target=%{buildroot}/%{_libdir}/pkgconfig/$(basename ${file})
    sed 's/_FEDORA_VERSION/%{version}/' $file > $target
    touch -r $file $target
done

# Upstream installs tbb32.pc on 32-bit but it's already in a separate directory
# because %_libdir is different for 32-bit and 64-bit, so rename it to tbb.pc.
if [ -f %{buildroot}/%{_libdir}/pkgconfig/%{name}32.pc ]; then
    mv %{buildroot}/%{_libdir}/pkgconfig/%{name}32.pc %{buildroot}/%{_libdir}/pkgconfig/%{name}.pc
fi

rm -fr %{buildroot}%{_datadir}/doc

%check
# Running the tests in parallel often leads to resource exhaustion.
ctest --output-on-failure --force-new-ctest-process

%files
%doc README.md
%license LICENSE.txt
%{_libdir}/libtbb.so.12*
%{_libdir}/libtbbmalloc.so.2*
%{_libdir}/libtbbmalloc_proxy.so.2*
%{_libdir}/libirml.so.1

%files bind
%{_libdir}/libtbbbind_2_5.so.3*

%files devel
%doc cmake/README.md
%{_includedir}/oneapi/
%{_includedir}/tbb/
%{_libdir}/*.so
%{_libdir}/cmake/TBB/
%{_libdir}/pkgconfig/*.pc

%files doc
%doc getting-started html

%files -n python3-%{name}
%doc python/README.md
%{python3_sitearch}/TBB*
%{python3_sitearch}/tbb/
%{python3_sitearch}/__pycache__/TBB*

%changelog
* Sat Jul 20 2024 Fedora Release Engineering <releng@fedoraproject.org> - 2021.13.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild
