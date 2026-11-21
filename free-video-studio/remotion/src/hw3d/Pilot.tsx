// 3D pilot (0 – 29.5 s of "Highway"): reference style — real 3D sets, big centred bean characters.
import React, {useMemo} from 'react';
import * as THREE from 'three';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import {Outlines, RoundedBox, Text} from '@react-three/drei';
import {Bloom, DepthOfField, EffectComposer, Vignette} from '@react-three/postprocessing';
import {AbsoluteFill, random, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
const FONT_URL = staticFile('fonts/Poppins-ExtraBold.ttf');
import tl from '../../../projects/highway/timeline.json';
import {Bean, Car, City, clamp01, Detonator, Ground, Jam, lerp, Notebook, ramp, SkyDome, Skyway, smooth, Stopwatch, Sun, useTime} from './kit';

const B = tl.beats as Record<string, number>;
const END = tl.scenes.find((s) => s.id === 'engineer')!.end;

// ---------------------------------------------------------------- camera rig
type V3 = [number, number, number];
const Rig: React.FC<{from: V3; to: V3; lookFrom: V3; lookTo: V3; dur: number; fov?: number; roll?: number}> = ({from, to, lookFrom, lookTo, dur, fov = 35, roll = 0}) => {
  const {camera} = useThree();
  const t = useTime();
  const p = smooth(t / dur);
  const pos = from.map((v, i) => lerp(v, to[i], p)) as V3;
  const look = lookFrom.map((v, i) => lerp(v, lookTo[i], p)) as V3;
  camera.position.set(...pos);
  (camera as THREE.PerspectiveCamera).fov = fov;
  camera.up.set(Math.sin(roll), Math.cos(roll), 0);
  camera.lookAt(...look);
  camera.updateProjectionMatrix();
  return null;
};

const Light: React.FC<{preset: 'dusk' | 'day' | 'sunrise' | 'night'}> = ({preset}) => {
  const P = {
    dusk: {sky: '#ffb38a', ground: '#3a2a4a', hemi: 0.7, sun: '#ffb070', sunI: 2.6, pos: [-40, 18, -60] as V3, amb: 0.25},
    day: {sky: '#cfe8ff', ground: '#6b6b5a', hemi: 0.9, sun: '#fff4e0', sunI: 2.8, pos: [40, 60, 30] as V3, amb: 0.3},
    sunrise: {sky: '#ffcf9e', ground: '#4a3a3a', hemi: 0.8, sun: '#ffc078', sunI: 2.8, pos: [-50, 14, -40] as V3, amb: 0.3},
    night: {sky: '#4a5a8a', ground: '#1a1a22', hemi: 0.5, sun: '#9fb4ff', sunI: 1.2, pos: [20, 40, 10] as V3, amb: 0.2},
  }[preset];
  return (
    <>
      <hemisphereLight args={[P.sky, P.ground, P.hemi]} />
      <ambientLight intensity={P.amb} />
      <directionalLight position={P.pos} intensity={P.sunI} color={P.sun} castShadow shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-40} shadow-camera-right={40} shadow-camera-top={40} shadow-camera-bottom={-40} shadow-camera-far={300} shadow-bias={-0.0004} />
    </>
  );
};

const Post: React.FC<{focus: V3; bokeh?: number; bloom?: number}> = ({focus, bokeh = 3, bloom = 0.9}) => (
  <EffectComposer multisampling={0}>
    <DepthOfField target={focus} focalLength={0.03} bokehScale={bokeh} height={720} />
    <Bloom intensity={bloom} luminanceThreshold={0.75} luminanceSmoothing={0.2} mipmapBlur />
    <Vignette eskil={false} offset={0.25} darkness={0.75} />
  </EffectComposer>
);

const Stage: React.FC<{children: React.ReactNode; fog?: string; near?: number; far?: number}> = ({children, fog, near = 60, far = 420}) => {
  const {width, height} = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height} shadows gl={{antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.25, outputColorSpace: THREE.SRGBColorSpace}}
      camera={{fov: 35, near: 0.1, far: 2000}}>
      {fog && <fog attach="fog" args={[fog, near, far]} />}
      {children}
    </ThreeCanvas>
  );
};

