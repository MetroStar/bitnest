{ pkgs ? import <nixpkgs> { }, pythonPackages ? pkgs.python39Packages }:

pkgs.mkShell {
  buildInputs = [
    pythonPackages.graphviz
    pythonPackages.astor
    # development
    pythonPackages.ipython
    pythonPackages.pytest
    pythonPackages.pytest-cov
    pythonPackages.black
    pythonPackages.flake8
    pythonPackages.sphinx
    pythonPackages.sphinx_rtd_theme
    pythonPackages.recommonmark
  ];
}
