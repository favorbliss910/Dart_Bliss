import {ThreeCanvas} from '@remotion/three';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import React from 'react';
export const Bench: React.FC = () => {
  const f = useCurrentFrame();
  const {width, height} = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height} shadows camera={{position: [0, 4, 12], fov: 40}} style={{background: '#87b5e0'}}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} intensity={2} castShadow shadow-mapSize={[2048, 2048]} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow><planeGeometry args={[100, 100]} /><meshStandardMaterial color="#777" /></mesh>
      {[...Array(120)].map((_, i) => <mesh key={i} position={[(i % 12) * 2 - 12, 0.5, -Math.floor(i / 12) * 3 + Math.sin(f / 20 + i)]} castShadow>
        <boxGeometry args={[1.6, 1, 2.4]} /><meshStandardMaterial color={`hsl(${i * 37 % 360},60%,50%)`} /></mesh>)}
    </ThreeCanvas>
  );
};
