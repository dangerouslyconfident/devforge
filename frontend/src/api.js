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
