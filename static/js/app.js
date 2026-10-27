/**
 * REWIND - Main Application Controller
 */
(function() {
    'use strict';

    // State
    let uploadedFile = null;
    let fileId = null;
    let renderer = null;
    let damageType = 'auto';

    // Elements
    const screenUpload = document.getElementById('screen-upload');
    const screenAnalysis = document.getElementById('screen-analysis');
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const damageTypeSelector = document.getElementById('damage-type-selector');
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnBack = document.getElementById('btn-back');
    const btnPlay = document.getElementById('btn-play');
    const btnReset = document.getElementById('btn-reset');
    const timelineSlider = document.getElementById('timeline-slider');
    const timeDisplay = document.getElementById('time-display');
    const analysisImage = document.getElementById('analysis-image');
    const overlayCanvas = document.getElementById('overlay-canvas');

    // Upload handling
    uploadZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    async function handleFile(file) {
        if (!file) return;

        const ext = file.name.split('.').pop().toLowerCase();
        if (!['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
            alert('Please upload a JPG, PNG, or WebP image.');
            return;
        }

        uploadedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewContainer.style.display = 'block';
            damageTypeSelector.style.display = 'block';
        };
        reader.readAsDataURL(file);

        // Upload to server
        const formData = new FormData();
        formData.append('file', file);

        try {
            const resp = await fetch('/api/upload', { method: 'POST', body: formData });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.detail || 'Upload failed');
            fileId = data.file_id;
        } catch (err) {
            console.error('Upload error:', err);
            alert('Upload failed: ' + err.message);
        }
    }

    // Damage type selection
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            damageType = btn.dataset.type;
        });
    });

    // Analyze button
    btnAnalyze.addEventListener('click', startReconstruction);

    async function startReconstruction() {
        if (!fileId) {
            alert('Please upload an image first.');
            return;
        }

        // Switch to analysis screen
        screenUpload.classList.remove('active');
        screenAnalysis.classList.add('active');

        // Set the image
        analysisImage.src = previewImage.src;
        analysisImage.onload = () => {
            renderer = new RewindRenderer(overlayCanvas, analysisImage);
        };

        // Reset pipeline stages UI
        document.querySelectorAll('.stage').forEach(s => {
            s.className = 'stage';
            s.querySelector('.stage-status').textContent = 'waiting';
        });

        // Reset panels
        document.getElementById('narrative-panel').style.display = 'none';
        document.getElementById('params-panel').style.display = 'none';
        document.getElementById('timeline-panel').style.display = 'none';
        document.getElementById('recon-image-panel').style.display = 'none';

        // Build form data
        const formData = new FormData();
        formData.append('file_id', fileId);
        formData.append('damage_type', damageType);
        formData.append('deep_reasoning', document.getElementById('deep-reasoning').checked);

        // Start SSE stream
        try {
            const response = await fetch('/api/reconstruct', {
                method: 'POST',
                body: formData,
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Parse SSE events from buffer
                const events = buffer.split('\n\n');
                buffer = events.pop(); // Keep incomplete event in buffer

                for (const eventStr of events) {
                    if (!eventStr.trim()) continue;

                    const lines = eventStr.split('\n');
                    let eventType = '';
                    let eventData = '';

                    for (const line of lines) {
                        if (line.startsWith('event: ')) {
                            eventType = line.slice(7);
                        } else if (line.startsWith('data: ')) {
                            eventData = line.slice(6);
                        }
                    }

                    if (eventType && eventData) {
                        try {
                            handleEvent(eventType, JSON.parse(eventData));
                        } catch (e) {
                            console.error('Event parse error:', e);
                        }
                    }
                }
            }
        } catch (err) {
            console.error('Reconstruction error:', err);
        }
    }

    function handleEvent(type, data) {
        if (type === 'stage') {
            updateStage(data);
        } else if (type === 'complete') {
            onComplete(data);
        } else if (type === 'error') {
            console.error('Pipeline error:', data.message);
        }
    }

    function updateStage(data) {
        const stageEl = document.querySelector(`.stage[data-stage="${data.stage}"]`);
        if (!stageEl) return;

        stageEl.className = `stage ${data.status}`;
        stageEl.querySelector('.stage-status').textContent = data.status;

        if (data.status === 'complete' && data.data) {
            // Process stage-specific data
            if (data.stage === 'segmentation' && data.data.segments && renderer) {
                renderer.setSegments(data.data.segments);
            }

            if (data.stage === 'analysis' && data.data) {
                showAnalysis(data.data);
            }

            if (data.stage === 'simulation' && data.data.frames && renderer) {
                renderer.setFrames(data.data.frames);
            }

            if (data.stage === 'visualization' && data.data.image_url) {
                showReconImage(data.data.image_url);
            }
        }
    }

    function showAnalysis(analysis) {
        // Narrative
        const narrative = analysis.reconstruction?.narrative;
        if (narrative) {
            document.getElementById('narrative-panel').style.display = 'block';
            document.getElementById('narrative-content').textContent = narrative;
        }

        // Parameters
        const params = analysis.parameters?.estimated_values;
        const units = analysis.parameters?.units || {};
        if (params && Object.keys(params).length > 0) {
            document.getElementById('params-panel').style.display = 'block';
            const grid = document.getElementById('params-content');
            grid.innerHTML = '';

            for (const [key, value] of Object.entries(params)) {
                const card = document.createElement('div');
                card.className = 'param-card';
                const label = key.replace(/_/g, ' ');
                const unit = units[key] || '';
                card.innerHTML = `
                    <div class="param-label">${label}</div>
                    <div class="param-value">${formatValue(value)}<span class="param-unit">${unit}</span></div>
                `;
                grid.appendChild(card);
            }
        }

        // Timeline
        const timeline = analysis.reconstruction?.timeline;
        if (timeline && timeline.length > 0) {
            document.getElementById('timeline-panel').style.display = 'block';
            const list = document.getElementById('timeline-content');
            list.innerHTML = '';

            timeline.forEach((event, i) => {
                const item = document.createElement('div');
                item.className = 'timeline-item';
                const desc = typeof event === 'string' ? event : event.description || event.event || JSON.stringify(event);
                item.innerHTML = `
                    <span class="tl-time">T+${i}</span>
                    <span class="tl-desc">${desc}</span>
                `;
                list.appendChild(item);
            });
        }
    }

    function showReconImage(imageUrl) {
        if (!imageUrl) return;
        document.getElementById('recon-image-panel').style.display = 'block';
        document.getElementById('recon-image').src = imageUrl;
    }

    function onComplete(data) {
        // Update badge
        const badge = document.querySelector('.analysis-badge');
        if (badge) {
            badge.textContent = 'COMPLETE';
            badge.classList.add('done');
        }

        // Show processing time
        if (data.processing_time_ms) {
            const secs = (data.processing_time_ms / 1000).toFixed(1);
            const badge2 = document.querySelector('.analysis-badge');
            if (badge2) badge2.textContent = `DONE in ${secs}s`;
        }
    }

    function formatValue(v) {
        if (typeof v === 'number') {
            return v % 1 === 0 ? v.toString() : v.toFixed(2);
        }
        return String(v);
    }

    // Playback controls
    btnPlay.addEventListener('click', () => {
        if (!renderer) return;
        if (renderer.playing) {
            renderer.pause();
            btnPlay.textContent = '▶';
        } else {
            renderer.play();
            btnPlay.textContent = '⏸';
        }
    });

    btnReset.addEventListener('click', () => {
        if (!renderer) return;
        renderer.reset();
        btnPlay.textContent = '▶';
        timelineSlider.value = 0;
        timeDisplay.textContent = 't = 0.000s';
    });

    timelineSlider.addEventListener('input', (e) => {
        if (!renderer) return;
        renderer.seekTo(e.target.value / 100);
        timeDisplay.textContent = `t = ${renderer.getCurrentTime().toFixed(3)}s`;
    });

    // Update slider during playback
    setInterval(() => {
        if (renderer && renderer.playing) {
            timelineSlider.value = renderer.getProgress() * 100;
            timeDisplay.textContent = `t = ${renderer.getCurrentTime().toFixed(3)}s`;
        }
    }, 50);

    // Back button
    btnBack.addEventListener('click', () => {
        if (renderer) {
            renderer.pause();
            renderer = null;
        }
        screenAnalysis.classList.remove('active');
        screenUpload.classList.add('active');
    });

})();
