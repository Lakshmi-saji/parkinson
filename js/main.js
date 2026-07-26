// ===== MAIN JS =====
document.addEventListener('DOMContentLoaded', function () {

  // --- User dropdown ---
  const userBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');
  if (userBtn && userDropdown) {
    userBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      const open = userDropdown.classList.toggle('open');
      userBtn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function () {
      userDropdown.classList.remove('open');
      userBtn.setAttribute('aria-expanded', 'false');
    });
  }

  // --- Mobile hamburger ---
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function () {
      const open = navLinks.classList.toggle('mobile-open');
      hamburger.setAttribute('aria-expanded', String(open));
    });
  }

  // --- Toggle password visibility ---
  document.querySelectorAll('.toggle-password').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
      }
    });
  });

  // --- Tab switch (dashboard) ---
  document.querySelectorAll('.tab-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const tab = btn.getAttribute('data-tab');
      document.querySelectorAll('.tab-btn').forEach(function (b) {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      document.querySelectorAll('.tab-panel').forEach(function (p) {
        p.style.display = 'none';
      });
      const panel = document.getElementById(tab + 'Panel');
      if (panel) panel.style.display = 'block';
    });
  });

  // --- File upload drag-and-drop ---
  const dropZone = document.getElementById('dropZone');
  const audioFileInput = document.getElementById('audioFileInput');
  const filePreview = document.getElementById('filePreview');
  const fileName = document.getElementById('fileName');
  const fileSize = document.getElementById('fileSize');
  const uploadedAudio = document.getElementById('uploadedAudio');
  const analyzeUploadBtn = document.getElementById('analyzeUploadBtn');

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function handleFile(file) {
    if (!file) return;
    const url = URL.createObjectURL(file);
    if (fileName) fileName.textContent = file.name;
    if (fileSize) fileSize.textContent = formatBytes(file.size);
    if (uploadedAudio) uploadedAudio.src = url;
    if (filePreview) filePreview.style.display = 'block';
    if (analyzeUploadBtn) analyzeUploadBtn.disabled = false;
  }

  if (audioFileInput) {
    audioFileInput.addEventListener('change', function () {
      if (this.files && this.files[0]) handleFile(this.files[0]);
    });
  }

  if (dropZone) {
    dropZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', function () {
      dropZone.classList.remove('dragover');
    });
    dropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file && audioFileInput) {
        const dt = new DataTransfer();
        dt.items.add(file);
        audioFileInput.files = dt.files;
        handleFile(file);
      }
    });
  }

  // --- Processing overlay on form submit ---
  const uploadForm = document.getElementById('uploadForm');
  const recordForm = document.getElementById('recordForm');
  const overlay = document.getElementById('processingOverlay');
  const processingStep = document.getElementById('processingStep');
  const steps = ['ps1','ps2','ps3','ps4'];
  const stepTexts = ['Preprocessing audio...','Extracting acoustic features...','Running ML inference...','Generating PDF report...'];

  function showProcessing(form) {
    if (!overlay) return;
    overlay.style.display = 'flex';
    let i = 0;
    function nextStep() {
      if (i > 0) {
        const prev = document.getElementById(steps[i-1]);
        if (prev) { prev.classList.remove('active'); prev.classList.add('done'); }
      }
      if (i < steps.length) {
        const cur = document.getElementById(steps[i]);
        if (cur) cur.classList.add('active');
        if (processingStep) processingStep.textContent = stepTexts[i];
        i++;
        setTimeout(nextStep, 1200);
      }
    }
    nextStep();
  }

  if (uploadForm) {
    uploadForm.addEventListener('submit', function (e) {
      const btn = document.getElementById('analyzeUploadBtn');
      if (btn && btn.disabled) { e.preventDefault(); return; }
      showProcessing(this);
    });
  }
  if (recordForm) {
    recordForm.addEventListener('submit', function (e) {
      const btn = document.getElementById('analyzeRecordBtn');
      if (btn && btn.disabled) { e.preventDefault(); return; }
      showProcessing(this);
    });
  }

  // --- Auto-close flash messages ---
  document.querySelectorAll('.flash').forEach(function (flash) {
    setTimeout(function () {
      flash.style.opacity = '0';
      flash.style.transition = 'opacity 0.5s';
      setTimeout(function () { flash.remove(); }, 500);
    }, 5000);
  });
});