// ---------------------------------------------------------------- set pieces
const Pillar: React.FC<{position: V3; t: number}> = ({position, t}) => (
  <group position={position}>
    <mesh position={[0, 5, 0]} castShadow receiveShadow><boxGeometry args={[2.6, 10, 2.6]} /><meshStandardMaterial color="#a6a39d" roughness={0.9} /></mesh>
    {[...Array(5)].map((_, i) => (
      <mesh key={i} position={[-0.8 + i * 0.4, 2.4, 1.42]} castShadow><cylinderGeometry args={[0.18, 0.18, 1.6, 16]} /><meshStandardMaterial color="#d2302a" roughness={0.5} /><Outlines thickness={0.02} color="#1b1b22" /></mesh>
    ))}
    {[1.9, 2.9].map((y) => <mesh key={y} position={[0, y, 1.42]}><boxGeometry args={[2.2, 0.14, 0.42]} /><meshStandardMaterial color="#222" /></mesh>)}
    <mesh position={[0, 2.5, 1.68]}><boxGeometry args={[0.7, 0.4, 0.1]} /><meshStandardMaterial color="#111" /></mesh>
    <Text font={FONT_URL} position={[0, 2.5, 1.74]} fontSize={0.26} color={Math.floor(t * 4) % 2 ? '#ff3030' : '#ff9090'} anchorX="center" anchorY="middle">00:05</Text>
    {/* fuse sparks */}
    {[...Array(14)].map((_, i) => {
      const life = (t * 2.4 + random('sp' + i)) % 1, a = random('sa' + i) * Math.PI * 2;
      return <mesh key={'s' + i} position={[-0.8 + Math.cos(a) * life * 0.7, 3.4 + life * 0.6 - life * life * 0.9, 1.5 + Math.sin(a) * life * 0.5]}>
        <sphereGeometry args={[0.05 * (1 - life), 6, 6]} /><meshBasicMaterial color="#ffd36b" toneMapped={false} /></mesh>;
    })}
    <pointLight position={[-0.8, 3.5, 2]} color="#ffb040" intensity={6 + Math.sin(t * 30) * 2} distance={6} />
  </group>
);

const Sign: React.FC<{position: V3; drop: number}> = ({position, drop}) => (
  <group position={[position[0], position[1] + (1 - drop) * 14, position[2]]}>
    {[-9, 9].map((x) => <mesh key={x} position={[x, -4, 0]} castShadow><boxGeometry args={[0.5, 8, 0.5]} /><meshStandardMaterial color="#9aa0a7" metalness={0.6} roughness={0.4} /></mesh>)}
    <mesh position={[0, 0, 0]} castShadow><boxGeometry args={[19, 0.5, 0.5]} /><meshStandardMaterial color="#9aa0a7" metalness={0.6} /></mesh>
    <RoundedBox args={[11, 4.2, 0.3]} radius={0.3} position={[0, 0.6, 0.3]} castShadow><meshStandardMaterial color="#1a7f45" roughness={0.5} /></RoundedBox>
    <Text font={FONT_URL} position={[0, 1.6, 0.5]} fontSize={0.8} color="#ffffff" anchorX="center">SKYWAY  ➜</Text>
    <Text font={FONT_URL} position={[0, 0.4, 0.5]} fontSize={1.3} color="#ffffff" anchorX="center"  >DOWNTOWN</Text>
    <Text font={FONT_URL} position={[0, -0.8, 0.5]} fontSize={0.8} color="#e8ffe8" anchorX="center">5 MIN</Text>
  </group>
);

