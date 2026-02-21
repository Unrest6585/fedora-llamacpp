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
BuildRequires:  glslang
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
# Fedora 43 ships glslangValidator (from the glslang package) but not glslc.
# llama.cpp's cmake calls find_package(Vulkan REQUIRED COMPONENTS glslc), so
# we provide a shim named glslc that translates its arguments to glslangValidator.
mkdir -p %{_builddir}/glslc-shim
cat > %{_builddir}/glslc-shim/glslc << 'GLSLC_SHIM_EOF'
#!/bin/bash
ARGS=("-V")
STAGE="" TARGET_ENV="" OUTPUT="" INPUTS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -fshader-stage=*)
            STAGE="${1#-fshader-stage=}"
            # glslangValidator uses abbreviated stage names (comp, vert, frag, ...)
            case "$STAGE" in
                compute)     STAGE="comp" ;;
                vertex)      STAGE="vert" ;;
                fragment)    STAGE="frag" ;;
                geometry)    STAGE="geom" ;;
                tesscontrol) STAGE="tesc" ;;
                tesseval)    STAGE="tese" ;;
            esac
            ;;
        --target-env=*)   TARGET_ENV="${1#--target-env=}" ;;
        -o)               shift; OUTPUT="$1" ;;
        -I*|-D*)          ARGS+=("$1") ;;
        -O|-O0|-O1|-O2|-MD|-MP|-Werror) ;;
        -MF|-MT|-x)       shift ;;
        --)               shift; INPUTS+=("$@"); break ;;
        -*)               ;;
        *)                INPUTS+=("$1") ;;
    esac
    shift
done
[[ -n "$TARGET_ENV" ]] && ARGS+=("--target-env" "$TARGET_ENV")
[[ -n "$STAGE" ]]      && ARGS+=("-S" "$STAGE")
[[ -n "$OUTPUT" ]]     && ARGS+=("-o" "$OUTPUT")
ARGS+=("${INPUTS[@]}")
exec /usr/bin/glslangValidator "${ARGS[@]}"
GLSLC_SHIM_EOF
chmod +x %{_builddir}/glslc-shim/glslc
export PATH="%{_builddir}/glslc-shim:${PATH}"

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
