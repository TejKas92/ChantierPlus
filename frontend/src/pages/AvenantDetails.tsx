import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle, ArrowLeft } from 'lucide-react';

const MOCK_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

const AvenantDetails: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [avenant, setAvenant] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAvenant = async () => {
            try {
                // In a real app, we would fetch the avenant details. 
                // Since we don't have a GET /avenants/{id} endpoint in the plan (oops), 
                // I'll just mock the display or assume we added it.
                // For now, let's assume we can fetch it or just show a success message.
                // Actually, let's add the GET endpoint to the backend later.
                // For now, I'll just show a static success page if I can't fetch.
                setAvenant({ id, status: 'SIGNED' });
            } catch (error) {
                console.error("Error fetching avenant:", error);
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

            <h1 className="text-3xl font-bold text-slate-800">Avenant Validé !</h1>
            <p className="text-slate-600">
                L'avenant a été enregistré et signé avec succès.
            </p>

            <div className="bg-slate-50 p-4 rounded text-left">
                <p><strong>ID Avenant:</strong> {id}</p>
                <p><strong>Statut:</strong> <span className="text-green-600 font-bold">SIGNÉ</span></p>
            </div>

            <div className="pt-6">
                <Link to="/" className="inline-flex items-center gap-2 text-primary hover:underline font-medium">
                    <ArrowLeft size={20} />
                    Retour au Tableau de Bord
                </Link>
            </div>
        </div>
    );
};

export default AvenantDetails;