const Ambulance: React.FC<{position: V3; t: number}> = ({position, t}) => {
  const on = Math.floor(t * 6) % 2 === 0;
  return (
    <group position={position}>
      <RoundedBox args={[2.2, 2.3, 5.2]} radius={0.2} position={[0, 1.6, 0]} castShadow><meshStandardMaterial color="#f4f6f8" roughness={0.4} /><Outlines thickness={0.03} color="#1b1b22" /></RoundedBox>
      <mesh position={[0, 1.4, 0]}><boxGeometry args={[2.24, 0.35, 5.24]} /><meshStandardMaterial color="#d62828" /></mesh>
      {[-0.55, 0.55].map((x) => <mesh key={x} position={[x, 2.85, 1.6]}><boxGeometry args={[0.8, 0.22, 0.4]} /><meshBasicMaterial color={(x < 0) === on ? (x < 0 ? '#ff2020' : '#3040ff') : '#330808'} toneMapped={false} /></mesh>)}
      <pointLight position={[-0.6, 3.4, 1.6]} color="#ff2020" intensity={on ? 40 : 0} distance={16} />
      <pointLight position={[0.6, 3.4, 1.6]} color="#3040ff" intensity={on ? 0 : 40} distance={16} />
      {[[-1.1, -1.8], [1.1, -1.8], [-1.1, 1.8], [1.1, 1.8]].map(([x, z], i) => <mesh key={i} position={[x, 0.42, z]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.42, 0.42, 0.3, 18]} /><meshStandardMaterial color="#141414" /></mesh>)}
    </group>
  );
};

const Bridge: React.FC<{y: number}> = ({y}) => (
  <group position={[0, y, 0]}>
    <mesh position={[0, -0.4, 0]} castShadow receiveShadow><boxGeometry args={[120, 0.8, 4]} /><meshStandardMaterial color="#8c9097" roughness={0.8} /></mesh>
    {[-1.9, 1.9].map((z) => <group key={z}>
      <mesh position={[0, 1.1, z]} castShadow><boxGeometry args={[120, 0.12, 0.12]} /><meshStandardMaterial color="#3e434a" metalness={0.5} /></mesh>
      {[...Array(60)].map((_, i) => <mesh key={i} position={[-60 + i * 2, 0.55, z]} castShadow><boxGeometry args={[0.08, 1.1, 0.08]} /><meshStandardMaterial color="#3e434a" /></mesh>)}
    </group>)}
  </group>
);

// ---------------------------------------------------------------- shots
const shots: {from: number; to: number; C: React.FC<{d: number}>}[] = [];
const shot = (from: number, to: number, C: React.FC<{d: number}>) => shots.push({from, to, C});

// A — over-the-shoulder: engineer looks up at the jammed skyway at dusk
shot(0, B.blowup, ({d}) => (
  <Stage fog="#c8798a" near={40} far={330}>
    <Rig from={[6.5, 14.6, 15]} to={[5.6, 14.2, 13.2]} lookFrom={[-12, 10.5, -22]} lookTo={[-13, 11, -24]} dur={d} fov={44} />
    <Light preset="dusk" /><SkyDome top="#1f1846" horizon="#ff9a76" /><Sun position={[-120, 40, -400]} color="#ffbe78" size={160} />
    <Ground color="#3d3a44" />
    <Skyway position={[-12, 0, 30]} length={420} />
    <Jam y={9.7} lanes={[-18, -14.2, -9.8, -5.8]} z0={26} z1={-260} seed="A" />
    <City seed="A" night area={[-140, 140, -380, -60]} count={70} clear={[[-12, -60, 14]]} />
    <City seed="A2" night area={[18, 120, -120, 0]} count={14} minH={10} maxH={30} clear={[[5, 13, 14]]} />
    <mesh position={[3, 5, 6]} castShadow receiveShadow><boxGeometry args={[14, 10, 14]} /><meshStandardMaterial color="#5a4a5a" roughness={0.9} /></mesh>
    <Bean position={[2.0, 10, 7.6]} rotY={Math.PI + 0.55} scale={1.1} vest hat="hard" glasses face="smirk" />
    <Post focus={[-9, 9, -20]} bokeh={2.5} />
  </Stage>
));

