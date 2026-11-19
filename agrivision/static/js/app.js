// AgriVision AI — Client Application Script
let currentInspectionData = null;
let activeLayer = 'overlay';
let selectedFile = null;
let currentSampleUrl = '/samples/sample_early_blight.jpg';

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initFarms();
  initSamples();
  initUpload();
  initCamera();
  initSliders();
  initLayerViewer();
  initModals();
  initBatchUpload();
  initWeatherLab();
  loadModelsRegistry();
  loadInspectionHistory();

  // Run initial diagnostic test on default sample
  setTimeout(() => {
    selectPreset('sample-early-blight', '/samples/sample_early_blight.jpg', {
      temperature: 27.5,
      humidity: 82.0,
      rainfall: 3.5,
      stage: 'Fruiting'
    });
  }, 400);
});

// 1. TABS NAVIGATION
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(`tab-${tabId}`);
      if (targetPane) targetPane.classList.add('active');

      if (tabId === 'history') loadInspectionHistory();
      if (tabId === 'farm-health') loadFarmHealth();
      if (tabId === 'models') loadModelsRegistry();

      if (tabId !== 'studio') {
        stopCamera();
        switchInputMode('upload');
      }
    });
  });
}

// 2. FARMS MANAGEMENT
async function initFarms() {
  try {
    const res = await fetch('/api/v1/farms');
    const farms = await res.json();
    const select = document.getElementById('globalFarmSelect');
    select.innerHTML = '';
    farms.forEach(f => {
      const opt = document.createElement('option');
      opt.value = f.farm_id;
      opt.textContent = `${f.name} (${f.crop_type})`;
      select.appendChild(opt);
    });

    select.addEventListener('change', () => {
      loadFarmHealth();
    });
  } catch (err) {
    console.error('Failed to load farms:', err);
  }
}

// 3. SAMPLE PRESET GALLERY
async function initSamples() {
  try {
    const res = await fetch('/api/v1/samples');
    const samples = await res.json();
    const gallery = document.getElementById('presetGallery');
    gallery.innerHTML = '';

    samples.forEach(s => {
      const chip = document.createElement('div');
      chip.className = 'preset-chip';
      chip.id = s.id;
      chip.innerHTML = `
        <img src="${s.image_url}" alt="${s.name}" class="preset-thumb">
        <span class="preset-label" title="${s.name}">${s.name.split('(')[0]}</span>
      `;
      chip.addEventListener('click', () => {
        document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        selectPreset(s.id, s.image_url, s.preset_weather);
      });
      gallery.appendChild(chip);
    });
  } catch (err) {
    console.error('Failed to load samples:', err);
  }
}

async function selectPreset(id, url, weather) {
  stopCamera();
  switchInputMode('upload');
  currentSampleUrl = url;
  selectedFile = null; // Clear file input since using preset
  
  // Set weather sliders if provided
  if (weather) {
    document.getElementById('tempSlider').value = weather.temperature;
    document.getElementById('tempValueDisplay').textContent = `${weather.temperature} °C`;
    document.getElementById('humiditySlider').value = weather.humidity;
    document.getElementById('humidityValueDisplay').textContent = `${weather.humidity} %`;
    document.getElementById('rainSlider').value = weather.rainfall;
    document.getElementById('rainValueDisplay').textContent = `${weather.rainfall} mm`;
    if (weather.stage) document.getElementById('growthStageSelect').value = weather.stage;
  }

  // Update image preview directly
  document.getElementById('activeCanvasImg').src = url;
  document.getElementById('specimenBadge').textContent = 'Preset Loaded';
  document.getElementById('specimenBadge').className = 'badge badge-info';

  // Trigger analysis
  runDiagnosis(url);
}

// 4. UPLOAD & CAMERA HANDLING
let cameraStream = null;
let currentCameraDeviceId = null;
let cameraFacingMode = 'environment'; // Default to rear camera on mobile / normal on PC

function initUpload() {
  const dropzone = document.getElementById('leafDropzone');
  const fileInput = document.getElementById('leafFileInput');

  dropzone.addEventListener('click', (e) => {
    if (e.target.closest('#btnQuickCameraLaunch')) return;
    fileInput.click();
  });

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  });

  document.getElementById('btnRunDiagnosis').addEventListener('click', () => {
    runDiagnosis();
  });

  document.getElementById('btnNasaAutoFetch').addEventListener('click', autoFetchNasaWeather);
}

function handleFile(file) {
  stopCamera();
  switchInputMode('upload');
  selectedFile = file;
  document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
  
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('activeCanvasImg').src = e.target.result;
    document.getElementById('specimenBadge').textContent = file.name;
    document.getElementById('specimenBadge').className = 'badge badge-success';
  };
  reader.readAsDataURL(file);
}

