import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Snackbar,
  CircularProgress
} from '@mui/material';
import {
  MailOutline as MailIcon,
  Telegram as TelegramIcon,
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import MainLayout from '../layouts/MainLayout';
import { api, saveUserConfig } from '../services/api';

interface UserConfig {
  id: string;
  name: string;
  email: string;
  chat_id: string;
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

const UserConfigPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [config, setConfig] = useState<UserConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  useEffect(() => {
    fetchUserConfig();
  }, [userId]);

  const fetchUserConfig = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await api.get(`/users/${userId}/config`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setConfig(response.data);
    } catch (err) {
      // Simulação para desenvolvimento
      if (localStorage.getItem('token') === 'admin-default-token') {
        setConfig({
          id: userId || '',
          name: 'Usuário Exemplo',
          email: 'exemplo@email.com',
          chat_id: '123456789',
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
        setSnackbar({
          open: true,
          message: 'Erro ao carregar configurações do usuário.',
          severity: 'error'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    if (!config) return;

    setConfig(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      };
    });
  };

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    try {
      await saveUserConfig(userId || '', config);
      setSnackbar({
        open: true,
        message: 'Configurações salvas com sucesso!',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Erro ao salvar configurações. Por favor, tente novamente.',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  if (loading) {
    return (
      <MainLayout title="Configurações do Usuário">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  if (!config) {
    return (
      <MainLayout title="Configurações do Usuário">
        <Alert severity="error">Usuário não encontrado</Alert>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Configurações do Usuário">
      <Box sx={{ maxWidth: 1200, margin: '0 auto', p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/users')}
            sx={{ mr: 2 }}
            startIcon={<ArrowBackIcon />}
          >
            Voltar para Usuários
          </Button>
          <Typography variant="h5" sx={{ flex: 1 }}>
            Configurações do Usuário: {config?.name}
          </Typography>
        </Box>

        <Paper sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {/* Informações do Usuário */}
            <Grid item xs={12}>
              <Typography variant="h5" gutterBottom>
                Configurações do Usuário: {config.name}
              </Typography>
            </Grid>

            {/* Configurações de Monitoramento */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <MailIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">
                      Monitoramento de E-mail
                    </Typography>
                  </Box>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.imapMonitoring}
                        onChange={handleInputChange}
                        name="imapMonitoring"
                        color="primary"
                      />
                    }
                    label="Monitoramento IMAP"
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Intervalo de Verificação (segundos)"
                    type="number"
                    name="emailCheckInterval"
                    value={config.emailCheckInterval}
                    onChange={handleInputChange}
                    disabled={!config.imapMonitoring}
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Endereço do Servidor"
                    name="serverAddress"
                    value={config.serverAddress}
                    onChange={handleInputChange}
                    disabled={!config.imapMonitoring}
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Porta"
                    type="number"
                    name="serverPort"
                    value={config.serverPort}
                    onChange={handleInputChange}
                    disabled={!config.imapMonitoring}
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Usuário"
                    name="emailUser"
                    value={config.emailUser}
                    onChange={handleInputChange}
                    disabled={!config.imapMonitoring}
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Senha"
                    type="password"
                    name="emailPassword"
                    value={config.emailPassword}
                    onChange={handleInputChange}
                    disabled={!config.imapMonitoring}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Configurações de Notificação */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TelegramIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">
                      Configurações de Notificação
                    </Typography>
                  </Box>

                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.notificationsEnabled}
                        onChange={handleInputChange}
                        name="notificationsEnabled"
                      />
                    }
                    label="Notificações Ativadas"
                  />

                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.telegramEnabled}
                        onChange={handleInputChange}
                        name="telegramEnabled"
                        disabled={!config.notificationsEnabled}
                      />
                    }
                    label="Telegram"
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Chat ID do Telegram"
                    name="telegramDefaultChatId"
                    value={config.telegramDefaultChatId}
                    onChange={handleInputChange}
                    disabled={!config.telegramEnabled || !config.notificationsEnabled}
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Token do Bot Telegram"
                    name="telegramBotToken"
                    value={config.telegramBotToken}
                    onChange={handleInputChange}
                    disabled={!config.telegramEnabled || !config.notificationsEnabled}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Botões de Ação */}
            <Grid item xs={12}>
              <Box sx={{ 
                display: 'flex', 
                gap: 2, 
                justifyContent: 'flex-end',
                mt: 3,
                borderTop: '1px solid',
                borderColor: 'divider',
                pt: 3
              }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/users')}
                  startIcon={<ArrowBackIcon />}
                >
                  Cancelar
                </Button>
                <Button
                  variant="contained"
                  onClick={handleSave}
                  disabled={saving}
                  startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                >
                  {saving ? 'Salvando...' : 'Salvar Alterações'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </MainLayout>
  );
};

export default UserConfigPage;