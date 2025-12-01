import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Plus, Calendar } from 'lucide-react';
import { API_BASE_URL } from '../config';
import CreateChantierModal from '../components/CreateChantierModal';

interface Chantier {
    id: string;
    name: string;
    address: string;
    created_at: string;
}

const Dashboard: React.FC = () => {
    const [chantiers, setChantiers] = useState<Chantier[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);

    const fetchChantiers = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_BASE_URL}/chantiers/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setChantiers(response.data);
        } catch (error) {
            console.error("Error fetching chantiers:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchChantiers();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-slate-800">Mes Chantiers</h1>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-primary text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-amber-600 transition shadow-md"
                >
                    <Plus size={20} /> Nouveau Chantier
                </button>
            </div>

            {loading ? (
                <p>Chargement...</p>
            ) : chantiers.length === 0 ? (
                <div className="text-center py-10 bg-white rounded-lg shadow border border-slate-200">
                    <p className="text-slate-500">Aucun chantier trouvé.</p>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {chantiers.map((chantier) => (
                        <div key={chantier.id} className="bg-white p-6 rounded-lg shadow-md border border-slate-200 hover:shadow-lg transition">
                            <h2 className="text-xl font-semibold text-slate-800 mb-2">{chantier.name}</h2>
                            <p className="text-slate-500 mb-2">{chantier.address}</p>
                            <div className="flex items-center gap-1 text-sm text-slate-400 mb-4">
                                <Calendar size={14} />
                                <span>Créé le {new Date(chantier.created_at).toLocaleDateString('fr-FR')}</span>
                            </div>
                            <Link
                                to={`/chantier/${chantier.id}`}
                                className="block w-full text-center bg-slate-100 text-slate-700 py-2 rounded hover:bg-slate-200 transition font-medium"
                            >
                                Gérer les Avenants
                            </Link>
                        </div>
                    ))}
                </div>
            )}

            <CreateChantierModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onSuccess={fetchChantiers}
            />
        </div>
    );
};

export default Dashboard;
