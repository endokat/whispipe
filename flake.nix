{
  description = "route voice to shell via pipe";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs = { self, nixpkgs, poetry2nix }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      # create a custom "mkPoetryApplication" API function that under the hood uses
      # the packages and versions (python3, poetry etc.) from our pinned nixpkgs above:
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      whispipe = mkPoetryApplication {
        projectDir = ./.;
      };
    in
    {
      apps.${system}.default = {
        type = "app";
        program = "${whispipe}/bin/whispipe";
      };
    };
}
