const API_BASE_URL = 'http://127.0.0.1:8000/api/';

function $id(id) {
  const el = document.getElementById(id);
  if (!el) {
    console.warn(`Warning: element with id '${id}' not found in DOM.`);
  }
  return el;
}

function getTaskData() {
  const textarea = $id('jsonInput');
  if (!textarea) throw new Error("Internal: input textarea not found (jsonInput).");
  const jsonInput = textarea.value;
  if (!jsonInput || !jsonInput.trim()) {
    throw new Error("JSON input cannot be empty.");
  }
  try {
    const tasks = JSON.parse(jsonInput);
    if (!Array.isArray(tasks) || tasks.length === 0) {
      throw new Error("Input must be a non-empty JSON array of tasks.");
    }
    tasks.forEach(task => {
      if (!task.title || !task.due_date || task.estimated_hours === undefined || task.importance === undefined) {
        throw new Error("Each task must have 'title', 'due_date', 'estimated_hours', and 'importance'.");
      }
      if (task.importance < 1 || task.importance > 10) {
        throw new Error(`Importance for task '${task.title}' must be between 1 and 10.`);
      }
    });
    return tasks;
  } catch (e) {
    throw new Error("Invalid JSON format or missing required fields: " + e.message);
  }
}

function getPriorityClass(score, strategy) {
  if (strategy !== 'smart' && strategy !== 'suggest') return 'medium';
  if (score > 1.5) return 'critical';
  if (score > 1.0) return 'high';
  if (score > 0.5) return 'medium';
  return 'low';
}

function renderTasks(tasks, strategy) {
  const container = $id('resultsContainer');
  const placeholder = $id('placeholderMsg');
  if (!container) {
    console.error('resultsContainer missing — cannot render tasks.');
    return;
  }
  container.innerHTML = '';

  if (placeholder) placeholder.classList?.add('hidden');

  if (!tasks || tasks.length === 0) {
    container.innerHTML = '<p class="text-gray-500">No tasks found or all tasks filtered out.</p>';
    return;
  }

  tasks.forEach((task, index) => {
    const priorityLevel = getPriorityClass(task.priority_score || 0, strategy);
    const isSuggestion = strategy === 'suggest';

    const cardClasses = `task-card p-4 rounded-xl shadow-md border-l-4 priority-${priorityLevel}-bg priority-${priorityLevel}-border`;

    const card = document.createElement('div');
    card.className = cardClasses;

    let explanationHTML = '';
    if (task.explanation) {
      explanationHTML = `
        <div class="mt-3 pt-2 border-t border-gray-300">
          <p class="font-semibold text-sm text-gray-700">Reasoning:</p>
          <p class="text-xs text-gray-600">${task.explanation}</p>
        </div>
      `;
    }

    const taskDetails = isSuggestion ? '' : `
      <div class="mt-2 text-sm text-gray-700 grid grid-cols-2 gap-x-4">
          <p><strong>Due:</strong> ${task.due_date || 'N/A'}</p>
          <p><strong>Effort:</strong> ${task.estimated_hours || 'N/A'} hrs</p>
          <p><strong>Importance:</strong> ${task.importance || 'N/A'}/10</p>
          <p><strong>Dependencies:</strong> ${Array.isArray(task.dependencies) ? (task.dependencies.join(', ') || 'None') : (task.dependencies || 'None')}</p>
      </div>
    `;

    card.innerHTML = `
      <div class="flex justify-between items-start">
        <div class="flex flex-col">
          <h3 class="text-lg font-bold text-gray-800">${index + 1}. ${task.title}</h3>
          ${typeof task.priority_score === 'number' ? `<p class="text-sm font-mono mt-1 text-gray-600">Score: ${task.priority_score.toFixed(4)}</p>` : ''}
        </div>
        <span class="inline-block px-3 py-1 text-xs font-semibold rounded-full uppercase shadow-inner ${priorityLevel === 'critical' ? 'bg-red-700 text-white' : priorityLevel === 'high' ? 'bg-red-400 text-red-900' : priorityLevel === 'medium' ? 'bg-yellow-400 text-yellow-900' : 'bg-green-400 text-green-900'}">
          ${priorityLevel.charAt(0).toUpperCase() + priorityLevel.slice(1)} Priority
        </span>
      </div>
      ${taskDetails}
      ${explanationHTML}
    `;
    container.appendChild(card);
  });

  if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
    try { lucide.createIcons(); } catch (e) { console.warn('lucide.createIcons failed', e); }
  }
}

async function analyzeTasks() {
  const analyzeBtn = $id('analyzeBtn');
  const loadingMessage = $id('loadingMessage');
  const errorMessage = $id('errorMessage');
  const strategyEl = $id('sortStrategy');

  if (!analyzeBtn) { console.error('analyzeBtn not found'); return; }
  if (!strategyEl) { console.error('sortStrategy not found'); return; }

  try {
    if (errorMessage) { errorMessage.classList?.add('hidden'); errorMessage.textContent = ''; }
    analyzeBtn.disabled = true;
    if (loadingMessage) loadingMessage.classList?.remove('hidden');

    const tasks = getTaskData();

    let endpoint = strategyEl.value === 'suggest' ? 'tasks/suggest/' : 'tasks/analyze/';
    const url = API_BASE_URL + endpoint;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tasks),
    });

    if (!response.ok) {
      let errorText = await response.text();
      try {
        const errObj = JSON.parse(errorText);
        errorText = errObj.error || errObj.detail || JSON.stringify(errObj);
      } catch {}
      throw new Error(`API returned status ${response.status}. Details: ${errorText}`);
    }

    const data = await response.json();
    let sortedTasks = data;

    const strategy = strategyEl.value;
    if (strategy !== 'suggest' && strategy !== 'smart') {
      if (strategy === 'fastest') {
        sortedTasks.sort((a, b) => (a.estimated_hours || 0) - (b.estimated_hours || 0));
      } else if (strategy === 'highimpact') {
        sortedTasks.sort((a, b) => (b.importance || 0) - (a.importance || 0));
      } else if (strategy === 'deadline') {
        sortedTasks.sort((a, b) => new Date(a.due_date || 9999999999999) - new Date(b.due_date || 9999999999999));
      }
    }

    renderTasks(sortedTasks, strategy);
  } catch (err) {
    console.error('Analysis Error:', err);
    const errorMessageEl = $id('errorMessage');
    if (errorMessageEl) {
      errorMessageEl.textContent = `Error: ${err.message}`;
      errorMessageEl.classList?.remove('hidden');
    }
    const container = $id('resultsContainer');
    if (container) container.innerHTML = '';
    const placeholder = $id('placeholderMsg');
    if (placeholder) placeholder.classList?.remove('hidden');
  } finally {
    const analyzeBtnFinal = $id('analyzeBtn');
    if (analyzeBtnFinal) analyzeBtnFinal.disabled = false;
    const loadingMessageFinal = $id('loadingMessage');
    if (loadingMessageFinal) loadingMessageFinal.classList?.add('hidden');

    if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
      try { lucide.createIcons(); } catch (e) { }
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const analyzeBtn = $id('analyzeBtn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', analyzeTasks);
  } else {
    console.warn('analyzeBtn not found on DOMContentLoaded — click handler not attached.');
  }

  if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
    try { lucide.createIcons(); } catch (e) { console.warn('lucide init failed', e); }
  }
});

