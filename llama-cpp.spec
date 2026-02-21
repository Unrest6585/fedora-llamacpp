# Version is set to the upstream release tag (e.g. b5153) by the build workflow.
# For local builds, run build.sh which patches this line automatically.
Name:           llama-cpp
Version:        b0
Release:        1%{?dist}
Summary:        LLM inference engine in C/C++ with Vulkan GPU acceleration
License:        MIT
URL:            https://github.com/ggml-org/llama.cpp
Source0:        https://github.com/ggml-org/llama.cpp/archive/refs/tags/%{version}.tar.gz

BuildRequires:  cmake >= 3.14
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  vulkan-devel
BuildRequires:  glslc
BuildRequires:  libcurl-devel

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       vulkan-loader

%description
llama.cpp is an LLM inference engine written in C/C++. This build
enables the Vulkan backend for GPU-accelerated inference on any
Vulkan-capable GPU (AMD, Intel, NVIDIA).

%package libs
Summary:        Shared libraries for %{name}
Requires:       vulkan-loader

%description libs
Shared libraries for llama.cpp, including the Vulkan compute backend.

%prep
%autosetup -n llama.cpp-%{version}

%build
%cmake \
    -DGGML_NATIVE=OFF \
    -DGGML_VULKAN=ON \
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
