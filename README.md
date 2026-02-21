# llama-cpp-vulkan

Automated builds of [llama.cpp](https://github.com/ggerganov/llama.cpp) for Fedora 43, 44, and rawhide, with the Vulkan GPU backend enabled. Tracks upstream releases daily and rebuilds automatically.

## Features

- Vulkan backend enabled (`-DGGML_VULKAN=ON`) — runs on any Vulkan-capable GPU
- Curl support for llama-server
- Tracks upstream `bNNNN` releases daily
- Builds for Fedora 43, 44, and rawhide simultaneously from a single SRPM

## Installation

```bash
sudo dnf copr enable YOUR_USERNAME/llama-cpp-vulkan
sudo dnf install llama-cpp
```

For the shared libraries only (e.g. for embedding):

```bash
sudo dnf install llama-cpp-libs
```

## GitHub Actions Setup

### 1. Create a COPR project

Go to https://copr.fedorainfracloud.org and create a project named `llama-cpp-vulkan`.

When creating the project, enable these chroots:
- `fedora-43-x86_64`
- `fedora-44-x86_64`
- `fedora-rawhide-x86_64`

**Important:** In the project settings, enable **"Follow Fedora branching"**. This makes COPR automatically add the next Fedora chroot (e.g. `fedora-45-x86_64`) when rawhide branches. You then only need to add the new version to `CHROOTS` in `build.yml` to start explicitly targeting it.

### 2. Get a COPR API token

Go to https://copr.fedorainfracloud.org/api/ and copy your credentials.

### 3. Add GitHub Secrets

Add these to your repository (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `COPR_LOGIN` | Your COPR login token |
| `COPR_USERNAME` | Your COPR/Fedora username |
| `COPR_TOKEN` | Your COPR API token |

### 4. Workflow triggers

- **Daily** at 6 AM UTC — checks for new upstream releases
- **On push** to `llama-cpp.spec` or workflow files — rebuilds with spec changes
- **Manually** via workflow_dispatch (with optional force build)

## Local Build

```bash
# Install build dependencies
sudo dnf install rpm-build rpmdevtools wget python3

# Clone this repository
git clone https://github.com/YOUR_USERNAME/fedora-llamacpp.git
cd fedora-llamacpp

# Run the build script
./build.sh

# Upload the resulting SRPM to all chroots
copr-cli build llama-cpp-vulkan llama-cpp-*.src.rpm \
  --chroot fedora-43-x86_64 \
  --chroot fedora-44-x86_64 \
  --chroot fedora-rawhide-x86_64 \
  --nowait
```

## Build Dependencies (for local builds)

```bash
sudo dnf install cmake gcc-c++ ninja-build vulkan-devel glslang shaderc libcurl-devel
```

## Upstream

- https://github.com/ggerganov/llama.cpp
