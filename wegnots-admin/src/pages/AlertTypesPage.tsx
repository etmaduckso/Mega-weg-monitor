import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip,
  FormHelperText,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  PriorityHigh as PriorityHighIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import { api } from '../services/api';

// Tipo de prioridade do alerta
type AlertPriority = 'critical' | 'high' | 'medium' | 'low' | 'info';

// Interface para o tipo de alerta
interface AlertType {
  id: string;
  name: string;
  description: string;
  priority: AlertPriority;
  patterns: {
    senderPatterns: string[];
    subjectPatterns: string[];
    contentPatterns: string[];
  };
  color: string;
  icon: string;
  active: boolean;
}

// Interface para o formulário de alerta
interface AlertTypeForm extends Omit<AlertType, 'id'> {}

const AlertTypesPage: React.FC = () => {
  const [alertTypes, setAlertTypes] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<{[key: string]: string}>({});
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info' | 'warning'
  });

  // Estado para o formulário
  const [form, setForm] = useState<AlertTypeForm>({
    name: '',
    description: '',
    priority: 'medium',
    patterns: {
      senderPatterns: [],
      subjectPatterns: [],
      contentPatterns: []
    },
    color: '#1976d2',
    icon: 'warning',
    active: true
  });

  // Estados para os campos de padrões
  const [newSenderPattern, setNewSenderPattern] = useState('');
  const [newSubjectPattern, setNewSubjectPattern] = useState('');
  const [newContentPattern, setNewContentPattern] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    fetchAlertTypes();
  }, []);

  const fetchAlertTypes = async () => {
    setLoading(true);
    try {
      // Tentativa de buscar tipos de alertas da API
      try {
        const token = localStorage.getItem('token');
        const res = await api.get('/alert-types', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAlertTypes(res.data);
      } catch (err) {
        // Caso a API falhe, carregamos dados de exemplo para o usuário admin
        if (localStorage.getItem('token') === 'admin-default-token') {
          setAlertTypes([
            {
              id: '1',
              name: 'Intrusão',
              description: 'Alertas de intrusão detectados',
              priority: 'critical',
              patterns: {
                senderPatterns: ['sistema@alarmes.com', 'alarme@empresa.com'],
                subjectPatterns: ['INTRUSAO', 'INVASÃO', 'ALARME'],
                contentPatterns: ['movimento detectado', 'sensor acionado', 'DEVICE NAME:']
              },
              color: '#d32f2f',
              icon: 'warning',
              active: true
            },
            {
              id: '2',
              name: 'Procurado ou Foragido',
              description: 'Detecção de pessoas procuradas',
              priority: 'high',
              patterns: {
                senderPatterns: ['camera@security.com'],
                subjectPatterns: ['PROCURADO', 'FORAGIDO', 'URGENTE'],
                contentPatterns: ['pessoa identificada', 'reconhecimento facial']
              },
              color: '#f44336',
              icon: 'error',
              active: true
            },
            {
              id: '3',
              name: 'Suspeito',
              description: 'Detecção de pessoas suspeitas',
              priority: 'medium',
              patterns: {
                senderPatterns: ['camera@security.com'],
                subjectPatterns: ['SUSPEITO', 'ATENÇÃO', 'ALERTA'],
                contentPatterns: ['comportamento suspeito', 'pessoa não identificada']
              },
              color: '#ff9800',
              icon: 'info',
              active: true
            },
            {
              id: '4',
              name: 'Teste Facial',
              description: 'Testes de reconhecimento facial',
              priority: 'low',
              patterns: {
                senderPatterns: ['test@sistema.com'],
                subjectPatterns: ['FACIAL TESTE', 'TESTE'],
                contentPatterns: ['reconhecimento', 'identificação', 'Default library']
              },
              color: '#2196f3',
              icon: 'info',
              active: true
            }
          ]);
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Erro ao carregar tipos de alertas.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenForm = (alertType?: AlertType) => {
    if (alertType) {
      // Modo edição
      setForm({
        name: alertType.name,
        description: alertType.description,
        priority: alertType.priority,
        patterns: { ...alertType.patterns },
        color: alertType.color,
        icon: alertType.icon,
        active: alertType.active
      });
      setCurrentId(alertType.id);
      setEditMode(true);
    } else {
      // Modo criação
      setForm({
        name: '',
        description: '',
        priority: 'medium',
        patterns: {
          senderPatterns: [],
          subjectPatterns: [],
          contentPatterns: []
        },
        color: '#1976d2',
        icon: 'warning',
        active: true
      });
      setCurrentId(null);
      setEditMode(false);
    }
    setFormOpen(true);
  };

  const handleCloseForm = () => {
    setFormOpen(false);
    setFormErrors({});
  };

  const validateForm = (): boolean => {
    const errors: {[key: string]: string} = {};
    
    if (!form.name.trim()) {
      errors.name = 'O nome é obrigatório';
    }
    
    if (!form.description.trim()) {
      errors.description = 'A descrição é obrigatória';
    }
    
    if (form.patterns.subjectPatterns.length === 0 && 
        form.patterns.senderPatterns.length === 0 && 
        form.patterns.contentPatterns.length === 0) {
      errors.patterns = 'Pelo menos um padrão de identificação deve ser informado';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSaveAlertType = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      if (editMode && currentId) {
        // Atualizar tipo de alerta existente
        const updatedAlertTypes = alertTypes.map(item => 
          item.id === currentId ? { ...form, id: currentId } : item
        );
        setAlertTypes(updatedAlertTypes);
        
        setSnackbar({
          open: true,
          message: 'Tipo de alerta atualizado com sucesso.',
          severity: 'success'
        });
      } else {
        // Criar novo tipo de alerta
        const newId = (Math.max(...alertTypes.map(item => parseInt(item.id))) + 1).toString();
        const newAlertType: AlertType = {
          ...form,
          id: newId
        };
        
        setAlertTypes([...alertTypes, newAlertType]);
        
        setSnackbar({
          open: true,
          message: 'Tipo de alerta criado com sucesso.',
          severity: 'success'
        });
      }
      
      handleCloseForm();
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao salvar tipo de alerta.',
        severity: 'error'
      });
    }
  };

  const handleDeleteAlertType = (id: string) => {
    try {
      const updatedAlertTypes = alertTypes.filter(item => item.id !== id);
      setAlertTypes(updatedAlertTypes);
      
      setSnackbar({
        open: true,
        message: 'Tipo de alerta excluído com sucesso.',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao excluir tipo de alerta.',
        severity: 'error'
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    if (name) {
      setForm(prev => ({
        ...prev,
        [name]: value
      }));
      
      // Limpar erro
      if (formErrors[name]) {
        setFormErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    }
  };

  const addPattern = (type: 'sender' | 'subject' | 'content') => {
    let pattern = '';
    let currentPatterns: string[] = [];
    
    switch (type) {
      case 'sender':
        pattern = newSenderPattern.trim();
        currentPatterns = [...form.patterns.senderPatterns];
        if (pattern && !currentPatterns.includes(pattern)) {
          currentPatterns.push(pattern);
          setForm(prev => ({
            ...prev,
            patterns: {
              ...prev.patterns,
              senderPatterns: currentPatterns
            }
          }));
          setNewSenderPattern('');
        }
        break;
      case 'subject':
        pattern = newSubjectPattern.trim();
        currentPatterns = [...form.patterns.subjectPatterns];
        if (pattern && !currentPatterns.includes(pattern)) {
          currentPatterns.push(pattern);
          setForm(prev => ({
            ...prev,
            patterns: {
              ...prev.patterns,
              subjectPatterns: currentPatterns
            }
          }));
          setNewSubjectPattern('');
        }
        break;
      case 'content':
        pattern = newContentPattern.trim();
        currentPatterns = [...form.patterns.contentPatterns];
        if (pattern && !currentPatterns.includes(pattern)) {
          currentPatterns.push(pattern);
          setForm(prev => ({
            ...prev,
            patterns: {
              ...prev.patterns,
              contentPatterns: currentPatterns
            }
          }));
          setNewContentPattern('');
        }
        break;
    }
    
    // Limpar erro de patterns se houver
    if (formErrors.patterns) {
      setFormErrors(prev => ({
        ...prev,
        patterns: ''
      }));
    }
  };

  const removePattern = (type: 'sender' | 'subject' | 'content', pattern: string) => {
    switch (type) {
      case 'sender':
        setForm(prev => ({
          ...prev,
          patterns: {
            ...prev.patterns,
            senderPatterns: prev.patterns.senderPatterns.filter(p => p !== pattern)
          }
        }));
        break;
      case 'subject':
        setForm(prev => ({
          ...prev,
          patterns: {
            ...prev.patterns,
            subjectPatterns: prev.patterns.subjectPatterns.filter(p => p !== pattern)
          }
        }));
        break;
      case 'content':
        setForm(prev => ({
          ...prev,
          patterns: {
            ...prev.patterns,
            contentPatterns: prev.patterns.contentPatterns.filter(p => p !== pattern)
          }
        }));
        break;
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const getPriorityIcon = (priority: AlertPriority) => {
    switch (priority) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'high':
        return <WarningIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
        return <InfoIcon color="info" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getPriorityColor = (priority: AlertPriority) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const getPriorityText = (priority: AlertPriority) => {
    switch (priority) {
      case 'critical':
        return 'Crítico';
      case 'high':
        return 'Alto';
      case 'medium':
        return 'Médio';
      case 'low':
        return 'Baixo';
      case 'info':
        return 'Informativo';
      default:
        return priority;
    }
  };

  return (
    <MainLayout title="Tipos de Alertas">
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Gerenciamento de Tipos de Alertas
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenForm()}
          >
            Novo Tipo de Alerta
          </Button>
        </Box>

        <Paper sx={{ p: 2, mb: 3, bgcolor: 'info.lightest' }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
            <InfoIcon color="info" sx={{ mr: 1, mt: 0.5 }} />
            <Box>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                Configuração de Identificação de Alertas
              </Typography>
              <Typography variant="body2">
                Configure os padrões para identificação automática de alertas nos e-mails recebidos.
                O sistema verificará remetentes, assuntos e conteúdos dos e-mails para classificá-los
                corretamente e enviar notificações aos usuários.
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Explicação de como usar os padrões */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>Como funciona a identificação de alertas</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardHeader 
                  title="Padrões de Remetente" 
                  avatar={<PriorityHighIcon color="primary" />}
                />
                <Divider />
                <CardContent>
                  <Typography variant="body2">
                    Configure e-mails ou domínios específicos para identificação. 
                    Por exemplo: "alarme@empresa.com" ou "@security.com"
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardHeader 
                  title="Padrões de Assunto" 
                  avatar={<PriorityHighIcon color="primary" />}
                />
                <Divider />
                <CardContent>
                  <Typography variant="body2">
                    Palavras-chave que aparecem no assunto do e-mail.
                    Por exemplo: "URGENTE", "INTRUSÃO", "ALERTA"
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardHeader 
                  title="Padrões de Conteúdo" 
                  avatar={<PriorityHighIcon color="primary" />}
                />
                <Divider />
                <CardContent>
                  <Typography variant="body2">
                    Texto que pode aparecer no corpo do e-mail.
                    Por exemplo: "movimento detectado", "DEVICE NAME:"
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>

        {/* Tabela de tipos de alertas */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'primary.main' }}>
                  <TableCell sx={{ color: 'white' }}>Nome</TableCell>
                  <TableCell sx={{ color: 'white' }}>Prioridade</TableCell>
                  <TableCell sx={{ color: 'white' }}>Padrões de Identificação</TableCell>
                  <TableCell sx={{ color: 'white' }}>Status</TableCell>
                  <TableCell sx={{ color: 'white' }}>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alertTypes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      Nenhum tipo de alerta cadastrado.
                    </TableCell>
                  </TableRow>
                ) : (
                  alertTypes.map((alertType) => (
                    <TableRow key={alertType.id} sx={{ '&:nth-of-type(odd)': { backgroundColor: 'action.hover' } }}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getPriorityIcon(alertType.priority)}
                          <Typography sx={{ ml: 1, fontWeight: 'bold' }}>
                            {alertType.name}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {alertType.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={getPriorityText(alertType.priority)} 
                          color={getPriorityColor(alertType.priority) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          {alertType.patterns.subjectPatterns.length > 0 && (
                            <Box sx={{ mb: 1 }}>
                              <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                                Assunto:
                              </Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {alertType.patterns.subjectPatterns.slice(0, 3).map((pattern, idx) => (
                                  <Chip key={idx} label={pattern} size="small" variant="outlined" />
                                ))}
                                {alertType.patterns.subjectPatterns.length > 3 && (
                                  <Chip 
                                    label={`+${alertType.patterns.subjectPatterns.length - 3}`} 
                                    size="small"
                                    variant="outlined" 
                                  />
                                )}
                              </Box>
                            </Box>
                          )}
                          {alertType.patterns.senderPatterns.length > 0 && (
                            <Box>
                              <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                                Remetente:
                              </Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {alertType.patterns.senderPatterns.slice(0, 2).map((pattern, idx) => (
                                  <Chip key={idx} label={pattern} size="small" variant="outlined" />
                                ))}
                                {alertType.patterns.senderPatterns.length > 2 && (
                                  <Chip 
                                    label={`+${alertType.patterns.senderPatterns.length - 2}`} 
                                    size="small"
                                    variant="outlined" 
                                  />
                                )}
                              </Box>
                            </Box>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={alertType.active ? "Ativo" : "Inativo"} 
                          color={alertType.active ? "success" : "default"}
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Editar">
                          <IconButton color="primary" onClick={() => handleOpenForm(alertType)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Excluir">
                          <IconButton color="error" onClick={() => handleDeleteAlertType(alertType.id)}>
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>

      {/* Dialog de formulário */}
      <Dialog open={formOpen} onClose={handleCloseForm} maxWidth="md" fullWidth>
        <DialogTitle>
          {editMode ? "Editar Tipo de Alerta" : "Novo Tipo de Alerta"}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Nome do Alerta"
                name="name"
                value={form.name}
                onChange={handleInputChange}
                error={!!formErrors.name}
                helperText={formErrors.name || ''}
                margin="dense"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="dense">
                <InputLabel>Prioridade</InputLabel>
                <Select
                  name="priority"
                  value={form.priority}
                  onChange={handleInputChange}
                  label="Prioridade"
                >
                  <MenuItem value="critical">Crítico</MenuItem>
                  <MenuItem value="high">Alto</MenuItem>
                  <MenuItem value="medium">Médio</MenuItem>
                  <MenuItem value="low">Baixo</MenuItem>
                  <MenuItem value="info">Informativo</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descrição"
                name="description"
                value={form.description}
                onChange={handleInputChange}
                error={!!formErrors.description}
                helperText={formErrors.description || ''}
                margin="dense"
                multiline
                rows={2}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Padrões para identificação automática
              </Typography>
              {!!formErrors.patterns && (
                <Alert severity="error" sx={{ mb: 2 }}>{formErrors.patterns}</Alert>
              )}
            </Grid>

            {/* Padrões de remetente */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Padrões de Remetente
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Digite um padrão de remetente"
                  value={newSenderPattern}
                  onChange={(e) => setNewSenderPattern(e.target.value)}
                  margin="none"
                />
                <Button 
                  variant="contained" 
                  onClick={() => addPattern('sender')}
                  sx={{ ml: 1, whiteSpace: 'nowrap' }}
                  disabled={!newSenderPattern.trim()}
                >
                  Adicionar
                </Button>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
                {form.patterns.senderPatterns.map((pattern, index) => (
                  <Chip
                    key={index}
                    label={pattern}
                    onDelete={() => removePattern('sender', pattern)}
                    color="primary"
                    variant="outlined"
                    size="small"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
              <FormHelperText>
                Use o e-mail completo (ex: sistema@empresa.com) ou domínio parcial (ex: @security.com)
              </FormHelperText>
            </Grid>

            {/* Padrões de assunto */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Padrões de Assunto
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Digite uma palavra-chave para assunto"
                  value={newSubjectPattern}
                  onChange={(e) => setNewSubjectPattern(e.target.value)}
                  margin="none"
                />
                <Button 
                  variant="contained" 
                  onClick={() => addPattern('subject')}
                  sx={{ ml: 1, whiteSpace: 'nowrap' }}
                  disabled={!newSubjectPattern.trim()}
                >
                  Adicionar
                </Button>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
                {form.patterns.subjectPatterns.map((pattern, index) => (
                  <Chip
                    key={index}
                    label={pattern}
                    onDelete={() => removePattern('subject', pattern)}
                    color="primary"
                    variant="outlined"
                    size="small"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
              <FormHelperText>
                Palavras-chave que aparecem no assunto do e-mail (ex: URGENTE, INTRUSÃO)
              </FormHelperText>
            </Grid>

            {/* Padrões de conteúdo */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Padrões de Conteúdo
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Digite um padrão para o conteúdo"
                  value={newContentPattern}
                  onChange={(e) => setNewContentPattern(e.target.value)}
                  margin="none"
                />
                <Button 
                  variant="contained" 
                  onClick={() => addPattern('content')}
                  sx={{ ml: 1, whiteSpace: 'nowrap' }}
                  disabled={!newContentPattern.trim()}
                >
                  Adicionar
                </Button>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {form.patterns.contentPatterns.map((pattern, index) => (
                  <Chip
                    key={index}
                    label={pattern}
                    onDelete={() => removePattern('content', pattern)}
                    color="primary"
                    variant="outlined"
                    size="small"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
              <FormHelperText>
                Palavras ou frases que podem aparecer no corpo do e-mail (ex: "movimento detectado", "DEVICE NAME:")
              </FormHelperText>
            </Grid>

            <Grid item xs={12}>
              <FormControl component="fieldset" sx={{ mt: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={form.active}
                      onChange={(e) => setForm(prev => ({ ...prev, active: e.target.checked }))}
                      name="active"
                      color="primary"
                    />
                  }
                  label="Alerta Ativo"
                />
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseForm} color="inherit">Cancelar</Button>
          <Button 
            onClick={handleSaveAlertType} 
            color="primary" 
            variant="contained"
            startIcon={<SaveIcon />}
          >
            {editMode ? 'Atualizar' : 'Salvar'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </MainLayout>
  );
};

export default AlertTypesPage;