{ pkgs ? import <nixpkgs> { }, pythonPackages ? pkgs.python39Packages }:

pkgs.mkShell {
  buildInputs = [
    pythonPackages.graphviz
    # development
    pythonPackages.pytest
    pythonPackages.black
    pythonPackages.flake8
  ];
}
