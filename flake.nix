{
  description = "Stan Nix Pkg overlay";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }: 
  let
    lib = import ./lib;
    allPkgs = lib.mkPkgs { inherit nixpkgs; };
  in {
    overlay = top: last: import ./pkgs top;

    packages.x86_64-linux = import ./pkgs allPkgs.x86_64-linux;
  };
}
