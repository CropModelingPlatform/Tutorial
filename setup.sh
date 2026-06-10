#!/usr/bin/env bash
set -eu

# setup.sh — run once per user

if [[ "${EUID}" -eq 0 ]]; then
    echo "Do not run this script as root."
    echo "Create and use a normal Linux user first."
    exit 1
fi

SINGULARITY_IMAGE="${1:-}"

if [[ -z "$SINGULARITY_IMAGE" ]]; then
  echo "Usage: bash setup.sh /full/path/to/your/image.sif"
  exit 1
fi

if [[ ! -f "$SINGULARITY_IMAGE" ]]; then
  echo "Image file not found: $SINGULARITY_IMAGE"
  exit 1
fi

# Normalize to an absolute path so kernels launched from other working
# directories still resolve the image correctly.
if command -v realpath >/dev/null 2>&1; then
  SINGULARITY_IMAGE="$(realpath "$SINGULARITY_IMAGE")"
elif command -v readlink >/dev/null 2>&1; then
  resolved_image="$(readlink -f "$SINGULARITY_IMAGE" 2>/dev/null || true)"
  if [[ -n "$resolved_image" ]]; then
    SINGULARITY_IMAGE="$resolved_image"
  fi
fi

CONTAINER_RUNTIME=""

if command -v singularity >/dev/null 2>&1; then
  CONTAINER_RUNTIME="singularity"
elif command -v apptainer >/dev/null 2>&1; then
  CONTAINER_RUNTIME="apptainer"
elif command -v apt-get >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
  sudo apt-get update
  if sudo apt-get install -y singularity-container; then
    if command -v singularity >/dev/null 2>&1; then
      CONTAINER_RUNTIME="singularity"
    elif command -v apptainer >/dev/null 2>&1; then
      CONTAINER_RUNTIME="apptainer"
    fi
  elif sudo apt-get install -y apptainer; then
    if command -v singularity >/dev/null 2>&1; then
      CONTAINER_RUNTIME="singularity"
    elif command -v apptainer >/dev/null 2>&1; then
      CONTAINER_RUNTIME="apptainer"
    fi
  fi
fi

if [[ -z "$CONTAINER_RUNTIME" ]]; then
  echo "Singularity/Apptainer was not found on PATH and could not be installed automatically."
  echo "Install Apptainer or Singularity first, then rerun this script."
  exit 1
fi

if ! python3 -c "import jupyter_client" >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3-jupyter-client python3-jupyter-core
  elif command -v pip >/dev/null 2>&1; then
    pip install --user jupyter-client jupyter-core
  else
    echo "Jupyter client is missing and could not be installed automatically."
    echo "Install python3-jupyter-client (or jupyter-client via pip), then rerun this script."
    exit 1
  fi
fi

# 1. Create the working directory that will hold the wrapper script.
mkdir -p "$HOME/datamill"

# 2. Create the Singularity launcher used by Jupyter.
cat > "$HOME/datamill/singularity_kernel.sh" << EOF
#!/usr/bin/env bash
set -euo pipefail

connection_file="\${1:-}"

if [[ -z "\$connection_file" ]]; then
  echo "Usage: singularity_kernel.sh <connection_file>" >&2
  exit 1
fi

exec "$CONTAINER_RUNTIME" exec --bind ~/datamill:/data --bind /run/user/\$(id -u):/run/user/\$(id -u) "$SINGULARITY_IMAGE" python -m ipykernel_launcher -f "\$connection_file"
EOF

chmod +x "$HOME/datamill/singularity_kernel.sh"

# 3. Register the custom Jupyter kernel.
mkdir -p "$HOME/.local/share/jupyter/kernels/singularity-kernel"

cat > "$HOME/.local/share/jupyter/kernels/singularity-kernel/kernel.json" << EOF
{
  "argv": [
    "/bin/bash",
    "$HOME/datamill/singularity_kernel.sh",
    "{connection_file}"
  ],
  "display_name": "Singularity (Python)",
  "language": "python"
}
EOF

echo "Done! Run: jupyter kernelspec list to verify"

