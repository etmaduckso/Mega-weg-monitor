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
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import type { MonitoredEmail } from '../../types/monitoring';
import { useMonitoringData } from '../../hooks/useMonitoringData';
import { useNotification } from '../../context/NotificationContext';
import { emailSchema } from '../../utils/validationSchemas';
import { handleApiError } from '../../utils/errorHandler';
import * as yup from 'yup';

interface EmailFormData {
  email: string;
  description: string;
}

export const MonitoredEmailsManager = () => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<EmailFormData>({ email: '', description: '' });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const { 
    emails: { data: emails = [], isLoading, error },
    createEmail,
    updateEmail,
    deleteEmail 
  } = useMonitoringData();

  const notification = useNotification();

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setFormData({ email: '', description: '' });
    setEditingId(null);
    setFormErrors({});
  };

  const validateForm = async () => {
    try {
      await emailSchema.validate(formData, { abortEarly: false });
      setFormErrors({});
      return true;
    } catch (err) {
      if (err instanceof yup.ValidationError) {
        const errors: Record<string, string> = {};
        err.inner.forEach((error: yup.ValidationError) => {
          if (error.path) {
            errors[error.path] = error.message;
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

    try {
      if (editingId) {
        await updateEmail.mutateAsync({
          id: editingId,
          data: formData
        });
        notification.showSuccess('E-mail atualizado com sucesso!');
      } else {
        await createEmail.mutateAsync({
          ...formData,
          isActive: true
        });
        notification.showSuccess('E-mail adicionado com sucesso!');
      }
      handleClose();
    } catch (error) {
      const message = handleApiError(error, 'Erro ao salvar e-mail');
      notification.showError(message);
    }
  };

  const handleEdit = (email: MonitoredEmail) => {
    setFormData({ email: email.email, description: email.description });
    setEditingId(email.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteEmail.mutateAsync(id);
      notification.showSuccess('E-mail removido com sucesso!');
    } catch (error) {
      console.error('Erro ao excluir e-mail:', error);
      notification.showError('Erro ao excluir e-mail. Por favor, tente novamente.');
    }
  };

  const handleToggleActive = async (email: MonitoredEmail) => {
    try {
      await updateEmail.mutateAsync({
        id: email.id,
        data: { isActive: !email.isActive }
      });
      notification.showSuccess(
        `Monitoramento ${!email.isActive ? 'ativado' : 'desativado'} com sucesso!`
      );
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      notification.showError('Erro ao atualizar status. Por favor, tente novamente.');
    }
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
        Erro ao carregar e-mails monitorados. Por favor, tente novamente.
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">E-mails Monitorados</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          Adicionar E-mail
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>E-mail</TableCell>
              <TableCell>Descrição</TableCell>
              <TableCell align="center">Ativo</TableCell>
              <TableCell>Última Atualização</TableCell>
              <TableCell align="center">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {emails.map((email) => (
              <TableRow key={email.id}>
                <TableCell>{email.email}</TableCell>
                <TableCell>{email.description}</TableCell>
                <TableCell align="center">
                  <Switch
                    checked={email.isActive}
                    onChange={() => handleToggleActive(email)}
                  />
                </TableCell>
                <TableCell>
                  {new Date(email.updatedAt).toLocaleDateString()}
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Editar">
                    <IconButton onClick={() => handleEdit(email)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Excluir">
                    <IconButton 
                      onClick={() => handleDelete(email.id)} 
                      color="error"
                      disabled={deleteEmail.isPending}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {emails.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  Nenhum e-mail monitorado cadastrado
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>
          {editingId ? 'Editar E-mail' : 'Adicionar Novo E-mail'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="E-mail"
            type="email"
            fullWidth
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            error={!!formErrors.email}
            helperText={formErrors.email}
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
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancelar</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={createEmail.isPending || updateEmail.isPending}
          >
            {editingId ? 'Salvar' : 'Adicionar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};