// B — hero close-up: engineer with the detonator, dynamite on the pillar behind
shot(B.blowup, tl.scenes[1].start, ({d}) => {
  const t = useTime();
  return (
    <Stage fog="#2b1a24" near={14} far={120}>
      <Rig from={[0.6, 3.3, 7.4]} to={[0.2, 3.25, 5.6]} lookFrom={[0, 2.9, 0]} lookTo={[0, 3.0, 0]} dur={d} fov={38} roll={0.05} />
      <Light preset="night" /><SkyDome top="#120c26" horizon="#5a2440" />
      <Ground color="#2a2830" />
      <Pillar position={[2.2, 0, -4.5]} t={t} />
      <Skyway position={[2.2, 0, 40]} length={200} />
      <Jam y={9.7} lanes={[-4.5, -0.5, 3.5, 7.5]} z0={36} z1={-120} seed="B" />
      <City seed="B" night area={[-80, 80, -220, -40]} count={40} />
      <Bean position={[-0.3, 0, 0]} rotY={0.12} scale={1} vest hat="hard" glasses face="smirk" sweat={t > 1.6}
        armR={1.25 + Math.sin(t * 3) * 0.04} rightHand={<group rotation={[-1.2, 0, 0]} scale={0.9}><Detonator press={ramp(t, d - 0.4, d - 0.1)} /></group>} />
      <pointLight position={[1.5, 3.2, 3]} color="#ff9f40" intensity={22} distance={10} />
      <Post focus={[-0.3, 3, 0]} bokeh={4.5} bloom={1.2} />
    </Stage>
  );
});

// C — aerial: the skyway slices through downtown as it gets built
shot(tl.scenes[1].start, B.shortcut1, ({d}) => {
  const t = useTime();
  return (
    <Stage fog="#cfe2f2" near={260} far={1100}>
      <Rig from={[60, 110, 90]} to={[38, 70, 50]} lookFrom={[0, 6, -80]} lookTo={[0, 8, -60]} dur={d} fov={45} />
      <Light preset="day" /><SkyDome top="#3d84d0" horizon="#d9ecfa" bottom="#9aa6b2" /><Sun position={[300, 260, -500]} color="#fff3c4" size={140} />
      <Ground color="#7c8187" />
      <City seed="C" area={[-200, 200, -340, 120]} count={120} avoidX={16} minH={10} maxH={60} clear={[[70, 70, 45], [55, 50, 40], [40, 30, 35]]} />
      <Skyway position={[0, 0, 140]} length={480} build={0.12 + 0.88 * ramp(t, 0.1, 2.6)} />
      {t > 2.6 && <Jam y={9.7} lanes={[-6, -2, 2, 6]} z0={130} z1={-330} seed="C" brake={false} crawl={-14} />}
      <Post focus={[0, 8, -40]} bokeh={1.2} bloom={0.4} />
    </Stage>
  );
});

// D — on the deck: the great shortcut sign drops in, traffic flies past
shot(B.shortcut1, tl.scenes[2].start, ({d}) => {
  const t = useTime();
  return (
    <Stage fog="#cfe2f2" near={160} far={800}>
      <Rig from={[3, 11.6, 12]} to={[3.2, 12.2, 6]} lookFrom={[0, 15, -40]} lookTo={[0, 15.5, -40]} dur={d} fov={48} />
      <Light preset="day" /><SkyDome top="#3d84d0" horizon="#d9ecfa" /><Sun position={[300, 260, -500]} color="#fff3c4" size={140} />
      <Ground color="#7c8187" />
      <City seed="D" area={[-180, 180, -420, 40]} count={90} avoidX={22} minH={10} maxH={70} />
      <Skyway position={[0, 0, 60]} length={480} />
      {[[-6, 0], [-2, 7], [2, 3], [6, 11]].map(([x, o], li) => [...Array(7)].map((_, k) => (
        <Car key={li + '-' + k} position={[x, 9.7, -200 + ((t * 38 + o + k * 30) % 220)]} seed={li * 10 + k} brake={false} lights rotY={0} />
      )))}
      <Sign position={[0, 19.5, -26]} drop={spring({frame: Math.round(t * 60) - 6, fps: 60, config: {damping: 9, stiffness: 120}})} />
      <Post focus={[0, 19, -26]} bokeh={1.6} bloom={0.5} />
    </Stage>
  );
});

