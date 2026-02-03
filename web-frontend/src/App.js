import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function App() {
  const [file, setFile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [chartKey, setChartKey] = useState(0); 

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first");
    
    setLoading(true);
    setUploadProgress(0);
    setStats(null); 
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      setTimeout(() => {
        setStats(res.data);
        setChartKey(prev => prev + 1); 
        setLoading(false);
      }, 500);

    } catch (err) {
      alert("Upload failed. Ensure the Django server is running.");
      setLoading(false);
    }
  };

  const performanceData = stats?.raw_data?.map(item => ({
    ...item,
    score: parseFloat((item['Temperature'] / item['Pressure']).toFixed(2)),
  })) || [];

  const filteredData = stats?.raw_data?.filter(item => 
    item['Equipment Name'].toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // DECORATED LANDING PAGE VIEW
  if (!stats && !loading) {
    return (
      <div style={heroContainerStyle}>
        <div style={heroCardStyle}>
          <h1 style={{ fontSize: '36px', fontWeight: '900', color: '#1a2a6c', marginBottom: '15px' }}>
            Chemical Equipment<br/>Parameter Visualizer
          </h1>
          <p style={{ color: '#64748b', fontSize: '16px', marginBottom: '35px', lineHeight: '1.6' }}>
            Harness industrial-grade analytics to monitor plant pressure, temperature, and flow metrics in real-time.
          </p>
          
          <div style={uploadBoxStyle}>
            <input 
              type="file" 
              id="file-upload"
              onChange={(e) => setFile(e.target.files[0])} 
              style={{ display: 'none' }}
            />
            <label htmlFor="file-upload" style={fileLabelStyle}>
              {file ? `📄 ${file.name}` : "📁 Choose CSV Dataset"}
            </label>
            
            <button onClick={handleUpload} style={heroBtnStyle}>
              Run Analysis →
            </button>
          </div>
          
          <div style={{ marginTop: '30px', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Supports .CSV datasets • Secure local processing
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#f4f7f9', minHeight: '100vh', padding: '20px', fontFamily: 'sans-serif' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        
        {/* SMALL HEADER FOR DASHBOARD MODE */}
        <div style={{ display: 'flex', justifyContent: 'space-between', backgroundColor: '#1a2a6c', padding: '15px 25px', borderRadius: '12px', color: 'white', marginBottom: '25px' }}>
          <h3 style={{ margin: 0 }}>Chemical Equipment Visualizer</h3>
          <button onClick={() => setStats(null)} style={{ background: 'rgba(255,255,255,0.1)', color: 'white', border: '1px solid rgba(255,255,255,0.3)', padding: '5px 15px', borderRadius: '6px', cursor: 'pointer' }}>
            Analyze New File
          </button>
        </div>

        {loading && (
          <div style={{ marginBottom: '25px' }}>
            <div style={{ color: '#1a2a6c', fontWeight: 'bold', marginBottom: '8px', fontSize: '14px' }}>
              Processing {file?.name}... {uploadProgress}%
            </div>
            <div style={{ width: '100%', backgroundColor: '#e0e0e0', borderRadius: '10px', height: '12px', overflow: 'hidden' }}>
              <div style={{ width: `${uploadProgress}%`, backgroundColor: '#1a2a6c', height: '100%', transition: 'width 0.4s ease-in-out' }}></div>
            </div>
          </div>
        )}

        {stats && (
          <div key={chartKey}> 
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '25px' }}>
              <Card title="Total Units" value={stats.total_count} icon="🏭" />
              <Card title="Avg Pressure" value={`${stats.avg_pressure} bar`} icon="🌡️" />
              <Card title="Max Temp" value={`${stats.max_temp} °C`} icon="🔥" />
              <Card title="Avg Flow" value={`${stats.avg_flowrate} m³/h`} icon="💧" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '25px', marginBottom: '25px' }}>
              <div style={panelStyle}>
                <Bar 
                  data={{ 
                    labels: Object.keys(stats.type_distribution), 
                    datasets: [{ 
                      label: 'Units', 
                      data: Object.values(stats.type_distribution), 
                      backgroundColor: ['#1a2a6c', '#b21f1f', '#006400', '#b8860b', '#4b0082', '#2f4f4f'],
                      borderRadius: 5 
                    }] 
                  }} 
                  options={{
                    animation: { 
                      duration: 2000, 
                      easing: 'easeOutQuart'
                    },
                    scales: { y: { beginAtZero: true, grid: { display: false } } },
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                  }}
                  height={300}
                />
              </div>
              <div style={panelStyle}>
                <Pie 
                  data={{ 
                    labels: Object.keys(stats.type_distribution), 
                    datasets: [{ 
                      data: Object.values(stats.type_distribution), 
                      backgroundColor: ['#1a2a6c', '#b21f1f', '#006400', '#b8860b'] 
                    }] 
                  }} 
                  options={{ animation: { animateRotate: true, animateScale: true, duration: 2000 } }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr 1fr', gap: '20px' }}>
              <div style={panelStyle}>
                <h3 style={{ marginTop: 0 }}>Detailed Equipment Log</h3>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ textAlign: 'left', borderBottom: '2px solid #eee' }}><th>NAME</th><th>TEMP</th></tr>
                  </thead>
                  <tbody>
                    {filteredData.map((row, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #f9f9f9' }}>
                        <td style={{ padding: '10px' }}>{row['Equipment Name']}</td>
                        <td style={{ color: row['Temperature'] > 115 ? 'red' : 'black' }}>{row['Temperature']} °C</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div style={{ ...panelStyle, borderTop: '5px solid #fdbb2d' }}>
                <h4 style={{ margin: '0 0 15px 0' }}>🏆 Leaderboard</h4>
                {performanceData.sort((a, b) => a.score - b.score).slice(0, 5).map((unit, i) => {
                  const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : "";
                  return (
                    <div key={i} style={{ ...sideCardStyle, borderLeft: i < 3 ? '4px solid #fdbb2d' : '1px solid #f1f5f9' }}>
                      <strong>{unit['Equipment Name']} {medal}</strong><br/>
                      <small>Efficiency: {unit.score}</small>
                    </div>
                  );
                })}
              </div>

              <div style={{ ...panelStyle, borderTop: '5px solid #1a2a6c' }}>
                <h4>📂 History</h4>
                {stats.history.map((h, i) => (
                  <div key={i} style={sideCardStyle}>
                    <strong>{h.filename}</strong><br/><small>{h.date}</small>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const Card = ({ title, value, icon }) => (
  <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 2px 5px rgba(0,0,0,0.05)' }}>
    <div style={{ fontSize: '24px' }}>{icon}</div>
    <div style={{ color: '#888', fontSize: '12px' }}>{title}</div>
    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{value}</div>
  </div>
);

// --- NEW STYLES FOR DECORATED LANDING PAGE ---
const heroContainerStyle = {
  height: '100vh',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  background: 'linear-gradient(135deg, #1a2a6c 0%, #b21f1f 100%)',
  fontFamily: 'sans-serif'
};

const heroCardStyle = {
  backgroundColor: 'rgba(255, 255, 255, 0.95)',
  padding: '60px',
  borderRadius: '30px',
  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
  textAlign: 'center',
  maxWidth: '650px',
  width: '90%',
  backdropFilter: 'blur(10px)'
};

const uploadBoxStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '15px',
  alignItems: 'center'
};

const fileLabelStyle = {
  display: 'block',
  width: '100%',
  maxWidth: '350px',
  padding: '15px 20px',
  backgroundColor: '#f8fafc',
  border: '2px dashed #cbd5e1',
  borderRadius: '12px',
  cursor: 'pointer',
  fontWeight: '600',
  color: '#475569',
  transition: 'all 0.3s ease'
};

const heroBtnStyle = {
  backgroundColor: '#1a2a6c',
  color: 'white',
  border: 'none',
  padding: '16px 45px',
  borderRadius: '12px',
  fontWeight: 'bold',
  fontSize: '16px',
  cursor: 'pointer',
  transition: 'transform 0.2s',
  boxShadow: '0 10px 15px -3px rgba(26, 42, 108, 0.4)'
};

const btnStyle = { backgroundColor: '#fdbb2d', color: '#1a2a6c', border: 'none', padding: '10px 20px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', marginLeft: '10px' };
const panelStyle = { backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' };
const sideCardStyle = { padding: '10px', marginBottom: '10px', backgroundColor: '#f8f9fa', borderRadius: '8px' };

export default App;