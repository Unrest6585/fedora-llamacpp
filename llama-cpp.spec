# Build number from upstream release tag bNNNN
# Build with: rpmbuild --define "llama_build_num NNNN" -bs llama-cpp.spec
%{!?llama_build_num: %global llama_build_num 0}
%global build_tag b%{llama_build_num}

Name:           llama-cpp
Version:        %{llama_build_num}
Release:        1%{?dist}
Summary:        LLM inference engine in C/C++ with Vulkan GPU acceleration
License:        MIT
URL:            https://github.com/ggerganov/llama.cpp
Source0:        https://github.com/ggerganov/llama.cpp/archive/refs/tags/%{build_tag}.tar.gz

BuildRequires:  cmake >= 3.14
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  vulkan-devel
BuildRequires:  glslang
BuildRequires:  shaderc
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
%autosetup -n llama.cpp-%{build_tag}

%build
%cmake \
    -DGGML_VULKAN=ON \
    -DLLAMA_CURL=ON \
    -DBUILD_SHARED_LIBS=ON \
    -G Ninja
%cmake_build

%install
%cmake_install

# Remove devel files (headers, cmake configs, unversioned .so symlinks)
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
find %{buildroot}%{_libdir} -name '*.so' -delete

%files
%license LICENSE
%doc README.md
%{_bindir}/llama-*

%files libs
%license LICENSE
%{_libdir}/lib*.so.*
