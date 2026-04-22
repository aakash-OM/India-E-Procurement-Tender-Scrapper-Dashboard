/**
 * Three.js Particle Network Background
 * Animated 3D particle cloud with connecting lines
 */
(function () {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
  camera.position.z = 500;

  // ── Particle config ───────────────────────────────────────────
  const COUNT       = 180;
  const SPREAD      = 700;
  const CONNECT_DIST = 120;
  const SPEED       = 0.18;

  // Particle positions and velocities
  const positions = new Float32Array(COUNT * 3);
  const velocities = [];

  for (let i = 0; i < COUNT; i++) {
    positions[i * 3]     = (Math.random() - 0.5) * SPREAD;
    positions[i * 3 + 1] = (Math.random() - 0.5) * SPREAD;
    positions[i * 3 + 2] = (Math.random() - 0.5) * SPREAD * 0.4;
    velocities.push({
      x: (Math.random() - 0.5) * SPEED,
      y: (Math.random() - 0.5) * SPEED,
      z: (Math.random() - 0.5) * SPEED * 0.3,
    });
  }

  // Particles geometry
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  const pMat = new THREE.PointsMaterial({
    color: 0x00d4ff,
    size: 2.5,
    transparent: true,
    opacity: 0.7,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const points = new THREE.Points(pGeo, pMat);
  scene.add(points);

  // Line segments geometry (dynamic)
  const MAX_LINES = COUNT * COUNT;
  const linePositions = new Float32Array(MAX_LINES * 6);
  const lineColors    = new Float32Array(MAX_LINES * 6);

  const lGeo = new THREE.BufferGeometry();
  lGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
  lGeo.setAttribute('color',    new THREE.BufferAttribute(lineColors,    3));

  const lMat = new THREE.LineSegmentsMaterial({
    vertexColors: true,
    transparent: true,
    opacity: 0.25,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const lineSegs = new THREE.LineSegments(lGeo, lMat);
  scene.add(lineSegs);

  // Mouse parallax
  const mouse = { x: 0, y: 0 };
  document.addEventListener('mousemove', e => {
    mouse.x = (e.clientX / window.innerWidth  - 0.5) * 2;
    mouse.y = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  // Resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Color helpers
  const cCyan   = new THREE.Color(0x00d4ff);
  const cPurple = new THREE.Color(0x7b2fff);
  const cBlue   = new THREE.Color(0x1a3a6b);

  // ── Animation loop ────────────────────────────────────────────
  let frame = 0;
  function animate() {
    requestAnimationFrame(animate);
    frame++;

    // Move particles
    for (let i = 0; i < COUNT; i++) {
      positions[i * 3]     += velocities[i].x;
      positions[i * 3 + 1] += velocities[i].y;
      positions[i * 3 + 2] += velocities[i].z;

      // Bounce off bounds
      const half = SPREAD / 2;
      if (Math.abs(positions[i * 3])     > half) velocities[i].x *= -1;
      if (Math.abs(positions[i * 3 + 1]) > half) velocities[i].y *= -1;
      if (Math.abs(positions[i * 3 + 2]) > SPREAD * 0.2) velocities[i].z *= -1;
    }
    pGeo.attributes.position.needsUpdate = true;

    // Build connection lines
    let lineIdx = 0;
    for (let i = 0; i < COUNT; i++) {
      for (let j = i + 1; j < COUNT; j++) {
        const dx = positions[i * 3]     - positions[j * 3];
        const dy = positions[i * 3 + 1] - positions[j * 3 + 1];
        const dz = positions[i * 3 + 2] - positions[j * 3 + 2];
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        if (dist < CONNECT_DIST) {
          const alpha = 1 - dist / CONNECT_DIST;
          const col = cCyan.clone().lerp(cPurple, dist / CONNECT_DIST);

          linePositions[lineIdx * 6]     = positions[i * 3];
          linePositions[lineIdx * 6 + 1] = positions[i * 3 + 1];
          linePositions[lineIdx * 6 + 2] = positions[i * 3 + 2];
          linePositions[lineIdx * 6 + 3] = positions[j * 3];
          linePositions[lineIdx * 6 + 4] = positions[j * 3 + 1];
          linePositions[lineIdx * 6 + 5] = positions[j * 3 + 2];

          lineColors[lineIdx * 6]     = col.r * alpha;
          lineColors[lineIdx * 6 + 1] = col.g * alpha;
          lineColors[lineIdx * 6 + 2] = col.b * alpha;
          lineColors[lineIdx * 6 + 3] = col.r * alpha;
          lineColors[lineIdx * 6 + 4] = col.g * alpha;
          lineColors[lineIdx * 6 + 5] = col.b * alpha;

          lineIdx++;
          if (lineIdx >= MAX_LINES) break;
        }
      }
      if (lineIdx >= MAX_LINES) break;
    }

    lGeo.setDrawRange(0, lineIdx * 2);
    lGeo.attributes.position.needsUpdate = true;
    lGeo.attributes.color.needsUpdate    = true;

    // Camera parallax
    camera.position.x += (mouse.x * 60 - camera.position.x) * 0.03;
    camera.position.y += (-mouse.y * 40 - camera.position.y) * 0.03;
    camera.lookAt(0, 0, 0);

    // Slow rotation
    scene.rotation.y = frame * 0.0003;

    renderer.render(scene, camera);
  }

  animate();
})();
