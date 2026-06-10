import "./style.css";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GPUComputationRenderer } from "three/addons/misc/GPUComputationRenderer.js";

const PARTICLE_PRESETS = [2048, 4096, 8192, 16384, 65536, 262144, 1048576];
const MAX_ATTRACTORS = 4;
const WORKGROUP_SIZE = 256;

const state = {
  particleCount: 16384,
  gravity: -1.2,
  attraction: 9,
  damping: 0.986,
  bounce: 0.68,
  pointSize: 0.14,
  debugMode: 0,
  boundsMode: 0,
  attractorCount: 2,
  mouseAttractor: true,
  paused: false,
  resetNonce: 1,
};

const els = {
  canvas: document.querySelector("#particle-canvas"),
  engineStatus: document.querySelector("#engine-status"),
  fpsLabel: document.querySelector("#fps-label"),
  particleCount: document.querySelector("#particle-count"),
  gravity: document.querySelector("#gravity"),
  gravityValue: document.querySelector("#gravity-value"),
  attraction: document.querySelector("#attraction"),
  attractionValue: document.querySelector("#attraction-value"),
  damping: document.querySelector("#damping"),
  dampingValue: document.querySelector("#damping-value"),
  bounce: document.querySelector("#bounce"),
  bounceValue: document.querySelector("#bounce-value"),
  pointSize: document.querySelector("#point-size"),
  pointSizeValue: document.querySelector("#point-size-value"),
  debugMode: document.querySelector("#debug-mode"),
  boundsMode: document.querySelector("#bounds-mode"),
  attractorCount: document.querySelector("#attractor-count"),
  attractorCountValue: document.querySelector("#attractor-count-value"),
  mouseAttractor: document.querySelector("#mouse-attractor"),
  pauseSim: document.querySelector("#pause-sim"),
  resetButton: document.querySelector("#reset-button"),
  randomizeButton: document.querySelector("#randomize-button"),
};

const pointer = {
  active: false,
  x: 0,
  y: 0,
  world: new THREE.Vector3(),
};

function syncControls() {
  els.gravityValue.value = state.gravity.toFixed(1);
  els.attractionValue.value = state.attraction.toFixed(1);
  els.dampingValue.value = state.damping.toFixed(3);
  els.bounceValue.value = state.bounce.toFixed(2);
  els.pointSizeValue.value = state.pointSize.toFixed(2);
  els.attractorCountValue.value = String(state.attractorCount);
}

function createInitialParticles(count, seed = 1) {
  const data = new Float32Array(count * 8);
  let randomState = seed >>> 0;
  const rand = () => {
    randomState = (1664525 * randomState + 1013904223) >>> 0;
    return randomState / 0xffffffff;
  };

  for (let i = 0; i < count; i += 1) {
    const r = Math.cbrt(rand()) * 18;
    const theta = rand() * Math.PI * 2;
    const phi = Math.acos(rand() * 2 - 1);
    const sinPhi = Math.sin(phi);
    const base = i * 8;
    data[base + 0] = Math.cos(theta) * sinPhi * r;
    data[base + 1] = Math.sin(theta) * sinPhi * r;
    data[base + 2] = Math.cos(phi) * r;
    data[base + 3] = rand() * 12;
    data[base + 4] = (rand() - 0.5) * 2.4;
    data[base + 5] = (rand() - 0.5) * 2.4;
    data[base + 6] = (rand() - 0.5) * 2.4;
    data[base + 7] = rand();
  }

  return data;
}

function resizeCanvasToDisplaySize(canvas) {
  const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
  const width = Math.max(1, Math.floor(canvas.clientWidth * pixelRatio));
  const height = Math.max(1, Math.floor(canvas.clientHeight * pixelRatio));
  const changed = canvas.width !== width || canvas.height !== height;
  if (changed) {
    canvas.width = width;
    canvas.height = height;
  }
  return changed;
}

function pointerToWorld(event) {
  const rect = els.canvas.getBoundingClientRect();
  const nx = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  const ny = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
  pointer.active = true;
  pointer.x = nx;
  pointer.y = ny;
}

function updatePointerWorld(camera) {
  const aspect = Math.max(0.01, els.canvas.clientWidth / Math.max(1, els.canvas.clientHeight));
  pointer.world.set(pointer.x * 24 * aspect, pointer.y * 24, 0);
  pointer.world.applyAxisAngle(new THREE.Vector3(0, 1, 0), camera.rotation.y * 0.4);
}

