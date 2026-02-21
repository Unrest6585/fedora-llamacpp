#!/bin/bash
# Local build script for llama-cpp SRPM with Vulkan support
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"

echo "==> Fetching latest llama.cpp release tag..."
TAG=$(curl -sf \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ggerganov/llama.cpp/releases/latest \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")

if [ -z "${TAG}" ]; then
  echo "Error: Could not determine latest release tag"
  exit 1
fi

BUILD_NUM="${TAG#b}"
echo "==> Latest release: ${TAG} (build_num=${BUILD_NUM})"

mkdir -p "${BUILD_DIR}"
rpmdev-setuptree

echo "==> Downloading source tarball..."
wget "https://github.com/ggerganov/llama.cpp/archive/refs/tags/${TAG}.tar.gz" \
  -O ~/rpmbuild/SOURCES/${TAG}.tar.gz

echo "==> Copying spec file..."
cp "${SCRIPT_DIR}/llama-cpp.spec" ~/rpmbuild/SPECS/

echo "==> Building SRPM..."
rpmbuild -bs \
  --define "llama_build_num ${BUILD_NUM}" \
  ~/rpmbuild/SPECS/llama-cpp.spec

SRPM=$(ls -1t ~/rpmbuild/SRPMS/llama-cpp-*.src.rpm | head -1)
echo "==> Created: ${SRPM}"
cp "${SRPM}" "${SCRIPT_DIR}/"

echo "==> Done! SRPM ready for COPR upload: ${SCRIPT_DIR}/$(basename ${SRPM})"
echo ""
echo "To upload manually:"
echo "  copr-cli build llama-cpp-vulkan $(basename ${SRPM}) --chroot fedora-43-x86_64 --nowait"
