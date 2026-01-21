Summary:	    Intel Neural Processing Unit Driver
Name:		    intel-npu-driver
Version:	    1.28.0
Release:	    2%{?dist}
License:	    MIT AND Apache-2.0
Vendor:         Intel Corporation
Distribution:   Edge Microvisor Toolkit
URL:		    https://github.com/intel/linux-npu-driver
Source0:	    %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-v%{version}.tar.gz
Source1:	    https://github.com/intel/level-zero-npu-extensions/archive/61e4aeb00afd2a5b6955986269eed3a713c7b562/level-zero-npu-extensions-61e4aeb.tar.gz
Source2:	    https://github.com/openvinotoolkit/npu_compiler_elf/archive/9d91134722e70bf52297adaeb221a0be8e408b14/npu_compiler_elf-9d91134.tar.gz
Source3:        https://github.com/openvinotoolkit/openvino/archive/7a975177ff432c687e5619e8fb22e4bf265e48b7/openvino-7a97517.tar.gz
Source4:        https://github.com/openvinotoolkit/npu_compiler/archive/a1ae54e94faea6f35566ef4ed03ee98156808306/npu_compiler-a1ae54e.tar.gz
Source5:        https://github.com/openvinotoolkit/openvino/archive/5fb69ea158126752aa9d8aa5ee4d6f65a5b409b5/openvino-5fb69ea.tar.gz
Source6:        https://github.com/oneapi-src/level-zero/archive/7ae9d18f888dd4a9960e230b138ecd915ea187ac/level-zero-7ae9d18.tar.gz

ExclusiveArch:	x86_64

BuildRequires:	cmake
BuildRequires:	gcc-c++
BuildRequires:	glibc-devel
BuildRequires:	gmock-devel
BuildRequires:	gtest-devel
BuildRequires:	libudev-devel
BuildRequires:	intel-level-zero-devel
BuildRequires:	openssl-devel
BuildRequires:	yaml-cpp-devel
BuildRequires:  pugixml-devel
BuildRequires:	snappy-devel
BuildRequires:  protobuf-compiler
BuildRequires:  protobuf-devel
BuildRequires:  flatbuffers-devel
BuildRequires:  flatbuffers-compiler
BuildRequires:	build-essential git git-lfs python3

Requires:	intel-level-zero

%description
Intel NPU device is an AI inference accelerator integrated with Intel client CPUs, starting from Intel Core Ultra generation of CPUs (formerly known as Meteor Lake).
It enables energy-efficient execution of artificial neural network tasks.


%prep
%setup -q -n linux-npu-driver-%{version}

# thirdparty deps
rm -rf thirdparty/googletest thirdparty/level-zero third_party/level-zero-npu-extensions \
   thirdparty/perfetto thirdparty/yaml-cpp third_party/npu_compiler_elf
tar xf %{SOURCE1}
mv level-zero-npu-extensions-* third_party/level-zero-npu-extensions
tar xf %{SOURCE2}
mv npu_compiler_elf-* third_party/npu_compiler_elf

sed -i '/add_subdirectory(googletest EXCLUDE_FROM_ALL)/s/^/#/' third_party/CMakeLists.txt
sed -i '/add_subdirectory(yaml-cpp EXCLUDE_FROM_ALL)/s/^/#/' third_party/CMakeLists.txt

#sed -i '/^set(OPENVINO_CMAKE_ARGS$/a\    -DENABLE_PROFILING_ITT=OFF' compiler/openvino_build.cmake

# echo -e "set(NPU_COMPILER_TAG npu_ud_2025_48_rc1)\nadd_custom_target(npu_compiler_source)" > compiler/compiler_source.cmake
cat > compiler/compiler_source.cmake << 'EOF'
if(DEFINED ENV{TARGET_DISTRO})
  set(TARGET_DISTRO $ENV{TARGET_DISTRO})
else()
  set(TARGET_DISTRO ${CMAKE_SYSTEM_NAME})
