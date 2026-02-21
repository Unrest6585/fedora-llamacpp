# Version is set to the upstream release tag (e.g. b5153) by the build workflow.
# For local builds, run build-rocm.sh which patches this line automatically.
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
    -DLLAMA_CURL=ON \
    -DBUILD_SHARED_LIBS=ON \
    -G Ninja
%cmake_build

%install
%cmake_install

# Remove devel files (headers, cmake configs, unversioned .so symlinks, pkgconfig)
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}%{_libdir}/pkgconfig
find %{buildroot}%{_libdir} -name '*.so' -delete

# Remove test binaries and conversion scripts not needed at runtime
rm -f %{buildroot}%{_bindir}/test-*
rm -f %{buildroot}%{_bindir}/convert_hf_to_gguf.py

%files
%license LICENSE
%doc README.md
%{_bindir}/llama-*

%files libs
%license LICENSE
%{_libdir}/lib*.so.*
