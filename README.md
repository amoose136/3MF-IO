# blender-3mf-texture-io

Experimental 3MF import/export core for Blender, built on top of **lib3mf**, with a focus on:

-   **Textures / UVs** (Texture2D + Texture2DGroup)
-   Future **segmentation / multimaterial** workflows

The long-term goal is to make it easy to go:

> **Blender painting / texturing → 3MF with textures → slicers / viewers → back to Blender**

without being locked into per-face segmentation strings.

---

## Status

Early scaffolding.

-   [x] Repo + basic Python package layout
-   [x] MIT license
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

Follow the instructions on the Pixi site, then in the repo root:

```bash
pixi install
```
