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
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Chip,
  CircularProgress,
  Alert,
  FormHelperText
} from '@mui/material';
import { LoadingButton } from '@mui/lab';
import type { LoadingButtonProps } from '@mui/lab/LoadingButton';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import type { NotificationRouting } from '../../types/monitoring';
import { useMonitoringData } from '../../hooks/useMonitoringData';
import { useNotification } from '../../context/NotificationContext';
import * as yup from 'yup';
import { routingSchema } from '../../utils/validationSchemas';
import { handleApiError } from '../../utils/errorHandler';

interface RoutingFormData {
  emailId: string;
  telegramChatIds: string[];
  useRocketChat: boolean;
  rocketChatChannel: string;
}

export const NotificationRoutingManager: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<RoutingFormData>({
    emailId: '',
    telegramChatIds: [],
    useRocketChat: false,
    rocketChatChannel: '',
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const {
    emails: { data: emails = [], isLoading: emailsLoading },
    telegramConfigs: { data: telegramConfigs = [], isLoading: telegramLoading },
    routings: { data: routings = [], isLoading: routingsLoading, error: routingsError },
    createRouting,
    updateRouting,
    deleteRouting,
  } = useMonitoringData();

  const notification = useNotification();

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setFormData({
      emailId: '',
      telegramChatIds: [],
      useRocketChat: false,
      rocketChatChannel: '',
    });
    setEditingId(null);
    setFormErrors({});
  };

  const validateForm = async () => {
    try {
      await routingSchema.validate(formData, { abortEarly: false });
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

  const handleSubmit = async () => {
    const isValid = await validateForm();
    if (!isValid) return;

    setIsLoading(true);
    try {
      if (editingId) {
        await updateRouting.mutateAsync({
          id: editingId,
          data: formData
        });
        notification.showSuccess('Roteamento de notificações atualizado com sucesso!');
      } else {
        await createRouting.mutateAsync(formData);
        notification.showSuccess('Roteamento de notificações criado com sucesso!');
      }
      handleClose();
    } catch (error) {
      const message = handleApiError(error, 'Erro ao salvar roteamento');
      notification.showError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (routing: NotificationRouting) => {
    setFormData({
      emailId: routing.emailId,
      telegramChatIds: routing.telegramChatIds,
      useRocketChat: routing.useRocketChat,
      rocketChatChannel: routing.rocketChatChannel || '',
    });
    setEditingId(routing.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteRouting.mutateAsync(id);
      notification.showSuccess('Roteamento de notificações removido com sucesso!');
    } catch (error) {
      console.error('Erro ao excluir roteamento:', error);
      notification.showError('Erro ao excluir roteamento de notificações. Por favor, tente novamente.');
    }
  };

  const getEmailDescription = (emailId: string) => {
    const email = emails.find(e => e.id === emailId);
    return email ? `${email.email} (${email.description})` : emailId;
  };

  const getTelegramDescriptions = (chatIds: string[]) => {
    return chatIds.map(chatId => {
      const config = telegramConfigs.find(c => c.id === chatId);
      return config ? `${config.description} (${config.chatId})` : chatId;
    });
  };

  if (emailsLoading || telegramLoading || routingsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (routingsError) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Erro ao carregar configurações de roteamento. Por favor, tente novamente.
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Roteamento de Notificações</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpen}
          disabled={emails.length === 0 || telegramConfigs.length === 0}
        >
          Adicionar Roteamento
        </Button>
      </Box>

      {(emails.length === 0 || telegramConfigs.length === 0) && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Para configurar o roteamento, é necessário ter pelo menos um e-mail e um chat ID do Telegram cadastrados.
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>E-mail Monitorado</TableCell>
              <TableCell>Destinatários Telegram</TableCell>
              <TableCell>RocketChat</TableCell>
              <TableCell>Última Atualização</TableCell>
              <TableCell align="center">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {routings.map((routing) => (
              <TableRow key={routing.id}>
                <TableCell>{getEmailDescription(routing.emailId)}</TableCell>
                <TableCell>
                  {getTelegramDescriptions(routing.telegramChatIds).map((desc, index) => (
                    <Chip
                      key={index}
                      label={desc}
                      sx={{ mr: 0.5, mb: 0.5 }}
                      size="small"
                    />
                  ))}
                </TableCell>
                <TableCell>
                  {routing.useRocketChat ? (
                    <Chip
                      label={routing.rocketChatChannel || 'Canal padrão'}
                      color="primary"
                      size="small"
                    />
                  ) : (
                    'Desativado'
                  )}
                </TableCell>
                <TableCell>
                  {new Date(routing.updatedAt).toLocaleDateString()}
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Editar">
                    <IconButton onClick={() => handleEdit(routing)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Excluir">
                    <IconButton
                      onClick={() => handleDelete(routing.id)}
                      color="error"
                      disabled={deleteRouting.isPending}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {routings.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  Nenhum roteamento configurado
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingId ? 'Editar Roteamento' : 'Adicionar Novo Roteamento'}
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 1 }} error={!!formErrors.emailId}>
            <InputLabel>E-mail Monitorado</InputLabel>
            <Select
              value={formData.emailId}
              label="E-mail Monitorado"
              onChange={(e) => setFormData({ ...formData, emailId: e.target.value })}
            >
              {emails.map((email) => (
                <MenuItem key={email.id} value={email.id}>
                  {email.email} ({email.description})
                </MenuItem>
              ))}
            </Select>
            {formErrors.emailId && (
              <FormHelperText>{formErrors.emailId}</FormHelperText>
            )}
          </FormControl>

          <FormControl fullWidth sx={{ mt: 2 }} error={!!formErrors.telegramChatIds}>
            <InputLabel>Destinatários Telegram</InputLabel>
            <Select
              multiple
              value={formData.telegramChatIds}
              label="Destinatários Telegram"
              onChange={(e) => setFormData({
                ...formData,
                telegramChatIds: typeof e.target.value === 'string'
                  ? [e.target.value]
                  : e.target.value
              })}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((chatId) => {
                    const config = telegramConfigs.find(c => c.id === chatId);
                    return (
                      <Chip
                        key={chatId}
                        label={config ? `${config.description} (${config.chatId})` : chatId}
                        size="small"
                      />
                    );
                  })}
                </Box>
              )}
            >
              {telegramConfigs.map((config) => (
                <MenuItem key={config.id} value={config.id}>
                  {config.description} ({config.chatId})
                </MenuItem>
              ))}
            </Select>
            {formErrors.telegramChatIds && (
              <FormHelperText>{formErrors.telegramChatIds}</FormHelperText>
            )}
            {!formErrors.telegramChatIds && (
              <FormHelperText>
                Selecione um ou mais destinatários para receber as notificações
              </FormHelperText>
            )}
          </FormControl>

          <FormControlLabel
            control={
              <Checkbox
                checked={formData.useRocketChat}
                onChange={(e) => setFormData({ ...formData, useRocketChat: e.target.checked })}
              />
            }
            label="Enviar para RocketChat"
            sx={{ mt: 2 }}
          />

          {formData.useRocketChat && (
            <TextField
              margin="dense"
              label="Canal do RocketChat"
              type="text"
              fullWidth
              value={formData.rocketChatChannel}
              onChange={(e) => setFormData({ ...formData, rocketChatChannel: e.target.value })}
              error={!!formErrors.rocketChatChannel}
              helperText={formErrors.rocketChatChannel || 'Deixe em branco para usar o canal padrão'}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancelar</Button>
          <LoadingButton
            onClick={handleSubmit}
            loading={isLoading}
            variant="contained"
            disabled={!formData.emailId || formData.telegramChatIds.length === 0}
          >
            {editingId ? 'Salvar' : 'Adicionar'}
          </LoadingButton>
        </DialogActions>
      </Dialog>
    </Box>
  );
};