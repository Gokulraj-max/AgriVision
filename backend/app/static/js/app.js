/**
 * AgriVision AI 2.0 - Core Frontend Controller & Mobile Simulator Logic
 */

// State
let currentTab = 'home';
let currentLanguage = 'ta'; // Default to Tamil
let isWebcamActive = false;
let webcamStream = null;
let liveScanInterval = null;
let activeSampleLeaf = 'tomato_early_blight';
let currentHeatmapVisible = true;
let supportedCropsData = [];
let recentInspectionsData = [];

// Sample leaf library for testing without physical camera
const SAMPLE_LEAF_PRESETS = {
  tomato_early_blight: {
    crop: 'Tomato',
    disease: 'Early Blight (Alternaria solani)',
    disease_ta: 'தக்காளி ஆரம்பகால கருகல் நோய்',
    pathogen: 'Alternaria solani (Fungus)',
    confidence: 0.94,
    severity_pct: 18.4,
    leaf_type: 'diseased',
    guidance: 'பாதிக்கப்பட்ட கீழ் இலைகளை வெட்டி அகற்றவும். சொட்டு நீர்ப்பாசன முறையை பயன்படுத்தி இலைகளில் நீர் தேங்குவதை தவிர்க்கவும். தேவைப்படின் அங்கீகரிக்கப்பட்ட தாமிர ஹைட்ராக்சைடு தெளிக்கவும்.',
    guidance_en: 'Prune infected lower foliage up to 30 cm from ground. Ensure drip irrigation to avoid canopy wetting. Apply bio-fungicide Trichoderma viride or approved copper hydroxide spray.',
    boxes: [
      { ymin: 0.28, xmin: 0.30, ymax: 0.58, xmax: 0.65, label: 'Target-Spot Lesion', conf: 0.93, color: '#ef4444' },
      { ymin: 0.60, xmin: 0.45, ymax: 0.78, xmax: 0.75, label: 'Chlorotic Margin', conf: 0.88, color: '#f59e0b' }
    ],
    color: '#3f6212',
    spotColor: '#78350f'
  },
  potato_late_blight: {
    crop: 'Potato',
    disease: 'Late Blight (Phytophthora infestans)',
    disease_ta: 'உருளைக்கிழங்கு பிந்தைய கருகல் நோய்',
    pathogen: 'Phytophthora infestans (Oomycete)',
    confidence: 0.96,
    severity_pct: 26.8,
    leaf_type: 'diseased',
    guidance: 'உடனடியாக பாதிக்கப்பட்ட செடிகளை தனிமைப்படுத்தவும். மழைக்காலங்களில் அதிக ஈரப்பதத்தை கட்டுப்படுத்த வடிகால் வசதி செய்யவும். மண்கோசெப் 2 கி/லி தெளிக்கவும்.',
    guidance_en: 'Isolate affected plants immediately. Improve field drainage during high humidity periods. Apply protective Mancozeb 2g/L before rain events.',
    boxes: [
      { ymin: 0.20, xmin: 0.25, ymax: 0.62, xmax: 0.72, label: 'Water-Soaked Necrosis', conf: 0.95, color: '#dc2626' }
    ],
    color: '#2d4a1d',
    spotColor: '#451a03'
  },
  rice_blast: {
    crop: 'Rice',
    disease: 'Rice Blast (Magnaporthe oryzae)',
    disease_ta: 'நெல் குலை நோய் (இலை வெடிப்பு)',
    pathogen: 'Magnaporthe oryzae (Fungus)',
    confidence: 0.91,
    severity_pct: 14.2,
    leaf_type: 'diseased',
    guidance: 'தழைச்சத்து உரங்களை (யுரியா) பிரித்து இடவும். சூடோமோனாஸ் புளோரசன்ஸ் விதை நேர்த்தி மற்றும் இலைவழி தெளிப்பு மேற்கொள்ளவும்.',
    guidance_en: 'Avoid excess nitrogen fertilizer application. Split urea doses. Apply Pseudomonas fluorescens 10g/L foliar spray.',
    boxes: [
      { ymin: 0.35, xmin: 0.20, ymax: 0.55, xmax: 0.80, label: 'Spindle-shaped Lesion', conf: 0.91, color: '#ea580c' }
    ],
    color: '#4d7c0f',
    spotColor: '#7c2d12'
  },
  cotton_curl: {
    crop: 'Cotton',
    disease: 'Cotton Leaf Curl Virus (CLCuV)',
    disease_ta: 'பருத்தி இலை சுருள் நச்சுயிரி',
    pathogen: 'Begomovirus / Whitefly vector',
    confidence: 0.89,
    severity_pct: 21.0,
    leaf_type: 'diseased',
    guidance: 'வெள்ளை ஈக்களை கட்டுப்படுத்த மஞ்சள் ஒட்டும் பொறிகளை அமைக்கவும். வேப்ப எண்ணெய் கரைசல் 3% தெளிக்கவும்.',
    guidance_en: 'Install yellow sticky traps (10/acre) to control vector whiteflies. Spray neem oil 3% formulation.',
    boxes: [
      { ymin: 0.25, xmin: 0.25, ymax: 0.75, xmax: 0.75, label: 'Upward Leaf Curling & Enation', conf: 0.89, color: '#f59e0b' }
    ],
    color: '#15803d',
    spotColor: '#a16207'
  },
  tomato_healthy: {
    crop: 'Tomato',
    disease: 'Healthy Foliage',
    disease_ta: 'ஆரோக்கியமான தக்காளி இலை',
    pathogen: 'None (Healthy Tissue)',
    confidence: 0.98,
    severity_pct: 0.0,
    leaf_type: 'healthy',
    guidance: 'பயிர் மிக ஆரோக்கியமாக உள்ளது. சொட்டு நீர்ப்பாசனம் மற்றும் வழக்கமான ஊட்டச்சத்து மேலாண்மையை தொடரவும்.',
    guidance_en: 'Crop is in vigorous healthy state. Continue regular drip irrigation and scout weekly for foliar pests.',
    boxes: [
      { ymin: 0.15, xmin: 0.15, ymax: 0.85, xmax: 0.85, label: 'Healthy Leaf Canopy', conf: 0.98, color: '#22c55e' }
    ],
    color: '#16a34a',
    spotColor: null
  }
};

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  initCanvas();
  renderSampleLeaf(activeSampleLeaf);
  startLiveScanSimulation();
  fetchInitialData();
  updateTime();
  setInterval(updateTime, 10000);
});

