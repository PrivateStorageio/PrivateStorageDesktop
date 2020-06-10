{ lib, python3Packages, fetchFromGitHub }:
python3Packages.buildPythonPackage rec {
  version = "v4.4.28";
  name = "zxcvbn-${version}";
  src = fetchFromGitHub {
    owner = "dwolfhub";
    repo = "zxcvbn-python";
    rev = version;
    sha256 = "0xzlsqc9h0llfy19w4m39jgfcnvzqviv8jhgwn3r75kip97i5mvs";
  };

  meta = with lib; {
    description = "Low-Budget Password Strength Estimation";
    homepage = https://github.com/dwolfhub/zxcvbn-python;
    license = licenses.mit;
    platform = platforms.linux;
  };
}
