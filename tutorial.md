# Tutorial: Install ACME Locally (Windows WSL or Linux)

This tutorial prepares the local environment needed to run **ACME**, the notebook used to design experiments and simulate crop models without a cluster. Agriscale — the full distributed, spatialized platform — is only presented briefly during the session; this tutorial does not cover it. Part A prepares the environment on Windows or Linux, Part B downloads the Agriscale RN container that ACME runs inside, Part C registers the custom Jupyter kernel used by VS Code and Jupyter, and Part D validates the installation before the hands-on session.

This is the guide to follow end to end for the training. For installation failures and platform-specific details, see [troubleshooting.md](troubleshooting.md).

## Architecture

The setup has three components:

1. the AgriScale RN `v1.2.5` Singularity Image Format (`.sif`) container, which holds the scientific software stack;
2. Singularity or Apptainer as the container runtime;
3. a Jupyter kernelspec that launches Python inside the container.

Notebooks and project data remain on the host and are accessed through bind mounts. Pinning the image version makes the computational environment easier to reproduce across participants and machines.

## Part A - Environment Prerequisites

### A.1 Install WSL and Ubuntu on Windows

1. Open **PowerShell as Administrator**.
1. Run:

   ```powershell
   wsl --install -d Ubuntu
   ```

1. Restart Windows if prompted.
1. Launch **Ubuntu** from the Start menu.
1. Complete the first-time setup by creating:
   - A UNIX username
   - A password

If `wsl --install` does not work, update WSL first:

```powershell
wsl --update
```

If Ubuntu does not appear after restarting Windows, you can install it from the
**Microsoft Store**:

1. Open the Microsoft Store.
1. Search for **Ubuntu**.
1. Select **Ubuntu** (or an Ubuntu LTS version) and click **Install**.
1. Launch Ubuntu from the Start menu.
1. Complete the first-time setup by creating your UNIX username and password.

You can then verify that Ubuntu is installed from PowerShell:

```powershell
wsl -l -v
```

To launch it directly from PowerShell, run:

```powershell
wsl -d Ubuntu
```

### A.2 Verify Ubuntu Works Correctly

Inside Ubuntu, run:

```bash
whoami
uname -a
```

Expected result:
- `whoami` should show your Linux username, not `root`.
- `uname -a` should print Linux kernel details.

You can also verify installed distros from PowerShell:

```powershell
wsl -l -v
```

### A.3 If Ubuntu Starts as root, Fix the Default User

If `whoami` returns `root` every time, set your normal user as the default.

#### Option A: Use the Ubuntu command

Run this in PowerShell, replacing `<your-user>`:

```powershell
ubuntu config --default-user <your-user>
```

#### Option B: Use WSL directly

Run in PowerShell:

```powershell
wsl -d Ubuntu -u root
```

Then inside Ubuntu:

```bash
grep -E "^\[user\]|^default=" /etc/wsl.conf
```

If needed, create or edit `/etc/wsl.conf`:

```ini
[user]
default=<your-user>
```

Then from PowerShell, restart WSL:

```powershell
wsl --shutdown
```

Open Ubuntu again and verify with:

```bash
whoami
```

### A.4 Install VS Code on Windows

1. Download VS Code from the official website.
1. Install it with the default options.
1. Open VS Code once the installation finishes.

### A.5 Add the WSL Extension in VS Code

1. In VS Code, open the **Extensions** view (`Ctrl+Shift+X`).
1. Search for **WSL**.
1. Install **WSL** published by Microsoft.

### A.6 Open Your Ubuntu Environment in VS Code

From the Ubuntu terminal:

```bash
code .
```

If `code` is not found, reopen VS Code and ensure the WSL extension is installed.

When successful, VS Code shows `WSL: Ubuntu` in the lower-left corner.

### A.7 Quick Validation Checklist

- Ubuntu launches without errors.
- `whoami` returns your normal Linux user.
- VS Code opens from Ubuntu using `code .`.
- The VS Code status bar shows `WSL: Ubuntu`.

### A.8 Troubleshooting

- `wsl` command not found: update Windows and install the latest WSL.
- Ubuntu starts as root: re-run Step A.3 and restart WSL with `wsl --shutdown`.
- VS Code cannot connect to WSL: reinstall **WSL** and restart VS Code.

## Part B - Agriscale RN Prerequisites

### B.1 Download the Agriscale Container

Choose one of the following methods to download the Agriscale container.

#### Option A: Download Automatically with the Bash Script

From the tutorial folder, run:

```bash
bash download.sh
```

The script queries the GitHub release and downloads the matching `.sif` file
from the **Assets** section automatically.

#### Option B: Download Manually from GitHub Releases

1. Open the Agriscale Container release page:

   https://github.com/CropModelingPlatform/AgriscaleContainer/releases/tag/v1.2.5