// Update Phone Time
function updateTime() {
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const timeEl = document.getElementById('phoneTime');
  if (timeEl) timeEl.textContent = timeStr;
}

// Navigation & Tab Switching
function setupNavigation() {
  // Desktop view toggle
  const btnSim = document.getElementById('btnViewSimulator');
  const btnDash = document.getElementById('btnViewDashboard');
  const deskPanel = document.getElementById('desktopPanel');
  const simWrapper = document.getElementById('simulatorWrapper');

  btnSim.addEventListener('click', () => {
    btnSim.classList.add('active');
    btnDash.classList.remove('active');
    deskPanel.style.display = 'flex';
    simWrapper.style.display = 'flex';
  });

  btnDash.addEventListener('click', () => {
    btnDash.classList.add('active');
    btnSim.classList.remove('active');
    deskPanel.style.display = 'flex';
    simWrapper.style.display = 'none';
  });

  // Global Language Buttons
  const btnTa = document.getElementById('btnLangTa');
  const btnEn = document.getElementById('btnLangEn');

  btnTa.addEventListener('click', () => {
    setGlobalLanguage('ta');
  });

  btnEn.addEventListener('click', () => {
    setGlobalLanguage('en');
  });

  // Toggle Heatmap button
  const btnHeat = document.getElementById('btnToggleHeatmap');
  if (btnHeat) {
    btnHeat.addEventListener('click', toggleHeatmapOverlay);
  }

  // Camera buttons
  const btnCam = document.getElementById('btnToggleCamera');
  if (btnCam) {
    btnCam.addEventListener('click', toggleWebcam);
  }

  const btnCapture = document.getElementById('btnCaptureInspect');
  if (btnCapture) {
    btnCapture.addEventListener('click', () => {
      openInspectionDetail(activeSampleLeaf);
    });
  }

  const btnDetailVoice = document.getElementById('btnPlayDetailVoice');
  if (btnDetailVoice) {
    btnDetailVoice.addEventListener('click', () => {
      const preset = SAMPLE_LEAF_PRESETS[activeSampleLeaf];
      if (preset) {
        const text = currentLanguage === 'ta' ? preset.guidance : preset.guidance_en;
        playVoiceText(text);
      }
    });
  }
}

