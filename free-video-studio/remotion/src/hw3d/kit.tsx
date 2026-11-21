// 3D kit for the reference style: real 3D environments + big toon "bean" characters.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {Outlines, RoundedBox} from '@react-three/drei';
import {random, useCurrentFrame, useVideoConfig} from 'remotion';

export const useTime = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return f / fps;
};
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const t = clamp01(x); return t * t * (3 - 2 * t); };
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const ramp = (t: number, a: number, b: number) => smooth((t - a) / (b - a));

const INK = '#1b1b22';

// ---------------------------------------------------------------- face textures (drawn once per expression)
export type Face = 'smirk' | 'happy' | 'angry' | 'sad' | 'shock' | 'worried' | 'blink' | 'talk';
const faceCache = new Map<string, THREE.CanvasTexture>();
export function faceTexture(face: Face, glasses: boolean, sweat: boolean) {
  const key = `${face}-${glasses}-${sweat}`;
  if (faceCache.has(key)) return faceCache.get(key)!;
  const c = document.createElement('canvas');
  c.width = c.height = 512;
  const g = c.getContext('2d')!;
  g.lineCap = 'round'; g.lineJoin = 'round';
  const eyeY = 230, ex = 110;
  // eyes
  for (const s of [-1, 1]) {
    const x = 256 + s * ex;
    if (face === 'blink') {
      g.strokeStyle = INK; g.lineWidth = 16; g.beginPath(); g.moveTo(x - 38, eyeY); g.lineTo(x + 38, eyeY); g.stroke();
    } else {
      const r = face === 'shock' ? 58 : 46;
      g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 12;
      g.beginPath(); g.ellipse(x, eyeY, r, face === 'angry' ? r * 0.75 : r, 0, 0, Math.PI * 2); g.fill(); g.stroke();
      g.fillStyle = INK; const pr = face === 'shock' ? 16 : 22;
      g.beginPath(); g.arc(x + (face === 'worried' ? -6 : 6), eyeY + 4, pr, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#fff'; g.beginPath(); g.arc(x + 12, eyeY - 6, 7, 0, Math.PI * 2); g.fill();
    }
  }
  // glasses
  if (glasses) {
    g.strokeStyle = '#2a5bd7'; g.lineWidth = 16;
    for (const s of [-1, 1]) { g.beginPath(); g.roundRect(256 + s * ex - 78, eyeY - 64, 156, 128, 40); g.stroke(); }
    g.beginPath(); g.moveTo(256 - 32, eyeY - 10); g.quadraticCurveTo(256, eyeY - 28, 256 + 32, eyeY - 10); g.stroke();
  }
  // brows
  g.strokeStyle = INK; g.lineWidth = 18;
  const brow = (s: number, inner: number, outer: number) => { g.beginPath(); g.moveTo(256 + s * 60, eyeY - 90 + inner); g.lineTo(256 + s * 160, eyeY - 90 + outer); g.stroke(); };
  if (face === 'angry') { brow(-1, 26, -10); brow(1, 26, -10); }
  else if (face === 'worried' || face === 'sad') { brow(-1, -18, 10); brow(1, -18, 10); }
  else if (face === 'smirk') { brow(-1, 6, 0); brow(1, -20, -30); }
  else if (face === 'shock') { brow(-1, -30, -26); brow(1, -30, -26); }
  else { brow(-1, -4, 0); brow(1, -4, 0); }
  // mouth
  g.lineWidth = 16; g.strokeStyle = INK; g.fillStyle = '#7a1f2b';
  const my = 380;
  g.beginPath();
  if (face === 'happy' || face === 'talk') { g.moveTo(186, my - 14); g.quadraticCurveTo(256, my + 70, 326, my - 14); g.closePath(); g.fill(); g.stroke();
    g.fillStyle = '#fff'; g.fillRect(200, my - 10, 112, 18); }
  else if (face === 'smirk') { g.moveTo(190, my + 6); g.quadraticCurveTo(270, my + 40, 336, my - 22); g.stroke(); }
  else if (face === 'angry') { g.moveTo(196, my + 22); g.quadraticCurveTo(256, my - 18, 316, my + 22); g.stroke(); }
  else if (face === 'sad') { g.moveTo(206, my + 22); g.quadraticCurveTo(256, my - 6, 306, my + 22); g.stroke(); }
  else if (face === 'shock') { g.ellipse(256, my + 10, 34, 46, 0, 0, Math.PI * 2); g.fill(); g.stroke(); }
  else if (face === 'worried') { g.moveTo(200, my + 8); g.bezierCurveTo(230, my - 12, 260, my + 24, 312, my); g.stroke(); }
  else { g.moveTo(206, my); g.quadraticCurveTo(256, my + 16, 306, my); g.stroke(); }
  if (sweat) {
    g.fillStyle = '#5fc3ff'; g.strokeStyle = '#1b6fb0'; g.lineWidth = 6;
    g.beginPath(); g.moveTo(420, 90); g.quadraticCurveTo(450, 150, 420, 170); g.quadraticCurveTo(390, 150, 420, 90); g.fill(); g.stroke();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  faceCache.set(key, tex);
  return tex;
}

// ---------------------------------------------------------------- bean character
export type BeanProps = {
  position?: [number, number, number]; rotY?: number; scale?: number;
  shirt?: string; vest?: boolean; hair?: string; hat?: 'hard' | 'none'; glasses?: boolean;
  face?: Face; sweat?: boolean; walk?: number; armL?: number; armR?: number; lean?: number; seated?: boolean; bounce?: number;
  rightHand?: React.ReactNode; leftHand?: React.ReactNode; blinkSeed?: number;
};
export const Bean: React.FC<BeanProps> = ({
  position = [0, 0, 0], rotY = 0, scale = 1, shirt = '#f2f2f2', vest = false, hair = '#3b2a20', hat = 'none', glasses = false,
  face = 'happy', sweat = false, walk = 0, armL = 0, armR = 0, lean = 0, seated = false, bounce = 0, rightHand, leftHand, blinkSeed = 1,
}) => {
  const t = useTime();
  const blink = ((t + blinkSeed * 1.37) % 3.4) < 0.11;
  const tex = faceTexture(blink ? 'blink' : face, glasses, sweat);
  const step = walk ? Math.sin(t * 9 * walk) : 0;
  const bob = walk ? Math.abs(step) * 0.08 : Math.sin(t * 2.2 + blinkSeed) * 0.02 + bounce;
  const legL = seated ? -Math.PI / 2 : step * 0.55, legR = seated ? -Math.PI / 2 : -step * 0.55;
  const ink = <Outlines thickness={0.035} color={INK} />;
  return (
    <group position={position} rotation={[0, rotY, 0]} scale={scale}>
      <group position={[0, bob, 0]} rotation={[lean, 0, 0]}>
        {/* legs */}
        {[[-0.22, legL], [0.22, legR]].map(([x, a], i) => (
          <group key={i} position={[x as number, 1.0, 0]} rotation={[a as number, 0, 0]}>
            <mesh position={[0, -0.5, 0]} castShadow><cylinderGeometry args={[0.055, 0.055, 1.0, 10]} /><meshStandardMaterial color={INK} /></mesh>
            <mesh position={[0, -1.0, 0.1]} castShadow scale={[1, 0.6, 1.6]}><sphereGeometry args={[0.11, 16, 12]} /><meshStandardMaterial color={INK} /></mesh>
          </group>
        ))}
        {/* body */}
        <mesh position={[0, 1.55, 0]} castShadow>
          <capsuleGeometry args={[0.52, 0.75, 12, 24]} />
          <meshStandardMaterial color={vest ? '#ff7a12' : shirt} roughness={0.6} />
          {ink}
        </mesh>
        {vest && <>
          <mesh position={[0, 1.55, 0]} scale={[1.01, 1, 1.01]}><cylinderGeometry args={[0.525, 0.525, 0.09, 28, 1, true]} /><meshStandardMaterial color="#e8f6ff" emissive="#9fd4ff" emissiveIntensity={0.35} side={THREE.DoubleSide} /></mesh>
          <mesh position={[0, 1.55, 0.36]} rotation={[0.18, 0, 0]}><boxGeometry args={[0.32, 1.25, 0.4]} /><meshStandardMaterial color={shirt} roughness={0.7} /></mesh>
          <mesh position={[0, 1.78, 0.56]} rotation={[0.25, 0, 0]}><coneGeometry args={[0.07, 0.42, 4]} /><meshStandardMaterial color="#2b4c7e" /></mesh>
        </>}
        {/* arms */}
        {[[-1, armL, leftHand], [1, armR, rightHand]].map(([s, a, prop], i) => (
          <group key={i} position={[(s as number) * 0.52, 1.95, 0]} rotation={[-(a as number) - (walk ? -step * (s as number) * 0.5 : 0), 0, (s as number) * 0.25]}>
            <mesh position={[0, -0.42, 0]} castShadow><cylinderGeometry args={[0.05, 0.05, 0.84, 10]} /><meshStandardMaterial color={INK} /></mesh>
            <mesh position={[0, -0.88, 0]} castShadow><sphereGeometry args={[0.14, 16, 12]} /><meshStandardMaterial color="#ffffff" roughness={0.5} />{ink}</mesh>
            {prop && <group position={[0, -0.95, 0.05]}>{prop as React.ReactNode}</group>}
          </group>
        ))}
        {/* head */}
        <group position={[0, 3.05, 0]}>
          <mesh castShadow><sphereGeometry args={[0.95, 48, 36]} /><meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.42} roughness={0.5} />{ink}</mesh>
          <mesh><sphereGeometry args={[0.97, 48, 36, -0.7 + Math.PI / 2 - 0.15, 1.7, 0.55, 1.55]} /><meshBasicMaterial map={tex} transparent toneMapped={false} depthWrite={false} polygonOffset polygonOffsetFactor={-2} /></mesh>
          {/* hair */}
          <mesh position={[0, 0.18, -0.02]} rotation={[-0.15, 0, 0]}><sphereGeometry args={[1.0, 40, 24, 0, Math.PI * 2, 0, 1.05]} /><meshStandardMaterial color={hair} roughness={0.8} />{ink}</mesh>
          {hat === 'hard' && <group position={[0, 0.62, 0]} rotation={[-0.1, 0, 0]}>
            <mesh castShadow><sphereGeometry args={[0.82, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} /><meshStandardMaterial color="#ffc21a" roughness={0.35} />{ink}</mesh>
            <mesh position={[0, 0.02, 0.15]}><cylinderGeometry args={[1.0, 1.0, 0.06, 32]} /><meshStandardMaterial color="#ffb300" roughness={0.35} />{ink}</mesh>
          </group>}
        </group>
      </group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}><circleGeometry args={[0.9, 32]} /><meshBasicMaterial color="#000" transparent opacity={0.25} /></mesh>
    </group>
  );
};

// ---------------------------------------------------------------- props
export const Detonator: React.FC<{press?: number}> = ({press = 0}) => (
  <group rotation={[0.2, 0, 0]}>
    <RoundedBox args={[0.7, 0.45, 0.5]} radius={0.06} position={[0, 0, 0]} castShadow><meshStandardMaterial color="#c0392b" roughness={0.4} /><Outlines thickness={0.03} color={INK} /></RoundedBox>
    <mesh position={[0, 0.45 - press * 0.25, 0]}><cylinderGeometry args={[0.04, 0.04, 0.6, 8]} /><meshStandardMaterial color="#888" metalness={0.8} roughness={0.3} /></mesh>
    <mesh position={[0, 0.75 - press * 0.25, 0]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.06, 0.06, 0.6, 12]} /><meshStandardMaterial color="#222" /></mesh>
    <mesh position={[0.2, 0.1, 0.26]}><boxGeometry args={[0.16, 0.08, 0.02]} /><meshBasicMaterial color="#ffcc00" /></mesh>
  </group>
);
export const Stopwatch: React.FC<{t: number}> = ({t}) => (
  <group rotation={[Math.PI / 2 - 0.3, 0, 0]} scale={0.9}>
    <mesh castShadow><cylinderGeometry args={[0.32, 0.32, 0.12, 32]} /><meshStandardMaterial color="#d9dee3" metalness={0.7} roughness={0.25} /><Outlines thickness={0.02} color={INK} /></mesh>
    <mesh position={[0, 0.065, 0]}><cylinderGeometry args={[0.27, 0.27, 0.01, 32]} /><meshBasicMaterial color="#fff" /></mesh>
    <mesh position={[0, 0.075, 0]} rotation={[0, -t * 6, 0]}><boxGeometry args={[0.02, 0.01, 0.42]} /><meshBasicMaterial color="#d62828" /></mesh>
    <mesh position={[0, 0, -0.38]}><cylinderGeometry args={[0.05, 0.05, 0.1, 12]} /><meshStandardMaterial color="#999" metalness={0.8} /></mesh>
  </group>
);
export const Notebook: React.FC = () => (
  <group rotation={[-0.6, 0.2, 0]}>
    <RoundedBox args={[0.6, 0.06, 0.8]} radius={0.02} castShadow><meshStandardMaterial color="#f6e7b0" /><Outlines thickness={0.02} color={INK} /></RoundedBox>
    {[0, 1, 2, 3].map((k) => <mesh key={k} position={[0, 0.035, -0.25 + k * 0.15]}><boxGeometry args={[0.4, 0.005, 0.02]} /><meshBasicMaterial color="#5b6b8a" /></mesh>)}
  </group>
);