// E — stuck driver close-up (45 minutes)
shot(tl.scenes[2].start, B.ambulance, ({d}) => {
  const t = useTime();
  return (
    <Stage fog="#e8b07a" near={30} far={260}>
      <Rig from={[-0.2, 2.25, 5.6]} to={[-0.3, 2.2, 4.5]} lookFrom={[-0.4, 1.95, 0]} lookTo={[-0.4, 2.0, 0]} dur={d} fov={30} />
      <Light preset="sunrise" /><SkyDome top="#e98a52" horizon="#ffe0aa" /><Sun position={[-200, 60, -400]} color="#fff0b0" size={160} />
      <Ground color="#55575c" />
      <Car position={[0, 0, 0]} rotY={0} seed={3} color="#d64545"
        driver={<Bean position={[0, 0, 0]} rotY={0} face="angry" shirt="#3a7bd5" hair="#2a1d14" sweat={t > 1} bounce={Math.abs(Math.sin(t * 14)) * 0.05} />} />
      <Jam y={0} lanes={[-4.3, 4.3]} z0={6} z1={-140} seed="E" />
      <Jam y={0} lanes={[0]} z0={-6} z1={-140} seed="E2" />
      <City seed="E" area={[-140, 140, -380, -60]} count={60} />
      <Post focus={[-0.4, 2.0, 0.1]} bokeh={5} />
    </Stage>
  );
});

// F — ambulance trapped, sirens painting the jam red and blue
shot(B.ambulance, B.pizza, ({d}) => {
  const t = useTime();
  return (
    <Stage fog="#3a2a3a" near={20} far={200}>
      <Rig from={[11, 2.0, 15]} to={[9, 2.2, 12]} lookFrom={[0, 2.2, -1]} lookTo={[0, 2.4, -1]} dur={d} fov={40} roll={-0.05} />
      <Light preset="dusk" /><SkyDome top="#2a1c46" horizon="#e07a6a" />
      <Ground color="#45434a" />
      <Ambulance position={[0, 0, 0]} t={t} />
      <Jam y={0} lanes={[0]} z0={-5.5} z1={-160} seed="F1" />
      <Jam y={0} lanes={[0]} z0={25} z1={5} seed="F0" />
      <Jam y={0} lanes={[-4.4, 4.4]} z0={20} z1={-160} seed="F2" />
      <City seed="F" night area={[-140, 140, -380, -60]} count={60} />
      <Bean position={[4.6, 0, 4]} rotY={-0.8} scale={0.95} face="shock" shirt="#27ae60" sweat />
      <Post focus={[0, 2, 0]} bokeh={3.5} bloom={1.4} />
    </Stage>
  );
});

// G — pizza guy, pizza going cold
shot(B.pizza, B.marriage, ({d}) => {
  const t = useTime();
  return (
    <Stage fog="#9fb4c8" near={10} far={140}>
      <Rig from={[0.4, 2.7, 8.6]} to={[0.3, 2.65, 7.6]} lookFrom={[0, 2.3, 0]} lookTo={[0, 2.35, 0]} dur={d} fov={36} />
      <Light preset="day" /><SkyDome top="#8aa6c2" horizon="#dfe8ef" />
      <Ground color="#5a5d62" />
      <Jam y={0} lanes={[-3.6, 3.6]} z0={-3} z1={-140} seed="G" />
      <Bean position={[0, 0, 0]} scale={1} face="sad" shirt="#d62828" hair="#111" armL={0.9} armR={0.9}
        rightHand={<group position={[-0.5, 0.1, 0.4]}><RoundedBox args={[1.3, 0.18, 1.3]} radius={0.03}><meshStandardMaterial color="#c8955a" /><Outlines thickness={0.02} color="#1b1b22" /></RoundedBox></group>} />
      {[...Array(40)].map((_, i) => <mesh key={i} position={[(random('sx' + i) - 0.5) * 6, 6 - ((t * 0.9 + random('sy' + i) * 6) % 6), (random('sz' + i) - 0.3) * 3]}>
        <sphereGeometry args={[0.04, 6, 6]} /><meshBasicMaterial color="#ffffff" /></mesh>)}
      <Post focus={[0, 2.6, 0]} bokeh={5} />
    </Stage>
  );
});