function setGlobalLanguage(lang) {
  currentLanguage = lang;
  document.getElementById('btnLangTa').classList.toggle('active', lang === 'ta');
  document.getElementById('btnLangEn').classList.toggle('active', lang === 'en');
  setAssistantLang(lang);
  updateActivePresetLabels();
}

function switchMobileTab(tabKey) {
  currentTab = tabKey;
  
  // Hide all tabs
  document.querySelectorAll('.tab-view').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-item').forEach(el => el.classList.remove('active'));

  // Show active tab
  const tabEl = document.getElementById(`tab${tabKey.charAt(0).toUpperCase() + tabKey.slice(1)}`);
  const btnEl = document.getElementById(`tabBtn${tabKey.charAt(0).toUpperCase() + tabKey.slice(1)}`);

  if (tabEl) tabEl.classList.add('active');
  if (btnEl) btnEl.classList.add('active');

  // Specific tab actions
  if (tabKey === 'scanner') {
    renderSampleLeaf(activeSampleLeaf);
  }
}

// -------------------------------------------------------------
// Live Viewfinder & Canvas Simulator
// -------------------------------------------------------------
let vfCanvas, vfCtx;

function initCanvas() {
  vfCanvas = document.getElementById('viewfinderCanvas');
  if (!vfCanvas) return;
  vfCanvas.width = 390;
  vfCanvas.height = 310;
  vfCtx = vfCanvas.getContext('2d');
}

function loadSampleLeaf(presetKey) {
  activeSampleLeaf = presetKey;
  // Update buttons
  document.querySelectorAll('.sample-leaf-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('onclick')?.includes(presetKey));
  });

  renderSampleLeaf(presetKey);
}

function renderSampleLeaf(presetKey) {
  const preset = SAMPLE_LEAF_PRESETS[presetKey] || SAMPLE_LEAF_PRESETS.tomato_early_blight;
  if (!vfCtx) return;

  const w = vfCanvas.width;
  const h = vfCanvas.height;

  // Background
  vfCtx.fillStyle = '#0f172a';
  vfCtx.fillRect(0, 0, w, h);

  // Draw organic leaf shape
  vfCtx.save();
  vfCtx.beginPath();
  vfCtx.moveTo(w * 0.5, h * 0.15);
  vfCtx.bezierCurveTo(w * 0.9, h * 0.35, w * 0.85, h * 0.75, w * 0.5, h * 0.88);
  vfCtx.bezierCurveTo(w * 0.15, h * 0.75, w * 0.1, h * 0.35, w * 0.5, h * 0.15);
  vfCtx.closePath();

  // Foliar green gradient
  const grad = vfCtx.createRadialGradient(w * 0.5, h * 0.5, 30, w * 0.5, h * 0.5, 140);
  grad.addColorStop(0, preset.color);
  grad.addColorStop(1, '#1e3a1b');
  vfCtx.fillStyle = grad;
  vfCtx.fill();
  vfCtx.strokeStyle = 'rgba(74, 222, 128, 0.4)';
  vfCtx.lineWidth = 2;
  vfCtx.stroke();

  // Leaf veins
  vfCtx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
  vfCtx.lineWidth = 2;
  vfCtx.beginPath();
  vfCtx.moveTo(w * 0.5, h * 0.18);
  vfCtx.lineTo(w * 0.5, h * 0.84);
  vfCtx.stroke();

  // Lateral veins
  for (let i = 0.3; i < 0.8; i += 0.12) {
    vfCtx.beginPath();
    vfCtx.moveTo(w * 0.5, h * i);
    vfCtx.lineTo(w * 0.75, h * (i - 0.05));
    vfCtx.moveTo(w * 0.5, h * i);
    vfCtx.lineTo(w * 0.25, h * (i - 0.05));
    vfCtx.stroke();
  }

  // Draw lesions if diseased
  if (preset.spotColor) {
    preset.boxes.forEach((b, idx) => {
      const bx = b.xmin * w;
      const by = b.ymin * h;
      const bw = (b.xmax - b.xmin) * w;
      const bh = (b.ymax - b.ymin) * h;

      // Concentric lesion rings
      const cx = bx + bw * 0.5;
      const cy = by + bh * 0.5;
      const r = Math.min(bw, bh) * 0.45;

      for (let cr = r; cr > 3; cr -= 6) {
        vfCtx.fillStyle = (cr % 12 === 0) ? preset.spotColor : 'rgba(0,0,0,0.5)';
        vfCtx.beginPath();
        vfCtx.arc(cx, cy, cr, 0, Math.PI * 2);
        vfCtx.fill();
      }

      // Draw AI Bounding Box
      vfCtx.strokeStyle = b.color;
      vfCtx.lineWidth = 2;
      vfCtx.strokeRect(bx, by, bw, bh);

      // Label Chip
      vfCtx.fillStyle = b.color;
      vfCtx.fillRect(bx, by - 16, Math.min(bw, 140), 16);
      vfCtx.fillStyle = '#ffffff';
      vfCtx.font = 'bold 9px sans-serif';
      vfCtx.fillText(`${b.label} (${(b.conf * 100).toFixed(0)}%)`, bx + 4, by - 4);
    });
  }

  vfCtx.restore();

  // Update UI Card
  updateActivePresetLabels();
}

