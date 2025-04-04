{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs.buildPackages; [
        flyctl
        #docker
        python312
        ansible
        glibcLocales
        esptool
        mpy-utils
        picocom
        mpremote
        micropython
    ];
}
