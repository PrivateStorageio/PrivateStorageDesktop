# PrivateStorage Desktop

This repository contains the various assets, grid-credentials, scripts, and other files that are ultimately required to build _PrivateStorage Desktop_ -- a "[PrivateStorage.io](https://privatestorage.io/)"-branded fork of the [Gridsync](http://gridsync.io/) application.

## Building (for local use)

At a higher level, building PrivateStorage Desktop effectively consists in three steps: 1) downloading the upstream Gridsync source code, 2) copying the relevant assets and other files into the Gridsync source tree, and 3) building the newly-PrivateStorage-branded Gridsync application. The `Makefile` in this repository automates the first two steps such that building the PrivateStorage Desktop application "from scratch" for a given system can be a achieved with just a few simple commands (to be entered after cloning and `cd`ing into the top level of this repository):

```
$ make source  # Clone Gridsync into "privatestorage" and apply PS.io branding
$ cd privatestorage  # Enter the PrivateStorage-branded Gridsync source tree
$ make  # Build PrivateStorage Desktop

```

## Building with Vagrant and VirtualBox (for distribution)

Given that PrivateStorage Desktop is essentially a "re-branded" build of Gridsync, all of the relevant build instructions and caveats outlined in the [Gridsync README](https://github.com/gridsync/gridsync/blob/master/README.rst) still apply: in particular, because PyInstaller-generated binaries are typically [forward- but not backward-compatible](https://pyinstaller.readthedocs.io/en/stable/usage.html#platform-specific-notes), it is crucial to build the application on the oldest supported operating system version available for a given platform (i.e., the oldest OS versions which are capable of successfully building the application while still being supported by upstream security updates). To facilitate this, the Gridsync project includes a [Vagrant](https://www.vagrantup.com/) [configuration file](https://github.com/gridsync/gridsync/tree/master/Vagrantfile) that can be used with in conjunction with [VirtualBox](https://www.virtualbox.org/) to provision a viable build envirnoment and thereby "cross-compile" highly-compatible binary distributions. After installing both Vagrant and VirtualBox, such binaries can be built as follows:

```
$ make source  # Clone Gridsync into "privatestorage" and apply PS.io branding
$ cd privatestorage  # Enter the PrivateStorage-branded Gridsync source tree
$ make vagrant-build-linux  # Build PrivateStorage for GNU/Linux (in a on CentOS7 VM)
$ make vagrant-build-macos  # Build PrivateStorage for macOS (in a macOS "Mojave"/10.14 VM)
$ make vagrant-build-windows  # Build PrivateStorage for Windows (in a Windows 10 VM)

```

After the build process successfully completes, the resultant binaries/artifacts can be found inside the `~/gridsync/dist` directory on the guest virtual machine.

For further information about building PrivateStorage/Gridsync, see the [Gridsync README](https://github.com/gridsync/gridsync/blob/master/README.rst).
