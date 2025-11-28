const API_URL = "http://localhost:8000";

export const transcribeAudio = async (audioBlob, style) => {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");
    formData.append("style", style);

    try {
        const response = await fetch(`${API_URL}/transcribe`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Transcription failed:", error);
        throw error;
    }
};

export const transcribeAudioStream = async (audioBlob, style, secondaryStyle, onChunk) => {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");
    formData.append("style", style);
    if (secondaryStyle && secondaryStyle !== "None") {
        formData.append("style2", secondaryStyle);
    }

    try {
        const response = await fetch(`${API_URL}/transcribe_stream`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const dataStr = line.replace("data: ", "").trim();
                    if (dataStr === "[DONE]") return;

                    try {
                        const data = JSON.parse(dataStr);
                        if (data.error) throw new Error(data.error);
                        onChunk(data);
                    } catch (e) {
                        console.error("Error parsing SSE data:", e);
                    }
                }
            }
        }
    } catch (error) {
        console.error("Streaming Transcription failed:", error);
        throw error;
    }
};
