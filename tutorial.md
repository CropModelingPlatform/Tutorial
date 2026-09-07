# Tutorial: Install ACME Locally (Windows WSL or Linux)

This tutorial prepares the local environment needed to run **ACME**, the
notebook used to design experiments and simulate crop models without a cluster.
Agriscale — the full distributed, spatialized platform — is only presented
briefly during the session; this tutorial does not cover it. Part A prepares
the environment on Windows or Linux, Part B downloads the Agriscale RN
container that ACME runs inside, Part C registers the custom Jupyter kernel
used by VS Code and Jupyter, and Part D opens and runs ACME in VS Code.

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

   https://github.com/CropModelingPlatform/AgriscaleContainer/releases/tag/v1.2.6

1. Scroll to the **Assets** section.
1. Download the `.sif` container file that matches your machine's architecture.
1. Place the file in the Tutorial directory

The downloaded `.sif` file is required before registering the custom kernel.

## Part C - Jupyter Custom Kernel Prerequisite

### C.1 Declare the Singularity (Python) kernel with setup.sh

This step creates a custom Jupyter kernel named **Singularity (Python)**. VS
Code and Jupyter will use it to launch Python inside your container through the
`singularity_kernel.sh` wrapper.

The `setup.sh` script uses `singularity` if it is already installed, falls back
to `apptainer` if available, and can install a container runtime automatically
on Ubuntu or WSL when `sudo` and `apt-get` are available. On Linux, the official
installation instructions are here:

[Apptainer installation documentation](https://apptainer.org/docs/admin/main/installation.html#installation-on-linux)

On some Ubuntu systems, the runtime package may appear as
`singularity-container`, while the command used by the script remains
`singularity` or `apptainer`.

1. Make sure the Agriscale container file (`datamill.sif`) downloaded in Part B
   is available locally.
1. Open a terminal in the project folder.
1. Run the setup workflow and pass the container image path as an argument:

   ```bash
   cd /full/path/to/Tutorial
   bash setup.sh /full/path/to/your/datamill.sif
   ```

Expected result: a `datamill` working directory is created in your Linux home
directory. Its initial contents are:

```text
/home/<your-user>/datamill/
├── CelsiusV3nov17_dataArise.db
├── MasterInput.db
├── ModelsDictionaryArise.db
├── acme.ipynb
├── cultivars/
├── ori_MasterInput.db
└── singularity_kernel.sh
```

The script also registers the `singularity-kernel` Jupyter kernelspec with the
display name **Singularity (Python)**. If setup is run again, existing tutorial
resources in `~/datamill` are kept so that local work is not overwritten.

### C.2 Use the Kernel in VS Code or Jupyter

After registration, select **Singularity (Python)** from the kernel picker in
Jupyter or in VS Code notebooks.

Note: the kernel wrapper uses `singularity_kernel.sh`, which runs Python inside
your Singularity or Apptainer image.

## Part D - Run ACME

### D.2 Run ACME in VS Code

1. Open VS Code in your WSL environment and confirm that the lower-left status
   bar shows **WSL: Ubuntu**.
1. In VS Code, select **File > Add Folder to Workspace...**.
1. Select the `/home/<your-user>/datamill` folder created during Part C.
1. In the VS Code Explorer, open `acme.ipynb` from the `datamill` folder.
1. Use the notebook kernel picker to select **Singularity (Python)**.
1. Run the first cell already present in `acme.ipynb`. It configures the working
   paths, creates the model output directories, and checks that the required
   databases and cultivar folders are available.
1. Run the remaining cells in order to execute the ACME simulations.

If the kernel does not start or an input is reported as missing, see
[troubleshooting.md](troubleshooting.md) and retain the complete error output
when asking for help.

## Updating AgriScale RN

If you receive another version of the Agriscale RN container, run `setup.sh`
again with the path to the new image:

```bash
cd /full/path/to/Tutorial
bash setup.sh /full/path/to/the/new/datamill.sif
```

Restart the notebook kernel in VS Code so that **Singularity (Python)** uses the
new container image.
