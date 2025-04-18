import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, Grid, Paper, CircularProgress, Alert, FormControlLabel, Switch } from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { sendNotification, getMonitoringConfig } from '../services/api';

interface FormData {
  checkInterval: number;
  reconnectAttempts: number;
  reconnectDelay: number;
  reconnectBackoffFactor: number;
  logLevel: string;
  emailServer: string;
  emailPort: number;
  emailUser: string;
}

export const MonitoringConfig = () => {
  const [loading, setLoading] = useState(true);
  const [configError, setConfigError] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [channel, setChannel] = useState('');
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notificationChannels, setNotificationChannels] = useState({
    telegram: false,
    rocketChat: false,
    email: false
  });

  const { control, handleSubmit, setValue } = useForm<FormData>({
    defaultValues: {
      checkInterval: 60,
      reconnectAttempts: 5,
      reconnectDelay: 30,
      reconnectBackoffFactor: 1.5,
      logLevel: 'INFO',
      emailServer: '',
      emailPort: 993,
      emailUser: ''
    }
  });

  // Carrega as configurações de monitoramento
  useEffect(() => {
    const loadConfig = async () => {
      try {
        setLoading(true);
        const config = await getMonitoringConfig();
        
        // Atualiza o formulário com os valores obtidos
        setValue('checkInterval', config.checkInterval);
        setValue('reconnectAttempts', config.reconnectAttempts);
        setValue('reconnectDelay', config.reconnectDelay);
        setValue('reconnectBackoffFactor', config.reconnectBackoffFactor);
        setValue('logLevel', config.logLevel);
        
        if (config.emailSettings) {
          setValue('emailServer', config.emailSettings.server);
          setValue('emailPort', config.emailSettings.port);
          setValue('emailUser', config.emailSettings.user);
        }
        
        if (config.notificationChannels) {
          setNotificationChannels(config.notificationChannels);
        }
        
        setConfigError(null);
      } catch (err) {
        setConfigError('Erro ao carregar configurações. Verifique se o servidor está em execução.');
        console.error('Erro ao carregar configurações:', err);
      } finally {
        setLoading(false);
      }
    };

    loadConfig();
  }, [setValue]);

  const onSubmit = (data: FormData) => {
    // TODO: Integrar com API backend para salvar dados
    console.log('Dados enviados:', data);
    setSuccess('Configurações salvas com sucesso!');
    setTimeout(() => setSuccess(null), 3000);
  };

  const handleSendNotification = async () => {
    try {
      const result = await sendNotification({ message, channel });
      setSuccess('Notificação enviada com sucesso!');
      setError(null);
      console.log('Resultado:', result);
      setMessage('');
      setChannel('');
    } catch (err) {
      setError('Erro ao enviar notificação.');
      setSuccess(null);
    }
  };

  const handleNotificationChannelChange = (channel: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setNotificationChannels({
      ...notificationChannels,
      [channel]: event.target.checked
    });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Configuração de Monitoramento
      </Typography>
      
      {configError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {configError}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Configurações Gerais
        </Typography>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Controller
                name="checkInterval"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Intervalo de Verificação (segundos)"
                    fullWidth
                    type="number"
                    inputProps={{ step: "1" }}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="reconnectAttempts"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Tentativas de Reconexão"
                    fullWidth
                    type="number"
                    inputProps={{ step: "1" }}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="reconnectDelay"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Delay de Reconexão (segundos)"
                    fullWidth
                    type="number"
                    inputProps={{ step: "1" }}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="reconnectBackoffFactor"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Fator de Backoff"
                    fullWidth
                    type="number"
                    inputProps={{ step: "0.1" }}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="logLevel"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Nível de Log"
                    fullWidth
                    select
                    SelectProps={{
                      native: true,
                    }}
                  >
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </TextField>
                )}
              />
            </Grid>
          </Grid>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Configurações de E-mail
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Controller
                name="emailServer"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Servidor IMAP"
                    fullWidth
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="emailPort"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Porta"
                    fullWidth
                    type="number"
                    inputProps={{ step: "1" }}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="emailUser"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Usuário"
                    fullWidth
                  />
                )}
              />
            </Grid>
          </Grid>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Canais de Notificação
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={notificationChannels.telegram}
                    onChange={handleNotificationChannelChange('telegram')}
                  />
                }
                label="Telegram"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={notificationChannels.rocketChat}
                    onChange={handleNotificationChannelChange('rocketChat')}
                  />
                }
                label="Rocket.Chat"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={notificationChannels.email}
                    onChange={handleNotificationChannelChange('email')}
                  />
                }
                label="E-mail"
              />
            </Grid>
          </Grid>
          
          <Box mt={3}>
            <Button type="submit" variant="contained" color="primary">
              Salvar Configurações
            </Button>
          </Box>
        </form>
      </Paper>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Enviar Notificação de Teste
        </Typography>
        <Box>
          <TextField
            label="Mensagem"
            fullWidth
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            label="Canal"
            fullWidth
            value={channel}
            onChange={(e) => setChannel(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button 
            variant="contained" 
            color="secondary" 
            onClick={handleSendNotification}
            disabled={!message || !channel}
          >
            Enviar Notificação
          </Button>
          {error && <Typography color="error" mt={2}>{error}</Typography>}
        </Box>
      </Paper>
    </Box>
  );
};
