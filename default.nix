{ mkDerivation, base, containers, ginger, hpack, lens, mtl, stdenv
, text
}:
mkDerivation {
  pname = "offertex";
  version = "2.0.0";
  src = ./.;
  isLibrary = true;
  isExecutable = true;
  libraryHaskellDepends = [ base containers ginger lens mtl text ];
  libraryToolDepends = [ hpack ];
  executableHaskellDepends = [
    base containers ginger lens mtl text
  ];
  preConfigure = "hpack";
  license = stdenv.lib.licenses.mit;
}
