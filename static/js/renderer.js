/**
 * REWIND Canvas Overlay Renderer
 * Draws physics simulation frames on top of the damage image.
 */
class RewindRenderer {
    constructor(canvas, image) {
        this.canvas = canvas;
        this.image = image;
        this.ctx = canvas.getContext('2d');
        this.frames = [];
        this.currentFrame = 0;
        this.playing = false;
        this.animationId = null;
        this.fps = 30;
        this.lastFrameTime = 0;
        this.segments = [];

        this._resize();
        window.addEventListener('resize', () => this._resize());
    }

    _resize() {
        const rect = this.image.getBoundingClientRect();
        this.canvas.width = rect.width * (window.devicePixelRatio || 1);
        this.canvas.height = rect.height * (window.devicePixelRatio || 1);
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        this.ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
        this.width = rect.width;
        this.height = rect.height;
        if (this.frames.length > 0) {
            this.renderFrame(this.currentFrame);
        }
    }

    setFrames(frames) {
        this.frames = frames;
        this.currentFrame = 0;
        if (frames.length > 0) {
            this.renderFrame(0);
        }
    }

    setSegments(segments) {
        this.segments = segments;
    }

    play() {
        if (this.frames.length === 0) return;
        this.playing = true;
        this.lastFrameTime = performance.now();
        this._animate();
    }

