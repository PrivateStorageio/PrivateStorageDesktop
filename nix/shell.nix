# Create an environment for development of the client or an easy way to run
# it.  `nix-shell` gives a development environment.  `nix-shell -A using`
# gives an environment with the client installed and ready to be run.
{ pkgs ? import <nixpkgs> { } }:
let
  gridsync = (pkgs.callPackage ./default.nix { });
  # Just create another derivation that has gridsync as a dependency.
  using = pkgs.stdenv.mkDerivation {
    name = "gridsync";
    src = ./.;
    buildInputs = [ gridsync ];
  };
in
  # Expose gridsync with the extra using attribute.
  gridsync // {
    inherit using;
  }