// 4B. LIVE CAMERA INTEGRATION
function initCamera() {
  const btnModeUpload = document.getElementById('btnModeUpload');
  const btnModeCamera = document.getElementById('btnModeCamera');
  const btnQuickLaunch = document.getElementById('btnQuickCameraLaunch');
  const btnCapture = document.getElementById('btnCaptureAndRecognize');
  const btnClose = document.getElementById('btnCloseCamera');
  const btnFlip = document.getElementById('btnFlipCamera');
  const cameraSelect = document.getElementById('cameraSourceSelect');

  if (btnModeUpload) {
    btnModeUpload.addEventListener('click', () => switchInputMode('upload'));
  }
  if (btnModeCamera) {
    btnModeCamera.addEventListener('click', () => switchInputMode('camera'));
  }
  if (btnQuickLaunch) {
    btnQuickLaunch.addEventListener('click', (e) => {
      e.stopPropagation();
      switchInputMode('camera');
    });
  }
  if (btnClose) {
    btnClose.addEventListener('click', () => switchInputMode('upload'));
  }
  if (btnFlip) {
    btnFlip.addEventListener('click', flipCamera);
  }
  if (cameraSelect) {
    cameraSelect.addEventListener('change', (e) => {
      currentCameraDeviceId = e.target.value;
      startCamera(currentCameraDeviceId);
    });
  }
  if (btnCapture) {
    btnCapture.addEventListener('click', captureAndDiagnose);
  }
}

function switchInputMode(mode) {
  const btnModeUpload = document.getElementById('btnModeUpload');
  const btnModeCamera = document.getElementById('btnModeCamera');
  const dropzone = document.getElementById('leafDropzone');
  const cameraSection = document.getElementById('cameraSection');

  if (!btnModeUpload || !btnModeCamera || !dropzone || !cameraSection) return;

  if (mode === 'camera') {
    btnModeCamera.classList.add('active');
    btnModeUpload.classList.remove('active');
    dropzone.classList.add('hidden');
    cameraSection.classList.remove('hidden');
    startCamera(currentCameraDeviceId);
  } else {
    btnModeUpload.classList.add('active');
    btnModeCamera.classList.remove('active');
    cameraSection.classList.add('hidden');
    dropzone.classList.remove('hidden');
    stopCamera();
  }
}

async function startCamera(deviceId = null) {
  const video = document.getElementById('cameraVideo');
  const overlay = document.getElementById('cameraLoadingOverlay');
  const loadingText = document.getElementById('cameraLoadingText');

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Camera API (getUserMedia) is not available or blocked in this browser environment. Please access through http://127.0.0.1:8000 or use the 'Upload File' option.");
    switchInputMode('upload');
    return;
  }

  stopCamera();

  if (overlay) {
    overlay.classList.remove('hidden');
    if (loadingText) loadingText.textContent = "Connecting to camera...";
  }

  try {
    const videoConstraints = {
      width: { ideal: 1280 },
      height: { ideal: 720 }
    };

    if (deviceId) {
      videoConstraints.deviceId = { exact: deviceId };
    } else if (cameraFacingMode) {
      videoConstraints.facingMode = { ideal: cameraFacingMode };
    }

    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: videoConstraints,
      audio: false
    });

    if (video) {
      video.srcObject = cameraStream;
      await video.play();

      const track = cameraStream.getVideoTracks()[0];
      const settings = track.getSettings ? track.getSettings() : {};
      if (settings.facingMode === 'user' || cameraFacingMode === 'user') {
        video.style.transform = 'scaleX(-1)';
      } else {
        video.style.transform = 'none';
      }
    }

    if (overlay) overlay.classList.add('hidden');
    await populateCameraDevices();

  } catch (err) {
    console.warn("Primary camera constraint failed, trying standard fallback:", err);
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      });
      if (video) {
        video.srcObject = cameraStream;
        await video.play();
      }
      if (overlay) overlay.classList.add('hidden');
      await populateCameraDevices();
    } catch (fallbackErr) {
      console.error("Camera access failed:", fallbackErr);
      if (overlay) overlay.classList.add('hidden');
      alert(`Could not start camera: ${fallbackErr.message || fallbackErr.name}. Please ensure camera permissions are allowed in your browser.`);
      switchInputMode('upload');
    }
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => {
      try { track.stop(); } catch (e) {}
    });
    cameraStream = null;
  }
  const video = document.getElementById('cameraVideo');
  if (video) {
    video.srcObject = null;
  }
}

