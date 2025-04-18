import React from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';

interface Notification {
  id: string;
  timestamp: string;
  type: 'email' | 'telegram' | 'rocketchat';
  status: 'success' | 'failure';
  recipient: string;
  subject?: string;
  message: string;
}

export const NotificationsPage: React.FC = () => {
  const { data: notifications = [], isLoading } = useQuery<Notification[]>({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/notifications', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch notifications');
      return response.json();
    },
  });

  const getStatusColor = (status: string) => {
    return status === 'success' ? 'success' : 'error';
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'email':
        return 'Email';
      case 'telegram':
        return 'Telegram';
      case 'rocketchat':
        return 'Rocket.Chat';
      default:
        return type;
    }
  };

  if (isLoading) {
    return <Typography>Carregando notificações...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 4 }}>
        Histórico de Notificações
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Data/Hora</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Destinatário</TableCell>
              <TableCell>Assunto</TableCell>
              <TableCell>Mensagem</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {notifications.map((notification) => (
              <TableRow key={notification.id}>
                <TableCell>
                  {new Date(notification.timestamp).toLocaleString('pt-BR')}
                </TableCell>
                <TableCell>
                  <Chip
                    label={getTypeLabel(notification.type)}
                    color="primary"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={notification.status === 'success' ? 'Sucesso' : 'Falha'}
                    color={getStatusColor(notification.status)}
                  />
                </TableCell>
                <TableCell>{notification.recipient}</TableCell>
                <TableCell>{notification.subject || '-'}</TableCell>
                <TableCell>
                  <Typography
                    sx={{
                      maxWidth: '300px',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {notification.message}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};