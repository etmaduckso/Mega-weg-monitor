import React, { useState, useRef } from 'react';
import { useMsal } from '@azure/msal-react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../services/api';
import { LocalLogin } from './LocalLogin';

export const Login = () => {
  const { instance } = useMsal();
  const [useLocalLogin, setUseLocalLogin] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const azureButtonRef = useRef<HTMLButtonElement>(null);
  const localButtonRef = useRef<HTMLButtonElement>(null);
  const navigate = useNavigate();

  const handleAzureLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await instance.loginRedirect();
    } catch (err: any) {
      setError('Erro ao tentar login com Azure AD. Tente novamente.');
      setLoading(false);
    }
  };

  const handleLocalLogin = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await loginUser({ email, password });
      localStorage.setItem('token', res.data.token);
      setLoggedIn(true);
      setError(null);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err?.response?.data?.message || 'E-mail ou senha inválidos.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLogin = (local: boolean) => {
    setUseLocalLogin(local);
    setError(null);
    setTimeout(() => {
      if (local) {
        localButtonRef.current?.focus();
      } else {
        azureButtonRef.current?.focus();
      }
    }, 0);
  };

  if (loggedIn) {
    return (
      <div role="status" aria-live="polite" style={{ textAlign: 'center', marginTop: 40 }}>
        <h2>Bem-vindo!</h2>
        <p>Você está logado com login local.</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 350, margin: '40px auto', padding: 24, border: '1px solid #eee', borderRadius: 8, background: '#fafbfc' }}>
      <h2 style={{ textAlign: 'center' }}>Login</h2>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 16 }}>
        <button
          ref={azureButtonRef}
          onClick={() => handleSelectLogin(false)}
          aria-pressed={!useLocalLogin}
          disabled={loading}
          style={{ fontWeight: !useLocalLogin ? 'bold' : 'normal' }}
        >
          Azure AD
        </button>
        <button
          ref={localButtonRef}
          onClick={() => handleSelectLogin(true)}
          aria-pressed={useLocalLogin}
          disabled={loading}
          style={{ fontWeight: useLocalLogin ? 'bold' : 'normal' }}
        >
          Login Local
        </button>
      </div>
      {error && (
        <div role="alert" style={{ color: '#b00020', marginBottom: 12, textAlign: 'center' }}>{error}</div>
      )}
      {useLocalLogin ? (
        <LocalLogin onLogin={handleLocalLogin} loading={loading} />
      ) : (
        <button
          onClick={handleAzureLogin}
          disabled={loading}
          style={{ width: '100%', padding: 10, fontSize: 16 }}
          aria-busy={loading}
        >
          {loading ? 'Entrando...' : 'Entrar com Azure AD'}
        </button>
      )}
      <div style={{ textAlign: 'center', marginTop: 16 }}>
        <span>Não tem uma conta? </span>
        <Link to="/register">Criar conta</Link>
      </div>
    </div>
  );
};
