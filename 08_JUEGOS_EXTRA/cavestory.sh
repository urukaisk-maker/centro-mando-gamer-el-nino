#!/bin/bash
exec retroarch -L ~/.config/retroarch/cores/nxengine_libretro.so "$(dirname "$0")/cavestory/CaveStory/Doukutsu.exe" "$@"
