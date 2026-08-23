#!/bin/bash
# Local build script for llama-cpp-rocm SRPM and binary RPMs with ROCm support
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build-rocm"

echo "==> Fetching latest llama.cpp release tag..."
# /releases/latest now returns a stable meta-release (e.g. v0.2.0) whose
# nightly-tag.txt asset pins the actual bXXXX build tag; the bXXXX releases
# themselves are marked prerelease and no longer surface via /releases/latest.
META_TAG=$(curl -sf \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ggml-org/llama.cpp/releases/latest \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")

if [ -z "${META_TAG}" ]; then
  echo "Error: Could not determine latest release tag"
  exit 1
fi

TAG=$(curl -sfL "https://github.com/ggml-org/llama.cpp/releases/download/${META_TAG}/nightly-tag.txt" | tr -d '[:space:]')

if [[ ! "${TAG}" =~ ^b[0-9]+$ ]]; then
  echo "Error: nightly-tag.txt from ${META_TAG} did not yield a bXXXX tag (got '${TAG}')"
  exit 1
fi

echo "==> Latest release: ${META_TAG} (pinned build: ${TAG})"

mkdir -p "${BUILD_DIR}"
rpmdev-setuptree

echo "==> Downloading source tarball..."
wget "https://github.com/ggml-org/llama.cpp/archive/refs/tags/${TAG}.tar.gz" \
  -O ~/rpmbuild/SOURCES/${TAG}.tar.gz

echo "==> Copying and versioning spec file..."
cp "${SCRIPT_DIR}/llama-cpp-rocm.spec" ~/rpmbuild/SPECS/
sed -i "s/^Version:.*/Version:        ${TAG}/" ~/rpmbuild/SPECS/llama-cpp-rocm.spec

echo "==> Building SRPM and binary RPMs..."
# Using -ba to build both Source and Binary RPMs locally
rpmbuild -ba ~/rpmbuild/SPECS/llama-cpp-rocm.spec

SRPM=$(ls -1t ~/rpmbuild/SRPMS/llama-cpp-rocm-*.src.rpm | head -1)
echo "==> Created SRPM: ${SRPM}"
cp "${SRPM}" "${SCRIPT_DIR}/"

echo "==> Done! Binary RPMs are located in ~/rpmbuild/RPMS/x86_64/"
