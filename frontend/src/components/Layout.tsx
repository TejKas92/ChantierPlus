import React, { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { Hammer, LogOut, UserPlus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import InviteEmployeeModal from './InviteEmployeeModal';

const Layout: React.FC = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showInviteModal, setShowInviteModal] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isOwner = user?.role === 'OWNER';

    return (
        <div className="min-h-screen flex flex-col">
            <header className="bg-secondary text-white p-4 shadow-md">
                <div className="container mx-auto flex justify-between items-center">
                    <Link to="/" className="flex items-center gap-2 text-xl font-bold text-primary">
                        <Hammer size={24} />
                        <span>ChantierPlus</span>
                    </Link>
                    <nav className="flex items-center gap-4">
                        <Link to="/" className="hover:text-primary transition">Chantiers</Link>
                        {isOwner && (
                            <button
                                onClick={() => setShowInviteModal(true)}
                                className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                            >
                                <UserPlus size={18} />
                                <span>Inviter un employé</span>
                            </button>
                        )}
                        <div className="flex items-center gap-2 text-sm">
                            <span className="text-gray-300">{user?.email}</span>
                            <span className="bg-blue-600 px-2 py-1 rounded text-xs">
                                {user?.role === 'OWNER' ? 'Propriétaire' : 'Employé'}
                            </span>
                        </div>
                        <button onClick={handleLogout} className="hover:text-primary transition">
                            <LogOut size={20} />
                        </button>
                    </nav>
                </div>
            </header>
            <main className="flex-1 container mx-auto p-4">
                <Outlet />
            </main>
            <footer className="bg-slate-200 p-4 text-center text-slate-600 text-sm">
                &copy; 2025 ChantierPlus
            </footer>

            <InviteEmployeeModal
                isOpen={showInviteModal}
                onClose={() => setShowInviteModal(false)}
            />
        </div>
    );
};

export default Layout;
