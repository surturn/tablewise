import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';

const FloatingShape = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.2;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3;
    }
  });

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <mesh ref={meshRef} scale={1.5}>
        <torusKnotGeometry args={[1, 0.3, 128, 32]} />
        <MeshDistortMaterial color="#D6A354" attach="material" distort={0.4} speed={2} roughness={0.2} metalness={0.8} />
      </mesh>
    </Float>
  );
};

const HeroScene: React.FC = () => {
  const { canRender3D } = useDeviceCapability();

  if (!canRender3D) {
    return (
      <div
        className="absolute inset-0 -z-10 bg-[#121212] bg-cover bg-center"
        style={{ backgroundImage: "linear-gradient(135deg, rgba(18,18,18,0.86), rgba(68,44,18,0.7)), url('/grand-hotel-hero.webp')" }}
        aria-label="GrandPlatform hotel hero image"
      />
    );
  }

  return (
    <div className="absolute inset-0 -z-10 bg-[#121212]">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }} dpr={[1, 1.5]}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} color="#ffffff" />
        <directionalLight position={[-10, -10, -5]} intensity={0.5} color="#D6A354" />
        <FloatingShape />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
      </Canvas>
    </div>
  );
};

export default HeroScene;