    pause() {
        this.playing = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    reset() {
        this.pause();
        this.currentFrame = 0;
        if (this.frames.length > 0) {
            this.renderFrame(0);
        }
    }

    seekTo(progress) {
        // progress is 0-1
        const frameIndex = Math.floor(progress * (this.frames.length - 1));
        this.currentFrame = Math.max(0, Math.min(frameIndex, this.frames.length - 1));
        this.renderFrame(this.currentFrame);
    }

    _animate() {
        if (!this.playing) return;

        const now = performance.now();
        const elapsed = now - this.lastFrameTime;
        const frameInterval = 1000 / this.fps;

        if (elapsed >= frameInterval) {
            this.currentFrame++;
            if (this.currentFrame >= this.frames.length) {
                this.currentFrame = 0; // loop
            }
            this.renderFrame(this.currentFrame);
            this.lastFrameTime = now - (elapsed % frameInterval);
        }

        this.animationId = requestAnimationFrame(() => this._animate());
    }

    renderFrame(index) {
        const frame = this.frames[index];
        if (!frame) return;

        const ctx = this.ctx;
        const w = this.width;
        const h = this.height;

        // Clear
        ctx.clearRect(0, 0, w, h);

        // Draw segmentation regions first (underneath everything)
        this._drawSegments(ctx, w, h);

        // Draw highlights
        if (frame.highlights) {
            for (const hl of frame.highlights) {
                this._drawHighlight(ctx, hl, w, h);
            }
        }

        // Draw objects
        if (frame.objects) {
            for (const obj of frame.objects) {
                this._drawObject(ctx, obj, w, h);
            }
        }

        // Draw vectors
        if (frame.vectors) {
            for (const vec of frame.vectors) {
                this._drawVector(ctx, vec, w, h);
            }
        }

        // Draw annotations
        if (frame.annotations) {
            for (const ann of frame.annotations) {
                this._drawAnnotation(ctx, ann, w, h);
            }
        }

        // Draw frame time
        ctx.font = `600 12px 'JetBrains Mono', monospace`;
        ctx.fillStyle = 'rgba(0, 212, 255, 0.8)';
        ctx.textAlign = 'right';
        ctx.fillText(`t = ${frame.time.toFixed(3)}s`, w - 12, h - 12);

        return frame.time;
    }

    _drawSegments(ctx, w, h) {
        for (const seg of this.segments) {
            if (!seg.box) continue;
            const box = seg.box;
            const x = box.x1 * w;
            const y = box.y1 * h;
            const bw = (box.x2 - box.x1) * w;
            const bh = (box.y2 - box.y1) * h;

            ctx.strokeStyle = 'rgba(255, 107, 53, 0.6)';
            ctx.lineWidth = 2;
            ctx.setLineDash([6, 4]);
            ctx.strokeRect(x, y, bw, bh);
            ctx.setLineDash([]);

            // Fill with transparent overlay
            ctx.fillStyle = 'rgba(255, 107, 53, 0.08)';
            ctx.fillRect(x, y, bw, bh);
        }
    }

    _drawHighlight(ctx, hl, w, h) {
        if (hl.type === 'radial') {
            const cx = hl.center.x * w;
            const cy = hl.center.y * h;
            const r = hl.radius * Math.max(w, h);

            const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
            gradient.addColorStop(0, hl.color || 'rgba(255, 0, 64, 0.3)');
            gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.fill();
        } else if (hl.type === 'flow_path') {
            const sx = hl.start.x * w;
            const sy = hl.start.y * h;
            const ex = hl.end.x * w;
            const ey = hl.end.y * h;
            const pathW = (hl.width || 0.05) * w;

            ctx.strokeStyle = hl.color || 'rgba(64, 164, 255, 0.15)';
            ctx.lineWidth = pathW;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.quadraticCurveTo((sx + ex) / 2, (sy + ey) / 2 + 20, ex, ey);
            ctx.stroke();
        } else if (hl.type === 'point') {
            const px = hl.position.x * w;
            const py = hl.position.y * h;

            ctx.fillStyle = hl.color || '#ff0040';
            ctx.beginPath();
            ctx.arc(px, py, 6, 0, Math.PI * 2);
            ctx.fill();

            if (hl.label) {
                ctx.font = `600 11px 'JetBrains Mono', monospace`;
                ctx.fillStyle = hl.color || '#ff0040';
                ctx.textAlign = 'left';
                ctx.fillText(hl.label, px + 10, py + 4);
            }
        }
    }

    _drawObject(ctx, obj, w, h) {
        if (obj.type === 'projectile') {
            const x = obj.x * w;
            const y = obj.y * h;
            const r = (obj.radius || 0.015) * Math.max(w, h);

            // Glow
            ctx.shadowColor = obj.color || '#ff6b35';
            ctx.shadowBlur = 15;

            ctx.fillStyle = obj.color || '#ff6b35';
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fill();

            ctx.shadowBlur = 0;
        } else if (obj.type === 'impact_flash') {
            const x = obj.x * w;
            const y = obj.y * h;
            const r = (obj.radius || 0.05) * Math.max(w, h);

            const gradient = ctx.createRadialGradient(x, y, 0, x, y, r);
            gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
            gradient.addColorStop(0.5, 'rgba(255, 200, 50, 0.5)');
            gradient.addColorStop(1, 'rgba(255, 0, 64, 0)');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fill();
        } else if (obj.type === 'crack') {
            const sx = obj.start.x * w;
            const sy = obj.start.y * h;
            const ex = obj.end.x * w;
            const ey = obj.end.y * h;

            ctx.strokeStyle = obj.color || '#ff6b35';
            ctx.lineWidth = obj.width || 2;
            ctx.shadowColor = obj.color || '#ff6b35';
            ctx.shadowBlur = 5;

            ctx.beginPath();
            ctx.moveTo(sx, sy);
            // Add slight randomness for organic crack look
            const mx = (sx + ex) / 2 + (Math.random() - 0.5) * 10;
            const my = (sy + ey) / 2 + (Math.random() - 0.5) * 10;
            ctx.quadraticCurveTo(mx, my, ex, ey);
            ctx.stroke();

            ctx.shadowBlur = 0;
        } else if (obj.type === 'rectangle') {
            const x = obj.x * w;
            const y = obj.y * h;
            const rw = obj.width * w;
            const rh = obj.height * h;
            const rotation = (obj.rotation || 0) * Math.PI / 180;

            ctx.save();

            if (obj.pivot) {
                const px = obj.pivot.x * w;
                const py = obj.pivot.y * h;
                ctx.translate(px, py);
                ctx.rotate(rotation);
                ctx.translate(-px, -py);
            } else {
                const cx = x + rw / 2;
                const cy = y + rh / 2;
                ctx.translate(cx, cy);
                ctx.rotate(rotation);
                ctx.translate(-cx, -cy);
            }

            ctx.fillStyle = obj.color || '#4a9eff';
            ctx.globalAlpha = 0.6;
            ctx.fillRect(x, y, rw, rh);
            ctx.globalAlpha = 1;

            ctx.strokeStyle = obj.color || '#4a9eff';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, rw, rh);

            ctx.restore();
        } else if (obj.type === 'particle') {
            const x = obj.x * w;
            const y = obj.y * h;
            const r = (obj.radius || 0.005) * Math.max(w, h);

            ctx.fillStyle = obj.color || 'rgba(64, 164, 255, 0.5)';
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fill();
        } else if (obj.type === 'source_marker') {
            const x = obj.x * w;
            const y = obj.y * h;
            const r = (obj.radius || 0.02) * Math.max(w, h);

            // Pulsing ring
            ctx.strokeStyle = obj.color || '#ff0040';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.stroke();

            ctx.fillStyle = obj.color || '#ff0040';
            ctx.beginPath();
            ctx.arc(x, y, r * 0.4, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    _drawVector(ctx, vec, w, h) {
        const ox = vec.origin.x * w;
        const oy = vec.origin.y * h;
        const dx = vec.direction.x;
        const dy = vec.direction.y;
        const mag = Math.min(vec.magnitude || 1, 100);
        const scale = 0.8; // vector display scale
        const len = mag * scale;

        const ex = ox + dx * len;
        const ey = oy + dy * len;

        // Arrow line
        ctx.strokeStyle = vec.color || '#00d4ff';
        ctx.lineWidth = 2;
        ctx.shadowColor = vec.color || '#00d4ff';
        ctx.shadowBlur = 8;

        ctx.beginPath();
        ctx.moveTo(ox, oy);
        ctx.lineTo(ex, ey);
        ctx.stroke();

        // Arrowhead
        const angle = Math.atan2(ey - oy, ex - ox);
        const headLen = 10;

        ctx.fillStyle = vec.color || '#00d4ff';
        ctx.beginPath();
        ctx.moveTo(ex, ey);
        ctx.lineTo(
            ex - headLen * Math.cos(angle - Math.PI / 6),
            ey - headLen * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(
            ex - headLen * Math.cos(angle + Math.PI / 6),
            ey - headLen * Math.sin(angle + Math.PI / 6)
        );
        ctx.closePath();
        ctx.fill();

        ctx.shadowBlur = 0;

        // Label
        if (vec.label) {
            ctx.font = `600 11px 'JetBrains Mono', monospace`;
            ctx.fillStyle = vec.color || '#00d4ff';
            ctx.textAlign = 'left';
            ctx.fillText(vec.label, (ox + ex) / 2 + 8, (oy + ey) / 2 - 8);
        }
    }

    _drawAnnotation(ctx, ann, w, h) {
        const x = ann.position.x * w;
        const y = ann.position.y * h;
        const size = ann.size === 'large' ? 16 : 12;

        // Background pill
        ctx.font = `600 ${size}px 'JetBrains Mono', monospace`;
        const metrics = ctx.measureText(ann.text);
        const padding = 6;

        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        const pillW = metrics.width + padding * 2;
        const pillH = size + padding * 2;
        const pillX = x - padding;
        const pillY = y - size - padding + 2;

        ctx.beginPath();
        ctx.roundRect(pillX, pillY, pillW, pillH, 4);
        ctx.fill();

        // Text
        ctx.fillStyle = ann.color || '#00d4ff';
        ctx.textAlign = 'left';
        ctx.fillText(ann.text, x, y);
    }

    getProgress() {
        if (this.frames.length === 0) return 0;
        return this.currentFrame / (this.frames.length - 1);
    }

    getCurrentTime() {
        if (this.frames.length === 0 || !this.frames[this.currentFrame]) return 0;
        return this.frames[this.currentFrame].time;
    }
}
