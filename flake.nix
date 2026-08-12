{
  description = "MesaNote dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
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
    };
}