// ---------------------------------------------------------------- vehicles
const CAR_COLORS = ['#c0392b', '#2c7fb8', '#ecf0f1', '#2d2d2d', '#f1c40f', '#27ae60', '#8e44ad', '#d35400', '#7f8c8d', '#16a085'];
export const Car: React.FC<{position: [number, number, number]; rotY?: number; seed: number; brake?: boolean; lights?: boolean; color?: string; driver?: React.ReactNode}> =
  ({position, rotY = 0, seed, brake = true, lights = false, color, driver}) => {
    const c = color ?? CAR_COLORS[Math.floor(random('car' + seed) * CAR_COLORS.length)];
    return (
      <group position={position} rotation={[0, rotY, 0]}>
        <RoundedBox args={[1.9, 0.7, 4.2]} radius={0.22} position={[0, 0.62, 0]} castShadow receiveShadow><meshStandardMaterial color={c} metalness={0.35} roughness={0.35} /><Outlines thickness={0.03} color={INK} /></RoundedBox>
        <RoundedBox args={[1.65, 0.62, 2.1]} radius={0.2} position={[0, 1.2, -0.25]} castShadow><meshStandardMaterial color={c} metalness={0.35} roughness={0.35} /><Outlines thickness={0.03} color={INK} /></RoundedBox>
        <mesh position={[0, 1.22, -0.25]}><boxGeometry args={[1.68, 0.44, 1.7]} /><meshStandardMaterial color="#9fc6dd" metalness={0.6} roughness={0.08} transparent opacity={0.85} /></mesh>
        {driver && <group position={[-0.4, 0.55, -0.15]} scale={0.38}>{driver}</group>}
        {[[-0.95, -1.35], [0.95, -1.35], [-0.95, 1.35], [0.95, 1.35]].map(([x, z], i) => (
          <mesh key={i} position={[x, 0.36, z]} rotation={[0, 0, Math.PI / 2]} castShadow><cylinderGeometry args={[0.36, 0.36, 0.28, 18]} /><meshStandardMaterial color="#141414" roughness={0.9} /></mesh>
        ))}
        {[-0.65, 0.65].map((x) => <mesh key={'t' + x} position={[x, 0.75, -2.11]}><boxGeometry args={[0.42, 0.16, 0.04]} /><meshBasicMaterial color={brake ? '#ff2a2a' : '#7a1010'} toneMapped={false} /></mesh>)}
        {[-0.65, 0.65].map((x) => <mesh key={'h' + x} position={[x, 0.75, 2.11]}><boxGeometry args={[0.42, 0.16, 0.04]} /><meshBasicMaterial color={lights ? '#fff6d0' : '#d9d4c0'} toneMapped={false} /></mesh>)}
      </group>
    );
  };

