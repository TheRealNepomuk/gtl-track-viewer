# GTL Track Viewer

Look at any GT Legends track in 3D without starting the game: the shape of the circuit,
height profile over the lap, sectors, pit lane and grid, plus a drive-along view.

Made for the GT Legends / [Altbierbude](https://www.altbierbude.de) community. Work in progress.

## How it works
GT Legends tracks ship with an AI waypoint file (`.AIW`) that describes the racing line:
road centre, road width, pit lane and starting grid. `tools/extract.py` reads those files
plus the track info (`.gdb`) from an installed game and writes small JSON files that the
web viewer in `docs/` draws with three.js.

## Track data
Only derived line data (centre line, road width, pit lane, grid, sectors) and the track info
from each `.gdb` are published here, in `docs/data/`. No 3D models, textures or other files
from the track mods. Those stay with their authors and on the download servers.

The tracks belong to their original builders and converters. The track data is **not**
covered by this project's license and is published for reference only.

If you made one of these tracks and want it removed or credited differently, please open an issue.

## Regenerate the data
```
python3 tools/extract.py "<GT Legends>/GameData/Locations" docs/data
```

## License
The code (extractor and web pages) is [MIT licensed](LICENSE): use it, change it, share it,
as long as the copyright notice stays with it. The track data is not included, see above.

If you build something on this, I'd appreciate a visible credit:
*based on [GTL Track Viewer](https://github.com/TheRealNepomuk/gtl-track-viewer) by TheRealNepomuk*.

## Support
If this is useful to you: [☕ Buy me a coffee](https://www.buymeacoffee.com/TheRealNepomuk)

## Related
Running GT Legends with Altbierbude on Linux:
[gt-legends-altbierbude-linux](https://github.com/TheRealNepomuk/gt-legends-altbierbude-linux)
