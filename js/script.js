// --- Utilidades y estado ---
  const charactersEl = document.getElementById('characters');
  const themeEl = document.getElementById('theme');
  const characterInputEl = document.getElementById('characterInput');
  const toneEl = document.getElementById('tone');
  const generateBtn = document.getElementById('generateBtn');
  const storyBox = document.getElementById('storyBox');
  const wordCountEl = document.getElementById('wordCount');
  const ttsBtn = document.getElementById('ttsBtn');
  const pauseBtn = document.getElementById('pauseBtn');
  const resumeBtn = document.getElementById('resumeBtn');
  const stopBtn = document.getElementById('stopBtn');
  const statusEl = document.getElementById('status');
  const saveBtn = document.getElementById('saveBtn');
  const clearBtn = document.getElementById('clearBtn');
  const historyBtn = document.getElementById('historyBtn');

  let utterance;

  // --- Selección de personajes ---
  charactersEl.addEventListener('click', (e)=>{
    const btn = e.target.closest('.char-btn');
    if(!btn) return;
    document.querySelectorAll('.char-btn').forEach(b=>b.classList.remove('selected'));
    btn.classList.add('selected');
    characterInputEl.value = btn.dataset.char;
  });

  // --- Loader ---
  function setLoading(on){
    if(on){
      generateBtn.disabled = true;
      generateBtn.innerHTML = '<span class="loader"></span> Contando...';
      statusEl.innerHTML = '';
    } else {
      generateBtn.disabled = false;
      generateBtn.innerHTML = 'Contar';
    }
  }

  // --- Contador ---
  function countWords(text){
    if(!text) return 0;
    return text.trim().split(/\s+/).filter(Boolean).length;
  }

  // --- Narración (Web Speech API) ---
  function narrar(texto) {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();

      utterance = new SpeechSynthesisUtterance(texto);
      utterance.lang = 'es-ES';
      utterance.rate = 1;
      utterance.pitch = 1;

      utterance.onend = () => {
        pauseBtn.disabled = true;
        resumeBtn.disabled = true;
        stopBtn.disabled = true;
      };

      speechSynthesis.speak(utterance);
    } else {
      alert("Tu navegador no soporta narración");
    }
  }

  function pausarNarracion() {
    if (speechSynthesis.speaking && !speechSynthesis.paused) {
      speechSynthesis.pause();
    }
  }

  function reanudarNarracion() {
    if (speechSynthesis.paused) {
      speechSynthesis.resume();
    }
  }

  function detenerNarracion() {
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
    }
  }

  // --- Generar cuento ---
  async function generateStory(){
    const theme = themeEl.value.trim();
    const character = characterInputEl.value.trim() || 'Un personaje amigable';
    const tone = toneEl.value;

    if(!theme){ 
      alert('Dime de qué quieres el cuento (tema).'); 
      themeEl.focus(); 
      return; 
    }

    setLoading(true);
    wordCountEl.textContent = 'Palabras: —';
    ttsBtn.disabled = true;

    try{
      const payload = { tema: theme, personaje: character, tono: tone};
      const res = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });

      if(!res.ok){
        const txt = await res.text(); 
        throw new Error('Error servidor: '+res.status+' '+txt);
      }

      const data = await res.json();
      const story = data.cuento || '';

      storyBox.textContent = story;
      storyBox.scrollTop = 0;

      const wc = countWords(story);
      wordCountEl.textContent = 'Palabras: ' + wc;
      ttsBtn.disabled = !story;
      statusEl.innerHTML = 'Generado ✓';

      const last = { id: data.id || null, tema: theme, personaje: character, tono: tone, story, words: wc, created_at: new Date().toISOString() };
      localStorage.setItem('cc_last_interaction', JSON.stringify(last));
      
      await saveStory(story, theme, character, tone);

    } catch(err){
      console.error(err);
      statusEl.innerHTML = '<span style="color:#c33">Error</span>';
      storyBox.textContent = 'Ha ocurrido un error: ' + err.message;
    } finally { 
      setLoading(false); 
    }
  }

  async function saveStory(story, theme, character, tone) {
    try {
      await fetch('http://localhost:5000/save_iteration', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({personaje: character, tema: theme, tono: tone, cuento: story })
      });
    } catch(e){
      console.warn("No se pudo guardar la interacción:", e);
    }
  }

  // --- Guardar PDF ---
  saveBtn.addEventListener('click', async () => {
    const story = storyBox.innerText.trim();
    if (!story) return alert('No hay cuento para guardar');
    const theme = themeEl.value.trim();
    const character = characterInputEl.value.trim();
    const tone = toneEl.value;
    try {
      const res = await fetch('http://localhost:5000/download_pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme, character, tone, story })
      });
      if (!res.ok) throw new Error('Error al generar PDF');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cuento_${theme.replace(/ /g, "_")}_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Error generando el PDF: ' + err.message);
    }
  });

  // --- Control narración ---
  ttsBtn.addEventListener("click", () => {
    const texto = storyBox.textContent.trim();
    if (!texto) return alert("No hay cuento para narrar");
    narrar(texto);

    pauseBtn.disabled = false;
    stopBtn.disabled = false;
    resumeBtn.disabled = true;
  });

  pauseBtn.addEventListener("click", () => {
    pausarNarracion();
    pauseBtn.disabled = true;
    resumeBtn.disabled = false;
  });

  resumeBtn.addEventListener("click", () => {
    reanudarNarracion();
    resumeBtn.disabled = true;
    pauseBtn.disabled = false;
  });

  stopBtn.addEventListener("click", () => {
    detenerNarracion();
    pauseBtn.disabled = true;
    resumeBtn.disabled = true;
    stopBtn.disabled = true;
  });

  // --- Limpiar ---
  clearBtn.addEventListener('click', () => {
    storyBox.textContent = 'Aquí aparecerá el cuento...';
    wordCountEl.textContent = 'Palabras: —';
    ttsBtn.disabled = true;
    storyBox.scrollTop = 0;
    document.querySelectorAll('.char-btn').forEach(b=>b.classList.remove('selected'));
    characterInputEl.value = '';
    statusEl.innerHTML = '';
  });

  // --- Eventos ---
  generateBtn.addEventListener('click', generateStory);

  if (historyBtn) {
    historyBtn.addEventListener('click', ()=>{
      const local = JSON.parse(localStorage.getItem('cc_history_v1')||'[]');
      let msg = '';
      if(local.length) msg += 'Historial local:\n' + local.slice(0,6).map(h=>`${h.created_at} — ${h.theme} — ${h.character.substring(0,30)}...`).join('\n');
      else msg += 'No hay historial local.';
      alert(msg);
    });
  }