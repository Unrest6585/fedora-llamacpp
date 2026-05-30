# Version is set to the upstream release tag (e.g. b5153) by the build workflow.
# For local builds, run build-rocm.sh which patches this line automatically.

# Numeric build number derived from the bXXXX release tag (e.g. b9413 -> 9413).
# We build from a release tarball, which has no .git, so llama.cpp's cmake would
# otherwise stamp the binaries as "version: 0 (unknown)". Feed it explicitly.
%define llama_build_number %(echo %{version} | sed 's/^b//')

Name:           llama-cpp-rocm
Version:        b0
Release:        1%{?dist}
Summary:        LLM inference engine in C/C++ with ROCm GPU acceleration
License:        MIT
URL:            https://github.com/ggml-org/llama.cpp
Source0:        https://github.com/ggml-org/llama.cpp/archive/refs/tags/%{version}.tar.gz

BuildRequires:  cmake >= 3.14
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  rocm-hip-devel
BuildRequires:  rocblas-devel
BuildRequires:  libcurl-devel

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description
llama.cpp is an LLM inference engine written in C/C++. This build
enables the ROCm backend for GPU-accelerated inference on supported
AMD GPUs.

%package libs
Summary:        Shared libraries for %{name}

%description libs
Shared libraries for llama.cpp, including the ROCm compute backend.

%prep
%autosetup -n llama.cpp-%{version}

%build
%cmake \
    -DGGML_NATIVE=OFF \
    -DGGML_HIP=ON \
    -DGGML_BACKEND_DL=ON \
    -DGGML_CPU_ALL_VARIANTS=ON \
    -DLLAMA_CURL=ON \
    -DLLAMA_BUILD_NUMBER=%{llama_build_number} \
    -DLLAMA_BUILD_COMMIT=%{version} \
    -DBUILD_SHARED_LIBS=ON \
    -G Ninja
%cmake_build

%install
%cmake_install

# Remove devel files (headers, cmake configs, unversioned .so symlinks, pkgconfig).
# Only delete symlinks: upstream (>= b9294) ships each CLI tool as an unversioned
# shared library (libllama-cli-impl.so, ...) whose SONAME is the bare filename.
# Those are real runtime libraries the launcher binaries link against, so they
# must be kept; only the devel symlinks (libggml.so -> libggml.so.0) are removed.
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}%{_libdir}/pkgconfig
find %{buildroot}%{_libdir} -type l -name '*.so' -delete

# Remove test binaries and conversion scripts not needed at runtime
rm -f %{buildroot}%{_bindir}/test-*
rm -f %{buildroot}%{_bindir}/convert_hf_to_gguf.py

%files
%license LICENSE
%doc README.md
%{_bindir}/llama-*

%files libs
%license LICENSE
%{_libdir}/lib*.so*
