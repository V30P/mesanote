{
  description = "A frill-free markup language for quickly creating structured notes.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    flake-parts.url = "github:hercules-ci/flake-parts";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs@{ self, flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem =
        {
          pkgs,
          system,
          config,
          ...
        }:
        let
          inherit (inputs) pyproject-nix uv2nix pyproject-build-systems;

          workspace = uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./core;
          };

          # Create the Python package set using:
          # 1. Python 3.12
          # 2. Python build-system support
          # 3. Dependencies from uv.lock
          pythonPackages =
            (pkgs.callPackage pyproject-nix.build.packages {
              python = pkgs.python312;
            }).overrideScope
              (
                pkgs.lib.composeManyExtensions [
                  pyproject-build-systems.overlays.default
                  (workspace.mkPyprojectOverlay {
                    sourcePreference = "wheel";
                  })
                ]
              );

          buildUtils = pkgs.callPackages pyproject-nix.build.util { };
        in
        {
          # Packages
          packages = {
            default =
              let
                buildUtils = pkgs.callPackages pyproject-nix.build.util { };
              in
              buildUtils.mkApplication {
                venv = pythonPackages.mkVirtualEnv "mesanote" workspace.deps.default;
                package = pythonPackages.mesanote;
              };

            extension =
              let
                extensionManifest = pkgs.lib.importJSON ./extension/package.json;

                # Derivation for the node modules
                extensionNodeModules = pkgs.buildNpmPackage {
                  pname = "${extensionManifest.name}-node-modules";
                  version = extensionManifest.version;
                  src = ./extension;
                  npmDepsHash = "sha256-XU+wiuHy77rsie54tFI/bpk2HS1kJj69RIIxO4nCtLA";
                  dontNpmBuild = true;
                  npmFlags = [ "--ignore-scripts" ];
                  installPhase = ''
                    mkdir -p $out
                    cp -r node_modules $out/node_modules
                  '';
                };

                # Derivation for compiling the extension source
                builtExtension = pkgs.stdenv.mkDerivation {
                  name = "extension";
                  pname = extensionManifest.name;
                  version = extensionManifest.version;
                  src = ./extension;

                  nativeBuildInputs = [ pkgs.nodejs_22 ];

                  buildPhase = ''
                    runHook preBuild
                    cp -r ${extensionNodeModules}/node_modules .
                    chmod -R u+w node_modules
                    npx tsc -p .
                    runHook postBuild
                  '';

                  installPhase = ''
                    runHook preInstall
                    mkdir -p $out
                    cp -r . $out
                    rm -rf $out/node_modules
                    runHook postInstall
                  '';
                };
              in
              pkgs.vscode-utils.buildVscodeExtension {
                pname = extensionManifest.name;
                src = builtExtension;
                vscodeExtUniqueId = "${extensionManifest.publisher}.${extensionManifest.name}";
                vscodeExtPublisher = extensionManifest.publisher;
                vscodeExtName = extensionManifest.name;
                version = extensionManifest.version;
              };
          };

          # Dev shell
          devShells.default =
            let
              editablePythonPackages = pythonPackages.overrideScope (
                workspace.mkEditablePyprojectOverlay {
                  root = "$REPO_ROOT/core";
                }
              );
            in
            pkgs.mkShell {
              packages = with pkgs; [
                (editablePythonPackages.mkVirtualEnv "mesanote-dev" workspace.deps.all)
                uv
                nodejs_22
              ];

              env = {
                UV_NO_SYNC = "1";
                UV_PYTHON = editablePythonPackages.python.interpreter;
                UV_PYTHON_DOWNLOADS = "never";
              };

              shellHook = ''
                unset PYTHONPATH
                export REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
              '';
            };
        };

      # Home-manager module
      flake = {
        homeManagerModules.default =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          {
            options.programs.mesanote.enable = lib.mkEnableOption "MesaNote";

            config = lib.mkIf config.programs.mesanote.enable {
              home.packages = [ self.packages.${pkgs.stdenv.hostPlatform.system}.default ];
            };
          };
      };
    };
}
