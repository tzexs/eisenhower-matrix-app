import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

// English translations
const TEXTS = {
  QUADRANT_DO: 'Urgent / Important',
  QUADRANT_SCHEDULE: 'Not Urgent / Important',
  QUADRANT_DELEGATE: 'Urgent / Not Important',
  QUADRANT_DELETE: 'Not Urgent / Not Important',
  APP_TITLE: 'Eisenhower Matrix',
  MANAGE_LABELS_BUTTON: 'Manage Labels',
  MANAGE_LABELS_MODAL_TITLE: 'Manage Labels',
  NEW_LABEL_NAME_PLACEHOLDER: 'New label name',
  ADD_LABEL_BUTTON: 'Add Label',
  EXISTING_LABELS_TITLE: 'Existing Labels:',
  NO_LABELS_CREATED_MODAL_MESSAGE: 'No labels created yet.',
  DELETE_BUTTON: 'Delete',
  CLOSE_BUTTON: 'Close',
  NEW_TASK_PLACEHOLDER: 'New task...',
  ASSIGN_LABELS_TITLE: 'Assign Labels:',
  NO_LABELS_FOR_TASK_MESSAGE: 'No labels created. Create labels in "Manage Labels".',
  ADD_TASK_BUTTON: 'Add Task',
  EMPTY_QUADRANT_MESSAGE: 'No tasks here.',
  LABEL_ALREADY_EXISTS_ALERT: 'This label already exists.',
  CREATE_NEW_MATRIX_BUTTON: 'Create New Shared Matrix',
  LOADING_MATRIX_MESSAGE: 'Loading Matrix...',
  ERROR_LOADING_MATRIX_MESSAGE: 'Error loading matrix. Please try creating a new one or check the URL.',
  MATRIX_ID_DISPLAY_LABEL: 'Current Matrix ID (Share this part of the URL):',
};

const QUADRANTS = {
  DO: TEXTS.QUADRANT_DO,
  SCHEDULE: TEXTS.QUADRANT_SCHEDULE,
  DELEGATE: TEXTS.QUADRANT_DELEGATE,
  DELETE: TEXTS.QUADRANT_DELETE,
};

// Define quadrantKeyMapping at a scope accessible by all functions that need it
const quadrantKeyMapping = {
  [TEXTS.QUADRANT_DO]: "urgent_important",
  [TEXTS.QUADRANT_SCHEDULE]: "not_urgent_important",
  [TEXTS.QUADRANT_DELEGATE]: "urgent_not_important",
  [TEXTS.QUADRANT_DELETE]: "not_urgent_not_important",
};

const API_BASE_URL = "https://eisenhower-matrix-7f482024b5b8.herokuapp.com/api/v1"; // Backend API URL
const POLLING_INTERVAL = 5000; // 5 seconds

