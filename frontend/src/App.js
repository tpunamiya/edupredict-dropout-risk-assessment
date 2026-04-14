import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // Form state - stores user input
  const [formData, setFormData] = useState({
    age: 15,
    gender: 'male',
    attendance_rate: 80,
    previous_grade: 'B',
    distance_to_school: 3,
    parent_education: 'secondary',
    household_income: 'medium'
  });

  // Prediction result state
  const [prediction, setPrediction] = useState(null);
  
  // Loading state
  const [loading, setLoading] = useState(false);
  
  // Error state
  const [error, setError] = useState(null);

  // History state
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Stats state
  const [stats, setStats] = useState(null);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'age' || name === 'attendance_rate' || name === 'distance_to_school' 
        ? parseFloat(value) 
        : value
    }));
  };

  // Submit prediction
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://localhost:8000/predict', formData);
      setPrediction(response.data);
      // Refresh stats after new prediction
      fetchStats();
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed. Please check your input.');
      console.error('Error:', err);
    }
    
    setLoading(false);
  };

  // Fetch prediction history
  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/history?limit=20');
      setHistory(response.data.predictions);
      setShowHistory(true);
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/history/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  // Load stats on component mount
  React.useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>📚 EduPredict</h1>
        <p className="subtitle">Student Dropout Risk Assessment System</p>
      </header>

      <div className="container">
        {/* Navigation */}
        <div className="nav-buttons">
          <button 
            className={!showHistory ? 'active' : ''} 
            onClick={() => setShowHistory(false)}
          >
            New Prediction
          </button>
          <button 
            className={showHistory ? 'active' : ''} 
            onClick={fetchHistory}
          >
            View History
          </button>
        </div>

        {/* Stats Bar */}
        {stats && (
          <div className="stats-bar">
            <div className="stat-item">
              <span className="stat-label">Total Predictions</span>
              <span className="stat-value">{stats.total_predictions}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">High Risk</span>
              <span className="stat-value risk-high">{stats.risk_distribution.high}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Medium Risk</span>
              <span className="stat-value risk-medium">{stats.risk_distribution.medium}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Low Risk</span>
              <span className="stat-value risk-low">{stats.risk_distribution.low}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Risk Score</span>
              <span className="stat-value">{(stats.average_risk_score * 100).toFixed(1)}%</span>
            </div>
          </div>
        )}

        {/* Prediction Form or History View */}
        {!showHistory ? (
          <div className="main-content">
            <div className="form-section">
              <h2>Student Information</h2>
              {error && <div className="error-message">{error}</div>}
              
              <form onSubmit={handleSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Age</label>
                    <input 
                      type="number" 
                      name="age" 
                      value={formData.age} 
                      onChange={handleChange}
                      min="10"
                      max="20"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Gender</label>
                    <select name="gender" value={formData.gender} onChange={handleChange}>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Attendance Rate (%)</label>
                    <input 
                      type="number" 
                      name="attendance_rate" 
                      value={formData.attendance_rate} 
                      onChange={handleChange}
                      min="0"
                      max="100"
                      step="0.1"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Previous Grade</label>
                    <select name="previous_grade" value={formData.previous_grade} onChange={handleChange}>
                      <option value="A">A</option>
                      <option value="B">B</option>
                      <option value="C">C</option>
                      <option value="D">D</option>
                      <option value="F">F</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Distance to School (km)</label>
                    <input 
                      type="number" 
                      name="distance_to_school" 
                      value={formData.distance_to_school} 
                      onChange={handleChange}
                      min="0"
                      step="0.1"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Parent Education</label>
                    <select name="parent_education" value={formData.parent_education} onChange={handleChange}>
                      <option value="none">None</option>
                      <option value="primary">Primary</option>
                      <option value="secondary">Secondary</option>
                      <option value="higher">Higher</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Household Income</label>
                  <select name="household_income" value={formData.household_income} onChange={handleChange}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <button type="submit" className="submit-button" disabled={loading}>
                  {loading ? 'Predicting...' : 'Predict Dropout Risk'}
                </button>
              </form>
            </div>

            {/* Prediction Results */}
            {prediction && (
              <div className="results-section">
                <h2>Prediction Results</h2>
                
                <div className={`risk-badge risk-${prediction.risk_category}`}>
                  <div className="risk-label">{prediction.risk_category.toUpperCase()} RISK</div>
                  <div className="risk-score">{(prediction.risk_score * 100).toFixed(1)}%</div>
                </div>

                <div className="prediction-details">
                  <div className="detail-item">
                    <span className="detail-label">Confidence:</span>
                    <span className="detail-value">{(prediction.confidence * 100).toFixed(1)}%</span>
                  </div>
                  
                  <div className="detail-item">
                    <span className="detail-label">Prediction ID:</span>
                    <span className="detail-value">#{prediction.prediction_id}</span>
                  </div>
                </div>

                <div className="risk-factors">
                  <h3>Top Risk Factors</h3>
                  <ul>
                    {prediction.top_risk_factors.map((factor, idx) => (
                      <li key={idx}>{factor}</li>
                    ))}
                  </ul>
                </div>

                <div className="recommendations">
                  <h3>Recommended Actions</h3>
                  {prediction.risk_category === 'high' && (
                    <ul>
                      <li>Schedule immediate counseling session</li>
                      <li>Contact parents/guardians</li>
                      <li>Develop personalized intervention plan</li>
                      <li>Assign mentor or buddy support</li>
                    </ul>
                  )}
                  {prediction.risk_category === 'medium' && (
                    <ul>
                      <li>Monitor attendance closely</li>
                      <li>Provide additional academic support</li>
                      <li>Regular check-ins with student</li>
                      <li>Engage parents in support plan</li>
                    </ul>
                  )}
                  {prediction.risk_category === 'low' && (
                    <ul>
                      <li>Continue current support level</li>
                      <li>Periodic monitoring recommended</li>
                      <li>Celebrate and encourage progress</li>
                    </ul>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          /* History View */
          <div className="history-section">
            <h2>Prediction History ({history.length} records)</h2>
            {history.length === 0 ? (
              <p>No predictions yet. Make your first prediction!</p>
            ) : (
              <div className="history-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Age</th>
                      <th>Gender</th>
                      <th>Attendance</th>
                      <th>Grade</th>
                      <th>Risk Score</th>
                      <th>Category</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((pred) => (
                      <tr key={pred.id} className={`row-${pred.risk_category}`}>
                        <td>{pred.id}</td>
                        <td>{pred.age}</td>
                        <td>{pred.gender}</td>
                        <td>{pred.attendance_rate}%</td>
                        <td>{pred.previous_grade}</td>
                        <td>{(pred.risk_score * 100).toFixed(1)}%</td>
                        <td>
                          <span className={`badge-small risk-${pred.risk_category}`}>
                            {pred.risk_category}
                          </span>
                        </td>
                        <td>{new Date(pred.timestamp).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;