import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { monitoringService } from '../../services/monitoring';
import { useNotification } from '../../hooks/useNotification';

interface AlertRule {
  id: string;
  name: string;
  type: 'keyword' | 'sender' | 'domain';
  value: string;
  alertLevel: 1 | 2 | 3;
  destinations: string[];
}

export const AlertRulesManager: React.FC = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const queryClient = useQueryClient();
  const notification = useNotification();

  const [formData, setFormData] = useState<Omit<AlertRule, 'id'>>({
    name: '',
    type: 'keyword',
    value: '',
    alertLevel: 3,
    destinations: []
  });

  // Busca regras existentes
  const { data: rules, isLoading, error } = useQuery({
    queryKey: ['alertRules'],
    queryFn: monitoringService.getAlertRules
  });

  // Mutation para criar/atualizar regra
  const updateRule = useMutation({
    mutationFn: (rule: AlertRule) => 
      editingRule 
        ? monitoringService.updateAlertRule(editingRule.id, rule)
        : monitoringService.createAlertRule(rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertRules'] });
      notification.showSuccess(
        editingRule ? 'Regra atualizada com sucesso!' : 'Regra criada com sucesso!'
      );
      handleCloseDialog();
    },
    onError: (error) => {
      notification.showError('Erro ao salvar regra');
      console.error('Erro:', error);
    }
  });

  // Mutation para deletar regra
  const deleteRule = useMutation({
    mutationFn: monitoringService.deleteAlertRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertRules'] });
      notification.showSuccess('Regra excluída com sucesso!');
    },
    onError: (error) => {
      notification.showError('Erro ao excluir regra');
      console.error('Erro:', error);
    }
  });

  const handleOpenDialog = (rule?: AlertRule) => {
    if (rule) {
      setEditingRule(rule);
      setFormData({
        name: rule.name,
        type: rule.type,
        value: rule.value,
        alertLevel: rule.alertLevel,
        destinations: rule.destinations
      });
    } else {
      setEditingRule(null);
      setFormData({
        name: '',
        type: 'keyword',
        value: '',
        alertLevel: 3,
        destinations: []
      });
    }
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setEditingRule(null);
  };

  const handleSave = async () => {
    try {
      await updateRule.mutateAsync(formData as AlertRule);
    } catch (error) {
      console.error('Erro ao salvar:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir esta regra?')) {
      try {
        await deleteRule.mutateAsync(id);
      } catch (error) {
        console.error('Erro ao excluir:', error);
      }
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
        Erro ao carregar regras de alerta. Por favor, tente novamente.
      </Alert>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Regras de Alerta</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Nova Regra
        </Button>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Valor</TableCell>
              <TableCell>Nível</TableCell>
              <TableCell>Destinos</TableCell>
              <TableCell align="right">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rules?.map((rule) => (
              <TableRow key={rule.id}>
                <TableCell>{rule.name}</TableCell>
                <TableCell>
                  <Chip 
                    label={rule.type} 
                    color={
                      rule.type === 'keyword' ? 'primary' :
                      rule.type === 'sender' ? 'secondary' : 'default'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>{rule.value}</TableCell>
                <TableCell>
                  <Chip 
                    label={
                      rule.alertLevel === 1 ? 'Crítico' :
                      rule.alertLevel === 2 ? 'Importante' : 'Normal'
                    }
                    color={
                      rule.alertLevel === 1 ? 'error' :
                      rule.alertLevel === 2 ? 'warning' : 'info'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {rule.destinations.map((dest) => (
                    <Chip
                      key={dest}
                      label={dest}
                      size="small"
                      sx={{ mr: 0.5 }}
                    />
                  ))}
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog(rule)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(rule.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={isDialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingRule ? 'Editar Regra' : 'Nova Regra'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Nome"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>Tipo</InputLabel>
              <Select
                value={formData.type}
                label="Tipo"
                onChange={(e) => setFormData({ 
                  ...formData, 
                  type: e.target.value as AlertRule['type']
                })}
              >
                <MenuItem value="keyword">Palavra-chave</MenuItem>
                <MenuItem value="sender">Remetente</MenuItem>
                <MenuItem value="domain">Domínio</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Valor"
              value={formData.value}
              onChange={(e) => setFormData({ ...formData, value: e.target.value })}
              fullWidth
              helperText={
                formData.type === 'keyword' ? 'Ex: urgente, crítico' :
                formData.type === 'sender' ? 'Ex: user@domain.com' :
                'Ex: @domain.com'
              }
            />

            <FormControl fullWidth>
              <InputLabel>Nível do Alerta</InputLabel>
              <Select
                value={formData.alertLevel}
                label="Nível do Alerta"
                onChange={(e) => setFormData({
                  ...formData,
                  alertLevel: e.target.value as AlertRule['alertLevel']
                })}
              >
                <MenuItem value={1}>Crítico</MenuItem>
                <MenuItem value={2}>Importante</MenuItem>
                <MenuItem value={3}>Normal</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Destinos"
              value={formData.destinations.join(', ')}
              onChange={(e) => setFormData({
                ...formData,
                destinations: e.target.value.split(',').map(d => d.trim())
              })}
              fullWidth
              multiline
              rows={2}
              helperText="Digite os chat IDs separados por vírgula"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button 
            onClick={handleSave}
            variant="contained"
            disabled={updateRule.isPending}
          >
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};