function updateActivePresetLabels() {
  const preset = SAMPLE_LEAF_PRESETS[activeSampleLeaf];
  if (!preset) return;

  const vCropChip = document.getElementById('vCropChip');
  if (vCropChip) {
    vCropChip.textContent = `🌿 ${preset.crop} Leaf (${(preset.confidence * 100).toFixed(0)}%)`;
  }

  const liveDiseaseName = document.getElementById('liveDiseaseName');
  if (liveDiseaseName) liveDiseaseName.textContent = preset.disease;

  const liveDiseaseTa = document.getElementById('liveDiseaseTa');
  if (liveDiseaseTa) liveDiseaseTa.textContent = preset.disease_ta;

  const liveConfVal = document.getElementById('liveConfVal');
  if (liveConfVal) liveConfVal.textContent = `${(preset.confidence * 100).toFixed(0)}%`;

  const liveSevPct = document.getElementById('liveSevPct');
  if (liveSevPct) liveSevPct.textContent = `${preset.severity_pct.toFixed(1)}%`;

  const liveSevFill = document.getElementById('liveSevFill');
  if (liveSevFill) liveSevFill.style.width = `${Math.min(preset.severity_pct * 2, 100)}%`;
}

// 1-2 FPS Live Sampling Simulation
function startLiveScanSimulation() {
  liveScanInterval = setInterval(() => {
    if (currentTab === 'scanner') {
      const vFpsChip = document.getElementById('vFpsChip');
      if (vFpsChip) {
        const fps = (1.6 + Math.random() * 0.4).toFixed(1);
        vFpsChip.textContent = `${fps} FPS`;
      }
    }
  }, 1200);
}

// Webcam support
async function toggleWebcam() {
  const video = document.getElementById('webcamVideo');
  if (!isWebcamActive) {
    try {
      webcamStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      video.srcObject = webcamStream;
      video.play();
      isWebcamActive = true;
      document.getElementById('btnToggleCamera').textContent = '⏹️ Stop Camera';
      renderWebcamLoop();
    } catch (e) {
      alert('Camera access denied or unavailable. You can use the preset leaf samples above.');
    }
  } else {
    if (webcamStream) {
      webcamStream.getTracks().forEach(t => t.stop());
    }
    isWebcamActive = false;
    document.getElementById('btnToggleCamera').textContent = '📷 Toggle Webcam';
    renderSampleLeaf(activeSampleLeaf);
  }
}

