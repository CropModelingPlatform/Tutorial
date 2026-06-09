# Tutorial: Run Agriscale RN Locally (Windows WSL or Linux)

This tutorial covers the prerequisites required to run Agriscale RN locally. Part A prepares the environment on Windows or Linux, Part B downloads the Agriscale container, and Part C registers the custom Jupyter kernel used by VS Code and Jupyter.

## Part A - Environment Prerequisites

### A.1 Install WSL and Ubuntu on Windows

1. Open **PowerShell as Administrator**.
2. Run:

```powershell
wsl --install -d Ubuntu
```

3. Restart Windows if prompted.
4. Launch **Ubuntu** from the Start menu.
5. Complete the first-time setup by creating:
   - A UNIX username
   - A password

If `wsl --install` does not work, update WSL first:

```powershell
wsl --update
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
2. Install it with the default options.
3. Open VS Code once the installation finishes.

### A.5 Add the WSL Extension in VS Code

1. In VS Code, open the **Extensions** view (`Ctrl+Shift+X`).
2. Search for **WSL**.
3. Install **WSL** published by Microsoft.

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

### B.1 Download the Agriscale Container from GitHub Releases

1. From the tutorial folder, run the download script:

```bash
bash download.sh
```

2. The script queries the GitHub release automatically and downloads the matching `.sif` file from the **Assets** section.

3. If you prefer to do it manually, open the release page:

https://github.com/CropModelingPlatform/AgriscaleContainer/releases/tag/v1.2.1

4. Scroll to the **Assets** section.
5. Download the container file that matches your machine (OS/architecture).
6. Place the downloaded file in a dedicated local Agriscale working directory, for example `~/agriscale` on Linux or WSL.

Note: this file is required before registering the custom kernel.

## Part C - Jupyter Custom Kernel Prerequisite

### C.1 Declare the Singularity (Python) kernel with setup.sh

This step creates a custom Jupyter kernel named **Singularity (Python)**. VS Code and Jupyter will use it to launch Python inside your container through the `singularity_kernel.sh` wrapper.

The `setup.sh` script uses `singularity` if it is already installed, falls back to `apptainer` if available, and can install a container runtime automatically on Ubuntu or WSL when `sudo` and `apt-get` are available. On Linux, the official installation instructions are here:

https://apptainer.org/docs/admin/main/installation.html#installation-on-linux

On some Ubuntu systems, the runtime package may appear as `singularity-container`, while the command used by the script remains `singularity` or `apptainer`.

1. Make sure the Agriscale container file downloaded in Part B is available locally.
2. Open a terminal in the project folder.
3. Run the setup workflow and pass the container image path as an argument:

```bash
bash setup.sh /full/path/to/your/agriscale-container.sif
```

4. Verify that the kernel was registered:

```bash
jupyter kernelspec list
```

Expected result:
- A kernelspec named `singularity-kernel` should appear.
- Its display name should be `Singularity (Python)`.

### C.2 Use the Kernel in VS Code or Jupyter

After registration, select **Singularity (Python)** from the kernel picker in Jupyter or in VS Code notebooks.

Note: the kernel wrapper uses `singularity_kernel.sh`, which runs Python inside your Singularity or Apptainer image.