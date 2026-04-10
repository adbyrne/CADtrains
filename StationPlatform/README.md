# StationPlatform

3D-printable station platform for a model railroad layout. Uses a FreeCAD embedded spreadsheet for parametric dimensions, allowing easy resizing.

![StationPlatform ISO view](images/stationplatform_iso.png)

## Parts

- **StationPlatform** — Full platform assembly
- **PlatformOnly** — Platform surface without additional structure

## Quick Start

### Print Settings
| Setting | Value |
|---------|-------|
| Material | PETG |
| Printer | Prusa Core One |
| Supports | None |

### Parametric Dimensions

Open `freecad/spreadsheet.FCStd` to adjust platform dimensions. Key parameters drive the main model in `StationPlatform.FCStd`.

## Project Structure

```
StationPlatform/
├── README.md              # This file
├── freecad/               # FreeCAD source files
│   ├── StationPlatform.FCStd
│   ├── StationPlatformTeam.FCStd
│   └── spreadsheet.FCStd  # Parametric dimension spreadsheet
└── printed_files/         # STL exports
    ├── StationPlatform_v1.stl
    └── PlatformOnly (Meshed).stl
```

## License

GNU General Public License v3.0 - see repository root.