function renderWebcamLoop() {
  if (!isWebcamActive) return;
  const video = document.getElementById('webcamVideo');
  if (vfCtx && video.readyState === video.HAVE_ENOUGH_DATA) {
    vfCtx.drawImage(video, 0, 0, vfCanvas.width, vfCanvas.height);
    // Draw bounding box overlay on webcam
    const preset = SAMPLE_LEAF_PRESETS[activeSampleLeaf];
    if (preset && preset.boxes) {
      preset.boxes.forEach(b => {
        const bx = b.xmin * vfCanvas.width;
        const by = b.ymin * vfCanvas.height;
        const bw = (b.xmax - b.xmin) * vfCanvas.width;
        const bh = (b.ymax - b.ymin) * vfCanvas.height;
        vfCtx.strokeStyle = b.color;
        vfCtx.lineWidth = 2;
        vfCtx.strokeRect(bx, by, bw, bh);
      });
    }
  }
  requestAnimationFrame(renderWebcamLoop);
}

// -------------------------------------------------------------
// Screen 3: Detail Inspection Report with U-Net Heatmap
// -------------------------------------------------------------
function openInspectionDetail(presetKey) {
  const preset = SAMPLE_LEAF_PRESETS[presetKey] || SAMPLE_LEAF_PRESETS.tomato_early_blight;
  
  // Switch to inspection tab
  switchMobileTab('inspection');

  document.getElementById('detailCropTag').textContent = preset.crop;
  document.getElementById('detailDisease').textContent = preset.disease;
  document.getElementById('detailDiseaseTa').textContent = preset.disease_ta;
  document.getElementById('detailPathogen').textContent = `Pathogen: ${preset.pathogen}`;
  document.getElementById('detailSevNum').textContent = `${preset.severity_pct.toFixed(1)}%`;
  document.getElementById('detailSevBar').style.width = `${Math.min(preset.severity_pct * 2, 100)}%`;

  const guidanceText = currentLanguage === 'ta' ? preset.guidance : preset.guidance_en;
  document.getElementById('detailGuidance').textContent = guidanceText;

  // Render heatmap canvas
  renderHeatmap(preset);
}

function renderHeatmap(preset) {
  const hCanvas = document.getElementById('detailHeatmapCanvas');
  const leafImg = document.getElementById('detailLeafImg');
  if (!hCanvas) return;

  hCanvas.width = 390;
  hCanvas.height = 220;
  const ctx = hCanvas.getContext('2d');

  // Background placeholder
  leafImg.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="390" height="220"><rect width="100%" height="100%" fill="%231e3a1b"/><circle cx="195" cy="110" r="80" fill="%233f6212"/></svg>';

  // Clear heatmap
  ctx.clearRect(0, 0, hCanvas.width, hCanvas.height);

  if (!currentHeatmapVisible) return;

  // Generate translucent U-Net Lesion Heatmap gradient
  preset.boxes.forEach(b => {
    const cx = ((b.xmin + b.xmax) / 2) * hCanvas.width;
    const cy = ((b.ymin + b.ymax) / 2) * hCanvas.height;
    const r = ((b.xmax - b.xmin) * hCanvas.width) / 1.6;

    const heatGrad = ctx.createRadialGradient(cx, cy, 5, cx, cy, r);
    heatGrad.addColorStop(0, 'rgba(239, 68, 68, 0.75)'); // Red core
    heatGrad.addColorStop(0.5, 'rgba(245, 158, 11, 0.55)'); // Orange
    heatGrad.addColorStop(0.8, 'rgba(234, 179, 8, 0.3)'); // Yellow halo
    heatGrad.addColorStop(1, 'rgba(34, 197, 94, 0)');

    ctx.fillStyle = heatGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();
  });
}

function toggleHeatmapOverlay() {
  currentHeatmapVisible = !currentHeatmapVisible;
  const lbl = document.getElementById('heatModeLabel');
  if (lbl) {
    lbl.textContent = currentHeatmapVisible ? '🔥 U-Net Lesion Heatmap Active' : '📷 RGB Visible Light Only';
  }
  const preset = SAMPLE_LEAF_PRESETS[activeSampleLeaf];
  renderHeatmap(preset);
}

function submitFeedback(isCorrect) {
  alert(isCorrect 
    ? '✅ Diagnosis verified! Recorded for active learning retraining.' 
    : '⚠️ Flagged for agronomist review. Thank you for your feedback!'
  );
}

