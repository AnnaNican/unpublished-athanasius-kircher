
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Torus, Cylinder, Stars, Environment, Icosahedron, Octahedron, Cone } from '@react-three/drei';
import * as THREE from 'three';

// --- ARMILLARY SPHERE COMPONENTS ---

const Ring = ({ args, rotationSpeed, color = "#C5A059" }: { args: [number, number, number, number], rotationSpeed: [number, number, number], color?: string }) => {
  const ref = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (ref.current) {
       const t = state.clock.getElapsedTime();
       ref.current.rotation.x = t * rotationSpeed[0];
       ref.current.rotation.y = t * rotationSpeed[1];
       ref.current.rotation.z = t * rotationSpeed[2];
    }
  });

  return (
    <Torus ref={ref} args={args}>
      <meshStandardMaterial 
        color={color} 
        metalness={0.8} 
        roughness={0.2} 
        emissive={color}
        emissiveIntensity={0.1}
      />
    </Torus>
  );
}

const CentralSun = () => {
    const ref = useRef<THREE.Mesh>(null);
    useFrame((state) => {
        if(ref.current) {
            ref.current.rotation.y += 0.005;
        }
    })
    return (
        <group ref={ref}>
            <Icosahedron args={[1, 0]}>
                <meshStandardMaterial color="#C5A059" wireframe emissive="#C5A059" emissiveIntensity={0.5} />
            </Icosahedron>
            <Octahedron args={[1.5, 0]}>
                <meshStandardMaterial color="#F9F8F4" wireframe transparent opacity={0.3} />
            </Octahedron>
        </group>
    )
}

export const ArmillaryScene: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 opacity-80 pointer-events-none grayscale-[30%]">
      <Canvas camera={{ position: [0, 0, 12], fov: 35 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#fff" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#C5A059" />
        
        <Float speed={1} rotationIntensity={0.2} floatIntensity={0.2}>
          <group rotation={[0.5, 0.5, 0]}>
            <CentralSun />
            {/* The Spheres of the Heavens */}
            <Ring args={[3, 0.05, 16, 100]} rotationSpeed={[0.1, 0.05, 0]} />
            <Ring args={[3.2, 0.08, 16, 100]} rotationSpeed={[-0.05, 0.1, 0.02]} />
            <Ring args={[4.5, 0.15, 16, 100]} rotationSpeed={[0.02, -0.05, 0.05]} color="#8B7355" />
            <Ring args={[4.6, 0.05, 16, 100]} rotationSpeed={[0.02, -0.05, 0.05]} />
            
            {/* The Prime Mobile */}
            <Ring args={[6, 0.02, 16, 100]} rotationSpeed={[0.01, 0.01, 0.01]} color="#F9F8F4" />
          </group>
        </Float>

        <Environment preset="sunset" />
        <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={0.5} />
      </Canvas>
    </div>
  );
};

// --- PYRAMID RESONATOR COMPONENTS ---

const ResonatingPyramid = () => {
    const groupRef = useRef<THREE.Group>(null);
    const coreRef = useRef<THREE.Mesh>(null);

    useFrame((state) => {
        const t = state.clock.getElapsedTime();
        if (groupRef.current) {
            groupRef.current.rotation.y = t * 0.05;
        }
        if (coreRef.current) {
            coreRef.current.position.y = Math.sin(t * 1.5) * 0.5;
            coreRef.current.rotation.x = t * 0.5;
            coreRef.current.rotation.z = t * 0.3;
            // Pulse scale
            const scale = 1 + Math.sin(t * 3) * 0.1;
            coreRef.current.scale.set(scale, scale, scale);
        }
    });

    return (
        <group ref={groupRef}>
            {/* The Great Pyramid Wireframe */}
            <Cone args={[3, 4, 4]} position={[0, 0, 0]}>
                <meshStandardMaterial 
                    color="#C5A059" 
                    wireframe 
                    transparent 
                    opacity={0.3} 
                    emissive="#C5A059" 
                    emissiveIntensity={0.2}
                />
            </Cone>

            {/* Internal Chamber */}
            <mesh ref={coreRef} position={[0, 0, 0]}>
                <Octahedron args={[0.5, 0]}>
                    <meshStandardMaterial color="#fff" emissive="#fff" emissiveIntensity={2} toneMapped={false} />
                </Octahedron>
            </mesh>

            {/* Base */}
            <Cylinder args={[3.5, 3.5, 0.1, 4]} position={[0, -2, 0]} rotation={[0, Math.PI/4, 0]}>
                 <meshStandardMaterial color="#222" roughness={0.8} />
            </Cylinder>
        </group>
    );
};

export const PyramidScene: React.FC = () => {
  return (
    <div className="w-full h-full absolute inset-0">
      <Canvas camera={{ position: [0, 2, 7], fov: 45 }}>
        <color attach="background" args={['#000']} />
        <fog attach="fog" args={['#000', 5, 15]} />
        
        <ambientLight intensity={0.2} />
        <pointLight position={[5, 5, 5]} intensity={1} color="#C5A059" />
        <pointLight position={[-5, 5, -5]} intensity={1} color="#444" />
        
        <Float speed={1} rotationIntensity={0.1} floatIntensity={0.2}>
            <ResonatingPyramid />
        </Float>

        {/* Particles */}
        <Stars radius={20} depth={10} count={500} factor={2} saturation={0} speed={1} />
      </Canvas>
    </div>
  );
}
