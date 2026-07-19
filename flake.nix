{
  description = "MesaNote dev environment";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      self,
      flake-utils,
      nixpkgs,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python314
            pkgs.poetry
          ];

          # Install the core CLI and activate venv
          shellHook = ''
            cd core
            poetry install -q
            source "$(poetry env info --path)/bin/activate"
            cd ..
          '';
        };
      }
    );
}