1. Scroll to the **Assets** section.
1. Download the `.sif` container file that matches your machine's architecture.
1. Place the file in the Tutorial directory

The downloaded `.sif` file is required before registering the custom kernel.

## Part C - Jupyter Custom Kernel Prerequisite

### C.1 Declare the Singularity (Python) kernel with setup.sh

This step creates a custom Jupyter kernel named **Singularity (Python)**. VS Code and Jupyter will use it to launch Python inside your container through the `singularity_kernel.sh` wrapper.

The `setup.sh` script uses `singularity` if it is already installed, falls back to `apptainer` if available, and can install a container runtime automatically on Ubuntu or WSL when `sudo` and `apt-get` are available. On Linux, the official installation instructions are here:

https://apptainer.org/docs/admin/main/installation.html#installation-on-linux

On some Ubuntu systems, the runtime package may appear as `singularity-container`, while the command used by the script remains `singularity` or `apptainer`.

1. Make sure the Agriscale container file (datamill.sif) downloaded in Part B is available locally.
1. Open a terminal in the project folder.
1. Run the setup workflow and pass the container image path as an argument:

   ```bash
   cd /full/path/to/Tutorial
   bash setup.sh /full/path/to/your/datamill.sif
   ```


Expected result:
- A kernelspec named `singularity-kernel` should appear.
- Its display name should be `Singularity (Python)`.

### C.2 Use the Kernel in VS Code or Jupyter

After registration, select **Singularity (Python)** from the kernel picker in Jupyter or in VS Code notebooks.

Note: the kernel wrapper uses `singularity_kernel.sh`, which runs Python inside your Singularity or Apptainer image.

## Part D - Validate the Installation and Run ACME

### D.1 Confirm the Container Runs Python Directly

This step separates container/runtime errors from Jupyter or VS Code integration errors. Replace `IMAGE` with the exact path to your downloaded `.sif` file:

```bash
RUNTIME="$(command -v singularity || command -v apptainer)"
IMAGE="/full/path/to/your/datamill.sif"
"$RUNTIME" exec "$IMAGE" python -c \
  'import sys, ipykernel; print(sys.version); print(ipykernel.__version__)'
```

Both the Python version and the `ipykernel` version should print without an exception.

### D.2 Run ACME in Jupyter or VS Code

1. Open `acme.ipynb` and select the **Singularity (Python)** kernel.
1. In VS Code under WSL, confirm the lower-left status bar shows the WSL environment.
1. Run this first cell:

   ```python
   import os
   import platform
   import sys

   print("Python executable:", sys.executable)
   print("Python version:", sys.version)
   print("Platform:", platform.platform())
   print("Working directory:", os.getcwd())
   ```

1. Then confirm the expected tutorial inputs are visible:

   ```python
   from pathlib import Path

   required = [
       Path("MasterInput.db"),
       Path("ModelsDictionaryArise.db"),
       Path("CelsiusV3nov17_dataArise.db"),
   ]

   missing = [str(path) for path in required if not path.exists()]
   if missing:
       raise FileNotFoundError(f"Missing tutorial inputs: {missing}")

   print("Required tutorial inputs are available.")
   ```

1. Run `acme.ipynb` in order and check that model inputs, working directories, and outputs correspond to the intended experiment.

### D.3 Completion Checklist

You are ready for the hands-on session when:

- the direct container smoke test (D.1) prints a Python and `ipykernel` version without error;
- `jupyter kernelspec list` includes `singularity-kernel`;
- **Singularity (Python)** starts without error in Jupyter or VS Code;
- `acme.ipynb` sees all required databases and input files;
- the reference workflow in `acme.ipynb` produces the expected outputs.

If any item fails, see [troubleshooting.md](troubleshooting.md) and keep the complete error output when asking for help.

## Reproducibility Record

For each training session or scientific analysis, retain:

- AgriScale release: `v1.2.5`;
- `.sif` filename and SHA-256 checksum;
- Singularity/Apptainer version;
- host operating system and architecture;
- notebook or analysis revision;
- input dataset versions and provenance;
- crop-model versions used inside AgriScale;
- configuration files and parameter sets;
- simulation outputs and execution date.

A minimal environment record can be generated with:

```bash
{
  uname -a
  "$RUNTIME" --version
  sha256sum "$IMAGE"
  jupyter kernelspec list
} > agriscale_environment.txt
```

Review `agriscale_environment.txt` before archiving it; it may contain local paths or host identifiers.

## Updating AgriScale RN

Do not silently replace the `v1.2.5` image during an ongoing experiment. Download a newer image alongside it, compute its checksum, register or select it explicitly, and rerun Part D. Treat a container upgrade as a change to the computational method and document it with the results.