// H — couple in the left lane, not speaking
shot(B.marriage, tl.scenes[3].start, ({d}) => (
  <Stage fog="#e8b07a" near={20} far={200}>
    <Rig from={[0.3, 2.6, 6.4]} to={[0.2, 2.5, 5.3]} lookFrom={[0, 1.85, 0]} lookTo={[0, 1.9, 0]} dur={d} fov={34} />
    <Light preset="sunrise" /><SkyDome top="#e98a52" horizon="#ffe0aa" />
    <Ground color="#55575c" />
    <group rotation={[0, Math.PI, 0]}>
      <Car position={[0, 0, 0]} seed={7} color="#2c7fb8" />
    </group>
    <Bean position={[0.42, 0.55, 0.15]} rotY={-0.9} scale={0.38} face="angry" shirt="#8e44ad" hair="#6b3a1a" />
    <Bean position={[-0.42, 0.55, 0.15]} rotY={0.7} scale={0.38} face="angry" shirt="#3a7bd5" hair="#2a1d14" />
    <Jam y={0} lanes={[-4.3, 4.3]} z0={6} z1={-140} seed="H" />
    <City seed="H" area={[-140, 140, -380, -60]} count={60} />
    <Post focus={[0, 1.8, 0]} bokeh={5} />
  </Stage>
));

// I — the new engineer walks onto the bridge at sunrise
shot(tl.scenes[3].start, B.bridge, ({d}) => {
  const t = useTime();
  const x = lerp(-6, 0, smooth(t / d));
  return (
    <Stage fog="#f0a37a" near={40} far={320}>
      <Rig from={[x + 1.5, 15.2, 8]} to={[x + 0.6, 15.0, 6.2]} lookFrom={[x, 14.2, 0]} lookTo={[x, 14.3, 0]} dur={d} fov={42} />
      <Light preset="sunrise" /><SkyDome top="#33467a" horizon="#ffb27a" /><Sun position={[-220, 40, -420]} color="#ffd38a" size={220} />
      <Ground color="#4b4d53" />
      <Bridge y={12} />
      <Skyway position={[0, 0, 60]} length={420} height={2} rotY={0} />
      <Jam y={2.7} lanes={[-6, -2, 2, 6]} z0={50} z1={-300} seed="I" />
      <City seed="I" night area={[-160, 160, -420, -80]} count={80} />
      <Bean position={[x, 12, 0]} rotY={0.25} scale={1} vest hat="hard" glasses face="happy" walk={1} />
      <Post focus={[x, 14, 0]} bokeh={3} bloom={0.8} />
    </Stage>
  );
});

// J — on the bridge with a stopwatch and a notebook, timing the city
shot(B.bridge, END, ({d}) => {
  const t = useTime();
  const sw = B.stopwatch - B.bridge;
  const raise = ramp(t, sw - 0.2, sw + 0.3);
  return (
    <Stage fog="#f0a37a" near={30} far={300}>
      <Rig from={[2.6, 14.6, 7.2]} to={[-1.2, 14.4, 6.4]} lookFrom={[0, 13.9, 0]} lookTo={[0, 14.0, 0]} dur={d} fov={38} />
      <Light preset="sunrise" /><SkyDome top="#33467a" horizon="#ffb27a" /><Sun position={[-220, 40, -420]} color="#ffd38a" size={220} />
      <Ground color="#4b4d53" />
      <Bridge y={12} />
      <Skyway position={[0, 0, 60]} length={420} height={2} />
      <Jam y={2.7} lanes={[-6, -2, 2, 6]} z0={50} z1={-300} seed="J" />
      <City seed="J" night area={[-160, 160, -420, -80]} count={80} />
      <Bean position={[0, 12.1, 0]} scale={1} vest hat="hard" glasses face={raise > 0.5 ? 'smirk' : 'happy'}
        armR={lerp(0.3, 1.6, raise)} rightHand={<group rotation={[-1.4, 0, 0]}><Stopwatch t={t} /></group>}
        armL={lerp(0.2, 0.9, raise)} leftHand={<group rotation={[-0.4, 0, 0]}><Notebook /></group>} />
      <Post focus={[0, 14, 0]} bokeh={3.5} bloom={0.8} />
    </Stage>
  );
});

