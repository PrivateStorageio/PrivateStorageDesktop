let
  pkgs = import <nixpkgs> {};
in
  pkgs.fetchFromGitHub {
    owner = "gridsync";
    repo = "gridsync";
    rev = "fcfaecbc18391248b11e5f8c7b80a5526f79f624";
    sha256 = "0cwjryj778rijxnvmghip0gmly1z7gn1bbbsczpmcvpsqj3a9i39";
  }
