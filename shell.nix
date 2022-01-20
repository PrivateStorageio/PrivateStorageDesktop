let
  gridsync = import ./default.nix {};
  inherit (gridsync) mach-nix;
in
  mach-nix.nixpkgs.mkShell {
    python = "python39";
    buildInputs = [
      gridsync.privatestorage-env
      gridsync.magic-folder-app
      gridsync.gridsync
      gridsync.gridsync-testing
    ];
  }
