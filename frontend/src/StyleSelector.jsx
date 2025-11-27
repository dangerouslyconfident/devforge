import { useState, useRef, useEffect } from 'react'

const styles = [
    { id: 'Neutral', label: 'Neutral', desc: 'Standard transcription.' },
    { id: 'Formal', label: 'Formal', desc: 'Professional and polished.' },
    { id: 'Casual', label: 'Casual', desc: 'Relaxed and conversational.' },
    { id: 'Concise', label: 'Concise', desc: 'Short and to the point.' }
]

const StyleSelector = ({ value, onChange }) => {
    const [isOpen, setIsOpen] = useState(false)
    const containerRef = useRef(null)

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (containerRef.current && !containerRef.current.contains(event.target)) {
                setIsOpen(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    const selectedStyle = styles.find(s => s.id === value) || styles[0]

    return (
        <div className="style-selector-container" ref={containerRef}>
            <button className="style-selector-btn" onClick={() => setIsOpen(!isOpen)}>
                <span style={{ fontWeight: 600 }}>{selectedStyle.label}</span>
                <span style={{ fontSize: '0.8em', opacity: 0.7 }}>▼</span>
            </button>

            {isOpen && (
                <div className="style-dropdown glass">
                    {styles.map(style => (
                        <div
                            key={style.id}
                            className={`style-option ${value === style.id ? 'active' : ''}`}
                            onClick={() => {
                                onChange(style.id)
                                setIsOpen(false)
                            }}
                        >
                            <div className="style-label">{style.label}</div>
                            <div className="style-desc">{style.desc}</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default StyleSelector