async function populateCameraDevices() {
  if (!navigator.mediaDevices.enumerateDevices) return;
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(d => d.kind === 'videoinput');
    const select = document.getElementById('cameraSourceSelect');
    const flipBtn = document.getElementById('btnFlipCamera');

    if (!select || !flipBtn) return;

    if (videoDevices.length > 1) {
      select.innerHTML = '';
      videoDevices.forEach((dev, idx) => {
        const opt = document.createElement('option');
        opt.value = dev.deviceId;
        opt.textContent = dev.label || `Camera ${idx + 1}`;
        if (currentCameraDeviceId === dev.deviceId) opt.selected = true;
        select.appendChild(opt);
      });
      select.style.display = 'block';
      flipBtn.style.display = 'inline-flex';
    } else {
      select.style.display = 'none';
      flipBtn.style.display = 'none';
    }
  } catch (e) {
    console.warn("Could not enumerate camera devices:", e);
  }
}

function flipCamera() {
  cameraFacingMode = (cameraFacingMode === 'environment') ? 'user' : 'environment';
  currentCameraDeviceId = null;
  startCamera();
}

async function captureAndDiagnose() {
  const video = document.getElementById('cameraVideo');
  const flash = document.getElementById('cameraFlash');
  const canvas = document.getElementById('cameraCanvas');
  const captureBtn = document.getElementById('btnCaptureAndRecognize');

  if (!video || !cameraStream || video.readyState < 2) {
    alert("Camera stream is not ready yet. Please wait a second.");
    return;
  }

  // Trigger snapshot flash
  if (flash) {
    flash.classList.add('flash-active');
    setTimeout(() => flash.classList.remove('flash-active'), 180);
  }

  const width = video.videoWidth || 640;
  const height = video.videoHeight || 480;
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext('2d');
  if (video.style.transform === 'scaleX(-1)') {
    ctx.translate(width, 0);
    ctx.scale(-1, 1);
  }
  ctx.drawImage(video, 0, 0, width, height);

  canvas.toBlob((blob) => {
    if (!blob) {
      alert("Failed to capture snapshot from camera.");
      return;
    }

    const timestamp = Date.now();
    const filename = `camera_specimen_${timestamp}.jpg`;
    selectedFile = new File([blob], filename, { type: 'image/jpeg' });

    // Show preview on main canvas
    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
    document.getElementById('activeCanvasImg').src = dataUrl;

    // Deselect preset chips
    document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));

    // Update specimen badge
    const badge = document.getElementById('specimenBadge');
    badge.textContent = `📷 Live Capture (${width}×${height})`;
    badge.className = 'badge badge-warning';

    // Stop camera feed and return to studio view
    stopCamera();
    switchInputMode('upload');

    // Update button text to reflect retake option
    const quickLaunch = document.getElementById('btnQuickCameraLaunch');
    if (quickLaunch) {
      quickLaunch.innerHTML = '📷 Retake Photo with Live Camera';
    }

    // IMMEDIATELY TRIGGER RECOGNITION PIPELINE
    runDiagnosis();

  }, 'image/jpeg', 0.95);
}

// 5. SLIDERS INTERACTIVITY
function initSliders() {
  const tempSlider = document.getElementById('tempSlider');
  const humSlider = document.getElementById('humiditySlider');
  const rainSlider = document.getElementById('rainSlider');

  tempSlider.addEventListener('input', (e) => {
    document.getElementById('tempValueDisplay').textContent = `${e.target.value} °C`;
  });
  humSlider.addEventListener('input', (e) => {
    document.getElementById('humidityValueDisplay').textContent = `${e.target.value} %`;
  });
  rainSlider.addEventListener('input', (e) => {
    document.getElementById('rainValueDisplay').textContent = `${e.target.value} mm`;
  });
}

// 6. LAYER VIEWER & SPLIT CANVAS
function initLayerViewer() {
  const layerBtns = document.querySelectorAll('.layer-btn');
  const opacitySlider = document.getElementById('layerOpacitySlider');
  const canvasImg = document.getElementById('activeCanvasImg');
  const splitCanvas = document.getElementById('splitCanvas');

  layerBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      layerBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeLayer = btn.getAttribute('data-layer');

      updateLayerDisplay();
    });
  });

  opacitySlider.addEventListener('input', (e) => {
    const val = e.target.value / 100;
    canvasImg.style.opacity = val;
  });
}

