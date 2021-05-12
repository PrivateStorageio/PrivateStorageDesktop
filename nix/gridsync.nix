{ pkgs }:
let
  repo = import ./gridsync-repo.nix;
  gridsync = pkgs.callPackage "${repo}/nix" { };
  psio-src = ../.;
  assets = [
    { src = "${psio-src}/assets/PrivateStorage*"; dst = "images/"; }
    { src = "${psio-src}/assets/PrivateStorage*"; dst = "gridsync/resources/"; }
    { src = "${psio-src}/assets/PrivateStorage.png"; dst = "gridsync/resources/tahoe-lafs.png"; }
    { src = "${psio-src}/credentials/*.json"; dst = "gridsync/resources/providers/"; }
    { src = "${psio-src}/build/config.txt"; dst = "gridsync/resources/"; }
    { src = "${psio-src}/build/InnoSetup6.iss"; dst = "misc/"; }
    { src = "${psio-src}/scripts/*"; dst = "./"; }
    { src = "gridsync/resources/laptop.png"; dst = "gridsync/resources/laptop-with-icon.png"; }
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
  gridsync.overrideAttrs (old: {
    name = "PrivateStorageDesktop";

    prePatch = ''
      # Replicate PrivateStorageDesktop `make source` logic here.
      ${apply-branding assets}
      ${if old ? prePatch then old.prePatch else ""}
    '';
})
