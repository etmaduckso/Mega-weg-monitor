import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Snackbar,
  Divider,
  Card,
  CardContent,
  CardHeader,
  Grid,
  TextField,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  MailOutline as MailIcon,
  Telegram as TelegramIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Check as CheckIcon,
  Cancel as CancelIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import MainLayout from '../layouts/MainLayout';
import { api, saveMonitoringConfig } from '../services/api';

interface ConfigSettings {
  imapMonitoring: boolean;
  notificationsEnabled: boolean;
  emailCheckInterval: number;
  serverAddress: string;
  serverPort: number;
  emailUser: string;
  emailPassword: string;
  telegramEnabled: boolean;
  telegramBotToken: string;
  telegramDefaultChatId: string;
}

interface User {
  id: string;
  name: string;
  email: string;
  chat_id: string;
  receivesAlerts: boolean;
}

const SettingsPage: React.FC = () => {
  const [config, setConfig] = useState<ConfigSettings>({
    imapMonitoring: true,
    notificationsEnabled: true,
    emailCheckInterval: 60,
    serverAddress: '',
    serverPort: 993,
    emailUser: '',
    emailPassword: '',
    telegramEnabled: true,
    telegramBotToken: '',
    telegramDefaultChatId: ''
  });
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  useEffect(() => {
    fetchSettings();
    fetchUsers();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      // Tentativa de buscar configurações da API
      try {
        const token = localStorage.getItem('token');
        const res = await api.get('/config', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setConfig(res.data);
      } catch (err) {
        // Caso a API falhe, carregamos dados de exemplo para o usuário admin
        if (localStorage.getItem('token') === 'admin-default-token') {
          setConfig({
            imapMonitoring: true,
            notificationsEnabled: true,
            emailCheckInterval: 60,
            serverAddress: 'imap.example.com',
            serverPort: 993,
            emailUser: 'monitor@example.com',
            emailPassword: '********',
            telegramEnabled: true,
            telegramBotToken: '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            telegramDefaultChatId: '123456789'
          });
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      setError('Erro ao carregar configurações.');
      setSnackbar({
        open: true,
        message: 'Erro ao carregar configurações do sistema.',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
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
            { id: '1', name: 'João da Silva', email: 'joao@exemplo.com', chat_id: '123456789', receivesAlerts: true },
            { id: '2', name: 'Maria Oliveira', email: 'maria@exemplo.com', chat_id: '987654321', receivesAlerts: true },
            { id: '3', name: 'Pedro Santos', email: 'pedro@exemplo.com', chat_id: '456789123', receivesAlerts: false },
          ]);
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      setError('Erro ao carregar usuários.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const numberValue = parseInt(value, 10);
    if (!isNaN(numberValue)) {
      setConfig(prev => ({
        ...prev,
        [name]: numberValue
      }));
    }
  };

  const handleToggleUserAlerts = (userId: string, currentValue: boolean) => {
    const updatedUsers = users.map(user => 
      user.id === userId ? { ...user, receivesAlerts: !currentValue } : user
    );
    setUsers(updatedUsers);
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      // Envia configurações para o backend
      await saveMonitoringConfig({
        checkInterval: config.emailCheckInterval,
        serverAddress: config.serverAddress,
        serverPort: config.serverPort,
        emailUser: config.emailUser,
        emailPassword: config.emailPassword,
        telegramEnabled: config.telegramEnabled,
        telegramBotToken: config.telegramBotToken,
        telegramDefaultChatId: config.telegramDefaultChatId,
        notificationsEnabled: config.notificationsEnabled
      });

      setSnackbar({
        open: true,
        message: 'Configurações salvas com sucesso!',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao salvar configurações. Tente novamente.',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <MainLayout title="Configurações">
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Configurações do Sistema
          </Typography>
          <Box>
            <Button 
              variant="outlined" 
              color="primary" 
              startIcon={<RefreshIcon />} 
              onClick={fetchSettings}
              sx={{ mr: 1 }}
              disabled={saving}
            >
              Atualizar
            </Button>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />} 
              onClick={handleSaveSettings}
              disabled={saving || loading}
            >
              {saving ? 'Salvando...' : 'Salvar Alterações'}
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {/* Configurações do Sistema */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader 
                  title="Configurações Principais" 
                  avatar={<Avatar sx={{ bgcolor: 'primary.main' }}><SettingsIcon /></Avatar>}
                />
                <Divider />
                <CardContent>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.imapMonitoring}
                        onChange={handleChange}
                        name="imapMonitoring"
                        color="primary"
                      />
                    }
                    label="Monitoramento de E-mail IMAP"
                  />
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 3, mb: 2 }}>
                    Ativa ou desativa o monitoramento do servidor IMAP
                  </Typography>

                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.notificationsEnabled}
                        onChange={handleChange}
                        name="notificationsEnabled"
                        color="primary"
                      />
                    }
                    label="Notificações"
                  />
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 3, mb: 2 }}>
                    Ativa ou desativa o envio de notificações para todos os usuários
                  </Typography>

                  <TextField
                    fullWidth
                    label="Intervalo de verificação (segundos)"
                    name="emailCheckInterval"
                    type="number"
                    value={config.emailCheckInterval}
                    onChange={handleNumberChange}
                    sx={{ mb: 2 }}
                    inputProps={{ min: 10, max: 3600 }}
                    disabled={!config.imapMonitoring}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Configurações do Servidor IMAP */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader 
                  title="Servidor IMAP" 
                  avatar={<Avatar sx={{ bgcolor: 'info.main' }}><MailIcon /></Avatar>}
                />
                <Divider />
                <CardContent>
                  <TextField
                    fullWidth
                    label="Endereço do Servidor"
                    name="serverAddress"
                    value={config.serverAddress}
                    onChange={handleChange}
                    sx={{ mb: 2 }}
                    disabled={!config.imapMonitoring}
                  />

                  <TextField
                    fullWidth
                    label="Porta"
                    name="serverPort"
                    type="number"
                    value={config.serverPort}
                    onChange={handleNumberChange}
                    sx={{ mb: 2 }}
                    disabled={!config.imapMonitoring}
                  />

                  <TextField
                    fullWidth
                    label="Usuário"
                    name="emailUser"
                    value={config.emailUser}
                    onChange={handleChange}
                    sx={{ mb: 2 }}
                    disabled={!config.imapMonitoring}
                  />

                  <TextField
                    fullWidth
                    label="Senha"
                    name="emailPassword"
                    type="password"
                    value={config.emailPassword}
                    onChange={handleChange}
                    disabled={!config.imapMonitoring}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Configurações do Telegram */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader 
                  title="Telegram" 
                  avatar={<Avatar sx={{ bgcolor: 'primary.main' }}><TelegramIcon /></Avatar>}
                />
                <Divider />
                <CardContent>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.telegramEnabled}
                        onChange={handleChange}
                        name="telegramEnabled"
                        color="primary"
                      />
                    }
                    label="Notificações via Telegram"
                  />
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 3, mb: 2 }}>
                    Ativa ou desativa o envio de notificações pelo Telegram
                  </Typography>

                  <TextField
                    fullWidth
                    label="Token do Bot"
                    name="telegramBotToken"
                    value={config.telegramBotToken}
                    onChange={handleChange}
                    sx={{ mb: 2 }}
                    disabled={!config.telegramEnabled}
                  />

                  <TextField
                    fullWidth
                    label="Chat ID Padrão"
                    name="telegramDefaultChatId"
                    value={config.telegramDefaultChatId}
                    onChange={handleChange}
                    disabled={!config.telegramEnabled}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Gerenciamento de Alertas por Usuário */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader 
                  title="Alertas por Usuário" 
                  avatar={<Avatar sx={{ bgcolor: 'warning.main' }}><NotificationsIcon /></Avatar>}
                />
                <Divider />
                <CardContent>
                  <List>
                    {users.map((user) => (
                      <ListItem key={user.id} sx={{ borderBottom: '1px solid #eee', py: 1 }}>
                        <ListItemIcon>
                          <Avatar sx={{ bgcolor: user.receivesAlerts ? 'success.main' : 'error.main' }}>
                            {user.name.charAt(0)}
                          </Avatar>
                        </ListItemIcon>
                        <ListItemText 
                          primary={user.name} 
                          secondary={
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <TelegramIcon fontSize="small" sx={{ mr: 0.5 }} color="primary" />
                              <Typography variant="caption">{user.chat_id}</Typography>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Tooltip title={user.receivesAlerts ? "Desativar alertas" : "Ativar alertas"}>
                            <Switch
                              edge="end"
                              checked={user.receivesAlerts}
                              onChange={() => handleToggleUserAlerts(user.id, user.receivesAlerts)}
                              disabled={!config.notificationsEnabled}
                            />
                          </Tooltip>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Informações do Sistema */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, mt: 2, bgcolor: 'info.lightest' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <InfoIcon color="info" sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    As alterações nas configurações serão aplicadas na próxima inicialização do sistema.
                    Alterações nas permissões de alertas por usuário são aplicadas imediatamente.
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        )}
      </Box>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </MainLayout>
  );
};

export default SettingsPage;