function updateLayerDisplay() {
  const canvasImg = document.getElementById('activeCanvasImg');
  const splitCanvas = document.getElementById('splitCanvas');
  const opacitySlider = document.getElementById('layerOpacitySlider');

  if (!currentInspectionData) return;

  if (activeLayer === 'split') {
    canvasImg.classList.add('hidden');
    splitCanvas.classList.remove('hidden');
    document.getElementById('splitOriginalImg').src = currentInspectionData.image_url;
    document.getElementById('splitOverlayImg').src = currentInspectionData.segmentation.overlay_url;
    return;
  }

  canvasImg.classList.remove('hidden');
  splitCanvas.classList.add('hidden');

  if (activeLayer === 'original') {
    canvasImg.src = currentInspectionData.image_url;
  } else if (activeLayer === 'detect') {
    canvasImg.src = currentInspectionData.detection.visualized_image_url;
  } else if (activeLayer === 'mask') {
    canvasImg.src = currentInspectionData.segmentation.mask_url;
  } else if (activeLayer === 'overlay') {
    canvasImg.src = currentInspectionData.segmentation.overlay_url;
  }
}

// 7. RUN DIAGNOSTIC PIPELINE
async function runDiagnosis(presetUrl = null) {
  const btn = document.getElementById('btnRunDiagnosis');
  const btnIcon = document.getElementById('btnIcon');
  const btnText = document.getElementById('btnText');
  const farmId = document.getElementById('globalFarmSelect').value;
  const temp = document.getElementById('tempSlider').value;
  const hum = document.getElementById('humiditySlider').value;
  const rain = document.getElementById('rainSlider').value;
  const stage = document.getElementById('growthStageSelect').value;

  btn.disabled = true;
  btnIcon.innerHTML = '<span class="spinner"></span>';
  btnText.textContent = 'Processing 5 ML Engines...';

  const formData = new FormData();
  formData.append('farm_id', farmId);
  formData.append('temperature', temp);
  formData.append('humidity', hum);
  formData.append('rainfall', rain);
  formData.append('growth_stage', stage);

  try {
    if (selectedFile) {
      formData.append('file', selectedFile);
    } else {
      // Fetch the preset image as blob to send through the same standard pipeline
      const blobRes = await fetch(presetUrl || currentSampleUrl);
      const blob = await blobRes.blob();
      formData.append('file', blob, 'sample_specimen.jpg');
    }

    const response = await fetch('/api/v1/inspect', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Diagnostic pipeline error');
    }

    const data = await response.json();
    currentInspectionData = data;

    renderDiagnosticResults(data);
    updateLayerDisplay();

  } catch (error) {
    alert(`Diagnosis failed: ${error.message}`);
    console.error(error);
  } finally {
    btn.disabled = false;
    btnIcon.innerHTML = '🔍';
    btnText.textContent = 'Analyze Specimen Pipeline';
  }
}

