import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

interface User {
  name: string;
  email: string;
  chat_id: string;
}

const UsersList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        const res = await api.get('/users', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUsers(res.data);
      } catch (err: any) {
        setError('Erro ao carregar usuários.');
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  return (
    <Box sx={{ maxWidth: 800, margin: '40px auto', padding: 3 }}>
      <Typography variant="h4" gutterBottom>
        Usuários Cadastrados
      </Typography>
      {loading && <Typography>Carregando...</Typography>}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && (
        <Paper sx={{ padding: 2 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left', padding: 8 }}>Nome</th>
                <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left', padding: 8 }}>E-mail</th>
                <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left', padding: 8 }}>ChatID do Telegram</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, idx) => (
                <tr key={idx}>
                  <td style={{ borderBottom: '1px solid #eee', padding: 8 }}>{user.name}</td>
                  <td style={{ borderBottom: '1px solid #eee', padding: 8 }}>{user.email}</td>
                  <td style={{ borderBottom: '1px solid #eee', padding: 8 }}>{user.chat_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Paper>
      )}
      <Box sx={{ marginTop: 2 }}>
        <button onClick={() => navigate('/dashboard')}>Voltar ao Dashboard</button>
      </Box>
    </Box>
  );
};

export default UsersList;
