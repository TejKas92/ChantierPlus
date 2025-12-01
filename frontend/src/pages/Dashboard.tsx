import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Plus, FileText } from 'lucide-react';
import API_URL from '../config';

// Mock User ID - In real app, this comes from auth context
const MOCK_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

interface Client {
    id: string;
    name: string;
    address: string;
}

const Dashboard: React.FC = () => {
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchClients = async () => {
            try {
                const response = await axios.get(`${API_URL}/clients/`, {
                    headers: { 'x-user-id': MOCK_USER_ID }
                });
                setClients(response.data);
            } catch (error) {
                console.error("Error fetching clients:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchClients();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-slate-800">Mes Chantiers</h1>
                <button className="bg-primary text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-amber-600 transition shadow-md">
                    <Plus size={20} /> Nouveau Client
                </button>
            </div>

            {loading ? (
                <p>Chargement...</p>
            ) : clients.length === 0 ? (
                <div className="text-center py-10 bg-white rounded-lg shadow border border-slate-200">
                    <p className="text-slate-500">Aucun chantier trouvé.</p>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {clients.map((client) => (
                        <div key={client.id} className="bg-white p-6 rounded-lg shadow-md border border-slate-200 hover:shadow-lg transition">
                            <h2 className="text-xl font-semibold text-slate-800 mb-2">{client.name}</h2>
                            <p className="text-slate-500 mb-4">{client.address}</p>
                            <Link
                                to={`/create-avenant/${client.id}`}
                                className="block w-full text-center bg-slate-100 text-slate-700 py-2 rounded hover:bg-slate-200 transition font-medium"
                            >
                                Créer un Avenant
                            </Link>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
