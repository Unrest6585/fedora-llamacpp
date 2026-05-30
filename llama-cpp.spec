# Version is set to the upstream release tag (e.g. b5153) by the build workflow.
# For local builds, run build.sh which patches this line automatically.
%define _privlibdir %{_libdir}/%{name}

# Numeric build number derived from the bXXXX release tag (e.g. b9413 -> 9413).
# We build from a release tarball, which has no .git, so llama.cpp's cmake would
# otherwise stamp the binaries as "version: 0 (unknown)". Feed it explicitly.
%define llama_build_number %(echo %{version} | sed 's/^b//')

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
BuildRequires:  spirv-headers-devel
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
Installed to a private directory to avoid conflicts with other ggml consumers.

%prep
%autosetup -n llama.cpp-%{version}

%build
%cmake \
    -DGGML_NATIVE=OFF \
    -DGGML_VULKAN=ON \
    -DGGML_BACKEND_DL=ON \
    -DGGML_CPU_ALL_VARIANTS=ON \
    -DLLAMA_CURL=ON \
    -DLLAMA_BUILD_NUMBER=%{llama_build_number} \
    -DLLAMA_BUILD_COMMIT=%{version} \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_RPATH=%{_privlibdir} \
    -DGGML_BACKEND_DIR=%{_privlibdir} \
    -G Ninja
%cmake_build

%install
%cmake_install

# Move all shared libraries to private directory to avoid conflicts with
# other ggml consumers (e.g. whisper-cpp-libs) that ship the same libggml*.so
mkdir -p %{buildroot}%{_privlibdir}
# Versioned libraries (libggml.so.0, libllama.so.0, ...) and their soname symlinks.
mv %{buildroot}%{_libdir}/lib*.so.* %{buildroot}%{_privlibdir}/
# Upstream (>= b9294) builds each CLI tool as an unversioned shared library
# (libllama-cli-impl.so, libllama-server-impl.so, ...) whose SONAME is the bare
# filename. These are real runtime libraries, not devel symlinks, so move them
# too -- otherwise the launcher binaries are left with unsatisfiable Requires.
find %{buildroot}%{_libdir} -maxdepth 1 -type f -name '*.so' -exec mv -t %{buildroot}%{_privlibdir}/ {} +

# ld.so.conf drop-in so the dynamic linker finds our private libs
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo %{_privlibdir} > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf

# Remove devel files (headers, cmake configs, unversioned .so symlinks, pkgconfig).
# Only delete symlinks here: the real .so runtime libraries were moved to the
# private directory above, so anything matching *.so left in %{_libdir} is a
# devel symlink (e.g. libggml.so -> libggml.so.0).
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}%{_libdir}/pkgconfig
find %{buildroot}%{_libdir} -type l -name '*.so' -delete

# Remove everything except llama-* binaries (test-*, convert scripts, and any
# other upstream tools that don't match our package's file list)
find %{buildroot}%{_bindir} -type f ! -name 'llama-*' -delete

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%license LICENSE
%doc README.md
%{_bindir}/llama-*

%files libs
%license LICENSE
%dir %{_privlibdir}
%{_privlibdir}/lib*.so*
%{_sysconfdir}/ld.so.conf.d/%{name}.conf

%changelog
* Fri May 30 2026 Unrest6585 <128709964+Unrest6585@users.noreply.github.com> - b0-1
- Stamp build version from the release tag (LLAMA_BUILD_NUMBER/COMMIT) so
  --version reports the build instead of "0 (unknown)"
- Build portable CPU backends via GGML_BACKEND_DL + GGML_CPU_ALL_VARIANTS,
  loaded from the private dir (GGML_BACKEND_DIR), for near-native CPU speed
  on any x86-64 while staying portable

* Fri May 29 2026 Unrest6585 <128709964+Unrest6585@users.noreply.github.com> - b0-1
- Package unversioned libllama-*-impl.so tool libraries (upstream >= b9294)
  in -libs; only delete devel .so symlinks so launcher binaries resolve

* Thu Apr 16 2026 Unrest6585 <128709964+Unrest6585@users.noreply.github.com> - b0-1
- Add missing SPIR-V headers build dependency for Vulkan builds
