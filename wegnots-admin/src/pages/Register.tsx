import React, { useState, useMemo } from 'react';
import { registerUser } from '../services/api';

const validateEmail = (email: string) => /\S+@\S+\.\S+/.test(email);
const validatePassword = (password: string) => {
  const requirements = {
    length: password.length >= 12,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };
  return {
    isValid: Object.values(requirements).every(Boolean),
    requirements
  };
};

const validateChatId = (chatId: string) => /^[0-9-]+$/.test(chatId);

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', chatId: '', password: '', confirmPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);

  const passwordValidation = useMemo(() => validatePassword(form.password), [form.password]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(null);
    if (e.target.name === 'password') {
      setShowPasswordRequirements(true);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!form.name.trim()) return setError('Nome é obrigatório.');
    if (!validateEmail(form.email)) return setError('E-mail inválido.');
    if (!validateChatId(form.chatId)) return setError('ChatID do Telegram inválido. Use apenas números e hífen.');
    if (!passwordValidation.isValid) return setError('A senha não atende aos requisitos mínimos.');
    if (form.password !== form.confirmPassword) return setError('As senhas não coincidem.');

    setLoading(true);
    try {
      await registerUser({ 
        name: form.name.trim(), 
        email: form.email.trim(), 
        chatId: form.chatId.trim(), 
        password: form.password 
      });
      setSuccess(true);
      setForm({ name: '', email: '', chatId: '', password: '', confirmPassword: '' });
      setShowPasswordRequirements(false);
    } catch (err: any) {
      console.error('Erro na requisição de registro:', err);
      setError(err?.response?.data?.detail || err?.response?.data?.message || 'Erro ao registrar. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const formStyles = {
    container: {
      maxWidth: 400,
      margin: '40px auto',
      padding: '24px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      background: '#fff',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    },
    title: {
      textAlign: 'center' as const,
      marginBottom: '24px',
      color: '#333'
    },
    label: {
      display: 'block',
      marginBottom: '4px',
      color: '#555'
    },
    input: {
      width: '100%',
      padding: '8px',
      marginBottom: '16px',
      border: '1px solid #ddd',
      borderRadius: '4px',
      fontSize: '14px'
    },
    button: {
      width: '100%',
      padding: '12px',
      fontSize: '16px',
      backgroundColor: '#0066cc',
      color: '#fff',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      transition: 'background-color 0.2s'
    },
    buttonDisabled: {
      backgroundColor: '#cccccc',
      cursor: 'not-allowed'
    },
    error: {
      color: '#b00020',
      marginBottom: '12px',
      padding: '8px',
      backgroundColor: '#fff5f5',
      borderRadius: '4px',
      fontSize: '14px'
    },
    success: {
      color: '#00802b',
      marginBottom: '12px',
      padding: '8px',
      backgroundColor: '#f0fff4',
      borderRadius: '4px',
      fontSize: '14px'
    },
    requirements: {
      fontSize: '12px',
      marginBottom: '16px',
      color: '#666'
    },
    requirementMet: {
      color: '#00802b'
    },
    requirementNotMet: {
      color: '#b00020'
    }
  };

  return (
    <div style={formStyles.container}>
      <h2 style={formStyles.title}>Cadastro de Usuário</h2>
      <form onSubmit={handleSubmit} autoComplete="off">
        <label htmlFor="name" style={formStyles.label}>Nome</label>
        <input
          id="name"
          name="name"
          type="text"
          value={form.name}
          onChange={handleChange}
          required
          autoFocus
          disabled={loading}
          style={formStyles.input}
        />

        <label htmlFor="email" style={formStyles.label}>E-mail</label>
        <input
          id="email"
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
          required
          disabled={loading}
          style={formStyles.input}
        />

        <label htmlFor="chatId" style={formStyles.label}>
          ChatID do Telegram
          <span style={{ fontSize: '12px', color: '#666', marginLeft: '4px' }}>
            (apenas números e hífen)
          </span>
        </label>
        <input
          id="chatId"
          name="chatId"
          type="text"
          value={form.chatId}
          onChange={handleChange}
          required
          disabled={loading}
          style={formStyles.input}
          placeholder="Ex: 123456789"
        />

        <label htmlFor="password" style={formStyles.label}>Senha</label>
        <input
          id="password"
          name="password"
          type="password"
          value={form.password}
          onChange={handleChange}
          required
          disabled={loading}
          style={formStyles.input}
        />

        {showPasswordRequirements && (
          <div style={formStyles.requirements}>
            <div style={passwordValidation.requirements.length ? formStyles.requirementMet : formStyles.requirementNotMet}>
              ✓ Mínimo de 12 caracteres
            </div>
            <div style={passwordValidation.requirements.uppercase ? formStyles.requirementMet : formStyles.requirementNotMet}>
              ✓ Pelo menos uma letra maiúscula
            </div>
            <div style={passwordValidation.requirements.lowercase ? formStyles.requirementMet : formStyles.requirementNotMet}>
              ✓ Pelo menos uma letra minúscula
            </div>
            <div style={passwordValidation.requirements.number ? formStyles.requirementMet : formStyles.requirementNotMet}>
              ✓ Pelo menos um número
            </div>
            <div style={passwordValidation.requirements.special ? formStyles.requirementMet : formStyles.requirementNotMet}>
              ✓ Pelo menos um caractere especial
            </div>
          </div>
        )}

        <label htmlFor="confirmPassword" style={formStyles.label}>Confirmar Senha</label>
        <input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          value={form.confirmPassword}
          onChange={handleChange}
          required
          disabled={loading}
          style={formStyles.input}
        />

        {error && <div role="alert" style={formStyles.error}>{error}</div>}
        {success && (
          <div role="status" style={formStyles.success}>
            Cadastro realizado com sucesso! Faça login para acessar.
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            ...formStyles.button,
            ...(loading ? formStyles.buttonDisabled : {})
          }}
        >
          {loading ? 'Cadastrando...' : 'Cadastrar'}
        </button>
      </form>
    </div>
  );
}