function renderDiagnosticResults(data) {
  // Title & Badges
  document.getElementById('diagTitle').textContent = data.classification.disease_display;
  
  const confPct = (data.classification.confidence * 100).toFixed(1);
  const confBadge = document.getElementById('diagConfidenceBadge');
  confBadge.textContent = `${confPct}% Confidence`;
  confBadge.className = data.classification.confidence > 0.80 ? 'badge badge-success' : 'badge badge-warning';

  const statusBadge = document.getElementById('diagStatusBadge');
  if (data.classification.needs_expert_review) {
    statusBadge.textContent = '⚠️ Needs Expert Review';
    statusBadge.className = 'badge badge-warning';
  } else {
    statusBadge.textContent = 'Automated Pipeline';
    statusBadge.className = 'badge badge-info';
  }

  // Foliar Severity
  const sev = data.severity;
  document.getElementById('severityPercentVal').textContent = `${sev.affected_area_percentage}%`;
  
  const sevBadge = document.getElementById('severityBadge');
  sevBadge.textContent = sev.severity_level;
  if (sev.severity_level === 'Healthy') sevBadge.className = 'badge badge-success';
  else if (sev.severity_level === 'Mild') sevBadge.className = 'badge badge-info';
  else if (sev.severity_level === 'Moderate') sevBadge.className = 'badge badge-warning';
  else sevBadge.className = 'badge badge-danger';

  document.getElementById('severityBarFill').style.width = `${Math.min(sev.affected_area_percentage, 100)}%`;
  document.getElementById('severityPixelDetails').textContent = `Affected: ${sev.affected_pixels.toLocaleString()} px / Canopy: ${sev.leaf_pixels.toLocaleString()} px`;

  // YOLO Localized defects
  const det = data.detection;
  document.getElementById('symptomCountVal').textContent = `${det.count} Defects`;
  document.getElementById('symptomLabelDetails').textContent = det.count > 0 ? det.detections[0].label : 'No localized necrotic lesions';

  // Weather Risk
  const w = data.weather_risk;
  document.getElementById('weatherRiskVal').textContent = `${w.risk_score}%`;
  const wBadge = document.getElementById('weatherRiskBadge');
  wBadge.textContent = `${w.risk_level} Risk`;
  if (w.risk_level === 'Low') wBadge.className = 'badge badge-success';
  else if (w.risk_level === 'Moderate') wBadge.className = 'badge badge-warning';
  else wBadge.className = 'badge badge-danger';

  document.getElementById('weatherBarFill').style.width = `${w.risk_score}%`;
  document.getElementById('weatherFavorableDetails').textContent = w.favorable_conditions || 'Standard microclimate balance';

  // Differential Probabilities Breakdown
  const probContainer = document.getElementById('probabilityBreakdownList');
  probContainer.innerHTML = '';
  data.classification.top_classes.forEach(c => {
    const item = document.createElement('div');
    item.className = 'prob-item';
    item.innerHTML = `
      <div class="prob-info">
        <span>${c.display_name}</span>
        <strong>${c.percentage}%</strong>
      </div>
      <div class="bar-track">
        <div class="bar-fill fill-emerald" style="width: ${c.percentage}%;"></div>
      </div>
    `;
    probContainer.appendChild(item);
  });

  // Agronomic Guidance
  const g = data.guidance;
  document.getElementById('guidanceTitle').textContent = g.title;
  document.getElementById('guidanceSummary').textContent = g.summary;

  const immList = document.getElementById('immediateActionsList');
  immList.innerHTML = '';
  g.immediate_actions.forEach(act => {
    const li = document.createElement('li');
    li.textContent = act;
    immList.appendChild(li);
  });

  const prevList = document.getElementById('preventionList');
  prevList.innerHTML = '';
  g.cultural_practices.concat(g.prevention).slice(0, 3).forEach(prev => {
    const li = document.createElement('li');
    li.textContent = prev;
    prevList.appendChild(li);
  });

  if (g.regulatory_warning) {
    document.getElementById('disclaimerText').textContent = g.regulatory_warning;
  }
}

// 8. AUTO-FETCH NASA WEATHER
async function autoFetchNasaWeather() {
  const farmId = document.getElementById('globalFarmSelect').value;
  const btn = document.getElementById('btnNasaAutoFetch');
  btn.textContent = 'Fetching...';

  try {
    const res = await fetch(`/api/v1/weather/risk?latitude=19.9975&longitude=73.7898`);
    const data = await res.json();
    const params = data.parameters;

    document.getElementById('tempSlider').value = params.temperature;
    document.getElementById('tempValueDisplay').textContent = `${params.temperature} °C`;
    document.getElementById('humiditySlider').value = params.humidity;
    document.getElementById('humidityValueDisplay').textContent = `${params.humidity} %`;
    document.getElementById('rainSlider').value = params.rainfall;
    document.getElementById('rainValueDisplay').textContent = `${params.rainfall} mm`;

    alert(`Microclimate fetched successfully from ${data.source}: ${params.temperature}°C, ${params.humidity}% RH, ${params.rainfall}mm rain.`);
  } catch (err) {
    alert('Failed to connect to meteorological service.');
  } finally {
    btn.textContent = '📡 Auto-Fetch';
  }
}

// 9. BATCH PROCESSING
function initBatchUpload() {
  const dropzone = document.getElementById('batchDropzone');
  const fileInput = document.getElementById('batchFileInput');

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      processBatchFiles(e.dataTransfer.files);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      processBatchFiles(e.target.files);
    }
  });
}

