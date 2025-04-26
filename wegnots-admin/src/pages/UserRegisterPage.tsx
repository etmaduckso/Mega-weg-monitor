import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  Grid, 
  Alert, 
  Snackbar,
  CircularProgress,
  InputAdornment,
  IconButton
} from '@mui/material';
import { ArrowBack, Telegram as TelegramIcon, Save as SaveIcon } from '@mui/icons-material';
import MainLayout from '../layouts/MainLayout';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

interface UserFormData {
  name: string;
  email: string;
  chat_id: string;
}

const UserRegisterPage: React.FC = () => {
  const [formData, setFormData] = useState<UserFormData>({
    name: '',
    email: '',
    chat_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const newErrors: {[key: string]: string} = {};
    if (!formData.name.trim()) {
      newErrors.name = 'O nome é obrigatório';
    } else if (formData.name.trim().split(' ').length < 2) {
      newErrors.name = 'Informe o nome completo (nome e sobrenome)';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'O e-mail é obrigatório';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'E-mail inválido';
    }

    if (!formData.chat_id.trim()) {
      newErrors.chat_id = 'O Chat ID do Telegram é obrigatório';
    } else if (!/^[0-9]+$/.test(formData.chat_id)) {
      newErrors.chat_id = 'O Chat ID deve conter apenas números';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Limpa o erro do campo que está sendo editado
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      // Simulação de cadastro - em produção, isso seria uma chamada real à API
      if (localStorage.getItem('token') === 'admin-default-token') {
        // Simulamos sucesso após um breve delay para demonstração
        await new Promise(resolve => setTimeout(resolve, 1000));
        setSnackbar({
          open: true,
          message: 'Usuário cadastrado com sucesso!',
          severity: 'success'
        });

        // Após o sucesso, redirecionamos para a lista de usuários
        setTimeout(() => {
          navigate('/users');
        }, 1500);
      } else {
        // Em produção, enviaríamos os dados para a API
        await api.post('/users', formData);
        setSnackbar({
          open: true,
          message: 'Usuário cadastrado com sucesso!',
          severity: 'success'
        });
        navigate('/users');
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao cadastrar usuário. Tente novamente.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/users');
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <MainLayout title="Cadastrar Novo Usuário">
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <IconButton onClick={handleBack} sx={{ mr: 2 }}>
              <ArrowBack />
            </IconButton>
            <Typography variant="h5" component="h1">
              Cadastrar Novo Usuário
            </Typography>
          </Box>

          <Typography variant="body2" color="text.secondary" paragraph>
            Preencha os dados abaixo para cadastrar um novo usuário que receberá alertas do sistema.
          </Typography>

          <Box component="form" onSubmit={handleSubmit} noValidate>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="name"
                  name="name"
                  label="Nome Completo"
                  value={formData.name}
                  onChange={handleChange}
                  error={!!errors.name}
                  helperText={errors.name || 'Digite o nome completo do usuário'}
                  disabled={loading}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="email"
                  name="email"
                  label="E-mail"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  error={!!errors.email}
                  helperText={errors.email || 'Digite o e-mail do usuário'}
                  disabled={loading}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="chat_id"
                  name="chat_id"
                  label="Chat ID do Telegram"
                  value={formData.chat_id}
                  onChange={handleChange}
                  error={!!errors.chat_id}
                  helperText={errors.chat_id || 'Digite o Chat ID do Telegram do usuário'}
                  disabled={loading}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <TelegramIcon color="primary" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
            </Grid>

            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                variant="outlined"
                onClick={handleBack}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
              >
                {loading ? 'Salvando...' : 'Salvar Usuário'}
              </Button>
            </Box>
          </Box>
        </Paper>

        <Box sx={{ mt: 3 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Como obter o Chat ID do Telegram
            </Typography>
            <ol>
              <li>Inicie uma conversa com o bot @WegNotsBot no Telegram</li>
              <li>Envie a mensagem /start para o bot</li>
              <li>O bot responderá com seu Chat ID</li>
              <li>Alternativamente, você pode usar o bot @userinfobot no Telegram para obter seu ID</li>
            </ol>
          </Paper>
        </Box>
      </Box>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </MainLayout>
  );
};

export default UserRegisterPage;