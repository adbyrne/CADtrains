# CADtrains

FreeCAD parametric designs for model railroad rolling stock and station structures. All components are 3D-printable on a Prusa Core One (250x210mm build plate), primarily in PETG.

## Projects

| Project | Description |
|---------|-------------|
| [Caboose](Caboose/) | Interior detail components for a caboose car |
| [CokeOvens](CokeOvens/) | HO scale modular bank coke oven bank (C&O Railway, circa 1900 WV coalfields) |
| [Station](Station/) | Station building structure |
| [StationPlatform](StationPlatform/) | Parametric station platform; dimensions driven by embedded FreeCAD spreadsheet |

## Project Structure Convention

Each project follows a standard layout:

```
ProjectName/
├── README.md              # Overview and print settings
├── DESIGN.md              # Full technical specification (if present)
├── freecad/               # FreeCAD source files (.FCStd)
├── printed_files/         # STL and 3MF exports
├── images/                # Screenshots and reference drawings (if present)
└── scripts/               # Parametric build scripts (if present)
```

## License

GNU General Public License v3.0
