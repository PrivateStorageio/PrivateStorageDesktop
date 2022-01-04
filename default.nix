let
  sources = import nix/sources.nix;
  # nixpkgs 21.11 packages a version of pkgconfig that is broken on Python 2.7
  # so supply our own.  mach-nix depends on this to set up its own build
  # environment and cannot discover a working version from pypi the way it
  # works for other dependencies.
  fixPkgconfig = self: super: {
    python27 = super.python27.override {
      packageOverrides = python-self: python-super: {
        pkgconfig = python-super.pythonPackages.callPackage ./pkgconfig.nix {};
      };
    };
  };
in
{ pkgs ? import sources.nixpkgs { overlays = [ fixPkgconfig ]; }
, pypiData ? sources.pypi-deps-db
, mach-nix ? import sources.mach-nix { inherit pkgs pypiData; }
, zkapauthorizer-source ? "zkapauthorizer"
, zkapauthorizer-repo ? sources.${zkapauthorizer-source}
, magic-folder-source ? "magic-folder"
, magic-folder-repo ? sources.${magic-folder-source}
, gridsync-source ? "gridsync"
, gridsync-repo ? sources.${gridsync-source}
}:
let
    python2 = "python27";
    python3 = "python39";
    lib = pkgs.lib;
    providers = {
      _default = "sdist,nixpkgs,wheel";
      # mach-nix doesn't provide a good way to depend on mach-nix packages,
      # so we get it as a nixpkgs dependency from an overlay. See below for
      # details.
      tahoe-lafs = "nixpkgs";
      # not packaged in nixpkgs at all, we can use the binary wheel from
      # pypi though.
      python-challenge-bypass-ristretto = "wheel";
      # Pure python packages that don't build correctly from sdists
      # - patches in nixpkgs that don't apply
      boltons = "wheel";
      chardet = "wheel";
      urllib3 = "wheel";
      # - incorrectly detected dependencies due to pbr
      fixtures = "wheel";
      testtools = "wheel";
      traceback2 = "wheel";
      # - Incorrectly merged extras - https://github.com/DavHau/mach-nix/pull/334
      tqdm = "wheel";

      # nixpkgs carries a patch that doesn't apply anymore
      klein = "wheel";

      # It is so hard to build!
      pyqt5 = "wheel";

      # - has an undetected poetry dependency and when trying to work around
      #   this another way, dependencies have undetected dependencies, easier
      #   to just use the wheel.
      collections-extended = "wheel";
      # same as collections-extended
      isort = "wheel";

      # From nixpkgs or sdist, fails with
      # cp: cannot stat 'benchmark/': No such file or directory
      # cp: cannot stat 'tests/': No such file or directory
      tomli = "wheel";

      # repo re-org or something?
      # find: ‘hypothesis-6.32.1/hypothesis-python’: No such file or directory
      hypothesis = "wheel";
    };

    inherit (pkgs.callPackage zkapauthorizer-repo { python = python2; }) privatestorage;
  in
    rec {
      inherit mach-nix;

      magic-folder =
        let
          inherit (pkgs.callPackage zkapauthorizer-repo { python = python2; }) tahoe-lafs;
        in
          mach-nix.buildPythonApplication rec {
            inherit providers;
            python = python2;
            name = "magic-folder";
            version = "0.0.1";
            src = magic-folder-repo;
            requirementsExtra = tahoe-lafs.requirements;
            overridesPre = [
              (
                self: super: {
                  inherit tahoe-lafs;
                }
              )
            ];
          };

      gridsync = pkgs.python39Packages.toPythonApplication gridsync-package;

      gridsync-lint = mach-nix.nixpkgs.mkShell {
        buildInputs = [
          (mach-nix.mkPython {
            python = python3;
            requirements = ''
            black==21.11b1
            isort==5.10.1
            # xxx this gridsync pin has moved too
            mypy==0.910
            mypy-extensions==0.4.3
            flake8==4.0.1
            # xxx gridsync pins pylint 2.12.2 but that's newer than our
            # pypi-db. we can upgrade if we bump our pypi-db.
            pylint==2.12.1
            types-attrs
            types-atomicwrites
            types-PyYAML
            '';
          })
        ];

        shellHook = ''
        pushd ${gridsync.src}
        mypy gridsync
        black --check --diff setup.py gridsync tests
        isort --check --diff setup.py gridsync tests
        popd
        '';
      };

      gridsync-testing = mach-nix.mkPython {
        python = python3;

        # Get GridSync's testing dependencies into this environment.
        # GridSync doesn't publish pytest.in upstream so we carry a version ourselves.
        # requirements = builtins.readFile "${gridsync-repo}/requirements/pytest.in";
        requirements = builtins.readFile (./. + "/pytest.in");
      };

      gridsync-package =
      let
        psio-src = lib.cleanSource ./.;
        assets = [
          { src = "${psio-src}/assets/PrivateStorage*"; dst = "images/"; }
          { src = "${psio-src}/assets/PrivateStorage*"; dst = "gridsync/resources/"; }
          { src = "${psio-src}/assets/PrivateStorage.png"; dst = "gridsync/resources/tahoe-lafs.png"; }
          { src = "${psio-src}/credentials/*.json"; dst = "gridsync/resources/providers/"; }
          { src = "${psio-src}/build/config.txt"; dst = "gridsync/resources/"; }
        ];
        apply-branding = assets:
          if builtins.length assets == 0 then
            ""
          else
            ''
            cp ${(builtins.head assets).src} ${(builtins.head assets).dst}
            ${apply-branding (builtins.tail assets)}
            '';
      in
      mach-nix.buildPythonPackage rec {
        inherit providers;
        python = python3;
        version = "0.5.0";
        prePatch = ''
           # Replicate PrivateStorageDesktop `make source` logic here.
           ${apply-branding assets}
        '';
        requirementsExtra = ''
          # work around https://github.com/DavHau/mach-nix/issues/305 with
          # explicit build-time dependencies here
          setuptools_rust
          flit_core

          # mach-nix has problems with environment markers too
          distro

          # Get a version of PyQt5 that's compatible with the version of the Qt5
          # libraries available from the nixpkgs we're using.  If we change nixpkgs, we
          # might need to change this pin as well.  Without this, mach-nix will
          # just pull in the newest PyQt5 from PyPI (unless GridSync pins it otherwise)
          # and chances are it will not play nicely with our version.
          pyqt5 == 5.15.3
        '';
        src = gridsync-repo;

        # Get qtWrapperArgs set, even though wrapQtAppsHook won't wrap the
        # gridsync executable for us.
        nativeBuildInputs = [ pkgs.qt5.wrapQtAppsHook ];

        # For some reason pyqt5 fails to build like this if we don't add this
        # hook:
        #
        #  Error: wrapQtAppsHook is not used, and dontWrapQtApps is not set.
        #
        _.pyqt5.nativeBuildInputs.add = [ pkgs.qt5.wrapQtAppsHook ];

        # Wrap it ourselves because non-ELF executables are ignored by the
        # automatic wrapping logic.  This gets the Qt environment properly
        # initialized.
        makeWrapperArgs = [
          "\${qtWrapperArgs[@]}"
          # import Qt.labs.platform failed without this
          # "--prefix QML2_IMPORT_PATH : ${qt5.qtquickcontrols2.bin}/${qt5.qtbase.qtQmlPrefix}"
        ];
      };

      magic-folder-env = mach-nix.mkPython {
        inherit providers;
        python = python2;
        packagesExtra = [ magic-folder ];
      };

      desktopclient =
        # Since we use this derivation in `environment.systemPackages`,
        # we create a derivation that has just the executables we use,
        # to avoid polluting the system PATH with all the executables
        # from our dependencies.
        pkgs.runCommandNoCC "privatestorage" {}
          ''
            mkdir -p $out/bin

            # Here's the main item.
            ln -s ${gridsync}/bin/gridsync $out/bin/gridsync

            # GridSync needs tahoe-lafs and magic-folder.
            ln -s ${privatestorage}/bin/tahoe $out/bin
            ln -s ${magic-folder-env}/bin/magic-folder $out/bin

            # Include some tools that are useful for debugging.
            ln -s ${privatestorage}/bin/flogtool $out/bin
            ln -s ${privatestorage}/bin/eliot-prettyprint $out/bin
          '';
    }
