/**
 * Hologram Particles — 全息粒子漂浮背景
 * 轻量级 Canvas 粒子系统，性能友好
 * 适中密度，不干扰内容阅读
 */
(function () {
  const canvas = document.getElementById("particle-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let width, height;
  let particles = [];
  let animationId;
  let mouseX = -1000;
  let mouseY = -1000;

  const CONFIG = {
    count: 45, // 粒子数量（适中）
    minSize: 1,
    maxSize: 3,
    minSpeed: 0.15,
    maxSpeed: 0.5,
    connectionDistance: 120, // 连线距离
    connectionOpacity: 0.15,
    colors: ["rgba(139, 92, 246, ", "rgba(6, 182, 212, ", "rgba(236, 72, 153, "],
    mouseRadius: 150, // 鼠标影响半径
  };

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  function createParticles() {
    particles = [];
    const count = Math.min(
      CONFIG.count,
      Math.floor((width * height) / 25000)
    );
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * CONFIG.maxSpeed * 2,
        vy: (Math.random() - 0.5) * CONFIG.maxSpeed * 2,
        size: CONFIG.minSize + Math.random() * (CONFIG.maxSize - CONFIG.minSize),
        colorIdx: Math.floor(Math.random() * CONFIG.colors.length),
        alpha: 0.3 + Math.random() * 0.5,
        pulse: Math.random() * Math.PI * 2, // 呼吸动画相位
        pulseSpeed: 0.005 + Math.random() * 0.01,
      });
    }
  }

  function drawParticle(p) {
    // 呼吸效果
    p.pulse += p.pulseSpeed;
    const pulseAlpha = p.alpha * (0.7 + 0.3 * Math.sin(p.pulse));

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = CONFIG.colors[p.colorIdx] + pulseAlpha + ")";
    ctx.fill();

    // 微光效果（大粒子才有）
    if (p.size > 2) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * 2.5, 0, Math.PI * 2);
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 2.5);
      gradient.addColorStop(0, CONFIG.colors[p.colorIdx] + pulseAlpha * 0.3 + ")");
      gradient.addColorStop(1, CONFIG.colors[p.colorIdx] + "0)");
      ctx.fillStyle = gradient;
      ctx.fill();
    }
  }

  function drawConnections() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONFIG.connectionDistance) {
          const opacity =
            (1 - dist / CONFIG.connectionDistance) * CONFIG.connectionOpacity;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(139, 92, 246, ${opacity})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function updateParticles() {
    for (const p of particles) {
      // 鼠标互动：轻微排斥
      const dx = p.x - mouseX;
      const dy = p.y - mouseY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < CONFIG.mouseRadius) {
        const force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius * 0.5;
        p.vx += (dx / dist) * force * 0.1;
        p.vy += (dy / dist) * force * 0.1;
      }

      // 速度衰减（回到正常速度）
      p.vx *= 0.99;
      p.vy *= 0.99;

      // 限制最大速度
      const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (speed > CONFIG.maxSpeed) {
        p.vx = (p.vx / speed) * CONFIG.maxSpeed;
        p.vy = (p.vy / speed) * CONFIG.maxSpeed;
      }
      // 限制最小速度
      if (speed < CONFIG.minSpeed) {
        p.vx = (p.vx / speed) * CONFIG.minSpeed;
        p.vy = (p.vy / speed) * CONFIG.minSpeed;
      }

      p.x += p.vx;
      p.y += p.vy;

      // 边界环绕
      if (p.x < -10) p.x = width + 10;
      if (p.x > width + 10) p.x = -10;
      if (p.y < -10) p.y = height + 10;
      if (p.y > height + 10) p.y = -10;
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    updateParticles();
    drawConnections();
    for (const p of particles) {
      drawParticle(p);
    }
    animationId = requestAnimationFrame(animate);
  }

  // 鼠标追踪
  function handleMouseMove(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
  }

  function handleMouseLeave() {
    mouseX = -1000;
    mouseY = -1000;
  }

  // 减少动画：尊重系统设置
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  if (prefersReducedMotion) {
    canvas.style.display = "none";
    return;
  }

  // 初始化
  resize();
  createParticles();
  animate();

  window.addEventListener("resize", () => {
    resize();
    createParticles();
  });

  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("mouseleave", handleMouseLeave);

  // 页面不可见时暂停动画（省电）
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(animationId);
    } else {
      animate();
    }
  });
})();
