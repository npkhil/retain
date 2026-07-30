(function () {
  const uploadForm = document.getElementById('uploadForm');
  const fileInput = document.getElementById('fileInput');
  const questionCount = document.getElementById('questionCount');
  const submitBtn = document.getElementById('submitBtn');
  const uploadStatus = document.getElementById('uploadStatus');

  const uploadPanel = document.getElementById('uploadPanel');
  const quizPanel = document.getElementById('quizPanel');
  const quizProgress = document.getElementById('quizProgress');
  const quizCard = document.getElementById('quizCard');
  const quizQuestion = document.getElementById('quizQuestion');
  const quizAnswer = document.getElementById('quizAnswer');
  const revealBtn = document.getElementById('revealBtn');
  const nextBtn = document.getElementById('nextBtn');
  const quizFinish = document.getElementById('quizFinish');
  const restartBtn = document.getElementById('restartBtn');

  let questions = [];
  let index = 0;

  function setStatus(message, isError) {
    uploadStatus.textContent = message || '';
    uploadStatus.classList.toggle('error', Boolean(isError));
  }

  uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const file = fileInput.files[0];
    if (!file) {
      setStatus('Choose a file first.', true);
      return;
    }

    submitBtn.disabled = true;
    try {
      setStatus('Uploading...');
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData });
      const uploadJson = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(uploadJson.error || 'Upload failed');

      setStatus('Generating questions... this can take a few seconds.');
      const genRes = await fetch('/api/questions/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: uploadJson.file_id,
          count: Number(questionCount.value) || 10,
        }),
      });
      const genJson = await genRes.json();
      if (!genRes.ok) throw new Error(genJson.error || 'Question generation failed');
      if (!genJson.questions || genJson.questions.length === 0) {
        throw new Error('No questions were generated for this file.');
      }

      setStatus('');
      startQuiz(genJson.questions);
    } catch (error) {
      setStatus('Error: ' + error.message, true);
    } finally {
      submitBtn.disabled = false;
    }
  });

  function startQuiz(newQuestions) {
    questions = newQuestions;
    index = 0;
    uploadPanel.hidden = true;
    quizPanel.hidden = false;
    quizFinish.hidden = true;
    quizCard.hidden = false;
    document.querySelector('.quiz-controls').hidden = false;
    renderCard();
  }

  function renderCard() {
    const current = questions[index];
    quizQuestion.textContent = current.question;
    quizAnswer.textContent = current.answer;
    quizAnswer.hidden = true;
    nextBtn.disabled = true;
    quizProgress.textContent = `Question ${index + 1} / ${questions.length}`;
  }

  revealBtn.addEventListener('click', () => {
    quizAnswer.hidden = false;
    nextBtn.disabled = false;
  });

  nextBtn.addEventListener('click', () => {
    index += 1;
    if (index >= questions.length) {
      quizCard.hidden = true;
      document.querySelector('.quiz-controls').hidden = true;
      quizProgress.textContent = '';
      quizFinish.hidden = false;
    } else {
      renderCard();
    }
  });

  restartBtn.addEventListener('click', () => {
    questions = [];
    index = 0;
    uploadForm.reset();
    setStatus('');
    quizPanel.hidden = true;
    uploadPanel.hidden = false;
  });
})();