async function processBatchFiles(fileList) {
  const progressArea = document.getElementById('batchProgressArea');
  const barFill = document.getElementById('batchBarFill');
  const label = document.getElementById('batchProgressLabel');
  const percentLabel = document.getElementById('batchProgressPercent');
  const tableContainer = document.getElementById('batchResultsTableContainer');
  const tbody = document.getElementById('batchTableBody');

  progressArea.classList.remove('hidden');
  tableContainer.classList.remove('hidden');
  tbody.innerHTML = '';

  const total = fileList.length;
  label.textContent = `Processing Batch (${total} files)...`;
  barFill.style.width = '20%';
  percentLabel.textContent = '20%';

  const formData = new FormData();
  const farmId = document.getElementById('globalFarmSelect').value;
  formData.append('farm_id', farmId);

  for (let i = 0; i < fileList.length; i++) {
    formData.append('files', fileList[i]);
  }

  try {
    const res = await fetch('/api/v1/inspect/batch', {
      method: 'POST',
      body: formData
    });
    const batchRes = await res.json();

    barFill.style.width = '100%';
    percentLabel.textContent = '100%';
    label.textContent = `Batch Completed: ${batchRes.successful} of ${batchRes.total_processed} analyzed.`;

    batchRes.results.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><img src="${r.image_url || '/samples/sample_healthy.jpg'}" style="width:40px; height:40px; border-radius:6px; object-fit:cover;"></td>
        <td><strong>${r.filename}</strong></td>
        <td>${r.predicted_disease || 'Error'}</td>
        <td>${r.confidence ? (r.confidence * 100).toFixed(1) + '%' : '-'}</td>
        <td>${r.severity_percentage ? r.severity_percentage + '%' : '-'}</td>
        <td><span class="badge badge-info">${r.severity_level || '-'}</span></td>
        <td><span class="badge ${r.success ? 'badge-success' : 'badge-danger'}">${r.success ? 'Completed' : 'Failed'}</span></td>
        <td><button class="btn-secondary" style="padding:4px 8px; font-size:0.75rem;" onclick="viewInspectionDetail('${r.inspection_id}')">View</button></td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    alert(`Batch analysis error: ${err.message}`);
  }
}

// 10. FARM HEALTH ANALYTICS
async function loadFarmHealth() {
  const farmId = document.getElementById('globalFarmSelect').value;
  try {
    const res = await fetch(`/api/v1/farms/${farmId}/health`);
    const data = await res.json();

    document.getElementById('farmLocationSubtitle').textContent = `${data.location} (${data.crop_type})`;
    document.getElementById('statHealthIndex').textContent = data.health_score;
    document.getElementById('statTotalInspections').textContent = data.total_inspections;
    document.getElementById('statHealthyRatio').textContent = `${data.healthy_count} Healthy / ${data.diseased_count} Diseased`;
    document.getElementById('statAvgSeverity').textContent = `${data.average_severity}%`;

    // Prevalence Chart
    const chartDiv = document.getElementById('diseasePrevalenceChart');
    chartDiv.innerHTML = '';
    const keys = Object.keys(data.disease_distribution);
    if (keys.length === 0) {
      chartDiv.innerHTML = '<p style="color:var(--text-dim); font-size:0.85rem;">No disease records yet for this farm.</p>';
    } else {
      keys.forEach(k => {
        const count = data.disease_distribution[k];
        const pct = ((count / data.total_inspections) * 100).toFixed(0);
        const row = document.createElement('div');
        row.style.marginBottom = '8px';
        row.innerHTML = `
          <div style="display:flex; justify-content:space-between; font-size:0.82rem; margin-bottom:2px;">
            <span>${k}</span>
            <strong>${count} (${pct}%)</strong>
          </div>
          <div class="bar-track">
            <div class="bar-fill fill-amber" style="width:${pct}%;"></div>
          </div>
        `;
        chartDiv.appendChild(row);
      });
    }

    // Recent list
    const recentDiv = document.getElementById('farmRecentList');
    recentDiv.innerHTML = '';
    if (data.recent_inspections.length === 0) {
      recentDiv.innerHTML = '<p style="color:var(--text-dim); font-size:0.85rem;">No recent inspections recorded.</p>';
    } else {
      data.recent_inspections.forEach(item => {
        const div = document.createElement('div');
        div.style.cssText = 'display:flex; justify-content:space-between; align-items:center; background:var(--bg-card); padding:8px 12px; border-radius:8px; border:1px solid var(--border);';
        div.innerHTML = `
          <div style="display:flex; align-items:center; gap:10px;">
            <img src="${item.image_url}" style="width:36px; height:36px; border-radius:6px; object-fit:cover;">
            <div>
              <div style="font-weight:600; font-size:0.85rem;">${item.disease_display}</div>
              <div style="font-size:0.75rem; color:var(--text-dim);">${item.created_at}</div>
            </div>
          </div>
          <span class="badge badge-warning">${item.severity_estimate}% (${item.severity_level})</span>
        `;
        recentDiv.appendChild(div);
      });
    }

  } catch (err) {
    console.error('Failed to load farm health:', err);
  }
}