function buildAttractors(time) {
  const attractors = [];
  for (let i = 0; i < MAX_ATTRACTORS; i += 1) {
    if (i >= state.attractorCount) {
      attractors.push(new THREE.Vector4(0, 0, 0, 0));
      continue;
    }
    const phase = time * (0.32 + i * 0.08) + i * 1.77;
    const radius = 10 + i * 3.2;
    attractors.push(
      new THREE.Vector4(
        Math.cos(phase) * radius,
        Math.sin(phase * 0.77) * 8,
        Math.sin(phase) * radius,
        1,
      ),
    );
  }
  return attractors;
}

class WebGPUParticleEngine {
  constructor(canvas, count) {
    this.canvas = canvas;
    this.count = count;
    this.frameIndex = 0;
    this.format = null;
    this.uniformData = new Float32Array(32);
    this.renderUniformData = new Float32Array(28);
  }

  static async isSupported() {
    return Boolean(navigator.gpu);
  }

  async init() {
    if (!navigator.gpu) {
      throw new Error("WebGPU is unavailable");
    }
    this.adapter = await navigator.gpu.requestAdapter();
    if (!this.adapter) {
      throw new Error("No WebGPU adapter found");
    }
    this.device = await this.adapter.requestDevice();
    this.context = this.canvas.getContext("webgpu");
    this.format = navigator.gpu.getPreferredCanvasFormat();
    this.device.addEventListener("uncapturederror", (event) => {
      console.error("WebGPU validation error:", event.error?.message || event.error);
    });
    this.configureContext();
    this.createBuffers();
    await this.createPipelines();
  }

  configureContext() {
    this.context.configure({
      device: this.device,
      format: this.format,
      alphaMode: "opaque",
    });
  }

  createBuffers() {
    const initial = createInitialParticles(this.count, state.resetNonce);
    const usage = GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST;
    this.particleBuffers = [
      this.device.createBuffer({ size: initial.byteLength, usage }),
      this.device.createBuffer({ size: initial.byteLength, usage }),
    ];
    this.device.queue.writeBuffer(this.particleBuffers[0], 0, initial);
    this.device.queue.writeBuffer(this.particleBuffers[1], 0, initial);

    this.simUniformBuffer = this.device.createBuffer({
      size: 32 * Float32Array.BYTES_PER_ELEMENT,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });
    this.renderUniformBuffer = this.device.createBuffer({
      size: 28 * Float32Array.BYTES_PER_ELEMENT,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });
  }

  async assertShaderModule(module, label) {
    if (!module.getCompilationInfo) {
      return;
    }
    const info = await module.getCompilationInfo();
    const errors = info.messages.filter((message) => message.type === "error");
    if (errors.length > 0) {
      const details = errors
        .map((message) => `${label}:${message.lineNum}:${message.linePos} ${message.message}`)
        .join("\n");
      throw new Error(details);
    }
  }

