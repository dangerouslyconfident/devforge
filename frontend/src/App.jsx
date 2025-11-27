import { useState, useRef, useEffect } from 'react'
import { transcribeAudio } from './api'
import Visualizer from './Visualizer'
import StyleSelector from './StyleSelector'
import './index.css'

function App() {
  const [activeTab, setActiveTab] = useState("live") // Default to Live
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [theme, setTheme] = useState("dark")

  // Data States
  const [streamText, setStreamText] = useState("")
  const [scenes, setScenes] = useState([])
  const [style, setStyle] = useState("Neutral")
  const [history, setHistory] = useState([])
  const [latency, setLatency] = useState(null)

  // Refs
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const socketRef = useRef(null)
  const audioContextRef = useRef(null)
  const processorRef = useRef(null)
  const sourceRef = useRef(null)
  const transcriptEndRef = useRef(null)

  // Visualizer State
  const [vizContext, setVizContext] = useState(null)
  const [vizSource, setVizSource] = useState(null)

  useEffect(() => {
    const saved = localStorage.getItem('dictation_history')
    if (saved) setHistory(JSON.parse(saved))

    const savedTheme = localStorage.getItem('theme') || 'dark'
    setTheme(savedTheme)
    document.documentElement.setAttribute('data-theme', savedTheme)
  }, [])

  // Auto-scroll
  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollTop = transcriptEndRef.current.scrollHeight
    }
  }, [streamText])

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'INPUT') {
        e.preventDefault()
        if (isRecording) stopRecording()
        else startRecording()
      }
      if (e.code === 'Escape' && isRecording) {
        stopRecording()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isRecording, activeTab])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  const saveToHistory = (text, modeUsed) => {
    if (!text) return
    const newItem = {
      id: Date.now(),
      text,
      style,
      mode: modeUsed,
      date: new Date().toLocaleString()
    }
    const newHistory = [newItem, ...history].slice(0, 50)
    setHistory(newHistory)
    localStorage.setItem('dictation_history', JSON.stringify(newHistory))
  }

  const clearHistory = () => {
    if (confirm("Clear all history?")) {
      setHistory([])
      localStorage.removeItem('dictation_history')
    }
  }

  const exportToTxt = () => {
    let content = ""
    if (activeTab === "scene") {
      content = scenes.map((s, i) => `Scene ${i + 1}: \n${s} `).join("\n\n")
    } else if (activeTab === "live") {
      content = streamText
    } else {
      content = history.map(h => `[${h.date}] ${h.mode} (${h.style}): \n${h.text} `).join("\n\n---\n\n")
    }

    if (!content) return alert("Nothing to export!")

    const element = document.createElement("a");
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = "flux_dictate_export.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

  const downsampleBuffer = (buffer, sampleRate, outSampleRate) => {
    if (outSampleRate === sampleRate) return buffer;
    if (outSampleRate > sampleRate) return buffer;
    const sampleRateRatio = sampleRate / outSampleRate;
    const newLength = Math.round(buffer.length / sampleRateRatio);
    const result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < result.length) {
      const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
      let accum = 0, count = 0;
      for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
        accum += buffer[i];
        count++;
      }
      result[offsetResult] = accum / count;
      offsetResult++;
      offsetBuffer = nextOffsetBuffer;
    }
    return result;
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // Setup Visualizer Context
      const vizCtx = new (window.AudioContext || window.webkitAudioContext)()
      const vizSrc = vizCtx.createMediaStreamSource(stream)
      setVizContext(vizCtx)
      setVizSource(vizSrc)

      if (activeTab === "live") {
        setStreamText("")
        socketRef.current = new WebSocket("ws://localhost:8000/stream")

        socketRef.current.onopen = () => {
          // Use the SAME context if possible, or a new one.
          // For simplicity and avoiding conflict, let's use a separate processing context or reuse.
          // Actually, we can reuse vizCtx for processing if we want, but let's keep logic separate to avoid breaking existing flow.

          audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
          const sampleRate = audioContextRef.current.sampleRate
          sourceRef.current = audioContextRef.current.createMediaStreamSource(stream)
          processorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1)

          processorRef.current.onaudioprocess = (e) => {
            if (socketRef.current?.readyState === WebSocket.OPEN) {
              const inputData = e.inputBuffer.getChannelData(0)
              const downsampled = downsampleBuffer(inputData, sampleRate, 16000)
              const buffer = new ArrayBuffer(downsampled.length * 2)
              const view = new DataView(buffer)
              for (let i = 0; i < downsampled.length; i++) {
                let s = Math.max(-1, Math.min(1, downsampled[i]))
                view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
              }
              socketRef.current.send(buffer)
            }
          }

          sourceRef.current.connect(processorRef.current)
          processorRef.current.connect(audioContextRef.current.destination)
        }

        socketRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.is_final) {
            setStreamText(prev => (prev + " " + data.text).trim())
          }
        }
      } else {
        // Scene Mode
        mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' })
        chunksRef.current = []
        mediaRecorderRef.current.ondataavailable = (e) => {
          if (e.data.size > 0) chunksRef.current.push(e.data)
        }
        mediaRecorderRef.current.onstop = async () => {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
          setIsProcessing(true)
          try {
            const res = await transcribeAudio(blob, style)
            if (res.status === "success") {
              setScenes(prev => [...prev, res.final_text])
              setLatency(res.latency_breakdown)
              saveToHistory(res.final_text, `Scene ${scenes.length + 1} `)
            } else {
              alert("Error: " + res.message)
            }
          } catch (e) {
            alert("Processing failed")
          } finally {
            setIsProcessing(false)
          }
        }
        mediaRecorderRef.current.start(1000)
      }
      setIsRecording(true)
    } catch (err) {
      console.error(err)
      alert("Microphone access denied")
    }
  }

  const stopRecording = () => {
    setIsRecording(false)

    // Cleanup Visualizer
    if (vizSource) vizSource.disconnect()
    if (vizContext) vizContext.close()
    setVizContext(null)
    setVizSource(null)

    if (activeTab === "live") {
      if (sourceRef.current) sourceRef.current.disconnect()
      if (processorRef.current) processorRef.current.disconnect()
      if (audioContextRef.current) audioContextRef.current.close()
      if (socketRef.current) socketRef.current.close()
      if (sourceRef.current?.mediaStream) {
        sourceRef.current.mediaStream.getTracks().forEach(t => t.stop())
      }
      saveToHistory(streamText, "Live Stream")
    } else {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop()
        mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop())
      }
    }
  }

  const deleteHistory = (id) => {
    const newH = history.filter(h => h.id !== id)
    setHistory(newH)
    localStorage.setItem('dictation_history', JSON.stringify(newH))
  }

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <div className="sidebar glass">
        <div className="brand">
          <span>🎙️</span> FluxDictate
        </div>

        <div className="nav-menu">
          <div className={`nav-item ${activeTab === 'live' ? 'active' : ''}`} onClick={() => setActiveTab('live')}>
            <span>⚡</span> Live Dictation
          </div>
          <div className={`nav-item ${activeTab === 'scene' ? 'active' : ''}`} onClick={() => setActiveTab('scene')}>
            <span>🎬</span> Scene Batch
          </div>
          <div className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
            <span>📜</span> History
          </div>
          <div className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>
            <span>⚙️</span> Settings
          </div>
        </div>

        <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '12px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>LAST LATENCY</div>
          <div style={{ fontSize: '1.1rem', fontWeight: '600', color: 'var(--success)' }}>
            {latency ? latency.Total : "-- ms"}
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="workspace glass">

        {/* Live Tab */}
        {activeTab === 'live' && (
          <div className="live-container">
            <textarea
              ref={transcriptEndRef}
              className="transcript-hero"
              placeholder="Start speaking..."
              value={streamText}
              readOnly
            />

            {/* Dynamic Island Controls */}
            <div className={`dynamic-island-container`}>
              <div className={`dynamic-island ${isRecording ? 'recording' : ''}`}>

                {/* Style Selector (Hidden when recording to save space/focus) */}
                {!isRecording && (
                  <StyleSelector value={style} onChange={setStyle} />
                )}

                {/* Mic Button */}
                <button
                  className={`island-mic ${isRecording ? 'active' : ''}`}
                  onClick={isRecording ? stopRecording : startRecording}
                >
                  {isRecording ? "⏹" : "🎙"}
                </button>

                {/* Waveform (Only when recording) */}
                {isRecording && (
                  <div className="island-waveform" style={{ width: '150px', height: '30px' }}>
                    <Visualizer audioContext={vizContext} source={vizSource} />
                  </div>
                )}

                {/* Export (Only when not recording and has text) */}
                {!isRecording && streamText && (
                  <button className="btn" onClick={exportToTxt}>Export</button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Scene Tab */}
        {activeTab === 'scene' && (
          <div style={{ padding: '2rem', height: '100%', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2>Scene Batch</h2>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                {scenes.length > 0 && <button className="btn" onClick={exportToTxt}>Export to TXT</button>}

                <div className="dynamic-island" style={{ position: 'relative', bottom: 'auto', left: 'auto', transform: 'none', minWidth: isRecording ? '200px' : 'auto' }}>
                  {isRecording && (
                    <div className="island-waveform" style={{ width: '100px', height: '30px', marginRight: '1rem' }}>
                      <Visualizer audioContext={vizContext} source={vizSource} />
                    </div>
                  )}
                  <button className={`island-mic ${isRecording ? 'active' : ''}`} onClick={isRecording ? stopRecording : startRecording}>
                    {isProcessing ? "⏳" : (isRecording ? "⏹" : "🎙")}
                  </button>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {scenes.map((scene, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '16px' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--accent)', marginBottom: '0.5rem', fontWeight: 'bold' }}>SCENE {i + 1}</div>
                  <div style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>{scene}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div style={{ padding: '2rem', height: '100%', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <h2>History</h2>
              <button className="btn" style={{ color: 'var(--danger)', borderColor: 'var(--danger)' }} onClick={clearHistory}>Clear All</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {history.map(item => (
                <div key={item.id} style={{ background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '16px', cursor: 'pointer' }} onClick={() => navigator.clipboard.writeText(item.text)}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    <span>{item.date}</span>
                    <span>{item.mode} • {item.style}</span>
                  </div>
                  <div style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>{item.text}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div style={{ padding: '3rem' }}>
            <h2>Settings</h2>
            <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <div>
                <h3 style={{ marginBottom: '1rem' }}>Appearance</h3>
                <button className="btn" onClick={toggleTheme}>
                  {theme === 'dark' ? '☀️ Switch to Light Mode' : '🌙 Switch to Dark Mode'}
                </button>
              </div>
              <div>
                <h3 style={{ marginBottom: '1rem' }}>Shortcuts</h3>
                <div style={{ display: 'grid', gap: '1rem', maxWidth: '300px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Record</span>
                    <kbd style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px' }}>Space</kbd>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Stop</span>
                    <kbd style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px' }}>Esc</kbd>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default App
