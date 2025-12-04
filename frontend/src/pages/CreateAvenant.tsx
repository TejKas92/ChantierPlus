import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import AudioRecorder from '../components/AudioRecorder';
import SignaturePad from '../components/SignaturePad';
import { Camera, Send, Loader2 } from 'lucide-react';
import API_URL from '../config';

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
    const [photoError, setPhotoError] = useState<string | null>(null);

    // Clear signature when critical fields change
    const clearSignature = () => {
        console.log('Clearing signature - before:', signatureData ? 'has signature' : 'no signature');
        setSignatureData('');
        console.log('Clearing signature - after: set to empty');
    };

    const handleDescriptionChange = (value: string) => {
        setDescription(value);
        if (signatureData) {
            console.log('Description changed, clearing signature');
            clearSignature();
        }
    };

    const handleTypeChange = (newType: 'FORFAIT' | 'REGIE') => {
        setType(newType);
        if (signatureData) {
            clearSignature();
        }
    };

    const handlePriceChange = (value: string) => {
        setPrice(value);
        if (signatureData) {
            clearSignature();
        }
    };

    const handleHoursChange = (value: string) => {
        setHours(value);
        if (signatureData) {
            clearSignature();
        }
    };

    const handleHourlyRateChange = (value: string) => {
        setHourlyRate(value);
        if (signatureData) {
            clearSignature();
        }
    };

    const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setPhotoError(null);

        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];

            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                setPhotoError('Type de fichier non autorisé. Utilisez JPG, PNG, GIF ou WebP.');
                e.target.value = ''; // Reset input
                return;
            }

            // Validate file size (10 MB max)
            const maxSize = 10 * 1024 * 1024; // 10 MB
            if (file.size > maxSize) {
                setPhotoError('Fichier trop volumineux. Taille maximale: 10 MB.');
                e.target.value = ''; // Reset input
                return;
            }

            setPhoto(file);
            // Clear signature when photo changes
            if (signatureData) {
                clearSignature();
            }
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                alert('Vous devez être connecté pour créer un avenant.');
                navigate('/login');
                return;
            }

            let photoUrl = null;
            if (photo) {
                const formData = new FormData();
                formData.append('file', photo);
                const uploadRes = await axios.post(`${API_URL}/avenants/files`, formData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
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
                headers: { Authorization: `Bearer ${token}` }
            });

            navigate(`/avenant/${response.data.id}`);
        } catch (error: any) {
            console.error("Error creating avenant:", error);
            const errorMessage = error.response?.data?.detail || "Erreur lors de la création de l'avenant.";
            alert(errorMessage);
        } finally {
            setSubmitting(false);
        }
    };

    const total = type === 'FORFAIT'
        ? (parseFloat(price) || 0)
        : (parseFloat(hours) || 0) * (parseFloat(hourlyRate) || 0);

    // Check if all required fields are filled
    const isFormValid = () => {
        if (!description.trim()) return false;
        if (!photo) return false;

        if (type === 'FORFAIT') {
            return parseFloat(price) > 0;
        } else {
            return parseFloat(hours) > 0 && parseFloat(hourlyRate) > 0;
        }
    };

    const canSign = isFormValid();

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
                            onChange={(e) => handleDescriptionChange(e.target.value)}
                            className="flex-1 border border-slate-300 rounded-lg p-2 min-h-[100px]"
                            placeholder="Décrivez les travaux supplémentaires..."
                            required
                        />
                    </div>
                    <AudioRecorder onTranscription={(text) => handleDescriptionChange(description + (description ? ' ' : '') + text)} />
                </div>

                {/* Photo Section */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">
                        Photo (Preuve) <span className="text-red-500">*</span>
                    </label>
                    <div className="flex items-center gap-4">
                        <label className="cursor-pointer bg-slate-100 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-slate-200 transition">
                            <Camera size={20} />
                            <span>Prendre une photo</span>
                            <input type="file" accept="image/jpeg,image/png,image/gif,image/webp" capture="environment" onChange={handlePhotoChange} className="hidden" />
                        </label>
                        {photo && <span className="text-sm text-green-600">Photo sélectionnée: {photo.name}</span>}
                    </div>
                    {photoError && <p className="text-sm text-red-500">{photoError}</p>}
                    <p className="text-xs text-slate-500">Formats acceptés: JPG, PNG, GIF, WebP (max 10 MB)</p>
                </div>

                {/* Pricing Section */}
                <div className="space-y-4 border-t pt-4">
                    <div className="flex gap-4">
                        <label className="flex items-center gap-2">
                            <input
                                type="radio"
                                checked={type === 'FORFAIT'}
                                onChange={() => handleTypeChange('FORFAIT')}
                                className="text-primary focus:ring-primary"
                            />
                            <span className="font-medium">Forfait</span>
                        </label>
                        <label className="flex items-center gap-2">
                            <input
                                type="radio"
                                checked={type === 'REGIE'}
                                onChange={() => handleTypeChange('REGIE')}
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
                                onChange={(e) => handlePriceChange(e.target.value)}
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
                                    onChange={(e) => handleHoursChange(e.target.value)}
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
                                    onChange={(e) => handleHourlyRateChange(e.target.value)}
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
                    <label className="block text-sm font-medium text-slate-700">
                        Signature du Client <span className="text-red-500">*</span>
                    </label>
                    {!canSign && (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-3">
                            <p className="text-sm text-amber-800">
                                ⚠️ Veuillez compléter tous les champs requis (description, photo, prix) avant de signer
                            </p>
                        </div>
                    )}
                    {signatureData && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                            <p className="text-sm text-blue-800">
                                ℹ️ Toute modification des champs ci-dessus effacera la signature
                            </p>
                        </div>
                    )}
                    <SignaturePad onEnd={setSignatureData} disabled={!canSign} signatureData={signatureData} />
                    {canSign && !signatureData && <p className="text-sm text-red-500">La signature est requise.</p>}
                </div>

                <button
                    type="submit"
                    disabled={submitting || !signatureData || !canSign}
                    className="w-full bg-primary text-white py-3 rounded-lg font-bold text-lg hover:bg-amber-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                >
                    {submitting ? <Loader2 className="animate-spin" /> : <Send />}
                    Valider et Envoyer par Email
                </button>
            </form>
        </div>
    );
};

export default CreateAvenant;