// 11. INSPECTION HISTORY
async function loadInspectionHistory() {
  const tbody = document.getElementById('historyTableBody');
  const search = document.getElementById('historySearchInput').value.toLowerCase();
  
  try {
    const res = await fetch('/api/v1/inspections');
    const inspections = await res.json();
    tbody.innerHTML = '';

    const filtered = inspections.filter(i => {
      const disp = (i.disease_display || '').toLowerCase();
      const fn = (i.filename || '').toLowerCase();
      return disp.includes(search) || fn.includes(search);
    });

    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-dim);">No inspections found.</td></tr>';
      return;
    }

    filtered.forEach(insp => {
      const tr = document.createElement('tr');
      const conf = (insp.confidence * 100).toFixed(1);
      tr.innerHTML = `
        <td><img src="${insp.image_url}" style="width:42px; height:42px; border-radius:6px; object-fit:cover;"></td>
        <td style="font-family:monospace; font-size:0.75rem;">${insp.inspection_id.slice(0, 8)}...</td>
        <td><strong>${insp.disease_display || insp.predicted_disease}</strong></td>
        <td>${conf}%</td>
        <td>${insp.severity_estimate}%</td>
        <td><span class="badge badge-warning">${insp.severity_level}</span></td>
        <td style="font-size:0.8rem; color:var(--text-muted);">${insp.created_at.replace('T', ' ').slice(0, 16)}</td>
        <td><span class="badge ${insp.status === 'expert_verified' ? 'badge-success' : 'badge-info'}">${insp.status}</span></td>
        <td><button class="btn-secondary" style="padding:4px 8px; font-size:0.75rem;" onclick="viewInspectionDetail('${insp.inspection_id}')">Details</button></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

async function viewInspectionDetail(inspectionId) {
  try {
    const res = await fetch(`/api/v1/inspections/${inspectionId}`);
    const insp = await res.json();

    // Map to Diagnostic Studio view
    currentInspectionData = {
      image_url: insp.image_url,
      classification: {
        predicted_disease: insp.predicted_disease,
        disease_display: insp.disease_display,
        confidence: insp.confidence,
        top_classes: (insp.visual_evidence && insp.visual_evidence.top_classes) || [],
        needs_expert_review: insp.status === 'needs_review'
      },
      detection: (insp.visual_evidence && insp.visual_evidence.detection) || { count: 0, detections: [], visualized_image_url: insp.image_url },
      segmentation: (insp.visual_evidence && insp.visual_evidence.segmentation) || { mask_url: insp.image_url, overlay_url: insp.image_url },
      severity: (insp.visual_evidence && insp.visual_evidence.severity) || {
        affected_area_percentage: insp.severity_estimate,
        severity_level: insp.severity_level,
        affected_pixels: 0,
        leaf_pixels: 1
      },
      weather_risk: insp.weather || { risk_score: 50, risk_level: 'Moderate', favorable_conditions: 'N/A' },
      guidance: insp.guidance
    };

    renderDiagnosticResults(currentInspectionData);
    updateLayerDisplay();

    // Switch to studio tab
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelector('.tab-btn[data-tab="studio"]').classList.add('active');
    document.getElementById('tab-studio').classList.add('active');

  } catch (err) {
    alert('Failed to load inspection details');
  }
}

// 12. AI MODELS REGISTRY
async function loadModelsRegistry() {
  const container = document.getElementById('modelCardsContainer');
  try {
    const res = await fetch('/api/v1/models');
    const data = await res.json();
    container.innerHTML = '';

    data.models.forEach((m, idx) => {
      const card = document.createElement('div');
      card.className = 'card';
      card.style.margin = '0';
      card.style.background = 'var(--bg-input)';

      let metricsHtml = '';
      if (m.evaluation_metrics) {
        Object.keys(m.evaluation_metrics).forEach(k => {
          metricsHtml += `
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
              <span style="color:var(--text-muted);">${k.replace('_', ' ').toUpperCase()}</span>
              <strong style="color:var(--primary-light);">${m.evaluation_metrics[k]}</strong>
            </div>
          `;
        });
      }

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <h3 style="font-size:1.02rem; font-weight:700;">Model ${idx+1}: ${m.name}</h3>
          <span class="badge badge-success">Production Active</span>
        </div>
        <div style="font-size:0.82rem; color:var(--text-muted); margin-bottom:12px;">
          <div><strong>Component:</strong> ${m.component}</div>
          <div><strong>Architecture:</strong> ${m.framework}</div>
        </div>
        <div style="background:var(--bg-card); padding:10px; border-radius:8px; border:1px solid var(--border); margin-bottom:10px;">
          <div style="font-size:0.75rem; text-transform:uppercase; color:var(--text-dim); margin-bottom:6px; font-weight:600;">Benchmark Evaluation</div>
          ${metricsHtml}
        </div>
        ${m.safety_safeguards ? `<div style="font-size:0.75rem; color:#fde68a; background:rgba(245,158,11,0.08); padding:8px; border-radius:6px;">⚠️ ${m.safety_safeguards}</div>` : ''}
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to load models:', err);
  }
}

// 13. WEATHER RISK LAB
function initWeatherLab() {
  const tempS = document.getElementById('labTempSlider');
  const humS = document.getElementById('labHumiditySlider');
  const rainS = document.getElementById('labRainSlider');
  const stageS = document.getElementById('labStageSelect');

  tempS.addEventListener('input', (e) => document.getElementById('labTempVal').textContent = `${e.target.value} °C`);
  humS.addEventListener('input', (e) => document.getElementById('labHumidityVal').textContent = `${e.target.value} %`);
  rainS.addEventListener('input', (e) => document.getElementById('labRainVal').textContent = `${e.target.value} mm`);

  document.getElementById('btnLabCompute').addEventListener('click', async () => {
    try {
      const url = `/api/v1/weather/risk?temperature=${tempS.value}&humidity=${humS.value}&rainfall=${rainS.value}&growth_stage=${stageS.value}`;
      const res = await fetch(url);
      const data = await res.json();

      document.getElementById('labRiskScoreText').textContent = `${data.risk_score}%`;
      const badge = document.getElementById('labRiskBadge');
      badge.textContent = `${data.risk_level} Risk`;
      if (data.risk_level === 'Low') badge.className = 'badge badge-success';
      else if (data.risk_level === 'Moderate') badge.className = 'badge badge-warning';
      else badge.className = 'badge badge-danger';

      document.getElementById('labFavorableText').textContent = data.favorable_conditions || 'Neutral microclimate balance.';
    } catch (err) {
      alert('Risk recalculation error');
    }
  });
}

// 14. MODALS (EXPERT FEEDBACK & REGISTER FARM)
function initModals() {
  // Feedback modal
  const fbModal = document.getElementById('feedbackModal');
  document.getElementById('btnOpenFeedbackModal').addEventListener('click', () => {
    if (!currentInspectionData || !currentInspectionData.inspection_id) {
      alert('Please run a specimen diagnosis first to verify.');
      return;
    }
    document.getElementById('feedbackInspectionId').value = currentInspectionData.inspection_id;
    fbModal.classList.add('active');
  });

  document.getElementById('btnCloseFeedbackModal').addEventListener('click', () => {
    fbModal.classList.remove('active');
  });

  document.getElementById('btnSubmitFeedback').addEventListener('click', async () => {
    const inspectionId = document.getElementById('feedbackInspectionId').value;
    const expertName = document.getElementById('feedbackExpertName').value;
    const agreement = document.getElementById('feedbackAgreement').value;
    const verifiedDisease = document.getElementById('feedbackVerifiedDisease').value;
    const comments = document.getElementById('feedbackComments').value;

    try {
      const res = await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          inspection_id: inspectionId,
          expert_name: expertName,
          agreement: agreement,
          verified_disease: verifiedDisease,
          comments: comments
        })
      });

      if (!res.ok) throw new Error('Feedback submission error');

      alert('Expert agronomist verification recorded and committed to audit trail!');
      fbModal.classList.remove('active');
      document.getElementById('diagStatusBadge').textContent = '✅ Expert Verified';
      document.getElementById('diagStatusBadge').className = 'badge badge-success';
    } catch (err) {
      alert(err.message);
    }
  });

  // Farm modal
  const farmModal = document.getElementById('farmModal');
  document.getElementById('btnOpenNewFarm').addEventListener('click', () => farmModal.classList.add('active'));
  document.getElementById('btnCloseFarmModal').addEventListener('click', () => farmModal.classList.remove('active'));

  document.getElementById('btnSaveFarm').addEventListener('click', async () => {
    const name = document.getElementById('newFarmName').value;
    const crop = document.getElementById('newFarmCrop').value;
    const loc = document.getElementById('newFarmLocation').value;
    const lat = parseFloat(document.getElementById('newFarmLat').value);
    const lng = parseFloat(document.getElementById('newFarmLng').value);

    if (!name) {
      alert('Please enter a farm name.');
      return;
    }

    try {
      const res = await fetch('/api/v1/farms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, crop_type: crop, location: loc, latitude: lat, longitude: lng })
      });
      const data = await res.json();
      alert(`Farm "${data.name}" registered successfully!`);
      farmModal.classList.remove('active');
      initFarms();
    } catch (err) {
      alert('Failed to register farm.');
    }
  });

  // History search filter
  document.getElementById('historySearchInput').addEventListener('input', () => {
    loadInspectionHistory();
  });
  document.getElementById('btnReloadHistory').addEventListener('click', () => {
    loadInspectionHistory();
  });
  document.getElementById('btnRefreshFarmHealth').addEventListener('click', () => {
    loadFarmHealth();
  });
}
