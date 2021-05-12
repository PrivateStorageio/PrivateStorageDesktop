# Build the PrivateStorage client as a Python application.
{ pkgs ? import <nixpkgs> { } }:
pkgs.callPackage ./gridsync.nix { }