  async createPipelines() {
    const computeShader = this.device.createShaderModule({
      label: "particle compute",
      code: `
struct Particle {
  posAge: vec4<f32>,
  velSeed: vec4<f32>,
}

struct SimParams {
  dt: f32,
  time: f32,
  count: f32,
  gravity: f32,
  attraction: f32,
  damping: f32,
  bounds: f32,
  bounce: f32,
  mouse: vec4<f32>,
  attractor0: vec4<f32>,
  attractor1: vec4<f32>,
  attractor2: vec4<f32>,
  attractor3: vec4<f32>,
  simMeta: vec4<f32>,
}

@group(0) @binding(0) var<storage, read> srcParticles: array<Particle>;
@group(0) @binding(1) var<storage, read_write> dstParticles: array<Particle>;
@group(0) @binding(2) var<uniform> params: SimParams;

fn hash(n: f32) -> f32 {
  return fract(sin(n) * 43758.5453123);
}

fn randomSphere(seed: f32) -> vec3<f32> {
  let z = hash(seed + 13.1) * 2.0 - 1.0;
  let a = hash(seed + 41.7) * 6.28318530718;
  let r = sqrt(max(0.0, 1.0 - z * z));
  return vec3<f32>(cos(a) * r, sin(a) * r, z);
}

fn attractForce(pos: vec3<f32>, attractorTarget: vec4<f32>, strength: f32) -> vec3<f32> {
  if (attractorTarget.w < 0.5) {
    return vec3<f32>(0.0);
  }
  let delta = attractorTarget.xyz - pos;
  let d2 = max(dot(delta, delta), 4.0);
  return normalize(delta) * strength / sqrt(d2);
}

@compute @workgroup_size(${WORKGROUP_SIZE})
fn main(@builtin(global_invocation_id) id: vec3<u32>) {
  let index = id.x;
  if (index >= u32(params.count)) {
    return;
  }

  var p = srcParticles[index];
  var pos = p.posAge.xyz;
  var age = p.posAge.w + params.dt;
  var vel = p.velSeed.xyz;
  let seed = p.velSeed.w + f32(index) * 0.0137;

  var force = vec3<f32>(0.0, params.gravity, 0.0);
  force += attractForce(pos, params.mouse, params.attraction * params.simMeta.y);
  force += attractForce(pos, params.attractor0, params.attraction);
  force += attractForce(pos, params.attractor1, params.attraction * 0.82);
  force += attractForce(pos, params.attractor2, params.attraction * 0.68);
  force += attractForce(pos, params.attractor3, params.attraction * 0.54);

  let swirl = normalize(vec3<f32>(-pos.z, 0.25 * sin(params.time + seed), pos.x) + vec3<f32>(0.001));
  force += swirl * 0.32;

  vel = (vel + force * params.dt) * pow(params.damping, params.dt * 60.0);
  pos = pos + vel * params.dt;

  if (params.simMeta.z < 0.5) {
    let dist = length(pos);
    if (dist > params.bounds) {
      let n = normalize(pos);
      pos = n * params.bounds;
      vel = reflect(vel, n) * params.bounce;
    }
  } else {
    if (pos.x > params.bounds) {
      pos.x = params.bounds;
      vel.x = -abs(vel.x) * params.bounce;
    }
    if (pos.x < -params.bounds) {
      pos.x = -params.bounds;
      vel.x = abs(vel.x) * params.bounce;
    }
    if (pos.y > params.bounds) {
      pos.y = params.bounds;
      vel.y = -abs(vel.y) * params.bounce;
    }
    if (pos.y < -params.bounds) {
      pos.y = -params.bounds;
      vel.y = abs(vel.y) * params.bounce;
    }
    if (pos.z > params.bounds) {
      pos.z = params.bounds;
      vel.z = -abs(vel.z) * params.bounce;
    }
    if (pos.z < -params.bounds) {
      pos.z = -params.bounds;
      vel.z = abs(vel.z) * params.bounce;
    }
  }

  let lifetime = 8.0 + hash(seed + 5.0) * 8.0;
  if (age > lifetime || length(pos) > params.bounds * 1.8) {
    let dir = randomSphere(seed + params.time);
    let radius = pow(hash(seed + 19.0), 0.3333) * params.bounds * 0.22;
    pos = dir * radius;
    vel = randomSphere(seed + 77.0) * (0.9 + hash(seed + 91.0) * 2.4);
    age = hash(seed + 31.0) * 2.0;
  }

  dstParticles[index].posAge = vec4<f32>(pos, age);
  dstParticles[index].velSeed = vec4<f32>(vel, p.velSeed.w);
}
      `,
    });

    const particleShader = this.device.createShaderModule({
      label: "particle render",
      code: `
struct Particle {
  posAge: vec4<f32>,
  velSeed: vec4<f32>,
}

struct RenderParams {
  viewProj: mat4x4<f32>,
  cameraRightPointSize: vec4<f32>,
  cameraUpDebug: vec4<f32>,
  boundsModeTime: vec4<f32>,
}

struct VertexOut {
  @builtin(position) position: vec4<f32>,
  @location(0) color: vec4<f32>,
  @location(1) local: vec2<f32>,
}

@group(0) @binding(0) var<storage, read> particles: array<Particle>;
@group(0) @binding(1) var<uniform> params: RenderParams;

fn palette(seed: f32, speed: f32, age: f32) -> vec3<f32> {
  let hot = vec3<f32>(1.0, 0.38 + 0.35 * seed, 0.16);
  let cool = vec3<f32>(0.12, 0.68, 1.0);
  let green = vec3<f32>(0.50, 1.0, 0.56);
  let mixA = mix(cool, hot, smoothstep(0.0, 9.0, speed));
  return mix(mixA, green, 0.22 + 0.18 * sin(seed * 17.0 + age));
}

@vertex
fn vs(@builtin(vertex_index) vertexIndex: u32, @builtin(instance_index) instanceIndex: u32) -> VertexOut {
  let corners = array<vec2<f32>, 6>(
    vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, -1.0), vec2<f32>(-1.0, 1.0),
    vec2<f32>(-1.0, 1.0), vec2<f32>(1.0, -1.0), vec2<f32>(1.0, 1.0)
  );
  let particle = particles[instanceIndex];
  let corner = corners[vertexIndex];
  let speed = length(particle.velSeed.xyz);
  let size = params.cameraRightPointSize.w * (0.7 + 0.45 * fract(particle.velSeed.w * 19.17));
  let offset = params.cameraRightPointSize.xyz * corner.x * size + params.cameraUpDebug.xyz * corner.y * size;
  var color = palette(particle.velSeed.w, speed, particle.posAge.w);
  let debugMode = i32(params.cameraUpDebug.w + 0.5);
  if (debugMode == 1) {
    color = abs(normalize(particle.velSeed.xyz + vec3<f32>(0.001)));
  } else if (debugMode == 2) {
    let v = fract(particle.posAge.w / 12.0);
    color = vec3<f32>(v, 1.0 - v, 0.65);
  } else if (debugMode == 3) {
    let v = smoothstep(0.0, 12.0, speed);
    color = vec3<f32>(v, v * v, 1.0 - v);
  } else if (debugMode == 4) {
    let edge = smoothstep(params.boundsModeTime.x * 0.78, params.boundsModeTime.x, length(particle.posAge.xyz));
    color = mix(vec3<f32>(0.08, 0.32, 0.92), vec3<f32>(1.0, 0.86, 0.28), edge);
  }

  var out: VertexOut;
  out.position = params.viewProj * vec4<f32>(particle.posAge.xyz + offset, 1.0);
  out.color = vec4<f32>(color, 0.58);
  out.local = corner;
  return out;
}

@fragment
fn fs(in: VertexOut) -> @location(0) vec4<f32> {
  let d = dot(in.local, in.local);
  let alpha = smoothstep(1.0, 0.05, d) * in.color.a;
  return vec4<f32>(in.color.rgb * alpha, alpha);
}
      `,
    });

    await this.assertShaderModule(computeShader, "particle compute");
    await this.assertShaderModule(particleShader, "particle render");

    this.computePipeline = this.device.createComputePipeline({
      label: "particle compute pipeline",
      layout: "auto",
      compute: { module: computeShader, entryPoint: "main" },
    });

    this.particlePipeline = this.device.createRenderPipeline({
      label: "particle render pipeline",
      layout: "auto",
      vertex: { module: particleShader, entryPoint: "vs" },
      fragment: {
        module: particleShader,
        entryPoint: "fs",
        targets: [
          {
            format: this.format,
            blend: {
              color: { srcFactor: "one", dstFactor: "one", operation: "add" },
              alpha: { srcFactor: "one", dstFactor: "one-minus-src-alpha", operation: "add" },
            },
          },
        ],
      },
      primitive: { topology: "triangle-list" },
    });

    this.computeBindGroups = [
      this.device.createBindGroup({
        layout: this.computePipeline.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: { buffer: this.particleBuffers[0] } },
          { binding: 1, resource: { buffer: this.particleBuffers[1] } },
          { binding: 2, resource: { buffer: this.simUniformBuffer } },
        ],
      }),
      this.device.createBindGroup({
        layout: this.computePipeline.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: { buffer: this.particleBuffers[1] } },
          { binding: 1, resource: { buffer: this.particleBuffers[0] } },
          { binding: 2, resource: { buffer: this.simUniformBuffer } },
        ],
      }),
    ];

    this.renderBindGroups = [
      this.device.createBindGroup({
        layout: this.particlePipeline.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: { buffer: this.particleBuffers[0] } },
          { binding: 1, resource: { buffer: this.renderUniformBuffer } },
        ],
      }),
      this.device.createBindGroup({
        layout: this.particlePipeline.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: { buffer: this.particleBuffers[1] } },
          { binding: 1, resource: { buffer: this.renderUniformBuffer } },
        ],
      }),
    ];
  }

  resize() {
    this.configureContext();
  }

  reset(seed) {
    state.resetNonce = seed;
    const initial = createInitialParticles(this.count, seed);
    this.device.queue.writeBuffer(this.particleBuffers[0], 0, initial);
    this.device.queue.writeBuffer(this.particleBuffers[1], 0, initial);
  }

  updateUniforms(params) {
    const attractors = buildAttractors(params.time);
    const mouseEnabled = params.mouseEnabled ? 1 : 0;
    this.uniformData.fill(0);
    this.uniformData.set([
      params.dt,
      params.time,
      this.count,
      state.gravity,
      state.attraction,
      state.damping,
      24,
      state.bounce,
      params.mouse.x,
      params.mouse.y,
      params.mouse.z,
      mouseEnabled,
    ]);
    for (let i = 0; i < MAX_ATTRACTORS; i += 1) {
      this.uniformData.set(attractors[i].toArray(), 12 + i * 4);
    }
    this.uniformData.set([state.attractorCount, mouseEnabled, state.boundsMode, state.resetNonce], 28);
    this.device.queue.writeBuffer(this.simUniformBuffer, 0, this.uniformData);

    const cameraRight = new THREE.Vector3().setFromMatrixColumn(params.camera.matrixWorld, 0);
    const cameraUp = new THREE.Vector3().setFromMatrixColumn(params.camera.matrixWorld, 1);
    this.renderUniformData.fill(0);
    this.renderUniformData.set(params.viewProjection.elements, 0);
    this.renderUniformData.set([cameraRight.x, cameraRight.y, cameraRight.z, state.pointSize], 16);
    this.renderUniformData.set([cameraUp.x, cameraUp.y, cameraUp.z, state.debugMode], 20);
    this.renderUniformData.set([24, state.boundsMode, params.time, 0], 24);
    this.device.queue.writeBuffer(this.renderUniformBuffer, 0, this.renderUniformData);
  }

  render(params) {
    this.updateUniforms(params);
    const encoder = this.device.createCommandEncoder();
    const readIndex = this.frameIndex % 2;
    const writeIndex = 1 - readIndex;

    if (!state.paused) {
      const computePass = encoder.beginComputePass();
      computePass.setPipeline(this.computePipeline);
      computePass.setBindGroup(0, this.computeBindGroups[readIndex]);
      computePass.dispatchWorkgroups(Math.ceil(this.count / WORKGROUP_SIZE));
      computePass.end();
    }

    const canvasPass = encoder.beginRenderPass({
      colorAttachments: [
        {
          view: this.context.getCurrentTexture().createView(),
          clearValue: { r: 0, g: 0, b: 0, a: 1 },
          loadOp: "clear",
          storeOp: "store",
        },
      ],
    });
    canvasPass.setPipeline(this.particlePipeline);
    canvasPass.setBindGroup(0, this.renderBindGroups[state.paused ? readIndex : writeIndex]);
    canvasPass.draw(6, this.count);
    canvasPass.end();

    this.device.queue.submit([encoder.finish()]);
    if (!state.paused) {
      this.frameIndex = writeIndex;
    }
  }

  dispose() {
    this.particleBuffers?.forEach((buffer) => buffer.destroy());
    this.simUniformBuffer?.destroy();
    this.renderUniformBuffer?.destroy();
  }
}

