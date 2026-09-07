# AgriScale RN installation troubleshooting

This document complements the [installation guide](tutorial.md). Run PowerShell commands from Windows and Bash commands inside Ubuntu/WSL or Linux.

## WSL is unavailable

Run PowerShell as Administrator:

```powershell
wsl --update
wsl --install -d Ubuntu
wsl -l -v
```

If Ubuntu remains unavailable, install an Ubuntu LTS release from the Microsoft Store. The `VERSION` column should normally show `2`.

## Ubuntu always starts as root

Configure the existing normal account in `/etc/wsl.conf`:

```ini
[user]
default=your-user
```

Restart WSL from PowerShell and check again:

```powershell
wsl --shutdown
```

```bash
whoami
```

Some Ubuntu launchers also support `ubuntu config --default-user your-user` from PowerShell.

## The `code` command is unavailable

Install VS Code on Windows and the Microsoft **WSL** extension. Close and reopen VS Code and Ubuntu, then retry `code .`. Do not install a separate Linux copy of VS Code inside WSL.

## VS Code does not offer the kernel

Install the Microsoft **Python** and **Jupyter** extensions in WSL, then check:

```bash
jupyter kernelspec list
```

If `singularity-kernel` is absent, rerun `setup.sh` with the absolute image path and restart VS Code.

## The container download fails

Install the downloader dependencies:

```bash
sudo apt-get update
sudo apt-get install -y curl jq
```

Run `bash download.sh` from the directory containing the script. If GitHub access is restricted, download the `.sif` manually from the [v1.2.5 release](https://github.com/CropModelingPlatform/AgriscaleContainer/releases/tag/v1.2.5).

## `setup.sh` cannot find the image

List the exact filename and pass its full path:

```bash
ls -lh /full/path/to/Tutorial/*.sif
bash setup.sh /full/path/to/Tutorial/exact-image-name.sif
```

Do not append a second `.sif` extension.

## Singularity or Apptainer is unavailable

Check both commands:

```bash
command -v singularity
command -v apptainer
```

If neither exists and automatic installation fails, follow the [official Apptainer installation instructions](https://apptainer.org/docs/admin/main/installation.html#installation-on-linux), then rerun `setup.sh`.

## The `/run/user/<uid>` bind fails when systemd is disabled

The Jupyter kernel may stop immediately with an error similar to:

```text
container creation failed: mount /run/user/1000->/run/user/1000 error:
mount source /run/user/1000 doesn't exist
```

The generated `singularity_kernel.sh` mounts the user runtime directory so
that the container can read the Jupyter connection file. On a systemd-based
session, `/run/user/<uid>` is created automatically for the user. Some WSL
sessions do not create it when systemd is disabled.

Check the current situation inside Ubuntu:

```bash
ps -p 1 -o comm=
ls -ld "/run/user/$(id -u)"
echo "$XDG_RUNTIME_DIR"
```

If PID 1 is displayed as `init(Ubuntu-...)` instead of `systemd`, enable
systemd in `/etc/wsl.conf`:

```ini
[boot]
systemd=true

[user]
default=your-user
```

The `systemd=true` setting must be under `[boot]`. If it is placed under
`[user]`, WSL reports:

```text
wsl: Unknown key 'user.systemd' in /etc/wsl.conf
```

Restart WSL completely from **Windows PowerShell**, not from the Ubuntu shell:

```powershell
wsl --shutdown
```

Open Ubuntu again and verify:

```bash
ps -p 1 -o comm=
ls -ld "/run/user/$(id -u)"
```

The first command should print `systemd`, and the second should show a runtime
directory owned by your Linux user. Restart the notebook kernel in VS Code
afterward.

### Keep systemd disabled

If systemd must remain disabled, the fixed `/run/user/<uid>` bind cannot be
used. The launcher must instead mount the directory that actually contains the
Jupyter connection file:

```bash
connection_dir="$(dirname -- "$connection_file")"

exec singularity exec \
  --bind "$HOME/datamill:/data" \
  --bind "$connection_dir:$connection_dir" \
  /absolute/path/to/datamill.sif \
  python -m ipykernel_launcher -f "$connection_file"
```

Apply the same change to `setup.sh`; otherwise, running setup again will
recreate the launcher with the fixed `/run/user/<uid>` bind.

## The kernel starts and immediately stops

Test the container independently, replacing its path as needed:

```bash
apptainer exec /absolute/path/to/datamill.sif python -c "import sys; print(sys.version); import ipykernel; print(ipykernel.__version__)"
```

Use `singularity` instead if that is your runtime. Inspect the generated launcher and kernel definition:

```bash
sed -n '1,160p' "$HOME/datamill/singularity_kernel.sh"
sed -n '1,160p' "$HOME/.local/share/jupyter/kernels/singularity-kernel/kernel.json"
```

## Files are not visible in the container

Keep the notebook and inputs under your Linux home directory in WSL. Confirm the working directory from a notebook:

```python
import os
print(os.getcwd())
print(os.listdir("."))
```

## Recreate the custom kernel

Remove only this user kernel, then register it again:

```bash
jupyter kernelspec uninstall singularity-kernel
bash setup.sh /absolute/path/to/datamill.sif
```

This does not remove the container image.

## Information to provide when requesting help

Collect:

```bash
whoami
uname -a
command -v singularity || command -v apptainer
jupyter kernelspec list
ls -lh *.sif
```

Include the complete error, operating system, WSL or native Linux, and AgriScale version. Never include passwords or access tokens.