// -------------------------------------------------------------
// Voice Synthesis (Tamil & English)
// -------------------------------------------------------------
function playVoiceText(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = currentLanguage === 'ta' ? 'ta-IN' : 'en-US';
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  } else {
    alert(`[Spoken Voice Audio]: ${text}`);
  }
}

// -------------------------------------------------------------
// Screen 6: Bilingual AI Assistant
// -------------------------------------------------------------
let assistantLang = 'ta';

function setAssistantLang(lang) {
  assistantLang = lang;
  document.getElementById('astLangTa').classList.toggle('active', lang === 'ta');
  document.getElementById('astLangEn').classList.toggle('active', lang === 'en');

  const welcome = document.getElementById('astWelcomeText');
  const input = document.getElementById('chatInput');

  if (lang === 'ta') {
    welcome.textContent = 'வணக்கம்! நான் அக்ரிவிஷன் AI உதவியாளர். தக்காளி, உருளைக்கிழங்கு, நெல், பருத்தி பயிர்களின் நோய்கள் மற்றும் கரிம தடுப்பு முறைகள் குறித்து கேளுங்கள்.';
    input.placeholder = 'பயிர் நோய்கள் பற்றி கேளுங்கள்...';
  } else {
    welcome.textContent = 'Hello! I am AgriVision AI Assistant. Ask me anything about crop diseases, organic remedies, or microclimate risks.';
    input.placeholder = 'Ask about crop health, treatments...';
  }
}

function sendQuickPrompt(query) {
  document.getElementById('chatInput').value = query;
  sendChatMessage();
}

function triggerMicInput() {
  const micBtn = document.getElementById('btnChatMic');
  micBtn.style.background = '#fee2e2';
  
  setTimeout(() => {
    micBtn.style.background = '#f1f5f9';
    const query = assistantLang === 'ta' 
      ? 'தக்காளியில் ஆரம்பகால கருகல் நோய் கட்டுப்பாடு?' 
      : 'How to control Tomato Early Blight organically?';
    document.getElementById('chatInput').value = query;
    sendChatMessage();
  }, 1000);
}

async function sendChatMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  const chatContainer = document.getElementById('chatContainer');

  // Append user message
  const userMsg = document.createElement('div');
  userMsg.className = 'chat-msg msg-user';
  userMsg.innerHTML = `<div class="msg-bubble"><p>${text}</p></div>`;
  chatContainer.appendChild(userMsg);
  input.value = '';
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Query Backend Assistant API
  try {
    const res = await fetch('/api/v1/assistant/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, language: assistantLang })
    });
    const data = await res.json();

    const replyMsg = document.createElement('div');
    replyMsg.className = 'chat-msg msg-assistant';
    replyMsg.innerHTML = `
      <div class="msg-bubble">
        <div class="msg-author">🌱 AgriVision AI</div>
        <p>${data.reply}</p>
        <button class="btn-msg-audio" onclick="playVoiceText('${data.reply.replace(/'/g, "\\'")}')">
          🔊 Listen (${assistantLang === 'ta' ? 'தமிழ்' : 'EN'})
        </button>
      </div>
    `;
    chatContainer.appendChild(replyMsg);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  } catch (err) {
    // Local fallback response
    const replyMsg = document.createElement('div');
    replyMsg.className = 'chat-msg msg-assistant';
    const fallbackText = assistantLang === 'ta'
      ? 'தக்காளியில் ஆரம்பகால கருகல் நோயைக் கட்டுப்படுத்த, கீழ் இலைகளை வெட்டி தழைக்கூளம் இடவும். அதிகப்படியான தெளிப்பு நீரை தவிர்க்கவும்.'
      : 'For early blight in tomato, remove lower infected foliage and apply organic mulch. Ensure proper canopy ventilation.';
    
    replyMsg.innerHTML = `
      <div class="msg-bubble">
        <div class="msg-author">🌱 AgriVision AI</div>
        <p>${fallbackText}</p>
        <button class="btn-msg-audio" onclick="playVoiceText('${fallbackText}')">🔊 Listen</button>
      </div>
    `;
    chatContainer.appendChild(replyMsg);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
}

