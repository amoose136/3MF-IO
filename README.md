# 3MF-IO

Experimental 3MF import/export core for Blender, built on top of **lib3mf**, with a focus on:

-   **Textures / UVs** (Texture2D + Texture2DGroup)
-   Future **segmentation / multimaterial** workflows

The long-term goal is to make it easy to go:

> **Blender painting / texturing → 3MF with textures → slicers / viewers → back to Blender**

without being locked into per-face segmentation strings. Currently 

---

## Status

Early scaffolding.

-   [x] Repo + basic Python package layout
-   [x] lib3mf-based reader
-   [x] Support Model Naming MetaData
-   [ ] Support Basic Model Transforms
-   [ ] Support Robust Units
-   [ ] lib3mf-based writer
-   [ ] Basic round-trip tests
-   [ ] Texture / UV support
-   [ ] Segmentation / multimaterial mapping
-   [ ] Seam Painting Support
-   [ ] Fuzzy Print Support

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

This will setup the python environment for development. To make it work in Blender you need lib3mf downloaded also which be accomplished with:

```bash
pixi run download-lib3mf-wheel
```

Which will download cross platform wheels of lib3mf into the wheels folder. 
Additionally I'd recommend symlinking ([windows](https://www.howtogeek.com/16226/complete-guide-to-symbolic-links-symlinks-on-windows-or-linux/), [mac / linux](https://linuxize.com/post/how-to-create-symbolic-links-in-linux-using-the-ln-command/)) a folder named 3mfimport in the [Blender extension system directory for your platform](https://blender.stackexchange.com/questions/293145/where-are-third-party-addons-stored) to the src directory of this addon and then it should work and get updates every time you restart Blender.
