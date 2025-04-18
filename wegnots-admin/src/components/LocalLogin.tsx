import React, { useState } from 'react';

interface LocalLoginProps {
  onLogin: (email: string, password: string) => void;
  loading: boolean;
}

export const LocalLogin: React.FC<LocalLoginProps> = ({ onLogin, loading }) => {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setError('Preencha todos os campos.');
      return;
    }
    onLogin(form.email, form.password);
  };

  return (
    <form onSubmit={handleSubmit} autoComplete="off">
      <label htmlFor="email">E-mail</label>
      <input id="email" name="email" type="email" value={form.email} onChange={handleChange} required disabled={loading} style={{ width: '100%', marginBottom: 8 }} />
      <label htmlFor="password">Senha</label>
      <input id="password" name="password" type="password" value={form.password} onChange={handleChange} required disabled={loading} style={{ width: '100%', marginBottom: 16 }} />
      {error && <div role="alert" style={{ color: '#b00020', marginBottom: 12 }}>{error}</div>}
      <button type="submit" disabled={loading} style={{ width: '100%', padding: 10, fontSize: 16 }}>
        {loading ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  );
};