endif()
set(NPU_COMPILER_TAG npu_ud_2025_48_rc1)
set(OPENVINO_SOURCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/src/openvino")
set(NPU_COMPILER_OPENVINO_SOURCE_DIR ${CMAKE_CURRENT_BINARY_DIR}/src/npu_compiler_openvino)
set(NPU_COMPILER_SOURCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/src/npu_compiler")
set(NPU_COMPILER_BUILD_DEPENDS npu_compiler_openvino_source)
add_custom_target(npu_compiler_source)
add_custom_target(npu_compiler_openvino_source)
add_custom_target(openvino_source)
EOF

mkdir -p ./build/compiler/src/openvino
tar xf %{SOURCE3} -C ./build/compiler/src/openvino --strip-components=1
ls ./build/compiler/src/openvino

mkdir -p ./build/compiler/src/npu_compiler
tar xf %{SOURCE4} -C ./build/compiler/src/npu_compiler --strip-components=1
git -C ./build/compiler/src/npu_compiler lfs install &&
    git -C ./build/compiler/src/npu_compiler lfs pull &&
    git -C ./build/compiler/src/npu_compiler/thirdparty/vpucostmodel lfs install &&
    git -C ./build/compiler/src/npu_compiler/thirdparty/vpucostmodel lfs pull
ls ./build/compiler/src/npu_compiler

mkdir -p ./build/compiler/src/npu_compiler_openvino
tar xf %{SOURCE5} -C ./build/compiler/src/npu_compiler_openvino --strip-components=1
ls ./build/compiler/src/npu_compiler_openvino
#rm -rf ./build/compiler/src/npu_compiler_openvino/thirdparty/ittapi
cd ./build/compiler/src/npu_compiler_openvino

sed -i 's/set(ENABLE_PROFILING_ITT_DEFAULT BASE)/set(ENABLE_PROFILING_ITT_DEFAULT OFF)/' cmake/features.cmake
sed -i 's/ov_option (ENABLE_SYSTEM_PUGIXML "Enables use of system PugiXML" OFF)/ov_option (ENABLE_SYSTEM_PUGIXML "Enables use of system PugiXML" ON)/' cmake/features.cmake

sed -i 's/set(ENABLE_SYSTEM_FLATBUFFERS_DEFAULT OFF)/set(ENABLE_SYSTEM_FLATBUFFERS_DEFAULT ON)/' cmake/features.cmake
sed -i 's/"ENABLE_OV_TF_LITE_FRONTEND" OFF)/"ENABLE_OV_TF_LITE_FRONTEND" ON)/' cmake/features.cmake

sed -i 's/"Enables use of system Protobuf" OFF/"Enables use of system Protobuf" ON/' cmake/features.cmake
sed -i 's/"ENABLE_OV_ONNX_FRONTEND OR ENABLE_OV_PADDLE_FRONTEND OR ENABLE_OV_TF_FRONTEND" OFF)/"ENABLE_OV_ONNX_FRONTEND OR ENABLE_OV_PADDLE_FRONTEND OR ENABLE_OV_TF_FRONTEND" ON)/' cmake/features.cmake

# thirdparty deps
rm -rf thirdparty/gtest thirdparty/gflags thirdparty/level-zero/level_zero third_party/itt_collector \
   thirdparty/pugixml third_party/telemetry
#tar xf %{SOURCE6}
#mkdir -p third_party/level_zero/level_zero
#mv level-zero-* third_party/level_zero/level_zero
cd -

mkdir ./build/compiler/src/npu_compiler_openvino/build && cd ./build/compiler/src/npu_compiler_openvino/build
cmake -DENABLE_SYSTEM_PUGIXML=ON -DENABLE_SYSTEM_SNAPPY=ON -DENABLE_SYSTEM_PROTOBUF=ON ..
cd -

%build
cmake \
	-B build -S . \
	-DENABLE_VALIDATION_BUILD=OFF \
	-DENABLE_NPU_COMPILER_BUILD=ON

cmake --build build

%install
mkdir -p %{buildroot}%{_libdir}
cmake --install build --prefix=%{buildroot}%{_libdir}
cp -a %{buildroot}%{_libdir}/lib64/libze_intel_npu.so.* %{buildroot}%{_libdir}
rm -rf %{buildroot}%{_libdir}/lib64

%files
%defattr(-,root,root)
%license LICENSE.md
%doc README.md
%{_libdir}/libze_intel_npu.so*

%changelog
* Mon Jan 19 2026 Andy <andy.peng@intel.com> - 1.28.0-1
- Initial Edge Microvisor Toolkit import from Fedora 42 (license: MIT). License verified.
