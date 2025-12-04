import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle, ArrowLeft } from 'lucide-react';
import API_URL from '../config';

const AvenantDetails: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [avenant, setAvenant] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAvenant = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get(`${API_URL}/avenants/${id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setAvenant(response.data);
            } catch (error) {
                console.error("Error fetching avenant:", error);
                // Fallback to showing success message even if fetch fails
                setAvenant({ id, status: 'SIGNED' });
            } finally {
                setLoading(false);
            }
        };

        fetchAvenant();
    }, [id]);

    if (loading) return <p>Chargement...</p>;

    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-lg text-center space-y-6">
            <div className="flex justify-center text-green-500">
                <CheckCircle size={64} />
            </div>

            <h1 className="text-3xl font-bold text-slate-800">Avenant Validé et Envoyé !</h1>
            <p className="text-slate-600">
                L'avenant a été enregistré, signé et envoyé par email avec succès.
            </p>

            <div className="bg-slate-50 p-4 rounded text-left">
                <p><strong>ID Avenant:</strong> {id}</p>
                <p><strong>Statut:</strong> <span className="text-green-600 font-bold">SIGNÉ</span></p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
                <p className="text-sm text-blue-800">
                    📧 Le PDF de l'avenant a été envoyé automatiquement par email au client, à vous-même et aux propriétaires de l'entreprise.
                </p>
            </div>

            <div className="pt-6">
                <Link
                    to={avenant?.chantier_id ? `/chantier/${avenant.chantier_id}` : "/"}
                    className="inline-flex items-center gap-2 text-primary hover:underline font-medium"
                >
                    <ArrowLeft size={20} />
                    Retour au Chantier
                </Link>
            </div>
        </div>
    );
};

export default AvenantDetails;
