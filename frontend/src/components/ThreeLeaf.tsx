import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export const ThreeLeaf: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = container.clientWidth || 300;
    const height = container.clientHeight || 300;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.IcosahedronGeometry(1.5, 3);
    const material = new THREE.MeshPhongMaterial({
      color: 0x19D3AE,
      wireframe: true,
      transparent: true,
      opacity: 0.65,
      emissive: 0x19D3AE,
      emissiveIntensity: 0.4
    });
    const leaf = new THREE.Mesh(geometry, material);
    scene.add(leaf);

    const ringGeo = new THREE.TorusGeometry(2, 0.02, 16, 100);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x55E6C1, transparent: true, opacity: 0.8 });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2;
    scene.add(ring);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x19D3AE, 2, 10);
    pointLight.position.set(2, 3, 4);
    scene.add(pointLight);

    camera.position.z = 4.5;

    let time = 0;
    let animId: number;
    function animate() {
      animId = requestAnimationFrame(animate);
      time += 0.015;
      leaf.rotation.y += 0.005;
      leaf.rotation.x += 0.003;
      leaf.scale.setScalar(1 + Math.sin(time * 2) * 0.04);
      ring.position.y = Math.sin(time) * 1.4;
      ring.material.opacity = 0.5 + Math.cos(time) * 0.3;
      renderer.render(scene, camera);
    }
    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  return <div ref={containerRef} className="w-full h-full min-h-[300px]" />;
};
