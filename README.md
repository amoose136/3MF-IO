# blender-3mf-texture-io

Experimental 3MF import/export core for Blender, built on top of **lib3mf**, with a focus on:

- **Textures / UVs** (Texture2D + Texture2DGroup)
- Future **segmentation / multimaterial** workflows
- Clean, testable Python core that can be used both:
  - inside a Blender add-on, and
  - standalone for tooling / CI.

This repo is split into:

- `src/blender3mf/` – pure Python + lib3mf “core” (no `bpy` dependencies)
- `addon/` – Blender add-on glue (import/export operators, UI)
- `tests/` – unit tests for the core

The long-term goal is to make it easy to go:

> **Blender painting / texturing → 3MF with textures → slicers / viewers → back to Blender**

without being locked into per-face segmentation strings.

---

## Status

Early scaffolding.

- [x] Repo + basic Python package layout
- [x] MIT license
- [ ] Minimal Model/mesh abstraction
- [ ] lib3mf-based reader/writer
- [ ] Basic round-trip tests
- [ ] Blender add-on stub
- [ ] Texture / UV support
- [ ] Segmentation / multimaterial mapping

---

## Development setup (Pixi)

This project uses [Pixi](https://pixi.sh) for environment management.

### 1. Install Pixi

Follow the instructions on the Pixi site, then in the repo root:

```bash
pixi install