class WebGLGpgpuFallbackEngine {
  constructor(canvas, count) {
    this.canvas = canvas;
    this.count = count;
    this.textureSize = Math.ceil(Math.sqrt(count));
    this.activeCount = this.textureSize * this.textureSize;
    this.clock = new THREE.Clock();
  }

  async init() {
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: false,
      alpha: false,
      preserveDrawingBuffer: true,
    });
    this.renderer.setClearColor(0x05070a, 1);
    this.renderer.autoClear = false;
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    this.camera = new THREE.PerspectiveCamera(55, 1, 0.1, 500);
    this.scene = new THREE.Scene();
    this.createGpgpu();
    this.createPoints();
    this.resize();
  }

  createTexture(fillVelocity = false) {
    const texture = this.gpuCompute.createTexture();
    const data = texture.image.data;
    const initial = createInitialParticles(this.activeCount, state.resetNonce);
    for (let i = 0; i < this.activeCount; i += 1) {
      const src = i * 8;
      const dst = i * 4;
      if (fillVelocity) {
        data[dst + 0] = initial[src + 4];
        data[dst + 1] = initial[src + 5];
        data[dst + 2] = initial[src + 6];
        data[dst + 3] = initial[src + 7];
      } else {
        data[dst + 0] = initial[src + 0];
        data[dst + 1] = initial[src + 1];
        data[dst + 2] = initial[src + 2];
        data[dst + 3] = initial[src + 3];
      }
    }
    return texture;
  }

  createGpgpu() {
    this.gpuCompute = new GPUComputationRenderer(this.textureSize, this.textureSize, this.renderer);
    if (!this.renderer.capabilities.isWebGL2) {
      this.gpuCompute.setDataType(THREE.HalfFloatType);
    }
    const positionTexture = this.createTexture(false);
    const velocityTexture = this.createTexture(true);
    this.positionVariable = this.gpuCompute.addVariable("texturePosition", positionFragmentShader(), positionTexture);
    this.velocityVariable = this.gpuCompute.addVariable("textureVelocity", velocityFragmentShader(), velocityTexture);
    this.gpuCompute.setVariableDependencies(this.positionVariable, [this.positionVariable, this.velocityVariable]);
    this.gpuCompute.setVariableDependencies(this.velocityVariable, [this.positionVariable, this.velocityVariable]);

    const commonUniforms = {
      dt: { value: 0.016 },
      time: { value: 0 },
      gravity: { value: state.gravity },
      attraction: { value: state.attraction },
      damping: { value: state.damping },
      bounds: { value: 24 },
      bounce: { value: state.bounce },
      mouse: { value: new THREE.Vector4() },
      attractor0: { value: new THREE.Vector4() },
      attractor1: { value: new THREE.Vector4() },
      attractor2: { value: new THREE.Vector4() },
      attractor3: { value: new THREE.Vector4() },
      boundsMode: { value: state.boundsMode },
    };
    this.positionVariable.material.uniforms = THREE.UniformsUtils.clone(commonUniforms);
    this.velocityVariable.material.uniforms = THREE.UniformsUtils.clone(commonUniforms);
    const error = this.gpuCompute.init();
    if (error) {
      throw new Error(error);
    }
  }

  createPoints() {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.activeCount * 3);
    const refs = new Float32Array(this.activeCount * 2);
    for (let i = 0; i < this.activeCount; i += 1) {
      const x = (i % this.textureSize) / (this.textureSize - 1);
      const y = Math.floor(i / this.textureSize) / (this.textureSize - 1);
      refs[i * 2 + 0] = x;
      refs[i * 2 + 1] = y;
    }
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("reference", new THREE.BufferAttribute(refs, 2));
    this.pointMaterial = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: {
        texturePosition: { value: null },
        textureVelocity: { value: null },
        pointSize: { value: state.pointSize },
        debugMode: { value: state.debugMode },
      },
      vertexShader: pointVertexShader(),
      fragmentShader: pointFragmentShader(),
    });
    this.points = new THREE.Points(geometry, this.pointMaterial);
    this.scene.add(this.points);
  }

  resize() {
    this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight, false);
  }

  reset(seed) {
    state.resetNonce = seed;
    this.disposeGpgpuOnly();
    this.createGpgpu();
  }

  updateGpgpuUniforms(params) {
    const attractors = buildAttractors(params.time);
    for (const variable of [this.positionVariable, this.velocityVariable]) {
      const uniforms = variable.material.uniforms;
      uniforms.dt.value = params.dt;
      uniforms.time.value = params.time;
      uniforms.gravity.value = state.gravity;
      uniforms.attraction.value = state.attraction;
      uniforms.damping.value = state.damping;
      uniforms.bounce.value = state.bounce;
      uniforms.boundsMode.value = state.boundsMode;
      uniforms.mouse.value.set(params.mouse.x, params.mouse.y, params.mouse.z, params.mouseEnabled ? 1 : 0);
      uniforms.attractor0.value.copy(attractors[0]);
      uniforms.attractor1.value.copy(attractors[1]);
      uniforms.attractor2.value.copy(attractors[2]);
      uniforms.attractor3.value.copy(attractors[3]);
    }
  }

  render(params) {
    this.camera.copy(params.camera);
    this.camera.aspect = Math.max(0.01, this.canvas.clientWidth / Math.max(1, this.canvas.clientHeight));
    this.camera.updateProjectionMatrix();
    this.updateGpgpuUniforms(params);

    if (!state.paused) {
      this.gpuCompute.compute();
    }

    this.renderer.clear();
    this.pointMaterial.uniforms.texturePosition.value = this.gpuCompute.getCurrentRenderTarget(this.positionVariable).texture;
    this.pointMaterial.uniforms.textureVelocity.value = this.gpuCompute.getCurrentRenderTarget(this.velocityVariable).texture;
    this.pointMaterial.uniforms.pointSize.value = state.pointSize * 120;
    this.pointMaterial.uniforms.debugMode.value = state.debugMode;
    this.renderer.render(this.scene, this.camera);
  }

  disposeGpgpuOnly() {
    this.gpuCompute?.dispose();
  }

  dispose() {
    this.disposeGpgpuOnly();
    this.pointMaterial?.dispose();
    this.points?.geometry?.dispose();
    this.renderer?.dispose();
  }
}

