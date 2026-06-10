# Miru GPU Particle Playground

Interactive particle simulation for studying browser GPU workflows.

## Run

```bash
npm install
npm run dev
```

Open the Vite URL in a browser with WebGPU support. The app falls back to a
Three.js WebGL GPGPU path when `navigator.gpu` is unavailable.

## Features

- WebGPU compute path with GPU-owned particle state buffers.
- WebGL fallback based on floating-point texture ping-pong.
- Particle presets: `2k`, `4k`, `8k`, `16k`, `64k`, `256k`, and `1M`.
- Gravity, damping, bounce, mouse/touch attractor, and animated attractors.
- Sphere or box bounds.
- Velocity, lifetime, force, and bounds debug modes.
- Direct per-frame rendering with no screen-space accumulation artifacts.
- Manual orbit controls for rotating around the 3D particle volume. Camera
  movement disables the mouse attractor so dragging rotates the view instead of
  pulling particles.

## Study Notes

The WebGPU path keeps the CPU responsible for parameters and camera matrices,
while particle position, velocity, age, lifetime, and seed values live in GPU
storage buffers. The fallback keeps equivalent state in floating-point textures
so the same mental model is preserved in WebGL.
