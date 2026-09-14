#!/bin/bash
exec retroarch -L ~/.config/retroarch/cores/prboom_libretro.so "$(dirname "$0")/freedoom/GAMES/FREEDOOM/PHASE1/DOOM.WAD" "$@"
