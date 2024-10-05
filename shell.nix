{ pkgs ? import <nixpkgs> {} }:

with pkgs.lib;

let
  pythonPkgs = (ps: with ps; []);
  pythonEnv = pkgs.python3.withPackages pythonPkgs;
in pkgs.mkShell {
    doCheck = false;
    propagatedBuildInputs = with pkgs; ([
      pythonEnv
      pkg-config
      portaudio
      libffi
      openssl
      libsndfile
      stdenv.cc.cc
      stdenv.cc.cc.lib
      gcc.cc
      zlib
      zlib.dev
    ]);
    shellHook = ''
      export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$NIX_LD_LIBRARY_PATH:~/.nix-profile/lib"
      export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:$LD_LIBRARY_PATH"
      export HIP_VISIBLE_DEVICES=0,1
      export HCC_AMDGPU_TARGET=gfx1100
      export HSA_OVERRIDE_GFX_VERSION=11.0.0
      poetry run zsh
    '';
  }
