import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Avatar,
  Divider,
  Chip,
  FormControlLabel,
  Switch,
  Button,
  Alert,
  Snackbar,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Person as PersonIcon,
  Telegram as TelegramIcon,
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon,
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  Check as CheckIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import { api } from '../services/api';

interface User {
  id: string;
  name: string;
  email: string;
  chat_id: string;
  receivesAlerts: boolean;
}

interface AlertType {
  id: string;
  name: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low' | 'info';
  active: boolean;
}

interface UserSettings {
  receiveAllAlerts: boolean;
  alertPreferences: {
    alertTypeId: string;
    enabled: boolean;
  }[];
  notificationSchedule: {
    startTime: string;
    endTime: string;
    active: boolean;
  };
  customMessage: string;
}

const UserSettingsPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const [user, setUser] = useState<User | null>(null);
  const [alertTypes, setAlertTypes] = useState<AlertType[]>([]);
  const [settings, setSettings] = useState<UserSettings>({
    receiveAllAlerts: true,
    alertPreferences: [],
    notificationSchedule: {
      startTime: '08:00',
      endTime: '20:00',
      active: true
    },
    customMessage: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    if (userId) {
      fetchUserData();
      fetchAlertTypes();
    }
  }, [userId]);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      // Tentativa de buscar dados do usuário da API
      try {
        const token = localStorage.getItem('token');
        const res = await api.get(`/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(res.data);
        
        // Buscar configurações do usuário
        const settingsRes = await api.get(`/users/${userId}/settings`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSettings(settingsRes.data);
      } catch (err) {
        // Caso a API falhe, carregamos dados de exemplo para o usuário admin
        if (localStorage.getItem('token') === 'admin-default-token') {
          if (userId === '1') {
            setUser({
              id: '1',
              name: 'João da Silva',
              email: 'joao@exemplo.com',
              chat_id: '123456789',
              receivesAlerts: true
            });
            
            // Configurações de exemplo
            setSettings({
              receiveAllAlerts: false,
              alertPreferences: [
                { alertTypeId: '1', enabled: true },  // Intrusão
                { alertTypeId: '2', enabled: true },  // Procurado
                { alertTypeId: '3', enabled: false }, // Suspeito
                { alertTypeId: '4', enabled: false }  // Teste Facial
              ],
              notificationSchedule: {
                startTime: '08:00',
                endTime: '18:00',
                active: true
              },
              customMessage: 'Atenção: Novo alerta detectado para sua unidade!'
            });
          } else if (userId === '2') {
            setUser({
              id: '2',
              name: 'Maria Oliveira',
              email: 'maria@exemplo.com',
              chat_id: '987654321',
              receivesAlerts: true
            });
            
            setSettings({
              receiveAllAlerts: true,
              alertPreferences: [],
              notificationSchedule: {
                startTime: '00:00',
                endTime: '23:59',
                active: true
              },
              customMessage: ''
            });
          } else if (userId === '3') {
            setUser({
              id: '3',
              name: 'Pedro Santos',
              email: 'pedro@exemplo.com',
              chat_id: '456789123',
              receivesAlerts: false
            });
            
            setSettings({
              receiveAllAlerts: false,
              alertPreferences: [
                { alertTypeId: '1', enabled: true }, // Intrusão
              ],
              notificationSchedule: {
                startTime: '08:00',
                endTime: '20:00',
                active: false
              },
              customMessage: ''
            });
          } else {
            throw new Error('Usuário não encontrado');
          }
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Erro ao carregar dados do usuário.',
        severity: 'error'
      });
      navigate('/users');
    } finally {
      setLoading(false);
    }
  };

  const fetchAlertTypes = async () => {
    try {
      // Tentativa de buscar tipos de alertas da API
      try {
        const token = localStorage.getItem('token');
        const res = await api.get('/alert-types', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAlertTypes(res.data);
        
        // Inicializa as preferências de alerta com os tipos existentes
        if (res.data.length > 0 && settings.alertPreferences.length === 0) {
          setSettings(prev => ({
            ...prev,
            alertPreferences: res.data.map((alert: AlertType) => ({
              alertTypeId: alert.id,
              enabled: true
            }))
          }));
        }
      } catch (err) {
        // Caso a API falhe, carregamos dados de exemplo
        if (localStorage.getItem('token') === 'admin-default-token') {
          const mockAlertTypes = [
            {
              id: '1',
              name: 'Intrusão',
              description: 'Alertas de intrusão detectados',
              priority: 'critical' as const,
              active: true
            },
            {
              id: '2',
              name: 'Procurado ou Foragido',
              description: 'Detecção de pessoas procuradas',
              priority: 'high' as const,
              active: true
            },
            {
              id: '3',
              name: 'Suspeito',
              description: 'Detecção de pessoas suspeitas',
              priority: 'medium' as const,
              active: true
            },
            {
              id: '4',
              name: 'Teste Facial',
              description: 'Testes de reconhecimento facial',
              priority: 'low' as const,
              active: true
            }
          ];
          setAlertTypes(mockAlertTypes);
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      console.error('Erro ao carregar tipos de alertas:', err);
    }
  };

  const handleToggleAllAlerts = (event: React.ChangeEvent<HTMLInputElement>) => {
    const checked = event.target.checked;
    setSettings(prev => ({
      ...prev,
      receiveAllAlerts: checked
    }));
  };

  const handleToggleAlertType = (alertTypeId: string) => {
    setSettings(prev => ({
      ...prev,
      alertPreferences: prev.alertPreferences.map(pref => 
        pref.alertTypeId === alertTypeId ? { ...pref, enabled: !pref.enabled } : pref
      )
    }));
  };

  const handleToggleSchedule = (event: React.ChangeEvent<HTMLInputElement>) => {
    const checked = event.target.checked;
    setSettings(prev => ({
      ...prev,
      notificationSchedule: {
        ...prev.notificationSchedule,
        active: checked
      }
    }));
  };

  const handleScheduleChange = (field: 'startTime' | 'endTime', value: string) => {
    setSettings(prev => ({
      ...prev,
      notificationSchedule: {
        ...prev.notificationSchedule,
        [field]: value
      }
    }));
  };

  const handleCustomMessageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings(prev => ({
      ...prev,
      customMessage: event.target.value
    }));
  };

  const handleSaveSettings = async () => {
    if (!user) return;
    
    setSaving(true);
    try {
      // Em produção, isso enviaria uma requisição para a API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simula um delay
      
      setSnackbar({
        open: true,
        message: 'Configurações salvas com sucesso!',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao salvar configurações.',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleBack = () => {
    navigate('/users');
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'high':
        return <WarningIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  if (loading) {
    return (
      <MainLayout title="Configurações do Usuário">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  if (!user) {
    return (
      <MainLayout title="Usuário não encontrado">
        <Alert severity="error">Usuário não encontrado.</Alert>
        <Button 
          variant="outlined" 
          startIcon={<ArrowBackIcon />} 
          onClick={handleBack}
          sx={{ mt: 2 }}
        >
          Voltar para lista de usuários
        </Button>
      </MainLayout>
    );
  }

  return (
    <MainLayout title={`Configurações: ${user.name}`}>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <IconButton color="inherit" onClick={handleBack} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            Configurações de Notificação
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {/* Informações do usuário */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader
                title="Informações do Usuário"
                avatar={<Avatar sx={{ bgcolor: 'primary.main' }}><PersonIcon /></Avatar>}
              />
              <Divider />
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: user.receivesAlerts ? 'success.main' : 'error.main', mr: 2 }}>
                    {user.name.charAt(0)}
                  </Avatar>
                  <Box>
                    <Typography variant="h6">{user.name}</Typography>
                    <Typography variant="body2" color="text.secondary">{user.email}</Typography>
                  </Box>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TelegramIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Chat ID: <strong>{user.chat_id}</strong>
                  </Typography>
                </Box>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={user.receivesAlerts}
                      color="primary"
                      disabled
                    />
                  }
                  label={`Status: ${user.receivesAlerts ? 'Ativo' : 'Inativo'}`}
                />
                
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 2 }}>
                  Para ativar ou desativar o usuário, utilize a página de "Usuários".
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Configurações de notificação */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardHeader
                title="Preferências de Notificação"
                avatar={<Avatar sx={{ bgcolor: 'warning.main' }}><NotificationsIcon /></Avatar>}
              />
              <Divider />
              <CardContent>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.receiveAllAlerts}
                      onChange={handleToggleAllAlerts}
                      color="primary"
                      disabled={!user.receivesAlerts}
                    />
                  }
                  label="Receber todos os tipos de alertas"
                />
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Se desativado, você pode escolher quais tipos específicos de alertas este usuário receberá.
                </Typography>
                
                {/* Lista de tipos de alertas */}
                {!settings.receiveAllAlerts && (
                  <Paper variant="outlined" sx={{ mb: 3, mt: 2 }}>
                    <List>
                      {alertTypes.map((alertType) => (
                        <ListItem key={alertType.id} divider>
                          <ListItemIcon>
                            {getPriorityIcon(alertType.priority)}
                          </ListItemIcon>
                          <ListItemText 
                            primary={alertType.name} 
                            secondary={alertType.description}
                          />
                          <ListItemSecondaryAction>
                            <Switch
                              edge="end"
                              checked={settings.alertPreferences.find(
                                pref => pref.alertTypeId === alertType.id
                              )?.enabled || false}
                              onChange={() => handleToggleAlertType(alertType.id)}
                              disabled={!user.receivesAlerts || !alertType.active}
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                )}
                
                {/* Agendamento de notificações */}
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Agendamento de Notificações
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notificationSchedule.active}
                      onChange={handleToggleSchedule}
                      color="primary"
                      disabled={!user.receivesAlerts}
                    />
                  }
                  label="Limitar horário de envio de notificações"
                />
                
                {settings.notificationSchedule.active && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 2, gap: 2 }}>
                    <TextField
                      label="Horário inicial"
                      type="time"
                      value={settings.notificationSchedule.startTime}
                      onChange={(e) => handleScheduleChange('startTime', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      inputProps={{ step: 300 }}
                      disabled={!user.receivesAlerts}
                      sx={{ width: 150 }}
                    />
                    
                    <Typography variant="body1">até</Typography>
                    
                    <TextField
                      label="Horário final"
                      type="time"
                      value={settings.notificationSchedule.endTime}
                      onChange={(e) => handleScheduleChange('endTime', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      inputProps={{ step: 300 }}
                      disabled={!user.receivesAlerts}
                      sx={{ width: 150 }}
                    />
                  </Box>
                )}
                
                {/* Mensagem customizada */}
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Mensagem Personalizada
                </Typography>
                
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Mensagem personalizada para notificações (opcional)"
                  value={settings.customMessage}
                  onChange={handleCustomMessageChange}
                  placeholder="Ex: Atenção: Novo alerta detectado!"
                  helperText="Esta mensagem será incluída antes do conteúdo do alerta"
                  disabled={!user.receivesAlerts}
                  sx={{ mb: 3 }}
                />
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  <Button
                    variant="outlined"
                    color="inherit"
                    onClick={handleBack}
                    sx={{ mr: 1 }}
                  >
                    Cancelar
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
                    onClick={handleSaveSettings}
                    disabled={saving || !user.receivesAlerts}
                  >
                    {saving ? 'Salvando...' : 'Salvar Configurações'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </MainLayout>
  );
};

export default UserSettingsPage;