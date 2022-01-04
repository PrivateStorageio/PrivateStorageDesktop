let
  gridsync = import ./default.nix {};
  inherit (gridsync) mach-nix;
in
  mach-nix.nixpkgs.mkShell {
    python = "python27";
    buildInputs = [
      gridsync.tahoe-lafs-env
      gridsync.magic-folder-env
      gridsync.gridsync
      gridsync.gridsync-testing
    ] ++ gridsync.gridsync-lint.buildInputs;
  }
