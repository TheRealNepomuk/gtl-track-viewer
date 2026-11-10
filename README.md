# GTL Track Viewer

Look at any GT Legends track in 3D without starting the game: the shape of the circuit,
elevation over the lap, sectors, pit lane and grid, plus a drive-along view.

Made for the GT Legends / [Altbierbude](https://www.altbierbude.de) community. Work in progress.

## How it works
GT Legends tracks ship with an AI waypoint file (`.AIW`) that describes the racing line:
road centre, road width, pit lane and starting grid. `tools/extract.py` reads those files
plus the track info (`.gdb`) from an installed game and writes small JSON files that the
web viewer in `docs/` draws with three.js.

## What is and isn't included
Only that derived line data and the track info are published here. No 3D models, textures
or other files from the track mods. Those stay with their authors and on the download servers.
All track credit goes to the original builders and converters.

If you made one of these tracks and want it removed or credited differently, please open an issue.

## Regenerate the data
```
python3 tools/extract.py "<GT Legends>/GameData/Locations" docs/data
```

## Related
Running GT Legends with Altbierbude on Linux:
[gt-legends-altbierbude-linux](https://github.com/TheRealNepomuk/gt-legends-altbierbude-linux)
