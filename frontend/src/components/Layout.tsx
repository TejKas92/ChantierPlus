import React, { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { Hammer, LogOut, Settings, Menu, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Layout: React.FC = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
        setMobileMenuOpen(false);
    };

    const isOwner = user?.role === 'OWNER';

    return (
        <div className="min-h-screen flex flex-col">
            <header className="bg-secondary text-white shadow-md">
                <div className="container mx-auto px-4 py-3">
                    <div className="flex justify-between items-center">
                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-2 text-xl font-bold text-primary">
                            <Hammer size={24} />
                            <div className="flex flex-col">
                                <span>ChantierPlus</span>
                                <span className="text-xs text-gray-400 font-normal">{user?.company_name}</span>
                            </div>
                        </Link>

                        {/* Desktop Navigation */}
                        <nav className="hidden md:flex items-center gap-4">
                            {isOwner && (
                                <Link
                                    to="/settings"
                                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                                >
                                    <Settings size={18} />
                                    <span className="hidden lg:inline">Gestion de la société</span>
                                    <span className="lg:hidden">Gestion</span>
                                </Link>
                            )}
                            <div className="hidden lg:flex items-center gap-2 text-sm px-3 py-2 bg-slate-700 rounded-lg">
                                <span className="text-gray-300">{user?.email}</span>
                                <span className="bg-blue-600 px-2 py-1 rounded text-xs">
                                    {user?.role === 'OWNER' ? 'Propriétaire' : 'Employé'}
                                </span>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="hover:text-primary transition p-2 rounded-lg hover:bg-slate-700"
                                title="Déconnexion"
                            >
                                <LogOut size={20} />
                            </button>
                        </nav>

                        {/* Mobile Menu Button */}
                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="md:hidden p-2 hover:bg-slate-700 rounded-lg transition"
                        >
                            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>

                    {/* Mobile Navigation */}
                    {mobileMenuOpen && (
                        <nav className="md:hidden mt-4 pb-4 border-t border-slate-600 pt-4 space-y-3">
                            {/* User info */}
                            <div className="flex flex-col gap-2 px-3 py-3 bg-slate-700 rounded-lg">
                                <span className="text-sm text-gray-300">{user?.email}</span>
                                <span className="bg-blue-600 px-3 py-1 rounded text-xs w-fit">
                                    {user?.role === 'OWNER' ? 'Propriétaire' : 'Employé'}
                                </span>
                            </div>

                            {/* Menu items */}
                            {isOwner && (
                                <Link
                                    to="/settings"
                                    onClick={() => setMobileMenuOpen(false)}
                                    className="w-full flex items-center gap-2 bg-primary text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition"
                                >
                                    <Settings size={18} />
                                    <span>Gestion de la société</span>
                                </Link>
                            )}

                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-700 rounded-lg transition text-left"
                            >
                                <LogOut size={20} />
                                <span>Déconnexion</span>
                            </button>
                        </nav>
                    )}
                </div>
            </header>

            <main className="flex-1 container mx-auto p-4">
                <Outlet />
            </main>

            <footer className="bg-slate-200 p-4 text-center text-slate-600 text-sm">
                &copy; 2025 ChantierPlus
            </footer>
        </div>
    );
};

export default Layout;