function App() {
  const [matrixId, setMatrixId] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [managedLabels, setManagedLabels] = useState([]);
  
  const [newTaskText, setNewTaskText] = useState('');
  const [newTaskQuadrant, setNewTaskQuadrant] = useState(QUADRANTS.DO);
  const [newTaskLabels, setNewTaskLabels] = useState([]); // Stores selected label IDs for a new task
  const [showLabelModal, setShowLabelModal] = useState(false);
  const [newLabelNameInput, setNewLabelNameInput] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [shareableLink, setShareableLink] = useState('');

  const fetchMatrixData = useCallback(async (currentMatrixId) => {
    if (!currentMatrixId) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/matrices/${currentMatrixId}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Matrix with ID ${currentMatrixId} not found. You can create a new one.`);
        }
        throw new Error(`Failed to fetch matrix data: ${response.statusText}`);
      }
      const data = await response.json();
      setTasks(data.tasks || []);
      setManagedLabels(data.labels || []);
    } catch (err) {
      console.error("Error fetching matrix data:", err);
      setError(err.message);
      setTasks([]);
      setManagedLabels([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const pathParts = window.location.pathname.split('/');
    const idFromUrl = pathParts.length === 3 && pathParts[1] === 'matrix' ? pathParts[2] : null;

    if (idFromUrl) {
      setMatrixId(idFromUrl);
      setShareableLink(window.location.href);
    } 
  }, []);

  useEffect(() => {
    if (matrixId) {
      fetchMatrixData(matrixId);
    }
  }, [matrixId, fetchMatrixData]);

  useEffect(() => {
    if (!matrixId) return;
    const intervalId = setInterval(() => {
      fetchMatrixData(matrixId);
    }, POLLING_INTERVAL);
    return () => clearInterval(intervalId);
  }, [matrixId, fetchMatrixData]);

  const handleCreateNewMatrix = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/matrices`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to create new matrix');
      }
      const data = await response.json();
      const newPath = `/matrix/${data.id}`;
      window.history.pushState({ path: newPath }, '', newPath);
      setMatrixId(data.id);
      setShareableLink(window.location.origin + newPath);
    } catch (err) {
      console.error("Error creating new matrix:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const addTask = async (e) => {
    e.preventDefault();
    if (!newTaskText.trim() || !matrixId) return;
    const taskPayload = {
      title: newTaskText,
      description: '',
      quadrant: quadrantKeyMapping[newTaskQuadrant],
      label_ids: newTaskLabels,
    };
    try {
      const response = await fetch(`${API_BASE_URL}/matrices/${matrixId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskPayload),
      });
      if (!response.ok) throw new Error('Failed to add task');
      setNewTaskText('');
      setNewTaskLabels([]);
      fetchMatrixData(matrixId);
    } catch (err) {
      console.error("Error adding task:", err);
      setError("Failed to add task. " + err.message);
    }
  };

  const updateTask = async (taskId, updates) => {
    if (!matrixId) return;
    try {
      const response = await fetch(`${API_BASE_URL}/matrices/${matrixId}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (!response.ok) throw new Error('Failed to update task');
      fetchMatrixData(matrixId);
    } catch (err) {
      console.error("Error updating task:", err);
      setError("Failed to update task. " + err.message);
    }
  };

  const deleteTask = async (taskId) => {
    if (!matrixId) return;
    try {
      const response = await fetch(`${API_BASE_URL}/matrices/${matrixId}/tasks/${taskId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete task');
      fetchMatrixData(matrixId);
    } catch (err) {
      console.error("Error deleting task:", err);
      setError("Failed to delete task. " + err.message);
    }
  };

  const moveTask = (taskId, newQuadrantName) => {
    updateTask(taskId, { quadrant: quadrantKeyMapping[newQuadrantName] });
  };

  const getTasksForQuadrant = (quadrantName) => {
    return tasks.filter((task) => task.quadrant === quadrantKeyMapping[quadrantName]);
  };

  const addManagedLabelHandler = async () => {
    if (!newLabelNameInput.trim() || !matrixId) return;
    const normalizedLabelName = newLabelNameInput.trim().toLowerCase();
    if (managedLabels.some(label => label.name.toLowerCase() === normalizedLabelName)) {
      alert(TEXTS.LABEL_ALREADY_EXISTS_ALERT);
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/matrices/${matrixId}/labels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newLabelNameInput.trim(), color: null }),
      });
      if (!response.ok) {
        if(response.status === 409) throw new Error(TEXTS.LABEL_ALREADY_EXISTS_ALERT);
        throw new Error('Failed to add label');
      }
      setNewLabelNameInput('');
      fetchMatrixData(matrixId);
    } catch (err) {
      console.error("Error adding label:", err);
      setError(err.message);
    }
  };

  const deleteManagedLabel = async (labelId) => {
    if (!matrixId) return;
    try {
      const response = await fetch(`${API_BASE_URL}/matrices/${matrixId}/labels/${labelId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete label');
      fetchMatrixData(matrixId);
      setNewTaskLabels(prev => prev.filter(id => id !== labelId));
    } catch (err) {
      console.error("Error deleting label:", err);
      setError("Failed to delete label. " + err.message);
    }
  };

  const handleNewLabelSelection = (labelId) => {
    setNewTaskLabels(prev =>
      prev.includes(labelId)
        ? prev.filter(id => id !== labelId)
        : [...prev, labelId]
    );
  };

  if (!matrixId && !isLoading) {
    return (
      <div className="app-container centered-prompt">
        <h1>{TEXTS.APP_TITLE}</h1>
        {error && <p className="error-message">Error: {error}</p>}
        <p>Welcome! To start, create a new shared Eisenhower Matrix.</p>
        <button onClick={handleCreateNewMatrix} className="create-matrix-button">
          {TEXTS.CREATE_NEW_MATRIX_BUTTON}
        </button>
      </div>
    );
  }
  
  return (
    <div className="app-container">
      <h1>{TEXTS.APP_TITLE}</h1>
      {matrixId && <p className="matrix-id-display">{TEXTS.MATRIX_ID_DISPLAY_LABEL} <code>{matrixId}</code></p>}

      {isLoading && <p>{TEXTS.LOADING_MATRIX_MESSAGE}</p>}
      {error && <p className="error-message">Error: {error}</p>}

      {!isLoading && matrixId && (
        <>
          <button onClick={() => setShowLabelModal(true)} className="manage-labels-button">
            {TEXTS.MANAGE_LABELS_BUTTON}
          </button>

          {showLabelModal && (
            <div className="label-management-section modal">
              <h2>{TEXTS.MANAGE_LABELS_MODAL_TITLE}</h2>
              <input 
                type="text" 
                value={newLabelNameInput}
                onChange={(e) => setNewLabelNameInput(e.target.value)}
                placeholder={TEXTS.NEW_LABEL_NAME_PLACEHOLDER} 
              />
              <button onClick={addManagedLabelHandler}>{TEXTS.ADD_LABEL_BUTTON}</button>
              <h4>{TEXTS.EXISTING_LABELS_TITLE}</h4>
              {managedLabels.length === 0 && <p>{TEXTS.NO_LABELS_CREATED_MODAL_MESSAGE}</p>}
              <ul>
                {managedLabels.map(label => (
                  <li key={label.id}>
                    {label.name}
                    <button onClick={() => deleteManagedLabel(label.id)} className="delete-label-button">{TEXTS.DELETE_BUTTON}</button>
                  </li>
                ))}
              </ul>
              <button onClick={() => setShowLabelModal(false)} style={{ marginTop: '15px' }}>{TEXTS.CLOSE_BUTTON}</button>
            </div>
          )}

          <form onSubmit={addTask} className="task-form">
            <input
              type="text"
              value={newTaskText}
              onChange={(e) => setNewTaskText(e.target.value)}
              placeholder={TEXTS.NEW_TASK_PLACEHOLDER}
              className="task-input"
            />
            <select
              value={newTaskQuadrant}
              onChange={(e) => setNewTaskQuadrant(e.target.value)}
              className="quadrant-select"
            >
              {Object.values(QUADRANTS).map((quadrantDisplayName) => (
                <option key={quadrantDisplayName} value={quadrantDisplayName}>
                  {quadrantDisplayName}
                </option>
              ))}
            </select>
            
            <div className="new-task-labels-selector">
              <p>{TEXTS.ASSIGN_LABELS_TITLE}</p>
              {managedLabels.length === 0 && <small>{TEXTS.NO_LABELS_FOR_TASK_MESSAGE}</small>}
              {managedLabels.map(label => (
                <label key={label.id}>
                  <input
                    type="checkbox"
                    checked={newTaskLabels.includes(label.id)}
                    onChange={() => handleNewLabelSelection(label.id)}
                  />
                  {label.name}
                </label>
              ))}
            </div>
            <button type="submit" className="add-button">{TEXTS.ADD_TASK_BUTTON}</button>
          </form>

          <div className="matrix-container">
            {Object.entries(QUADRANTS).map(([key, quadrantName]) => (
              <div key={key} className={`quadrant quadrant-${key.toLowerCase()}`}>
                <h2>{quadrantName}</h2>
                {getTasksForQuadrant(quadrantName).length === 0 && <p className="empty-quadrant-message">{TEXTS.EMPTY_QUADRANT_MESSAGE}</p>}
                <ul>
                  {getTasksForQuadrant(quadrantName).map((task) => (
                    <li key={task.id}>
                      <div className="task-details">
                        <div className="task-content">
                          <span className="task-text">{task.title}</span>
                        </div>                    
                      </div>
                      {task.labels && task.labels.length > 0 && (
                        <div className="task-labels-display">
                          {task.labels.map(labelObj => (
                            <span key={labelObj.id} className={`task-label-pill label-${labelObj.name.toLowerCase().replace(/\s+/g, '-')}`}>
                              {labelObj.name}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="task-actions">
                        <select
                          value={Object.keys(QUADRANTS).find(qKey => quadrantKeyMapping[QUADRANTS[qKey]] === task.quadrant) ? QUADRANTS[Object.keys(QUADRANTS).find(qKey => quadrantKeyMapping[QUADRANTS[qKey]] === task.quadrant)] : ''}
                          onChange={(e) => moveTask(task.id, e.target.value)}
                          className="task-quadrant-select"
                        >
                          {Object.values(QUADRANTS).map(qDisplayName =>
                            <option key={`${task.id}-${qDisplayName}`} value={qDisplayName}>{qDisplayName.split(' / ')[0]}</option>
                          )}
                        </select>
                        <button onClick={() => deleteTask(task.id)} className="delete-button">{TEXTS.DELETE_BUTTON}</button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;

