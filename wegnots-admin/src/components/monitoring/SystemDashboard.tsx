import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import {
  RefreshRounded,
  EmailRounded,
  NotificationsRounded,
  MemoryRounded,
  StorageRounded
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { monitoringService } from '../../services/monitoring';
import { SystemStatus } from '../../types/monitoring';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: string;
  progress?: number;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, progress }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Box sx={{ 
          backgroundColor: color || 'primary.main', 
          borderRadius: '50%',
          p: 1,
          mr: 2
        }}>
          {icon}
        </Box>
        <Typography variant="h6">{title}</Typography>
      </Box>
      <Typography variant="h4" sx={{ mb: 1 }}>{value}</Typography>
      {progress !== undefined && (
        <LinearProgress 
          variant="determinate" 
          value={progress}
          sx={{ 
            height: 8, 
            borderRadius: 4,
            backgroundColor: 'rgba(0,0,0,0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: color
            }
          }}
        />
      )}
    </CardContent>
  </Card>
);

export const SystemDashboard: React.FC = () => {
  const { data: status, isLoading, error, refetch } = useQuery<SystemStatus>({
    queryKey: ['systemStatus'],
    queryFn: monitoringService.getSystemStatus,
    refetchInterval: 30000 // Atualiza a cada 30 segundos
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return '#4caf50';
      case 'disconnected':
        return '#f44336';
      case 'error':
        return '#ff9800';
      default:
        return '#9e9e9e';
    }
  };

  const getStatusIcon = (serviceStatus: string) => {
    const color = getStatusColor(serviceStatus);
    return (
      <Chip
        label={serviceStatus.toUpperCase()}
        size="small"
        sx={{
          backgroundColor: color,
          color: 'white',
          fontWeight: 'bold'
        }}
      />
    );
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Erro ao carregar status do sistema. Por favor, tente novamente.
      </Alert>
    );
  }

  if (!status) return null;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          Dashboard do Sistema
        </Typography>
        <Tooltip title="Atualizar">
          <IconButton onClick={() => refetch()}>
            <RefreshRounded />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* Estatísticas de E-mails */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="E-mails Processados"
            value={status.monitoring.processedEmails}
            icon={<EmailRounded sx={{ color: 'white' }} />}
            color="#2196f3"
          />
        </Grid>

        {/* Estatísticas de Alertas */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Alertas Enviados"
            value={status.monitoring.sentAlerts}
            icon={<NotificationsRounded sx={{ color: 'white' }} />}
            color="#ff9800"
          />
        </Grid>

        {/* Uso de CPU */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="CPU"
            value={`${status.system.cpu}%`}
            icon={<MemoryRounded sx={{ color: 'white' }} />}
            color="#4caf50"
            progress={status.system.cpu}
          />
        </Grid>

        {/* Uso de Memória */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Memória"
            value={`${status.system.memory}%`}
            icon={<StorageRounded sx={{ color: 'white' }} />}
            color="#f44336"
            progress={status.system.memory}
          />
        </Grid>
      </Grid>

      {/* Status dos Serviços */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Status dos Serviços
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography>IMAP:</Typography>
                  {getStatusIcon(status.imap.status)}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Última verificação: {new Date(status.imap.lastCheck || '').toLocaleString()}
                </Typography>
              </Grid>

              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography>Telegram:</Typography>
                  {getStatusIcon(status.telegram.status)}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Última mensagem: {new Date(status.telegram.lastMessage || '').toLocaleString()}
                </Typography>
              </Grid>

              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography>MongoDB:</Typography>
                  {getStatusIcon(status.mongodb.status)}
                </Box>
                {status.mongodb.error && (
                  <Typography variant="caption" color="error">
                    Erro: {status.mongodb.error}
                  </Typography>
                )}
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};