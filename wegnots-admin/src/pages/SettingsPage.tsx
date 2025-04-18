import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface Settings {
  emailSettings: {
    smtpServer: string;
    smtpPort: number;
    username: string;
    password: string;
    enabled: boolean;
  };
  telegramSettings: {
    botToken: string;
    enabled: boolean;
  };
  rocketChatSettings: {
    serverUrl: string;
    username: string;
    password: string;
    enabled: boolean;
  };
}

export const SettingsPage: React.FC = () => {
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  const queryClient = useQueryClient();

  const { data: settings, isLoading } = useQuery<Settings>({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch settings');
      return response.json();
    },
  });

  const updateSettings = useMutation({
    mutationFn: async (newSettings: Partial<Settings>) => {
      const response = await fetch('http://localhost:8000/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(newSettings),
      });
      if (!response.ok) throw new Error('Failed to update settings');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      setSnackbar({
        open: true,
        message: 'Configurações atualizadas com sucesso',
        severity: 'success',
      });
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Erro ao atualizar configurações',
        severity: 'error',
      });
    },
  });

  const handleSubmit = (section: keyof Settings) => (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const sectionData = Object.fromEntries(formData.entries());
    
    // Convert enabled to boolean and port to number
    if ('enabled' in sectionData) {
      sectionData.enabled = sectionData.enabled === 'true';
    }
    if ('smtpPort' in sectionData) {
      sectionData.smtpPort = Number(sectionData.smtpPort);
    }

    updateSettings.mutate({ [section]: sectionData });
  };

  if (isLoading) {
    return <Typography>Carregando configurações...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 4 }}>
        Configurações do Sistema
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Email Settings */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Configurações de Email
            </Typography>
            <form onSubmit={handleSubmit('emailSettings')}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      name="enabled"
                      defaultChecked={settings?.emailSettings.enabled}
                    />
                  }
                  label="Ativar notificações por email"
                />
                <TextField
                  label="Servidor SMTP"
                  name="smtpServer"
                  defaultValue={settings?.emailSettings.smtpServer}
                  required
                />
                <TextField
                  label="Porta SMTP"
                  name="smtpPort"
                  type="number"
                  defaultValue={settings?.emailSettings.smtpPort}
                  required
                />
                <TextField
                  label="Usuário"
                  name="username"
                  defaultValue={settings?.emailSettings.username}
                  required
                />
                <TextField
                  label="Senha"
                  name="password"
                  type="password"
                  defaultValue={settings?.emailSettings.password}
                  required
                />
                <Button type="submit" variant="contained">
                  Salvar Configurações de Email
                </Button>
              </Box>
            </form>
          </CardContent>
        </Card>

        {/* Telegram Settings */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Configurações do Telegram
            </Typography>
            <form onSubmit={handleSubmit('telegramSettings')}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      name="enabled"
                      defaultChecked={settings?.telegramSettings.enabled}
                    />
                  }
                  label="Ativar notificações do Telegram"
                />
                <TextField
                  label="Token do Bot"
                  name="botToken"
                  defaultValue={settings?.telegramSettings.botToken}
                  required
                />
                <Button type="submit" variant="contained">
                  Salvar Configurações do Telegram
                </Button>
              </Box>
            </form>
          </CardContent>
        </Card>

        {/* RocketChat Settings */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Configurações do Rocket.Chat
            </Typography>
            <form onSubmit={handleSubmit('rocketChatSettings')}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      name="enabled"
                      defaultChecked={settings?.rocketChatSettings.enabled}
                    />
                  }
                  label="Ativar notificações do Rocket.Chat"
                />
                <TextField
                  label="URL do Servidor"
                  name="serverUrl"
                  defaultValue={settings?.rocketChatSettings.serverUrl}
                  required
                />
                <TextField
                  label="Usuário"
                  name="username"
                  defaultValue={settings?.rocketChatSettings.username}
                  required
                />
                <TextField
                  label="Senha"
                  name="password"
                  type="password"
                  defaultValue={settings?.rocketChatSettings.password}
                  required
                />
                <Button type="submit" variant="contained">
                  Salvar Configurações do Rocket.Chat
                </Button>
              </Box>
            </form>
          </CardContent>
        </Card>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};