function positionFragmentShader() {
  return `
uniform float dt;
uniform float bounds;
uniform float time;

void main() {
  vec2 uv = gl_FragCoord.xy / resolution.xy;
  vec4 posAge = texture2D(texturePosition, uv);
  vec4 velSeed = texture2D(textureVelocity, uv);
  posAge.xyz += velSeed.xyz * dt;
  posAge.w += dt;
  if (posAge.w > 16.0 || length(posAge.xyz) > bounds * 1.8) {
    float seed = velSeed.w + time;
    vec3 dir = normalize(vec3(
      sin(seed * 91.7),
      cos(seed * 63.3),
      sin(seed * 41.9)
    ));
    posAge.xyz = dir * fract(sin(seed * 7.1) * 43758.5453) * bounds * 0.22;
    posAge.w = fract(sin(seed * 13.1) * 43758.5453) * 2.0;
  }
  gl_FragColor = posAge;
}
`;
}

function velocityFragmentShader() {
  return `
uniform float dt;
uniform float time;
uniform float gravity;
uniform float attraction;
uniform float damping;
uniform float bounds;
uniform float bounce;
uniform float boundsMode;
uniform vec4 mouse;
uniform vec4 attractor0;
uniform vec4 attractor1;
uniform vec4 attractor2;
uniform vec4 attractor3;

vec3 attractForce(vec3 pos, vec4 target, float strength) {
  if (target.w < 0.5) {
    return vec3(0.0);
  }
  vec3 delta = target.xyz - pos;
  float d2 = max(dot(delta, delta), 4.0);
  return normalize(delta) * strength / sqrt(d2);
}

void main() {
  vec2 uv = gl_FragCoord.xy / resolution.xy;
  vec4 posAge = texture2D(texturePosition, uv);
  vec4 velSeed = texture2D(textureVelocity, uv);
  vec3 pos = posAge.xyz;
  vec3 vel = velSeed.xyz;
  vec3 force = vec3(0.0, gravity, 0.0);
  force += attractForce(pos, mouse, attraction);
  force += attractForce(pos, attractor0, attraction);
  force += attractForce(pos, attractor1, attraction * 0.82);
  force += attractForce(pos, attractor2, attraction * 0.68);
  force += attractForce(pos, attractor3, attraction * 0.54);
  force += normalize(vec3(-pos.z, 0.25 * sin(time + velSeed.w), pos.x) + 0.001) * 0.32;
  vel = (vel + force * dt) * pow(damping, dt * 60.0);
  vec3 nextPos = pos + vel * dt;
  if (boundsMode < 0.5) {
    float dist = length(nextPos);
    if (dist > bounds) {
      vec3 n = normalize(nextPos);
      vel = reflect(vel, n) * bounce;
    }
  } else {
    if (abs(nextPos.x) > bounds) vel.x = -vel.x * bounce;
    if (abs(nextPos.y) > bounds) vel.y = -vel.y * bounce;
    if (abs(nextPos.z) > bounds) vel.z = -vel.z * bounce;
  }
  gl_FragColor = vec4(vel, velSeed.w);
}
`;
}