// ---------------------------------------------------------------- environment
const winCache = new Map<string, THREE.CanvasTexture>();
export function windowTexture(seed: string, lit = 0.35, night = false) {
  const key = seed + lit + night;
  if (winCache.has(key)) return winCache.get(key)!;
  const c = document.createElement('canvas'); c.width = 256; c.height = 512;
  const g = c.getContext('2d')!;
  g.fillStyle = night ? '#1d1830' : '#b9c4cf'; g.fillRect(0, 0, 256, 512);
  for (let y = 0; y < 16; y++) for (let x = 0; x < 6; x++) {
    const on = random(seed + x + '-' + y) < lit;
    g.fillStyle = on ? (night ? '#ffcf7a' : '#e9f3fb') : (night ? '#2b2440' : '#6f8195');
    g.fillRect(10 + x * 41, 10 + y * 31, 30, 20);
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  winCache.set(key, t); return t;
}

export const City: React.FC<{seed: string; night?: boolean; area?: [number, number, number, number]; count?: number; minH?: number; maxH?: number; avoidX?: number; clear?: [number, number, number][]}> =
  ({seed, night = false, area = [-80, 80, -160, -30], count = 60, minH = 8, maxH = 45, avoidX = 0, clear = []}) => {
    const items = useMemo(() => [...Array(count)].map((_, i) => {
      let x = lerp(area[0], area[1], random(seed + 'x' + i));
      if (avoidX && Math.abs(x) < avoidX) x += Math.sign(x || 1) * avoidX;
      const z = lerp(area[2], area[3], random(seed + 'z' + i));
      const w = 6 + random(seed + 'w' + i) * 8, d = 6 + random(seed + 'd' + i) * 8, h = lerp(minH, maxH, random(seed + 'h' + i) ** 1.6);
      const blocked = clear.some(([cx, cz, r]) => Math.hypot(x - cx, z - cz) < r + Math.max(w, d) / 2);
      return {x, z, w, d, h, blocked, tex: random(seed + 't' + i) > 0.5 ? 'a' : 'b'};
    }).filter((b) => !b.blocked), [seed, count]);
    return <>{items.map((b, i) => {
      const tex = windowTexture(seed + b.tex, night ? 0.4 : 0.25, night).clone();
      tex.needsUpdate = true; tex.repeat.set(Math.max(1, b.w / 6), Math.max(1, b.h / 12));
      return (
        <mesh key={i} position={[b.x, b.h / 2, b.z]} castShadow receiveShadow>
          <boxGeometry args={[b.w, b.h, b.d]} />
          <meshStandardMaterial map={tex} color={night ? '#ffffff' : ['#f3e3c9', '#d9b8a0', '#c9d6e3', '#e8d7b8', '#b9c7c9', '#efe6da', '#d4a58a'][i % 7]} emissiveMap={night ? tex : undefined} emissive={night ? '#ffffff' : '#000000'} emissiveIntensity={night ? 0.9 : 0} roughness={0.8} />
        </mesh>
      );
    })}</>;
  };

export const SkyDome: React.FC<{top: string; horizon: string; bottom?: string}> = ({top, horizon, bottom = '#2a2a33'}) => {
  const mat = useMemo(() => new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: {top: {value: new THREE.Color(top)}, horizon: {value: new THREE.Color(horizon)}, bottom: {value: new THREE.Color(bottom)}},
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader: 'uniform vec3 top; uniform vec3 horizon; uniform vec3 bottom; varying vec3 vP; void main(){ float h=vP.y; vec3 c = h>0.0 ? mix(horizon, top, pow(h,0.55)) : mix(horizon, bottom, pow(-h,0.4)); gl_FragColor=vec4(c,1.0);}',
  }), [top, horizon, bottom]);
  return <mesh material={mat}><sphereGeometry args={[900, 32, 16]} /></mesh>;
};

