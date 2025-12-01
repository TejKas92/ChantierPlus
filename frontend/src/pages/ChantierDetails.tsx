import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Plus, FileText, Calendar, Euro, Clock } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface Avenant {
    id: string;
    description: string;
    type: string;
    total_ht: number | string;  // Can be string from JSON numeric
    status: string;
    signed_at: string | null;
    created_at: string;
}

interface Chantier {
    id: string;
    name: string;
    address: string;
    email: string;
    created_at: string;
}

const ChantierDetails: React.FC = () => {
    const { chantierId } = useParams<{ chantierId: string }>();
    const navigate = useNavigate();
    const [chantier, setChantier] = useState<Chantier | null>(null);
    const [avenants, setAvenants] = useState<Avenant[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchData();
    }, [chantierId]);

    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);
            const token = localStorage.getItem('token');

            console.log('Fetching chantier:', chantierId);
            console.log('API URL:', `${API_BASE_URL}/chantiers/${chantierId}`);

            // Fetch chantier details and avenants
            const [chantierRes, avenantsRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/chantiers/${chantierId}`, {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                axios.get(`${API_BASE_URL}/chantiers/${chantierId}/avenants`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);

            setChantier(chantierRes.data);
            setAvenants(avenantsRes.data);
        } catch (error: any) {
            console.error("Error fetching data:", error);
            console.error("Error response:", error.response?.data);
            setError(error.response?.data?.detail || "Erreur lors du chargement des données");
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status: string) => {
        const badges: Record<string, { bg: string; text: string; label: string }> = {
            DRAFT: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Brouillon' },
            SIGNED: { bg: 'bg-green-100', text: 'text-green-800', label: 'Signé' },
            SENT: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Envoyé' },
        };
        const badge = badges[status] || badges.DRAFT;
        return (
            <span className={`px-2 py-1 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>
                {badge.label}
            </span>
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error || !chantier) {
        return (
            <div className="text-center py-10">
                <p className="text-red-500">{error || "Chantier introuvable"}</p>
                <button
                    onClick={() => navigate('/')}
                    className="mt-4 text-blue-600 hover:underline"
                >
                    Retour aux chantiers
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto p-4 md:p-6">
            {/* Header */}
            <div className="mb-6">
                <button
                    onClick={() => navigate('/')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft size={20} />
                    Retour aux chantiers
                </button>

                <div className="bg-white rounded-lg shadow-md p-6">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">{chantier.name}</h1>
                    <p className="text-gray-600 mb-1">{chantier.address}</p>
                    <p className="text-gray-600 mb-2">{chantier.email}</p>
                    <div className="flex items-center gap-1 text-sm text-gray-400">
                        <Calendar size={14} />
                        <span>Créé le {new Date(chantier.created_at).toLocaleDateString('fr-FR')}</span>
                    </div>
                </div>
            </div>

            {/* Avenants Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">
                        Avenants ({avenants.length})
                    </h2>
                    <Link
                        to={`/create-avenant/${chantierId}`}
                        className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                    >
                        <Plus size={18} />
                        Nouvel Avenant
                    </Link>
                </div>

                {avenants.length === 0 ? (
                    <div className="text-center py-10 border-2 border-dashed border-gray-200 rounded-lg">
                        <FileText size={48} className="mx-auto text-gray-300 mb-3" />
                        <p className="text-gray-500 mb-4">Aucun avenant pour ce chantier</p>
                        <Link
                            to={`/create-avenant/${chantierId}`}
                            className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                        >
                            <Plus size={18} />
                            Créer le premier avenant
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {avenants.map((avenant) => (
                            <Link
                                key={avenant.id}
                                to={`/avenant/${avenant.id}`}
                                className="block border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
                            >
                                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                                    <div className="flex-1">
                                        <div className="flex items-start gap-2 mb-2">
                                            <FileText size={20} className="text-gray-400 flex-shrink-0 mt-0.5" />
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium text-gray-900 line-clamp-2">
                                                    {avenant.description}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 ml-7">
                                            <span className="flex items-center gap-1">
                                                <Euro size={14} />
                                                {parseFloat(String(avenant.total_ht)).toFixed(2)} € HT
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Clock size={14} />
                                                {avenant.type}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Calendar size={14} />
                                                {new Date(avenant.created_at).toLocaleDateString('fr-FR')}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 ml-7 md:ml-0">
                                        {getStatusBadge(avenant.status)}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChantierDetails;