function pointVertexShader() {
  return `
uniform sampler2D texturePosition;
uniform sampler2D textureVelocity;
uniform float pointSize;
uniform int debugMode;
attribute vec2 reference;
varying vec4 vColor;

vec3 palette(float seed, float speed, float age) {
  vec3 hot = vec3(1.0, 0.38 + 0.35 * seed, 0.16);
  vec3 cool = vec3(0.12, 0.68, 1.0);
  vec3 green = vec3(0.50, 1.0, 0.56);
  vec3 mixA = mix(cool, hot, smoothstep(0.0, 9.0, speed));
  return mix(mixA, green, 0.22 + 0.18 * sin(seed * 17.0 + age));
}

void main() {
  vec4 posAge = texture2D(texturePosition, reference);
  vec4 velSeed = texture2D(textureVelocity, reference);
  float speed = length(velSeed.xyz);
  vec3 color = palette(velSeed.w, speed, posAge.w);
  if (debugMode == 1) {
    color = abs(normalize(velSeed.xyz + 0.001));
  } else if (debugMode == 2) {
    float v = fract(posAge.w / 12.0);
    color = vec3(v, 1.0 - v, 0.65);
  } else if (debugMode == 3) {
    float v = smoothstep(0.0, 12.0, speed);
    color = vec3(v, v * v, 1.0 - v);
  } else if (debugMode == 4) {
    float edge = smoothstep(18.7, 24.0, length(posAge.xyz));
    color = mix(vec3(0.08, 0.32, 0.92), vec3(1.0, 0.86, 0.28), edge);
  }
  vColor = vec4(color, 0.62);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(posAge.xyz, 1.0);
  gl_PointSize = pointSize * (320.0 / max(20.0, -gl_Position.z));
}
`;
}