export const Sun: React.FC<{position: [number, number, number]; color: string; size?: number}> = ({position, color, size = 30}) => {
  const tex = useMemo(() => {
    const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d')!;
    const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, '#ffffff'); gr.addColorStop(0.15, color); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256); const t = new THREE.CanvasTexture(c); return t;
  }, [color]);
  return <sprite position={position} scale={[size, size, 1]}><spriteMaterial map={tex} transparent depthWrite={false} toneMapped={false} blending={THREE.AdditiveBlending} /></sprite>;
};

// elevated highway running along the Z axis (or X when rotated)
export const Skyway: React.FC<{length?: number; width?: number; height?: number; build?: number; position?: [number, number, number]; rotY?: number}> =
  ({length = 400, width = 18, height = 9, build = 1, position = [0, 0, 0], rotY = 0}) => {
    const L = length * build;
    return (
      <group position={position} rotation={[0, rotY, 0]}>
        <mesh position={[0, height, -L / 2]} castShadow receiveShadow><boxGeometry args={[width, 1.4, L]} /><meshStandardMaterial color="#8d939b" roughness={0.85} /></mesh>
        <mesh position={[0, height + 0.71, -L / 2]} receiveShadow><boxGeometry args={[width - 0.6, 0.02, L]} /><meshStandardMaterial color="#4b4f56" roughness={0.9} /></mesh>
        {[-1, 1].map((s) => <mesh key={s} position={[s * (width / 2 - 0.2), height + 1.3, -L / 2]} castShadow><boxGeometry args={[0.4, 1.2, L]} /><meshStandardMaterial color="#b9bec5" roughness={0.7} /></mesh>)}
        {[...Array(Math.floor(L / 24))].map((_, i) => (
          <group key={i} position={[0, 0, -12 - i * 24]}>
            <mesh position={[0, height / 2, 0]} castShadow receiveShadow><boxGeometry args={[3, height, 2.4]} /><meshStandardMaterial color="#a2a7ae" roughness={0.85} /></mesh>
            <mesh position={[0, height - 0.6, 0]} castShadow><boxGeometry args={[width * 0.8, 1.2, 2.6]} /><meshStandardMaterial color="#979ca3" roughness={0.85} /></mesh>
          </group>
        ))}
        {[...Array(Math.floor(L / 6))].map((_, i) => [-width / 6, width / 6].map((x) => (
          <mesh key={i + '-' + x} position={[x, height + 0.73, -3 - i * 6]}><boxGeometry args={[0.18, 0.01, 2.6]} /><meshBasicMaterial color="#eeeeee" /></mesh>
        )))}
      </group>
    );
  };

export const Ground: React.FC<{color?: string; size?: number}> = ({color = '#5b5e63', size = 1200}) => (
  <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow><planeGeometry args={[size, size]} /><meshStandardMaterial color={color} roughness={1} /></mesh>
);

// dense jammed traffic on a deck: lanes along Z
export const Jam: React.FC<{y: number; lanes: number[]; z0: number; z1: number; seed: string; brake?: boolean; crawl?: number}> =
  ({y, lanes, z0, z1, seed, brake = true, crawl = 0}) => {
    const t = useTime();
    const cars: React.ReactNode[] = [];
    lanes.forEach((x, li) => {
      for (let z = z0, k = 0; z > z1; k++) {
        const gap = 5.2 + random(seed + li + '-' + k) * 1.6;
        cars.push(<Car key={li + '-' + k} position={[x, y, z + Math.sin(t * 0.8 + k) * 0.05 + crawl * t]} seed={li * 100 + k + seed.length} brake={brake && random(seed + 'b' + li + k) > 0.2} />);
        z -= gap;
      }
    });
    return <>{cars}</>;
  };
