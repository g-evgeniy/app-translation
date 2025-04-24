// Voice Translator Web UI Logic
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const transcriptionField = document.getElementById('transcription');
const translationField = document.getElementById('translation');

let mediaRecorder;
let audioChunks = [];

startBtn.addEventListener('click', async () => {
  transcriptionField.value = '';
  translationField.value = '';
  audioChunks = [];
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('file', blob, 'recording.webm');
      const lang = navigator.language.split('-')[0] || 'en';
      formData.append('target_lang', lang);
      try {
        const response = await fetch('/api/translate', {
          method: 'POST',
          body: formData
        });
        if (!response.ok) {
          const err = await response.json();
          alert(`Error: ${err.detail || response.statusText}`);
          return;
        }
        const data = await response.json();
        transcriptionField.value = data.transcription || '';
        translationField.value = data.translation || '';
        if (data.translation) {
          try {
            await navigator.clipboard.writeText(data.translation);
          } catch (e) {
            console.error('Clipboard write failed', e);
          }
        }
      } catch (err) {
        alert('Translation request failed.');
        console.error(err);
      }
    };
    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (err) {
    alert('Could not start audio recording: ' + err.message);
    console.error(err);
  }
});

stopBtn.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
});
// After manual edits (on blur), re-translate the updated transcription
transcriptionField.addEventListener('blur', async () => {
  const text = transcriptionField.value.trim();
  if (!text) {
    translationField.value = '';
    transcriptionField.removeAttribute('redone');
    return;
  }
  try {
    const response = await fetch('/api/translate_text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!response.ok) {
      console.error('Re-translation error', await response.text());
    } else {
      const data = await response.json();
      translationField.value = data.translation || '';
      if (data.translation) {
        try {
          await navigator.clipboard.writeText(data.translation);
        } catch (e) {
          console.error('Clipboard write failed', e);
        }
      }
    }
  } catch (err) {
    console.error('Re-translation failed', err);
  } finally {
    transcriptionField.removeAttribute('redone');
  }
});