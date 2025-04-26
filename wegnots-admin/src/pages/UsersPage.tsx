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
  Button,
  IconButton,
  Switch,
  Chip,
  CircularProgress,
  Alert,
  Snackbar,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Settings as SettingsIcon,
  Telegram as TelegramIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import { api } from '../services/api';

interface User {
  id: string;
  name: string;
  email: string;
  chat_id: string;
  receivesAlerts: boolean;
  alertsReceived: number;
  lastAlertDate: string | null;
}

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info' | 'warning'
  });
  const [deleteDialog, setDeleteDialog] = useState({
    open: false,
    userId: '',
    userName: ''
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
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
            {
              id: '1',
              name: 'João da Silva',
              email: 'joao@exemplo.com',
              chat_id: '123456789',
              receivesAlerts: true,
              alertsReceived: 28,
              lastAlertDate: '2025-04-15T14:48:00'
            },
            {
              id: '2',
              name: 'Maria Oliveira',
              email: 'maria@exemplo.com',
              chat_id: '987654321',
              receivesAlerts: true,
              alertsReceived: 15,
              lastAlertDate: '2025-04-18T09:30:15'
            },
            {
              id: '3',
              name: 'Pedro Santos',
              email: 'pedro@exemplo.com',
              chat_id: '456789123',
              receivesAlerts: false,
              alertsReceived: 0,
              lastAlertDate: null
            }
          ]);
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      setError('Erro ao carregar usuários.');
      setSnackbar({
        open: true,
        message: 'Erro ao carregar lista de usuários.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      // Em produção, isso enviaria uma requisição para a API
      // await api.patch(`/users/${userId}`, { receivesAlerts: !currentStatus });
      
      // Atualização local temporária
      const updatedUsers = users.map(user =>
        user.id === userId ? { ...user, receivesAlerts: !currentStatus } : user
      );
      setUsers(updatedUsers);
      
      setSnackbar({
        open: true,
        message: `Usuário ${!currentStatus ? 'ativado' : 'desativado'} com sucesso.`,
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao alterar status do usuário.',
        severity: 'error'
      });
    }
  };

  const handleOpenDeleteDialog = (userId: string, userName: string) => {
    setDeleteDialog({
      open: true,
      userId,
      userName
    });
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialog({
      open: false,
      userId: '',
      userName: ''
    });
  };

  const handleDeleteUser = async () => {
    try {
      // Em produção, isso enviaria uma requisição para a API
      // await api.delete(`/users/${deleteDialog.userId}`);
      
      // Atualização local temporária
      const updatedUsers = users.filter(user => user.id !== deleteDialog.userId);
      setUsers(updatedUsers);
      
      setSnackbar({
        open: true,
        message: `Usuário ${deleteDialog.userName} excluído com sucesso.`,
        severity: 'success'
      });
      
      handleCloseDeleteDialog();
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao excluir usuário.',
        severity: 'error'
      });
      handleCloseDeleteDialog();
    }
  };

  const handleOpenUserSettings = (userId: string) => {
    navigate(`/users/settings/${userId}`);
  };

  const handleAddUser = () => {
    navigate('/users/register');
  };

  const handleEdit = (userId: string) => {
    navigate(`/users/config/${userId}`);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Nunca';
    
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <MainLayout title="Usuários">
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Gerenciamento de Usuários
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddUser}
          >
            Novo Usuário
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'primary.main' }}>
                  <TableCell sx={{ color: 'white' }}>Nome</TableCell>
                  <TableCell sx={{ color: 'white' }}>E-mail</TableCell>
                  <TableCell sx={{ color: 'white' }}>Chat ID (Telegram)</TableCell>
                  <TableCell sx={{ color: 'white' }}>Alertas Recebidos</TableCell>
                  <TableCell sx={{ color: 'white' }}>Último Alerta</TableCell>
                  <TableCell sx={{ color: 'white' }}>Status</TableCell>
                  <TableCell sx={{ color: 'white' }}>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                      <CircularProgress size={24} sx={{ mr: 1 }} />
                      Carregando usuários...
                    </TableCell>
                  </TableRow>
                ) : users.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                      Nenhum usuário cadastrado.
                    </TableCell>
                  </TableRow>
                ) : (
                  users.map((user) => (
                    <TableRow 
                      key={user.id}
                      sx={{ 
                        '&:nth-of-type(odd)': { backgroundColor: 'action.hover' },
                        bgcolor: !user.receivesAlerts ? 'grey.100' : undefined
                      }}
                    >
                      <TableCell sx={{ fontWeight: 'bold' }}>{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <TelegramIcon fontSize="small" color="primary" sx={{ mr: 1 }} />
                          {user.chat_id}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={user.alertsReceived} 
                          color={user.alertsReceived > 0 ? "primary" : "default"}
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>{formatDate(user.lastAlertDate)}</TableCell>
                      <TableCell>
                        <Switch
                          checked={user.receivesAlerts}
                          onChange={() => handleToggleUserStatus(user.id, user.receivesAlerts)}
                          color={user.receivesAlerts ? "success" : "default"}
                        />
                        <Typography variant="caption" display="block">
                          {user.receivesAlerts ? 'Ativo' : 'Inativo'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Configurações de notificação">
                          <IconButton 
                            color="primary" 
                            onClick={() => handleOpenUserSettings(user.id)}
                            size="small"
                          >
                            <SettingsIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Editar usuário">
                          <IconButton 
                            color="primary" 
                            onClick={() => handleEdit(user.id)}
                            size="small"
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Excluir usuário">
                          <IconButton 
                            color="error" 
                            onClick={() => handleOpenDeleteDialog(user.id, user.name)}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Box>

      {/* Diálogo de confirmação de exclusão */}
      <Dialog
        open={deleteDialog.open}
        onClose={handleCloseDeleteDialog}
      >
        <DialogTitle>Confirmar exclusão</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Tem certeza que deseja excluir o usuário <strong>{deleteDialog.userName}</strong>?
            Esta ação não pode ser desfeita.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="inherit">Cancelar</Button>
          <Button onClick={handleDeleteUser} color="error" variant="contained">
            Excluir
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </MainLayout>
  );
};

export default UsersPage;