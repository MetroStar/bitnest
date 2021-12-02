{
  description = "Bitnest";

  inputs = {
     nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs = { self, nixpkgs }:
      let
        pkgs = nixpkgs.legacyPackages.x86_64-linux;

        pythonPackages = pkgs.python3Packages;
      in {
      defaultPackage.x86_64-linux = pkgs.python3.buildPythonPackage {
        pname = "bitnest";
        version = "0.1.0";

        src = ./.;

        propagatedBuildInputs = [
          pythonPackages.graphviz
          pythonPackages.astor
        ];
      };

       devShell.x86_64-linux = pkgs.mkShell {
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
       };
  };
}
