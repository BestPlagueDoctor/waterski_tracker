{
  description = "";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs = inputs@{ self, nixpkgs, ... }: let
    config = {
      allowUnfree = true;
    };

    

    forAllSystems = f: nixpkgs.lib.genAttrs [
      "x86_64-linux"
      "aarch64-linux"
    ] (system: f system (
      import nixpkgs { inherit system config; }
    ));

  in {
    devShells = forAllSystems (system: pkgs: with pkgs; {
      default = mkShell rec {
        packages = [
          (python3.withPackages (ps: with ps; [ (ps.opencv4.override { enableGtk3 = true; }) tkinter ])) 
          pkg-config
          ffmpeg.dev
          pdm

          opencv4
          gst_all_1.gstreamer
          gst_all_1.gst-plugins-base
          gst_all_1.gst-plugins-good
          gst_all_1.gst-plugins-bad
          gst_all_1.gst-plugins-ugly
          gst_all_1.gst-libav
          gst_all_1.gst-vaapi

          texlive.combined.scheme-full
        ];

        libs = nixpkgs.lib.makeLibraryPath [
          stdenv.cc.cc.lib
          zlib
          ffmpeg
        ];

        shellHook = ''
        export PATH=$PWD/util:$PATH
        export LD_LIBRARY_PATH=${libs}:$LD_LIBRARY_PATH
        '';
      };
    });
  };
}
