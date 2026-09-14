#!/bin/bash
exec retroarch -L ~/.config/retroarch/cores/tyrquake_libretro.so "$(dirname "$0")/quake/id1/pak0.pak" "$@"