// -------------------------------------------------------------
// Fetch Backend Data (Crops, Weather, Inspections)
// -------------------------------------------------------------
async function fetchInitialData() {
  try {
    // 1. Fetch Supported Crops
    const cropsRes = await fetch('/api/v1/crops/supported');
    if (cropsRes.ok) {
      const data = await cropsRes.json();
      supportedCropsData = data.crops || [];
      renderCropsCatalog(data.registry || {});
    }

    // 2. Fetch Recent Inspections
    const inspRes = await fetch('/api/v1/inspections/?limit=8');
    if (inspRes.ok) {
      const data = await inspRes.json();
      recentInspectionsData = data.inspections || [];
      renderInspectionsTable(recentInspectionsData);
      renderMobileInspections(recentInspectionsData);
    }

    // 3. Fetch Weather & Risk
    const weatherRes = await fetch('/api/v1/weather/risk');
    if (weatherRes.ok) {
      const data = await weatherRes.json();
      renderWeatherData(data);
    }
  } catch (e) {
    console.warn('Initial data load fallback:', e);
    // Render defaults if backend is just launching
    renderDefaultInspections();
  }
}

function renderCropsCatalog(registry) {
  const container = document.getElementById('cropCatalogChips');
  if (!container) return;
  container.innerHTML = '';

  const cropNames = ['Tomato', 'Potato', 'Rice', 'Cotton', 'Maize', 'Pepper', 'Apple'];
  cropNames.forEach((crop, idx) => {
    const btn = document.createElement('button');
    btn.className = `crop-chip-btn ${idx === 0 ? 'active' : ''}`;
    btn.textContent = `🌱 ${crop}`;
    btn.onclick = () => {
      document.querySelectorAll('.crop-chip-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      showCropDiseases(crop, registry);
    };
    container.appendChild(btn);
  });

  showCropDiseases('Tomato', registry);
}

function showCropDiseases(crop, registry) {
  const detail = document.getElementById('cropDiseaseDetail');
  if (!detail) return;

  const filtered = Object.entries(registry).filter(([k, v]) => v.crop === crop);
  
  if (filtered.length === 0) {
    detail.innerHTML = `<p>Active AI model trained for <strong>${crop}</strong> foliar classification & defect detection.</p>`;
    return;
  }

  let html = `<h4 style="color:#ffffff; margin-bottom: 8px;">Diseases Monitored for ${crop}:</h4><ul style="list-style:none; padding:0; display:flex; flex-direction:column; gap:6px;">`;
  filtered.forEach(([k, d]) => {
    html += `
      <li style="font-size:12px; color:#cbd5e1; background:rgba(255,255,255,0.04); padding:6px 10px; border-radius:6px;">
        <strong style="color:#4ade80;">${d.display_name}</strong> • <span style="font-family:var(--font-ta); color:#94a3b8;">${d.display_name_ta || ''}</span>
        <div style="font-size:11px; color:#94a3b8; margin-top:2px;">Pathogen: ${d.pathogen}</div>
      </li>
    `;
  });
  html += `</ul>`;
  detail.innerHTML = html;
}

function renderInspectionsTable(list) {
  const tbody = document.getElementById('inspectionsTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  list.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><img src="${item.image_url || '/static/img/leaf_placeholder.png'}" class="table-thumb" alt="leaf" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'42\\' height=\\'42\\'><rect width=\\'100%\\' height=\\'100%\\' fill=\\'%2315803d\\'/></svg>'"></td>
      <td>
        <span class="table-crop-badge">${item.crop_name}</span>
        <div style="font-size:11px; color:#64748b;">Plot 1A</div>
      </td>
      <td>
        <strong>${item.disease_predicted}</strong>
        <div style="font-size:11px; color:#94a3b8; font-family:var(--font-ta);">${item.disease_predicted_ta || ''}</div>
      </td>
      <td>
        <span class="table-sev-pill ${item.severity_pct > 20 ? 'sev-high' : 'sev-med'}">
          ${item.severity_pct ? item.severity_pct.toFixed(1) : 0.0}%
        </span>
      </td>
      <td>${((item.confidence || 0.9) * 100).toFixed(0)}%</td>
      <td style="color:#94a3b8; font-size:11px;">${new Date(item.created_at).toLocaleDateString()}</td>
      <td>
        <button class="btn-table-action" onclick="openInspectionDetail('tomato_early_blight')">Inspect</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderMobileInspections(list) {
  const mList = document.getElementById('mInspectionsList');
  if (!mList) return;
  mList.innerHTML = '';

  list.slice(0, 4).forEach(item => {
    const div = document.createElement('div');
    div.className = 'm-insp-item';
    div.onclick = () => openInspectionDetail('tomato_early_blight');
    div.innerHTML = `
      <img src="${item.image_url || '/static/img/leaf_placeholder.png'}" class="m-insp-thumb" alt="leaf" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'54\\' height=\\'54\\'><rect width=\\'100%\\' height=\\'100%\\' fill=\\'%2315803d\\'/></svg>'">
      <div class="m-insp-details">
        <div class="m-insp-crop-row">
          <span class="m-insp-crop-badge">${item.crop_name}</span>
          <span style="color:#94a3b8;">${new Date(item.created_at).toLocaleDateString()}</span>
        </div>
        <div class="m-insp-disease">${item.disease_predicted}</div>
        <div class="m-insp-disease-ta">${item.disease_predicted_ta || ''}</div>
        <div class="m-insp-footer">
          <span class="m-sev-badge ${item.severity_pct > 20 ? 'sev-high' : 'sev-med'}">
            Severity: ${item.severity_pct ? item.severity_pct.toFixed(1) : 0}%
          </span>
          <span style="font-size:10px; color:#64748b;">${((item.confidence || 0.9) * 100).toFixed(0)}% Conf.</span>
        </div>
      </div>
    `;
    mList.appendChild(div);
  });
}

function renderDefaultInspections() {
  const defaults = [
    { crop_name: 'Tomato', disease_predicted: 'Tomato Early Blight', disease_predicted_ta: 'தக்காளி ஆரம்பகால கருகல் நோய்', severity_pct: 18.4, confidence: 0.94, created_at: new Date().toISOString() },
    { crop_name: 'Potato', disease_predicted: 'Late Blight (Phytophthora)', disease_predicted_ta: 'உருளைக்கிழங்கு பிந்தைய கருகல் நோய்', severity_pct: 26.8, confidence: 0.96, created_at: new Date().toISOString() },
    { crop_name: 'Rice', disease_predicted: 'Rice Leaf Blast', disease_predicted_ta: 'நெல் இலை குலை நோய்', severity_pct: 14.2, confidence: 0.91, created_at: new Date().toISOString() },
    { crop_name: 'Cotton', disease_predicted: 'Cotton Leaf Curl Virus', disease_predicted_ta: 'பருத்தி இலை சுருள் நச்சுயிரி', severity_pct: 21.0, confidence: 0.89, created_at: new Date().toISOString() }
  ];
  renderInspectionsTable(defaults);
  renderMobileInspections(defaults);
}

function renderWeatherData(data) {
  if (!data || !data.current) return;
  const c = data.current;

  document.getElementById('dashTemp').textContent = `${c.temperature_c} °C`;
  document.getElementById('dashHumidity').textContent = `${c.relative_humidity_pct} %`;
  document.getElementById('dashWetness').textContent = `${c.leaf_wetness_hours} hrs`;
  document.getElementById('dashRain').textContent = `${c.precipitation_mm} mm`;
  document.getElementById('dashWind').textContent = `${c.wind_speed_kmh} km/h`;

  // Render 5-day forecast
  const mForecast = document.getElementById('mForecastList');
  if (mForecast && data.forecast) {
    mForecast.innerHTML = '';
    data.forecast.forEach(d => {
      const item = document.createElement('div');
      item.className = 'm-forecast-item';
      item.innerHTML = `
        <div>
          <div class="m-f-day">${d.day_name}</div>
          <div class="m-f-sub">${d.date.substring(5)}</div>
        </div>
        <div>
          <div class="m-f-temp">${d.temp_min}° - ${d.temp_max}°C</div>
          <div class="m-f-rain">💧 ${d.rain_probability_pct}% rain</div>
        </div>
        <span class="chip ${d.overall_risk === 'HIGH' ? 'chip-warning' : 'chip-success'}">${d.overall_risk}</span>
      `;
      mForecast.appendChild(item);
    });
  }
}
