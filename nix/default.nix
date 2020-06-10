# Build the PrivateStorage client as a Python application.
{ pkgs ? import <nixpkgs> { } }:
let
  # Get a number of GridSync dependencies which are either unpackaged in
  # Nixpkgs or for which the packaged versions are too old.
  qt5reactor = pkgs.python3Packages.callPackage ./qt5reactor.nix { };
  zxcvbn = pkgs.python3Packages.callPackage ./zxcvbn.nix { };
  pytesttwisted = pkgs.python3Packages.callPackage ./pytesttwisted.nix { };
  pytestqt = pkgs.python3Packages.callPackage ./pytestqt.nix { };
  # PyQtChart is a Python library, too, but needs to be built a little
  # differently so it can find the various Qt libraries it binds.
  pyqtchart = pkgs.libsForQt5.callPackage ./pyqtchart.nix {
    # Make sure we build it for Python 3 since it's for GridSync which is a
    # Python 3 application.
    inherit (pkgs) python3Packages;
  };

  # Notice that ZKAPAuthorizer and the Tahoe-LAFS environment are built with
  # Python 2 because Tahoe-LAFS has not yet been ported to Python 3.  We have
  # to be careful not to mix these into the GridSync Python environment
  # because Python 2 and Python 3 stuff conflicts.
  zkapauthorizer = pkgs.python2Packages.callPackage (import ./zkapauthorizer.nix) { };
  tahoe-lafs-env = pkgs.python2.buildEnv.override {
    # twisted plugins causes collisions between any packages that supply
    # plugins.
    ignoreCollisions = true;
    extraLibs = [
      # zkapauthorizer pulls in tahoe-lafs.  It might be better to reference
      # it explicitly here but I'm not sure how to reach it.
      zkapauthorizer
    ];
  };
in
  # Build the PrivateStorage client, supplying the dependencies we just set
  # up.
  pkgs.python3Packages.callPackage ./gridsync.nix {
    inherit qt5reactor zxcvbn pytesttwisted pytestqt;
    inherit (pkgs.qt5) wrapQtAppsHook;
    inherit pyqtchart;
    inherit tahoe-lafs-env;
  }
