{ pkgs ? import <nixpkgs> {} }:

with pkgs.lib;

let
  pythonPkgs = (ps: with ps; [
    virtualenv
  ]);
  pythonEnv = pkgs.python3.withPackages pythonPkgs;
  venv = ".venv";
in pkgs.mkShell {
    doCheck = false;
    buildInputs = with pkgs; ([
      pythonEnv
      pkg-config
      libffi
      openssl
      stdenv.cc.cc
      stdenv.cc.cc.lib
      gcc.cc
      zlib
      zlib.dev
    ]);
    shellHook = ''
      export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$NIX_LD_LIBRARY_PATH:~/.nix-profile/lib"
      VENV=${venv}
      if test ! -d $VENV; then
        python -m venv $VENV
      fi
      source ./$VENV/bin/activate
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1
      export HIP_VISIBLE_DEVICES=0,1
      export HCC_AMDGPU_TARGET=gfx1100
      export HSA_OVERRIDE_GFX_VERSION=11.0.0
    '';
  }
