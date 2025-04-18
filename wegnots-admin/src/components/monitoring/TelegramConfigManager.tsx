import { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Switch,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, Send as SendIcon, Verified as VerifiedIcon } from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import type { LoadingButtonProps } from '@mui/lab/LoadingButton';
import type { TelegramConfig } from '../../types/monitoring';
import { useMonitoringData } from '../../hooks/useMonitoringData';
import { useNotification } from '../../context/NotificationContext';
import * as yup from 'yup';
import { telegramSchema } from '../../utils/validationSchemas';
import { handleApiError } from '../../utils/errorHandler';

interface TelegramFormData {
  chatId: string;
  description: string;
}

export const TelegramConfigManager: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<TelegramFormData>({ chatId: '', description: '' });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const { 
    telegramConfigs: { data: configs = [], isLoading: isConfigsLoading, error },
    createTelegramConfig,
    updateTelegramConfig,
    deleteTelegramConfig,
    testTelegram
  } = useMonitoringData();

  const notification = useNotification();

  const handleOpen = () => {
    setOpen(true);
    setTestResult(null);
  };

  const handleClose = () => {
    setOpen(false);
    setFormData({ chatId: '', description: '' });
    setEditingId(null);
    setTestResult(null);
    setFormErrors({});
  };

  const validateForm = async () => {
    try {
      await telegramSchema.validate(formData, { abortEarly: false });
      setFormErrors({});
      return true;
    } catch (err) {
      if (err instanceof yup.ValidationError) {
        const errors: Record<string, string> = {};
        err.inner.forEach((e) => {
          if (e.path) {
            errors[e.path] = e.message;
          }
        });
        setFormErrors(errors);
      }
      return false;
    }
  };

  const handleTestConnection = async () => {
    if (!formData.chatId) {
      setFormErrors({ chatId: 'Chat ID é obrigatório para testar a conexão' });
      return;
    }

    try {
      const result = await testTelegram.mutateAsync(formData.chatId);
      setTestResult(result);
      if (result.success) {
        notification.showSuccess('Conexão com Telegram estabelecida com sucesso!');
      } else {
        notification.showError('Falha ao conectar com Telegram: ' + result.message);
      }
    } catch (error) {
      setTestResult({ success: false, message: handleApiError(error, 'Erro ao testar conexão') });
      notification.showError('Erro ao testar conexão com Telegram. Por favor, tente novamente.');
    }
  };

  const handleSubmit = async () => {
    const isValid = await validateForm();
    if (!isValid) return;

    try {
      if (editingId) {
        await updateTelegramConfig.mutateAsync({ 
          id: editingId, 
          data: { 
            chatId: formData.chatId, 
            description: formData.description 
          } 
        });
        notification.showSuccess('Configuração do Telegram atualizada com sucesso!');
      } else {
        await createTelegramConfig.mutateAsync({ 
          chatId: formData.chatId, 
          description: formData.description,
          isActive: true 
        });
        notification.showSuccess('Configuração do Telegram adicionada com sucesso!');
      }
      handleClose();
    } catch (error) {
      const message = handleApiError(error, 'Erro ao salvar configuração do Telegram');
      notification.showError(message);
    }
  };

  const handleEdit = (config: TelegramConfig) => {
    setFormData({ chatId: config.chatId, description: config.description });
    setEditingId(config.id);
    setTestResult(null);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTelegramConfig.mutateAsync(id);
      notification.showSuccess('Configuração do Telegram removida com sucesso!');
    } catch (error) {
      console.error('Erro ao excluir configuração:', error);
      notification.showError('Erro ao excluir configuração do Telegram. Por favor, tente novamente.');
    }
  };

  const handleToggleActive = async (config: TelegramConfig) => {
    try {
      await updateTelegramConfig.mutateAsync({
        id: config.id,
        data: { isActive: !config.isActive }
      });
      notification.showSuccess(
        `Notificações do Telegram ${!config.isActive ? 'ativadas' : 'desativadas'} com sucesso!`
      );
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      notification.showError('Erro ao atualizar status. Por favor, tente novamente.');
    }
  };

  const handleSaveTelegramConfig = async () => {
    setIsLoading(true);
    try {
      // Add your save logic here
      await new Promise(resolve => setTimeout(resolve, 1000)); // Placeholder
    } catch (error) {
      console.error('Error saving telegram config:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isConfigsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Erro ao carregar configurações do Telegram. Por favor, tente novamente.
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Configurações do Telegram</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          Adicionar Chat ID
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Chat ID</TableCell>
              <TableCell>Descrição</TableCell>
              <TableCell align="center">Ativo</TableCell>
              <TableCell align="center">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {configs.map((config) => (
              <TableRow key={config.id}>
                <TableCell>{config.chatId}</TableCell>
                <TableCell>{config.description}</TableCell>
                <TableCell align="center">
                  <Switch
                    checked={config.isActive}
                    onChange={() => handleToggleActive(config)}
                  />
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Editar">
                    <IconButton onClick={() => handleEdit(config)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Excluir">
                    <IconButton 
                      onClick={() => handleDelete(config.id)} 
                      color="error"
                      disabled={deleteTelegramConfig.isPending}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {configs.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  Nenhuma configuração do Telegram cadastrada
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingId ? 'Editar Chat ID' : 'Adicionar Novo Chat ID'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Chat ID"
            type="text"
            fullWidth
            value={formData.chatId}
            onChange={(e) => setFormData({ ...formData, chatId: e.target.value })}
            error={!!formErrors.chatId}
            helperText={formErrors.chatId || "O Chat ID pode ser obtido através do comando /start no bot"}
          />
          <TextField
            margin="dense"
            label="Descrição"
            type="text"
            fullWidth
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            error={!!formErrors.description}
            helperText={formErrors.description}
          />
          
          {testResult && (
            <Alert 
              severity={testResult.success ? "success" : "error"}
              sx={{ mt: 2 }}
            >
              {testResult.message}
            </Alert>
          )}

          <Box sx={{ mt: 2 }}>
            <LoadingButton
              onClick={handleTestConnection}
              loading={testTelegram.isPending}
              disabled={!formData.chatId}
              variant="outlined"
              startIcon={<SendIcon />}
              fullWidth
            >
              Testar Conexão
            </LoadingButton>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancelar</Button>
          <LoadingButton 
            onClick={handleSubmit} 
            loading={createTelegramConfig.isPending || updateTelegramConfig.isPending}
            variant="contained"
          >
            {editingId ? 'Salvar' : 'Adicionar'}
          </LoadingButton>
          <LoadingButton
            onClick={handleSaveTelegramConfig}
            loading={isLoading}
            disabled={isLoading}
            variant="contained"
            fullWidth
          >
            Salvar Configuração
          </LoadingButton>
        </DialogActions>
      </Dialog>
    </Box>
  );
};