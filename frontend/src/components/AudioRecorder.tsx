import React, { useState, useRef } from 'react';
import { Mic, Square, Loader2 } from 'lucide-react';
import axios from 'axios';
import API_URL from '../config';

interface AudioRecorderProps {
    onTranscription: (text: string) => void;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ onTranscription }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            chunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorderRef.current.onstop = async () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                await processAudio(blob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Error accessing microphone:", err);
            alert("Impossible d'accéder au microphone.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const processAudio = async (blob: Blob) => {
        setIsProcessing(true);
        const formData = new FormData();
        formData.append('file', blob, 'recording.webm');

        try {
            const response = await axios.post(`${API_URL}/api/transcribe`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            onTranscription(response.data.text);
        } catch (error) {
            console.error("Transcription error:", error);
            alert("Erreur lors de la transcription.");
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="flex items-center gap-2">
            {!isRecording ? (
                <button
                    type="button"
                    onClick={startRecording}
                    disabled={isProcessing}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-full hover:bg-blue-700 disabled:opacity-50"
                >
                    {isProcessing ? <Loader2 className="animate-spin" size={20} /> : <Mic size={20} />}
                    {isProcessing ? "Traitement..." : "Dicter"}
                </button>
            ) : (
                <button
                    type="button"
                    onClick={stopRecording}
                    className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-full hover:bg-red-700 animate-pulse"
                >
                    <Square size={20} />
                    Arrêter
                </button>
            )}
        </div>
    );
};

export default AudioRecorder;
