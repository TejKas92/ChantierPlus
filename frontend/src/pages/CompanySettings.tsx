import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { useAuth } from '../contexts/AuthContext';
import { Building2, UserPlus, Trash2, Shield, User, Mail, Calendar, Save } from 'lucide-react';
import InviteEmployeeModal from '../components/InviteEmployeeModal';

interface Employee {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface Company {
  id: string;
  name: string;
  created_at: string;
}

const CompanySettings: React.FC = () => {
  const { user } = useAuth();
  const [company, setCompany] = useState<Company | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [companyName, setCompanyName] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [companyRes, employeesRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/company/info`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        axios.get(`${API_BASE_URL}/company/employees`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      setCompany(companyRes.data);
      setCompanyName(companyRes.data.name);
      setEmployees(employeesRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateCompanyName = async () => {
    if (!companyName.trim()) {
      setError('Le nom de la société ne peut pas être vide');
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `${API_BASE_URL}/company/update`,
        { name: companyName },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setCompany(response.data);
      setSuccess('Nom de la société mis à jour avec succès');

      // Update user in localStorage
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        userData.company_name = companyName;
        localStorage.setItem('user', JSON.stringify(userData));
      }

      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la mise à jour');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteEmployee = async (employeeId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet employé ?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_BASE_URL}/company/employees/${employeeId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setEmployees(employees.filter(emp => emp.id !== employeeId));
      setSuccess('Employé supprimé avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  const handleChangeRole = async (employeeId: string, newRole: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `${API_BASE_URL}/company/employees/${employeeId}/role`,
        { role: newRole },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setEmployees(employees.map(emp =>
        emp.id === employeeId ? response.data : emp
      ));
      setSuccess('Rôle mis à jour avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du changement de rôle');
    }
  };

  const handleInviteSuccess = () => {
    loadData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-4 md:p-6">
      <div className="mb-4 md:mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Building2 className="w-6 h-6 md:w-8 md:h-8" />
          Gestion de la société
        </h1>
        <p className="text-sm md:text-base text-gray-600 mt-2">Gérez les informations de votre société et vos employés</p>
      </div>

      {/* Messages */}
      {error && (
        <div className="mb-4 md:mb-6 p-3 md:p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 md:mb-6 p-3 md:p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
          {success}
        </div>
      )}

      {/* Company Info */}
      <div className="bg-white rounded-lg shadow-md p-4 md:p-6 mb-4 md:mb-6">
        <h2 className="text-lg md:text-xl font-bold text-gray-900 mb-4">Informations de la société</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-2">
              Nom de la société
            </label>
            <div className="flex flex-col sm:flex-row gap-2">
              <input
                id="companyName"
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="flex-1 px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm md:text-base"
              />
              <button
                onClick={handleUpdateCompanyName}
                disabled={saving || companyName === company?.name}
                className="flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap text-sm md:text-base"
              >
                <Save size={18} />
                <span className="hidden sm:inline">{saving ? 'Enregistrement...' : 'Enregistrer'}</span>
                <span className="sm:hidden">{saving ? 'Saving...' : 'Save'}</span>
              </button>
            </div>
          </div>

          <div className="text-xs md:text-sm text-gray-600">
            <span className="font-medium">Créée le :</span>{' '}
            {company && new Date(company.created_at).toLocaleDateString('fr-FR')}
          </div>
        </div>
      </div>

      {/* Employees */}
      <div className="bg-white rounded-lg shadow-md p-4 md:p-6">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-4">
          <h2 className="text-lg md:text-xl font-bold text-gray-900">Employés ({employees.length})</h2>
          <button
            onClick={() => setShowInviteModal(true)}
            className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition text-sm md:text-base whitespace-nowrap"
          >
            <UserPlus size={18} />
            <span className="hidden sm:inline">Inviter un employé</span>
            <span className="sm:hidden">Inviter</span>
          </button>
        </div>

        <div className="space-y-3">
          {employees.map((employee) => (
            <div
              key={employee.id}
              className="border border-gray-200 rounded-lg p-3 md:p-4 hover:bg-gray-50 transition"
            >
              <div className="flex flex-col gap-3">
                {/* Email and badges */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <Mail size={14} className="text-gray-400 flex-shrink-0" />
                    <span className="font-medium text-gray-900 text-sm md:text-base break-all">{employee.email}</span>
                    {employee.id === user?.id && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded whitespace-nowrap">
                        Vous
                      </span>
                    )}
                    {!employee.is_active && (
                      <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded whitespace-nowrap">
                        En attente
                      </span>
                    )}
                  </div>

                  {/* Role and date */}
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-xs md:text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      {employee.role === 'OWNER' ? <Shield size={14} /> : <User size={14} />}
                      {employee.role === 'OWNER' ? 'Propriétaire' : 'Employé'}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar size={14} />
                      Ajouté le {new Date(employee.created_at).toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                {employee.id !== user?.id && (
                  <div className="flex flex-col sm:flex-row gap-2 pt-2 border-t border-gray-100">
                    <select
                      value={employee.role}
                      onChange={(e) => handleChangeRole(employee.id, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                    >
                      <option value="EMPLOYEE">Employé</option>
                      <option value="OWNER">Propriétaire</option>
                    </select>
                    <button
                      onClick={() => handleDeleteEmployee(employee.id)}
                      className="flex items-center justify-center gap-2 px-4 py-2 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition text-sm whitespace-nowrap"
                      title="Supprimer"
                    >
                      <Trash2 size={16} />
                      <span>Supprimer</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <InviteEmployeeModal
        isOpen={showInviteModal}
        onClose={() => {
          setShowInviteModal(false);
          handleInviteSuccess();
        }}
      />
    </div>
  );
};

export default CompanySettings;
