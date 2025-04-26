import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Alert,
  Snackbar,
  CircularProgress,
  IconButton,
  Tooltip,
  Divider,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Telegram as TelegramIcon,
  Warning as WarningIcon,
  Check as CheckIcon,
  Info as InfoIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import MainLayout from '../layouts/MainLayout';
import { api } from '../services/api';

interface Notification {
  id: string;
  timestamp: string;
  type: 'critical' | 'moderate' | 'info';
  sender: string;
  recipient: string;
  subject: string;
  status: 'sent' | 'failed' | 'pending';
  user: string;
}

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    critical: 0,
    moderate: 0,
    info: 0,
    success: 0,
    failed: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      // Tentativa de buscar notificações da API
      try {
        const token = localStorage.getItem('token');
        const res = await api.get('/notifications', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setNotifications(res.data);
        calculateStats(res.data);
      } catch (err) {
        // Caso a API falhe, carregamos dados de exemplo para o usuário admin
        if (localStorage.getItem('token') === 'admin-default-token') {
          const mockNotifications: Notification[] = [
            {
              id: '1',
              timestamp: '2025-04-18T10:15:32',
              type: 'critical',
              sender: 'sistema@empresa.com',
              recipient: 'joao@exemplo.com',
              subject: 'URGENTE: Falha no servidor principal',
              status: 'sent',
              user: 'João da Silva'
            },
            {
              id: '2',
              timestamp: '2025-04-18T09:30:15',
              type: 'moderate',
              sender: 'monitoramento@empresa.com',
              recipient: 'maria@exemplo.com',
              subject: 'IMPORTANTE: Atualização de sistema pendente',
              status: 'sent',
              user: 'Maria Oliveira'
            },
            {
              id: '3',
              timestamp: '2025-04-18T08:45:00',
              type: 'info',
              sender: 'updates@empresa.com',
              recipient: 'pedro@exemplo.com',
              subject: 'Relatório diário disponível',
              status: 'sent',
              user: 'Pedro Santos'
            },
            {
              id: '4',
              timestamp: '2025-04-17T23:10:22',
              type: 'critical',
              sender: 'alertas@empresa.com',
              recipient: 'ana@exemplo.com',
              subject: 'CRÍTICO: Espaço em disco crítico',
              status: 'failed',
              user: 'Ana Souza'
            },
            {
              id: '5',
              timestamp: '2025-04-17T17:22:11',
              type: 'info',
              sender: 'sistema@empresa.com',
              recipient: 'carlos@exemplo.com',
              subject: 'Backup concluído com sucesso',
              status: 'sent',
              user: 'Carlos Ferreira'
            }
          ];
          setNotifications(mockNotifications);
          calculateStats(mockNotifications);
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      setError('Erro ao carregar notificações.');
      setSnackbar({
        open: true,
        message: 'Erro ao carregar histórico de notificações.',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data: Notification[]) => {
    const stats = {
      total: data.length,
      critical: data.filter(n => n.type === 'critical').length,
      moderate: data.filter(n => n.type === 'moderate').length,
      info: data.filter(n => n.type === 'info').length,
      success: data.filter(n => n.status === 'sent').length,
      failed: data.filter(n => n.status === 'failed').length
    };
    setStats(stats);
  };

  const renderAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'moderate':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const renderStatusChip = (status: string) => {
    switch (status) {
      case 'sent':
        return <Chip icon={<CheckIcon />} label="Enviado" color="success" size="small" />;
      case 'failed':
        return <Chip icon={<ErrorIcon />} label="Falha" color="error" size="small" />;
      case 'pending':
        return <Chip icon={<CircularProgress size={14} />} label="Pendente" color="warning" size="small" />;
      default:
        return <Chip label={status} />;
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <MainLayout title="Notificações">
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Histórico de Notificações
          </Typography>
          <Box>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<RefreshIcon />} 
              onClick={fetchNotifications}
              disabled={loading}
            >
              {loading ? 'Carregando...' : 'Atualizar'}
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Dashboard de estatísticas */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>Total de Notificações</Typography>
                <Typography variant="h4">{stats.total}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {stats.success} enviadas com sucesso • {stats.failed} falhas
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>Por Nível de Alerta</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 1 }}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Tooltip title="Alertas Críticos">
                      <IconButton color="error" sx={{ mb: 1 }}>
                        <ErrorIcon fontSize="large" />
                      </IconButton>
                    </Tooltip>
                    <Typography variant="h6">{stats.critical}</Typography>
                    <Typography variant="body2">Críticos</Typography>
                  </Box>
                  <Divider orientation="vertical" flexItem />
                  <Box sx={{ textAlign: 'center' }}>
                    <Tooltip title="Alertas Moderados">
                      <IconButton color="warning" sx={{ mb: 1 }}>
                        <WarningIcon fontSize="large" />
                      </IconButton>
                    </Tooltip>
                    <Typography variant="h6">{stats.moderate}</Typography>
                    <Typography variant="body2">Moderados</Typography>
                  </Box>
                  <Divider orientation="vertical" flexItem />
                  <Box sx={{ textAlign: 'center' }}>
                    <Tooltip title="Alertas Informativos">
                      <IconButton color="info" sx={{ mb: 1 }}>
                        <InfoIcon fontSize="large" />
                      </IconButton>
                    </Tooltip>
                    <Typography variant="h6">{stats.info}</Typography>
                    <Typography variant="body2">Informativos</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabela de notificações */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white' }}>Data/Hora</TableCell>
                <TableCell sx={{ color: 'white' }}>Tipo</TableCell>
                <TableCell sx={{ color: 'white' }}>Destinatário</TableCell>
                <TableCell sx={{ color: 'white' }}>Assunto</TableCell>
                <TableCell sx={{ color: 'white' }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    Carregando notificações...
                  </TableCell>
                </TableRow>
              ) : notifications.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">Nenhuma notificação encontrada.</TableCell>
                </TableRow>
              ) : (
                notifications.map((notification) => (
                  <TableRow 
                    key={notification.id} 
                    sx={{ 
                      '&:nth-of-type(odd)': { backgroundColor: 'action.hover' },
                      bgcolor: notification.type === 'critical' ? 'error.lightest' : undefined
                    }}
                  >
                    <TableCell>{formatDateTime(notification.timestamp)}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {renderAlertTypeIcon(notification.type)}
                        <Typography variant="body2" sx={{ ml: 1 }}>
                          {notification.type === 'critical' ? 'Crítico' : 
                           notification.type === 'moderate' ? 'Moderado' : 'Informativo'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TelegramIcon fontSize="small" color="primary" sx={{ mr: 1 }} />
                        <Typography variant="body2">{notification.user}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{notification.subject}</TableCell>
                    <TableCell>{renderStatusChip(notification.status)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </MainLayout>
  );
};

export default NotificationsPage;