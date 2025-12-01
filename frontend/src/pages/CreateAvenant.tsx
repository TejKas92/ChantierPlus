import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import AudioRecorder from '../components/AudioRecorder';
import SignaturePad from '../components/SignaturePad';
import { Camera, Save, Loader2 } from 'lucide-react';
import API_URL from '../config';

const MOCK_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

const CreateAvenant: React.FC = () => {
    const { chantierId } = useParams<{ chantierId: string }>();
    const navigate = useNavigate();

    const [description, setDescription] = useState('');
    const [type, setType] = useState<'FORFAIT' | 'REGIE'>('FORFAIT');
    const [price, setPrice] = useState<string>('');
    const [hours, setHours] = useState<string>('');
    const [hourlyRate, setHourlyRate] = useState<string>('');
    const [signatureData, setSignatureData] = useState('');
    const [photo, setPhoto] = useState<File | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setPhoto(e.target.files[0]);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            let photoUrl = null;
            if (photo) {
                const formData = new FormData();
                formData.append('file', photo);
                const uploadRes = await axios.post(`${API_URL}/avenants/files`, formData);
                photoUrl = uploadRes.data.photo_url;
            }

            const payload: any = {
                chantier_id: chantierId,
                description,
                type,
                photo_url: photoUrl,
                signature_data: signatureData,
            };

            if (type === 'FORFAIT') {
                payload.price = parseFloat(price);
            } else {
                payload.hours = parseFloat(hours);
                payload.hourly_rate = parseFloat(hourlyRate);
            }

            const response = await axios.post(`${API_URL}/avenants/`, payload, {
                headers: { 'x-user-id': MOCK_USER_ID }
            });

            navigate(`/avenant/${response.data.id}`);
        } catch (error) {
            console.error("Error creating avenant:", error);
            alert("Erreur lors de la création de l'avenant.");
        } finally {
            setSubmitting(false);
        }
    };

    const total = type === 'FORFAIT'
        ? (parseFloat(price) || 0)
        : (parseFloat(hours) || 0) * (parseFloat(hourlyRate) || 0);

    return (
        <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
            <h1 className="text-2xl font-bold mb-6 text-slate-800">Nouvel Avenant</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Description Section */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">Description des travaux</label>
                    <div className="flex gap-2">
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="flex-1 border border-slate-300 rounded-lg p-2 min-h-[100px]"
                            placeholder="Décrivez les travaux supplémentaires..."
                            required
                        />
                    </div>
                    <AudioRecorder onTranscription={(text) => setDescription(prev => prev + (prev ? ' ' : '') + text)} />
                </div>

                {/* Photo Section */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">Photo (Preuve)</label>
                    <div className="flex items-center gap-4">
                        <label className="cursor-pointer bg-slate-100 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-slate-200 transition">
                            <Camera size={20} />
                            <span>Prendre une photo</span>
                            <input type="file" accept="image/*" capture="environment" onChange={handlePhotoChange} className="hidden" />
                        </label>
                        {photo && <span className="text-sm text-green-600">Photo sélectionnée: {photo.name}</span>}
                    </div>
                </div>

                {/* Pricing Section */}
                <div className="space-y-4 border-t pt-4">
                    <div className="flex gap-4">
                        <label className="flex items-center gap-2">
                            <input
                                type="radio"
                                checked={type === 'FORFAIT'}
                                onChange={() => setType('FORFAIT')}
                                className="text-primary focus:ring-primary"
                            />
                            <span className="font-medium">Forfait</span>
                        </label>
                        <label className="flex items-center gap-2">
                            <input
                                type="radio"
                                checked={type === 'REGIE'}
                                onChange={() => setType('REGIE')}
                                className="text-primary focus:ring-primary"
                            />
                            <span className="font-medium">Régie</span>
                        </label>
                    </div>

                    {type === 'FORFAIT' ? (
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Montant Forfaitaire (€ HT)</label>
                            <input
                                type="number"
                                step="0.01"
                                value={price}
                                onChange={(e) => setPrice(e.target.value)}
                                className="w-full border border-slate-300 rounded-lg p-2 mt-1"
                                required
                            />
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700">Heures</label>
                                <input
                                    type="number"
                                    step="0.5"
                                    value={hours}
                                    onChange={(e) => setHours(e.target.value)}
                                    className="w-full border border-slate-300 rounded-lg p-2 mt-1"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700">Taux Horaire (€)</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={hourlyRate}
                                    onChange={(e) => setHourlyRate(e.target.value)}
                                    className="w-full border border-slate-300 rounded-lg p-2 mt-1"
                                    required
                                />
                            </div>
                        </div>
                    )}

                    <div className="bg-slate-50 p-4 rounded-lg flex justify-between items-center">
                        <span className="font-bold text-lg">Total HT</span>
                        <span className="font-bold text-2xl text-primary">{total.toFixed(2)} €</span>
                    </div>
                </div>

                {/* Signature Section */}
                <div className="space-y-2 border-t pt-4">
                    <label className="block text-sm font-medium text-slate-700">Signature du Client</label>
                    <SignaturePad onEnd={setSignatureData} />
                    {!signatureData && <p className="text-sm text-red-500">La signature est requise.</p>}
                </div>

                <button
                    type="submit"
                    disabled={submitting || !signatureData}
                    className="w-full bg-primary text-white py-3 rounded-lg font-bold text-lg hover:bg-amber-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                >
                    {submitting ? <Loader2 className="animate-spin" /> : <Save />}
                    Valider et Signer
                </button>
            </form>
        </div>
    );
};

export default CreateAvenant;
