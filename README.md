# 3MF-IO

Experimental 3MF import/export core for Blender, built on top of **lib3mf**, with a focus on:

-   **Textures / UVs** (Texture2D + Texture2DGroup)
-   Future **segmentation / multimaterial** workflows

The long-term goal is to make it easy to go:

> **Blender painting / texturing → 3MF with textures → slicers / viewers → back to Blender**

without being locked into per-face segmentation strings. Currently in early stages. For importing I aim to make this compatible with 3mf from standard consumer level 3d slicers. For exporting, a particular flavor of 3mf may need to be specified depending on the target slicer but I really would like things to be as confirming to the 3mf specification as possible and then hopefully over time the slicers can slowly make more compliant 3mf instead of using a bunch of different bespoke solutions to the same problems.

---

## Status

Very early days. Not useful yet.

- [x] Repo + basic Python package layout
- [x] Reader (3mf -> Blender data)
  - [x] Base Mesh Geometry
  - [x] Model Naming and Collection metadata (annoyingly using xml tree reading for this instead of lib3mf at the moment for technical reasons)
  - [ ] Basic Model and Collections Transforms (matrix)
  - [ ] Robust Unit Conversions (mm/in/ft/etc)
  - [ ] Base Material Support
  - [ ] Physical based / Shader Material Support (not made by slicers but other programs support it) 
  - [ ] Texture / UV support
  - [ ] Modifier Mesh Properties (support a subset of slicer settings)
  - [ ] Boolean objects as Boolean modifiers
  - [ ] Support / Enforcers Blockers
  - [ ] Segmentation / multimaterial mapping
  - [ ] Seam Painting Support
  - [ ] Text objects
  - [ ] Fuzzy Print Support (possibly later with a new V2 / UV texture based fuzzy printing)
  - [ ] Volumetrics extension? Blender supports sdfs / levelsets via geometry nodes as of version 5.0 (OpenVDB functions)... maybe this can be imported at least? Very low priority for now.
- [ ] Writer (Blender Data -> 3mf)
  - [ ] Base Mesh Geometry
  - [ ] Model Naming and Collection metadata
  - [ ] Basic Model and Collections Transforms (matrix)
  - [ ] Robust Unit Conversions (mm/in/ft/etc)
  - [ ] Base Material Support
  - [ ] Texture / UV support (currently no consumer slicer supports this...for now. 👀  Possibly can instead bake an texture / UV image to segmentation strings in the meantime but that's really gross. )
  - [ ] Modifier Mesh Properties (support a subset of slicer settings)
  - [ ] Boolean objects as Boolean modifiers
  - [ ] Support / Enforcers Blockers
  - [ ] Segmentation / multimaterial mapping
  - [ ] Seam Painting Support
  - [ ] Text objects
  - [ ] Fuzzy Print Support (possibly later with a new V2 / UV texture based fuzzy printing which would support grayscale mapping that would make it so fuzzy print isn't all or nothing but instead could have an intensity that fades in or out over a region)
  - [ ] Volumentrics? (currently no consumer slicer supports this but if a node tree only uses certain nodes, it's theoretically possible to save that to 3mf volumetrics...) Very very low priority.
- [ ] Basic round-trip testing to ensure the plugin doesn't break with new feature implementation
  - [ ] Files from BambuStudio, Cura, OrcaSlicer, PrusaSlicer, are all importable
  - [ ] Files from FreeCAD, Fusion360 are importable
  - [ ] Performance for IO should generally by on par or faster than Ghostkeeper's solution was (thanks Ghostkeeper for the previous work in enabling 3mf support for blender!).

---

## License

This project is licensed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**.  
See the [LICENSE](./LICENSE) file for details.

It also bundles `lib3mf`, which is licensed under a BSD/Zlib-style permissive license.

## Development setup (Pixi)

This project uses [Pixi](https://pixi.sh) for environment management.

### 1. Install Pixi

Follow the [instructions on the Pixi site](https://pixi.sh/latest/installation/), then in the repo root:

```bash
pixi install
```

This will setup the python environment for development. 

### 2. Download lib3mf wheels
To make it work in Blender you need lib3mf downloaded also which be accomplished with:

```bash
pixi run download-lib3mf-wheel
```

Which will download cross platform wheels of lib3mf into the wheels folder. 
Additionally I'd recommend symlinking ([windows](https://www.howtogeek.com/16226/complete-guide-to-symbolic-links-symlinks-on-windows-or-linux/), [mac / linux](https://linuxize.com/post/how-to-create-symbolic-links-in-linux-using-the-ln-command/)) a folder named something like `3mfio` in the [Blender extension system directory for your platform](https://blender.stackexchange.com/questions/293145/where-are-third-party-addons-stored) to the src directory of this addon and then it should work and get updates every time you restart Blender.