// ---------------------------------------------------------------- 2D overlays + captions
const Overlays: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const pop = (at: number) => (t < at ? 0 : spring({frame: f - Math.round(at * fps), fps, config: {damping: 10, stiffness: 220}}));
  const box: React.CSSProperties = {position: 'absolute', left: 720, transform: 'translate(-50%,-50%)', fontFamily: 'Poppins', fontWeight: 900, color: '#fff', textAlign: 'center'};
  const s2 = tl.scenes[2].start;
  const mins = Math.round(lerp(5, 45, clamp01((t - s2 - 0.2) / 2)));
  return (
    <>
      {t > B.sixlanes && t < B.shortcut1 && <div style={{...box, top: 620, transform: `translate(-50%,-50%) scale(${pop(B.sixlanes)}) rotate(-3deg)`, background: '#1d3557', border: '8px solid #111', borderRadius: 24, padding: '18px 44px', fontSize: 110, boxShadow: '0 16px 0 rgba(0,0,0,.35)'}}>6 LANES</div>}
      {t > s2 && t < B.ambulance && <div style={{...box, top: 420, transform: `translate(-50%,-50%) scale(${pop(s2 + 0.1)})`, background: 'rgba(12,12,16,.85)', border: '8px solid #fff', borderRadius: 40, padding: '30px 70px'}}>
        <div style={{fontSize: 70, opacity: 0.85}}>5 MILES</div><div style={{fontSize: 210, lineHeight: 1, color: mins > 30 ? '#ff4d4d' : '#fff'}}>{mins} MIN</div></div>}
      {t > B.pizza && t < B.marriage && <div style={{...box, top: 380, transform: `translate(-50%,-50%) scale(${pop(B.pizza + 0.05)}) rotate(-6deg)`, fontSize: 170, color: '#9ad8ff', WebkitTextStroke: '16px #0b2a44', paintOrder: 'stroke fill'}}>COLD ❄</div>}
      {t > B.marriage && t < tl.scenes[3].start && <div style={{...box, top: 380, transform: `translate(-50%,-50%) scale(${pop(B.marriage + 0.1)})`, fontSize: 300}}>💔</div>}
    </>
  );
};

const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const words = tl.words as {w: string; t: number; e: number}[];
  let i = -1;
  for (let k = 0; k < words.length; k++) { if (words[k].t <= t) i = k; else break; }
  if (i < 0 || t > words[i].e + 0.5) return null;
  const p = spring({frame: f - Math.round(words[i].t * fps), fps, config: {damping: 12, stiffness: 320, mass: 0.6}});
  return (
    <AbsoluteFill style={{alignItems: 'center', top: 1720}}>
      <div style={{fontFamily: 'Poppins', fontWeight: 800, fontSize: 118, color: '#fff', WebkitTextStroke: '16px #0b0b0b', paintOrder: 'stroke fill',
        textShadow: '0 10px 0 rgba(0,0,0,.4)', transform: `scale(${0.8 + 0.2 * p})`}}>{words[i].w}</div>
    </AbsoluteFill>
  );
};

export const Pilot: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {shots.map(({from, to, C}, i) => (
        <Sequence key={i} from={Math.round(from * fps)} durationInFrames={Math.round((to - from) * fps)}>
          <C d={to - from} />
        </Sequence>
      ))}
      <Overlays />
      <Captions />
    </AbsoluteFill>
  );
};
export const PILOT_FRAMES = Math.round(END * 60);
