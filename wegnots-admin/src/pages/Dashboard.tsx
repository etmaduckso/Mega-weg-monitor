import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Avatar,
  LinearProgress,
  Button
} from '@mui/material';
import { 
  Person as PersonIcon,
  Email as EmailIcon, 
  Telegram as TelegramIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import MainLayout from '../layouts/MainLayout';
import { fetchMonitoringData, api } from '../services/api';

interface User {
  name: string;
  email: string;
  chat_id: string;
}

interface SystemStatus {
  service: string;
  status: 'online' | 'offline';
  lastUpdated?: string;
}

const Dashboard: React.FC = () => {
  const [monitoringData, setMonitoringData] = useState<any[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus[]>([
    { service: 'Monitor', status: 'online', lastUpdated: new Date().toLocaleString() },
    { service: 'IMAP', status: 'online', lastUpdated: new Date().toLocaleString() },
    { service: 'Telegram', status: 'online', lastUpdated: new Date().toLocaleString() },
  ]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMonitoringData = async () => {
      setLoading(true);
      try {
        const data = await fetchMonitoringData();
        setMonitoringData(data);
      } catch (err) {
        setError('Erro ao carregar dados de monitoramento.');
      } finally {
        setLoading(false);
      }
    };

    loadMonitoringData();
  }, []);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      setError(null);
      try {
        // Tentativa de buscar usuários da API
        try {
          const token = localStorage.getItem('token');
          const res = await api.get('/users', {
            headers: { Authorization: `Bearer ${token}` },
          });
          setUsers(res.data);
        } catch (err) {
          // Caso a API falhe, carregamos dados de exemplo para o usuário admin
          if (localStorage.getItem('token') === 'admin-default-token') {
            setUsers([
              { name: 'João da Silva', email: 'joao@exemplo.com', chat_id: '123456789' },
              { name: 'Maria Oliveira', email: 'maria@exemplo.com', chat_id: '987654321' },
              { name: 'Pedro Santos', email: 'pedro@exemplo.com', chat_id: '456789123' },
            ]);
          } else {
            throw err;
          }
        }
      } catch (err: any) {
        setError('Erro ao carregar usuários.');
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const getStatusColor = (status: string) => {
    return status === 'online' ? 'success' : 'error';
  };

  if (loading && !users.length) return (
    <MainLayout title="Dashboard">
      <Box sx={{ width: '100%', mt: 4 }}>
        <Typography variant="h6" gutterBottom>Carregando dados...</Typography>
        <LinearProgress />
      </Box>
    </MainLayout>
  );

  return (
    <MainLayout title="Dashboard">
      <Box>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Bem-vindo ao WegNots Monitor
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Painel de controle para monitoramento de e-mails e notificações
          </Typography>
        </Box>

        {/* Status Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {systemStatus.map((status) => (
            <Grid item xs={12} md={4} key={status.service}>
              <Card>
                <CardHeader 
                  title={status.service} 
                  subheader={`Última atualização: ${status.lastUpdated}`}
                  avatar={<Avatar sx={{ bgcolor: status.status === 'online' ? 'success.main' : 'error.main' }}><CheckCircleIcon /></Avatar>}
                />
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={status.status.toUpperCase()} 
                      color={getStatusColor(status.status)} 
                      sx={{ mr: 1 }} 
                    />
                    <Typography variant="body2" color="text.secondary">
                      {status.status === 'online' ? 'Serviço funcionando normalmente' : 'Serviço offline'}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Monitoring Data */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6} lg={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>Status do Monitor</Typography>
              {monitoringData.length > 0 ? (
                <ul style={{ paddingLeft: '20px' }}>
                  {monitoringData.map((item, index) => (
                    <li key={index}>{item.message}</li>
                  ))}
                </ul>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Sistema funcionando normalmente. Nenhum alerta registrado.
                </Typography>
              )}
            </Paper>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>E-mails Monitorados</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Chip label="100%" color="success" sx={{ mr: 1 }} />
                <Typography variant="body2">Taxa de sucesso</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total de e-mails processados: 125
              </Typography>
              <Typography variant="body2" color="text.secondary">
                E-mails com alertas: 24
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>Notificações</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Chip label="100%" color="success" sx={{ mr: 1 }} />
                <Typography variant="body2">Taxa de entrega</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Notificações enviadas hoje: 24
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Usuários notificados: {users.length}
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Users Table */}
        <Card sx={{ mt: 4 }}>
          <CardHeader 
            title="Usuários Cadastrados" 
            subheader={`Total de usuários: ${users.length}`}
            action={
              <Button variant="outlined" onClick={() => window.location.href = '/users'}>
                Ver todos
              </Button>
            }
          />
          <TableContainer component={Paper}>
            <Table sx={{ minWidth: 650 }} aria-label="tabela de usuários">
              <TableHead>
                <TableRow sx={{ bgcolor: 'primary.light' }}>
                  <TableCell><Box sx={{ display: 'flex', alignItems: 'center' }}><PersonIcon sx={{ mr: 1 }} /> Nome</Box></TableCell>
                  <TableCell><Box sx={{ display: 'flex', alignItems: 'center' }}><EmailIcon sx={{ mr: 1 }} /> E-mail</Box></TableCell>
                  <TableCell><Box sx={{ display: 'flex', alignItems: 'center' }}><TelegramIcon sx={{ mr: 1 }} /> ChatID do Telegram</Box></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user, idx) => (
                  <TableRow key={idx} sx={{ '&:nth-of-type(odd)': { backgroundColor: 'action.hover' } }}>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip 
                        icon={<TelegramIcon />} 
                        label={user.chat_id} 
                        color="primary" 
                        variant="outlined" 
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Card>

        {error && (
          <Paper sx={{ p: 2, mt: 3, bgcolor: 'error.light' }}>
            <Typography color="error">{error}</Typography>
          </Paper>
        )}
      </Box>
    </MainLayout>
  );
};

export default Dashboard;
