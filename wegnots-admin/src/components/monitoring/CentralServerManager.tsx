import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Switch,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import { EditRounded, RefreshRounded } from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { monitoringService } from '../../services/monitoring';
import { useNotification } from '../../hooks/useNotification';

export const CentralServerManager = () => {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [emailConfig, setEmailConfig] = useState('');
  const queryClient = useQueryClient();
  const notification = useNotification();

  // Query para buscar dados do servidor central
  const { data: centralServer, isLoading, error } = useQuery({
    queryKey: ['centralServer'],
    queryFn: monitoringService.getCentralServer
  });

  // Mutation para atualizar status
  const updateStatus = useMutation({
    mutationFn: monitoringService.updateCentralServerStatus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['centralServer'] });
      notification.showSuccess('Status do servidor central atualizado com sucesso!');
    },
    onError: (error) => {
      notification.showError('Erro ao atualizar status do servidor central');
      console.error('Erro:', error);
    }
  });

  // Mutation para atualizar configuração
  const updateConfig = useMutation({
    mutationFn: monitoringService.updateCentralServerConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['centralServer'] });
      notification.showSuccess('Configuração do servidor central atualizada com sucesso!');
      setIsEditDialogOpen(false);
    },
    onError: (error) => {
      notification.showError('Erro ao atualizar configuração do servidor central');
      console.error('Erro:', error);
    }
  });

  // Atualiza estado do formulário quando dados são carregados
  useEffect(() => {
    if (centralServer) {
      setEmailConfig(centralServer.email);
    }
  }, [centralServer]);

  const handleStatusToggle = async () => {
    if (!centralServer) return;
    try {
      await updateStatus.mutateAsync(!centralServer.isActive);
    } catch (error) {
      console.error('Erro ao alterar status:', error);
    }
  };

  const handleConfigUpdate = async () => {
    try {
      await updateConfig.mutateAsync(emailConfig);
    } catch (error) {
      console.error('Erro ao atualizar configuração:', error);
    }
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['centralServer'] });
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
        Erro ao carregar informações do servidor central. Por favor, tente novamente.
      </Alert>
    );
  }

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="h2">
          Servidor Central
        </Typography>
        <Box>
          <Tooltip title="Atualizar">
            <IconButton onClick={handleRefresh} size="small">
              <RefreshRounded />
            </IconButton>
          </Tooltip>
          <Tooltip title="Editar Configuração">
            <IconButton onClick={() => setIsEditDialogOpen(true)} size="small">
              <EditRounded />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography>Status:</Typography>
          <Switch
            checked={centralServer?.isActive ?? false}
            onChange={handleStatusToggle}
            disabled={updateStatus.isPending}
          />
          <Chip
            label={centralServer?.isActive ? 'Ativo' : 'Inativo'}
            color={centralServer?.isActive ? 'success' : 'default'}
            size="small"
          />
        </Box>

        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Email:
          </Typography>
          <Typography>{centralServer?.email}</Typography>
        </Box>

        <Box>
          <Typography variant="subtitle2" color="text.secondary">
            Chat ID:
          </Typography>
          <Typography>{centralServer?.chatId}</Typography>
        </Box>
      </Box>

      <Dialog open={isEditDialogOpen} onClose={() => setIsEditDialogOpen(false)}>
        <DialogTitle>Editar Configuração do Servidor Central</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email"
            value={emailConfig}
            onChange={(e) => setEmailConfig(e.target.value)}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditDialogOpen(false)}>Cancelar</Button>
          <Button
            onClick={handleConfigUpdate}
            variant="contained"
            disabled={updateConfig.isPending}
          >
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};