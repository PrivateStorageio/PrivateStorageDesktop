{ lib, buildPythonPackage, fetchPypi, pkg-config }:

buildPythonPackage rec {
  pname = "pkgconfig";
  version = "1.5.2";

  inherit (pkg-config)
    setupHooks
    wrapperName
    suffixSalt
    targetPrefix
    baseBinName
  ;

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256:156a73vad65cm7i7bbriphyxc80xq2vcm2ks5rd7acq6ix415miq";
  };


  propagatedNativeBuildInputs = [ pkg-config ];

  doCheck = false;

  patches = [ ./executable.patch ];
  postPatch = ''
    substituteInPlace pkgconfig/pkgconfig.py --replace 'PKG_CONFIG_EXE = "pkg-config"' 'PKG_CONFIG_EXE = "${pkg-config}/bin/${pkg-config.targetPrefix}pkg-config"'
  '';

  pythonImportsCheck = [ "pkgconfig" ];

  meta = with lib; {
    description = "Interface Python with pkg-config";
    homepage = "https://github.com/matze/pkgconfig";
    license = licenses.mit;
  };
}
