import { useEffect, useRef } from 'react'

const Visualizer = ({ audioContext, source }) => {
    const canvasRef = useRef(null)
    const analyserRef = useRef(null)
    const rafRef = useRef(null)

    useEffect(() => {
        if (!audioContext || !source || !canvasRef.current) return

        // Create Analyser
        const analyser = audioContext.createAnalyser()
        analyser.fftSize = 64 // Low FFT size for chunky bars
        source.connect(analyser)
        analyserRef.current = analyser

        const bufferLength = analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')

        const draw = () => {
            rafRef.current = requestAnimationFrame(draw)

            analyser.getByteFrequencyData(dataArray)

            ctx.clearRect(0, 0, canvas.width, canvas.height)

            const barWidth = (canvas.width / bufferLength) * 2.5
            let barHeight
            let x = 0

            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2 // Scale down height

                // Gradient or Color based on theme
                ctx.fillStyle = `rgb(${barHeight + 100}, 50, 50)` // Red-ish tint
                // Or use CSS variable color if we could, but canvas needs explicit color.
                // Let's use the 'danger' color roughly: #ff453a
                ctx.fillStyle = '#ff453a'

                // Draw rounded rect (simulated)
                ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)

                x += barWidth + 2 // Spacing
            }
        }

        draw()

        return () => {
            if (rafRef.current) cancelAnimationFrame(rafRef.current)
            // Don't disconnect source/analyser here as it might break the chain for recording
            // But for visualization-only branches, it's fine.
            // We'll rely on the parent to manage the audio graph lifecycle mostly.
            try {
                // source.disconnect(analyser) // Optional, might be safer to leave connected if shared
            } catch (e) { }
        }
    }, [audioContext, source])

    return <canvas ref={canvasRef} width={200} height={40} style={{ width: '100%', height: '100%' }} />
}

export default Visualizer