function pointFragmentShader() {
  return `
varying vec4 vColor;
void main() {
  vec2 local = gl_PointCoord * 2.0 - 1.0;
  float d = dot(local, local);
  float alpha = smoothstep(1.0, 0.05, d) * vColor.a;
  gl_FragColor = vec4(vColor.rgb * alpha, alpha);
}
`;
}

class PlaygroundApp {
  constructor() {
    this.camera = new THREE.PerspectiveCamera(54, 1, 0.1, 500);
    this.camera.position.set(58, 24, 58);
    this.cameraInteracting = false;
    this.controls = this.createOrbitControls(els.canvas);
    this.viewProjection = new THREE.Matrix4();
    this.clock = new THREE.Clock();
    this.lastFpsTime = performance.now();
    this.frames = 0;
    this.engine = null;
  }

  createOrbitControls(canvas) {
    const controls = new OrbitControls(this.camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.autoRotate = false;
    controls.enablePan = false;
    controls.target.set(0, 0, 0);
    controls.addEventListener("start", () => {
      this.cameraInteracting = true;
    });
    controls.addEventListener("end", () => {
      this.cameraInteracting = false;
    });
    return controls;
  }

  async init() {
    this.bindControls();
    syncControls();
    await this.createEngine();
    window.addEventListener("resize", () => this.handleResize());
    this.handleResize();
    this.controls.update();
    requestAnimationFrame((time) => this.tick(time));
  }

  bindControls() {
    els.particleCount.addEventListener("change", async () => {
      state.particleCount = Number(els.particleCount.value);
      await this.createEngine();
    });
    const bindRange = (input, key, parser = Number) => {
      input.addEventListener("input", () => {
        state[key] = parser(input.value);
        syncControls();
      });
    };
    bindRange(els.gravity, "gravity");
    bindRange(els.attraction, "attraction");
    bindRange(els.damping, "damping");
    bindRange(els.bounce, "bounce");
    bindRange(els.pointSize, "pointSize");
    bindRange(els.attractorCount, "attractorCount", (value) => Number.parseInt(value, 10));
    els.debugMode.addEventListener("change", () => {
      state.debugMode = Number(els.debugMode.value);
    });
    els.boundsMode.addEventListener("change", () => {
      state.boundsMode = Number(els.boundsMode.value);
    });
    els.mouseAttractor.addEventListener("change", () => {
      state.mouseAttractor = els.mouseAttractor.checked;
    });
    els.pauseSim.addEventListener("change", () => {
      state.paused = els.pauseSim.checked;
    });
    els.resetButton.addEventListener("click", () => this.engine?.reset(1));
    els.randomizeButton.addEventListener("click", () => this.engine?.reset(Math.floor(Math.random() * 100000) + 1));
    this.bindCanvasEvents();
  }

  bindCanvasEvents() {
    els.canvas.addEventListener("pointermove", pointerToWorld);
    els.canvas.addEventListener("pointerdown", pointerToWorld);
    els.canvas.addEventListener("pointerleave", () => {
      pointer.active = false;
    });
  }

  async createEngine() {
    const previousEngine = this.engine;
    this.engine = null;
    previousEngine?.dispose();
    resizeCanvasToDisplaySize(els.canvas);

    try {
      if (await WebGPUParticleEngine.isSupported()) {
        const nextEngine = new WebGPUParticleEngine(els.canvas, state.particleCount);
        await nextEngine.init();
        this.engine = nextEngine;
        els.engineStatus.textContent = "WebGPU compute";
      } else {
        throw new Error("WebGPU unavailable");
      }
    } catch (error) {
      console.warn("Falling back to WebGL GPGPU:", error);
      const freshCanvas = els.canvas.cloneNode(false);
      els.canvas.replaceWith(freshCanvas);
      els.canvas = freshCanvas;
      this.bindCanvasEvents();
      this.controls.dispose();
      this.controls = this.createOrbitControls(els.canvas);
      resizeCanvasToDisplaySize(els.canvas);
      const nextEngine = new WebGLGpgpuFallbackEngine(els.canvas, state.particleCount);
      await nextEngine.init();
      this.engine = nextEngine;
      els.engineStatus.textContent = "WebGL GPGPU fallback";
    }
    this.handleResize();
  }

  handleResize() {
    const changed = resizeCanvasToDisplaySize(els.canvas);
    this.camera.aspect = Math.max(0.01, els.canvas.clientWidth / Math.max(1, els.canvas.clientHeight));
    this.camera.updateProjectionMatrix();
    if (changed) {
      this.engine?.resize();
    }
  }

  updateCamera() {
    this.controls.update();
    this.camera.updateMatrixWorld();
    this.camera.updateProjectionMatrix();
    this.viewProjection.multiplyMatrices(this.camera.projectionMatrix, this.camera.matrixWorldInverse);
  }

  tick(now) {
    const rawDt = this.clock.getDelta();
    const dt = Math.min(rawDt, 1 / 30);
    const time = now * 0.001;
    this.handleResize();
    this.updateCamera();
    updatePointerWorld(this.camera);
    if (this.engine) {
      const mouseEnabled = state.mouseAttractor && pointer.active && !this.cameraInteracting;
      this.engine.render({
        dt,
        time,
        camera: this.camera,
        viewProjection: this.viewProjection,
        mouse: pointer.world,
        mouseEnabled,
      });
    }
    this.updateFps(now);
    requestAnimationFrame((nextTime) => this.tick(nextTime));
  }

  updateFps(now) {
    this.frames += 1;
    if (now - this.lastFpsTime > 500) {
      const fps = Math.round((this.frames * 1000) / (now - this.lastFpsTime));
      els.fpsLabel.textContent = `${fps} fps`;
      this.frames = 0;
      this.lastFpsTime = now;
    }
  }
}

new PlaygroundApp().init().catch((error) => {
  els.engineStatus.textContent = "failed";
  console.error(error);
});
