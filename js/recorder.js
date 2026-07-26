// ===== VOICE RECORDER — V74 Clinical Calibration Engine =====
// Phase 1: 1.5s silence → captures exact room noise floor
// Phase 2: 4s voice recording → uses calibrated noise profile
document.addEventListener('DOMContentLoaded', function () {
    const recordBtn = document.getElementById('recordBtn');
    if (!recordBtn) return;

    const recordRing = document.getElementById('recordRing');
    const recordHint = document.getElementById('recordHint');
    const recordTimer = document.getElementById('recordTimer');
    const timerDisplay = document.getElementById('timerDisplay');
    const liveWaveform = document.getElementById('liveWaveform');
    const playbackArea = document.getElementById('playbackArea');
    const recordedAudio = document.getElementById('recordedAudio');
    const reRecordBtn = document.getElementById('reRecordBtn');
    const recordFileInput = document.getElementById('recordFileInput');
    const analyzeRecordBtn = document.getElementById('analyzeRecordBtn');
    const micSvg = recordBtn.querySelector('.mic-svg');
    const stopSvg = recordBtn.querySelector('.stop-svg');

    let timerInterval = null;
    let seconds = 0;
    let audioContext = null;
    let analyser = null;
    let waveformAnimId = null;
    let stream = null;

    const bars = liveWaveform ? Array.from(liveWaveform.querySelectorAll('.lw-bar')) : [];

    function formatTime(s) {
        return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    }

    function startWaveformAnimation(analyserNode) {
        const dataArray = new Uint8Array(analyserNode.frequencyBinCount);
        function draw() {
            waveformAnimId = requestAnimationFrame(draw);
            analyserNode.getByteFrequencyData(dataArray);
            bars.forEach(function (bar, i) {
                const idx = Math.floor((i / bars.length) * dataArray.length * 0.6);
                const val = dataArray[idx] / 255;
                bar.style.height = Math.max(4, val * 44) + 'px';
                bar.style.opacity = 0.4 + val * 0.6;
            });
        }
        draw();
    }

    function stopWaveformAnimation() {
        if (waveformAnimId) { cancelAnimationFrame(waveformAnimId); waveformAnimId = null; }
        bars.forEach(function (bar) { bar.style.height = '6px'; bar.style.opacity = '0.4'; });
    }

    function resetUI() {
        micSvg.style.display = 'block';
        stopSvg.style.display = 'none';
        recordBtn.classList.remove('recording');
        if (recordRing) recordRing.classList.remove('recording');
        if (recordHint) { recordHint.textContent = 'Click to start recording'; recordHint.style.color = ''; recordHint.style.display = 'block'; }
        if (recordTimer) recordTimer.style.display = 'none';
        timerDisplay && (timerDisplay.textContent = '0:00');
        seconds = 0;
        clearInterval(timerInterval);
        stopWaveformAnimation();
    }

    let isRecording = false;
    let recordingBuffers = [];   // Phase 2: actual voice
    let calibrationBuffers = []; // Phase 1: room noise
    let recorderNode = null;
    let source = null;
    let hwSampleRate = 44100;
    let phase = 'idle'; // 'calibrating' | 'recording' | 'done'

    const CALIBRATION_MS = 1500; // 1.5s silence for noise floor
    const VOICE_MS = 4000;       // 4s voice recording

    function finalizeRecording() {
        if (!isRecording) return;
        isRecording = false;
        phase = 'done';

        clearInterval(timerInterval);
        stopWaveformAnimation();
        if (recorderNode) recorderNode.disconnect();
        if (source) source.disconnect();
        if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
        if (audioContext) { audioContext.close(); audioContext = null; }

        // ── Combine: [calibration silence] + [voice] into one WAV ──
        // Backend reads first 1.5s as noise floor, rest as voice signal
        const allBuffers = [...calibrationBuffers, ...recordingBuffers];
        const totalLength = allBuffers.reduce((acc, b) => acc + b.length, 0);
        const merged = new Float32Array(totalLength);
        let offset = 0;
        for (const b of allBuffers) { merged.set(b, offset); offset += b.length; }

        const wavBlob = createWavBlob(merged, hwSampleRate || 44100);
        const url = URL.createObjectURL(wavBlob);
        if (recordedAudio) recordedAudio.src = url;
        if (playbackArea) playbackArea.style.display = 'block';
        if (analyzeRecordBtn) analyzeRecordBtn.disabled = false;

        const file = new File([wavBlob], 'recording.wav', { type: 'audio/wav' });
        const dt = new DataTransfer();
        dt.items.add(file);
        if (recordFileInput) recordFileInput.files = dt.files;

        resetUI();
        if (recordHint) {
            recordHint.textContent = '✅ Calibrated recording complete! Ready for analysis.';
            recordHint.style.color = '#2DCE89';
        }
    }

    recordBtn.addEventListener('click', async function () {
        if (isRecording) { finalizeRecording(); return; }

        if (!window.isSecureContext) {
            alert('Microphone access requires http://localhost:5050');
            return;
        }

        // ── Request raw mic stream (no browser processing) ──
        stream = await navigator.mediaDevices.getUserMedia({
            audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false },
            video: false
        });

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        if (audioContext.state === 'suspended') await audioContext.resume();
        hwSampleRate = audioContext.sampleRate;

        analyser = audioContext.createAnalyser();
        analyser.fftSize = 64;
        source = audioContext.createMediaStreamSource(stream);
        recorderNode = audioContext.createScriptProcessor(4096, 1, 1);
        recordingBuffers = [];
        calibrationBuffers = [];
        isRecording = true;
        phase = 'calibrating';

        source.connect(analyser);
        source.connect(recorderNode);
        recorderNode.connect(audioContext.destination);

        // Route PCM samples to correct phase buffer
        recorderNode.onaudioprocess = function (e) {
            if (!isRecording) return;
            const chunk = new Float32Array(e.inputBuffer.getChannelData(0));
            if (phase === 'calibrating') calibrationBuffers.push(chunk);
            else if (phase === 'recording') recordingBuffers.push(chunk);
        };

        // ── PHASE 1: Room Noise Calibration (1.5 seconds) ──
        micSvg.style.display = 'none';
        stopSvg.style.display = 'block';
        recordBtn.classList.add('recording');
        if (recordRing) recordRing.classList.add('recording');
        if (recordHint) {
            recordHint.style.display = 'block';
            recordHint.style.color = '#f5a623';
            recordHint.textContent = '🔇 Stay silent... calibrating your microphone (1.5s)';
        }
        if (recordTimer) recordTimer.style.display = 'none';

        await new Promise(r => setTimeout(r, CALIBRATION_MS));

        // ── PHASE 2: Voice Recording (4 seconds, auto-stops) ──
        phase = 'recording';
        if (recordHint) {
            recordHint.textContent = '🎤 Now say "Ahhh" and hold steady...';
            recordHint.style.color = '#2DCE89';
        }
        if (recordTimer) recordTimer.style.display = 'flex';
        seconds = 0;
        if (timerDisplay) timerDisplay.textContent = '0:00';
        timerInterval = setInterval(() => {
            seconds++;
            if (timerDisplay) timerDisplay.textContent = formatTime(seconds);
        }, 1000);

        startWaveformAnimation(analyser);

        // Auto-finalize after 4 seconds
        await new Promise(r => setTimeout(r, VOICE_MS));
        finalizeRecording();
    });

    // ── WAV Encoder: 16-bit PCM ──
    function createWavBlob(samples, sr) {
        const blockAlign = 2;
        const byteRate = sr * blockAlign;
        const dataSize = samples.length * blockAlign;
        const buffer = new ArrayBuffer(44 + dataSize);
        const view = new DataView(buffer);
        const writeStr = (o, s) => { for (let i = 0; i < s.length; i++) view.setUint8(o + i, s.charCodeAt(i)); };
        writeStr(0, 'RIFF'); view.setUint32(4, 36 + dataSize, true); writeStr(8, 'WAVE');
        writeStr(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
        view.setUint16(22, 1, true); view.setUint32(24, sr, true); view.setUint32(28, byteRate, true);
        view.setUint16(32, blockAlign, true); view.setUint16(34, 16, true);
        writeStr(36, 'data'); view.setUint32(40, dataSize, true);
        for (let i = 0; i < samples.length; i++) {
            const s = Math.max(-1, Math.min(1, samples[i]));
            view.setInt16(44 + i * 2, s < 0 ? s * 32768 : s * 32767, true);
        }
        return new Blob([buffer], { type: 'audio/wav' });
    }

    if (reRecordBtn) {
        reRecordBtn.addEventListener('click', function () {
            if (playbackArea) playbackArea.style.display = 'none';
            if (recordedAudio) recordedAudio.src = '';
            if (analyzeRecordBtn) analyzeRecordBtn.disabled = true;
            if (recordFileInput) recordFileInput.value = '';
            if (recordHint) { recordHint.textContent = 'Click to start recording'; recordHint.style.color = ''; recordHint.style.display = 'block'; }
        });
    }
});
