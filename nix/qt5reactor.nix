{ lib, python3Packages, fetchFromGitHub, twisted }:
python3Packages.buildPythonPackage rec {
  version = "v0.5";
  name = "qt5reactor";
  src = fetchFromGitHub {
    owner = "sunu";
    repo = "qt5reactor";
    rev = version;
    sha256 = "12y3q90r0f8zagwrfl09p8spivqg6zrwhfi4c2pm42h76iwwmyaj";
  };
  propagatedBuildInputs = [
    twisted
  ];

  meta = with lib; {
    description = "Twisted and PyQt5 eventloop integration.";
    homepage = https://github.com/sunu/qt5reactor;
    license = licenses.mit;
    platform = platforms.all;
  };
}
