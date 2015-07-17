let
  pkgs = import <nixpkgs> {};
in
{ stdenv ? pkgs.stdenv, python ? pkgs.python, pythonIRClib ? pkgs.pythonIRClib }:

stdenv.mkDerivation {
  name = "python-nix";
  version = "0.1.0.0";
  src = ./.;
  buildInputs = [ python pkgs.python27Packages.pyqt4 ];
}

