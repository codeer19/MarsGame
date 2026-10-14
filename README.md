# MarsPixelAssets — 2D Top-Down Mars Exploration Pixel-Art Asset Pack

A complete, game-ready 2D pixel-art asset library designed for a *Soul Knight*-inspired scientifically grounded Mars exploration game in HTML5 Canvas / JavaScript and standard 2D engines (Godot, Unity, Phaser, PixiJS).

## Key Specifications
- **True Native Pixel Grids**:
  - **Astronaut Character**: `32x32` pixels per frame (transparent PNGs)
  - **Mars Terrain Tileset**: `32x32` pixels per tile (32 tiles total: 24 core surface/geological tiles + 8 cliff/crater/path transition tiles)
  - **Minerals & Collectibles**: `24x24` pixels (`8` minerals & geological samples + `5` survival/scientific items = `13` collectibles)
  - **Environmental Objects & Props**: `32x32` (small props), `48x48` (storage container, ancient arch), `48x64` (comm tower), and `64x64` (Mars rover, research habitat dome)
  - **Hazards & Effects**: `32x32` pixels with multi-frame animations
  - **UI & HUD Icons**: `16x16` icons (`ui_icons.png`), `64x12` HUD bars (`hud_bars.png`), `64x64` minimap frame (`minimap_frame.png`), and touch/joystick controls (`controls.png`)
- **Restrained 16-Bit Palette**: 33 deliberate RGBA colors with hard-edged pixel clusters, consistent dark outlines (`#18121c`), and zero anti-aliasing.
- **Reproducibility**: Run `python3 generate_assets.py` with Pillow (`PIL`) to regenerate or customize any sprite, palette, or atlas.

## Directory Structure
- `characters/` — Directional sheets (`astronaut_down.png`, `astronaut_up.png`, `astronaut_left.png`, `astronaut_right.png`), `astronaut_walk_4_directions.png`, `astronaut_run_4_directions.png`, `astronaut_interactions.png`, `astronaut_alternate_skins.png`, `character_manifest.json`, and 152 individual frame PNGs in `characters/frames/`.
- `terrain/` — `mars_terrain_tiles_32px.png` (256x128 atlas), `terrain_manifest.json`, and 32 individual `32x32` PNG tiles in `terrain/individual/`.
- `minerals/` — `minerals_atlas.png` and individual `24x24` mineral/sample PNGs in `minerals/individual/`.
- `items/` — `items_atlas.png` and all 13 collectible individual `24x24` PNGs in `items/individual/`.
- `objects/` — `objects_atlas.png` and 17 individual prop/vehicle/building PNGs in `objects/individual/`.
- `hazards/` — `hazards_atlas.png` and 23 hazard base + animation frame PNGs in `hazards/individual/`.
- `effects/` — `effects_atlas.png` and 27 environmental effect frame PNGs in `effects/individual/`.
- `ui/` — `ui_icons.png`, `hud_bars.png`, `minimap_frame.png`, `controls.png`, and individual icons/bars in `ui/individual/`.
- `preview/` — Nearest-neighbor enlarged inspection sheets (`asset_contact_sheet.png`, `astronaut_preview.png`, `terrain_preview.png`, `example_level.png`).
- `examples/` — `sample_tilemap.json` and `sample_atlas_usage.html`.

## Scientific vs. Artistic Note
All sprites and the sample level layout (`examples/sample_tilemap.json`) are hand-crafted artistic pixel-art game assets inspired by Martian geology (basalt columns, ferric oxide dust, olivine/sulfur/azurite mineral veins, rover/habitat architecture) and are not direct exports of NASA orbital telemetry.
