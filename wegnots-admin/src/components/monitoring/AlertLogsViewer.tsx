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
  Chip,
  IconButton,
  TablePagination,
  TextField,
  InputAdornment,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardContent,
  Collapse,
  Grid,
  Divider,
  Tab,
  Tabs,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  MailOutline as MailIcon,
  Telegram as TelegramIcon,
  CheckCircleOutline as CheckIcon,
  ErrorOutline as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  FileDownload as FileDownloadIcon,
  PhotoCamera as PhotoCameraIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Interface para um alerta processado
interface AlertLog {
  id: string;
  timestamp: string;
  emailSubject: string;
  emailSender: string;
  emailContent: string;
  detectedAlertType: {
    id: string;
    name: string;
    priority: 'critical' | 'high' | 'medium' | 'low' | 'info';
  } | null;
  notificationSent: boolean;
  recipientUsers: {
    id: string;
    name: string;
    chat_id: string;
    notificationSuccess: boolean;
  }[];
  hasAttachment: boolean;
  attachmentType: 'image' | 'pdf' | 'video' | 'other' | null;
  processingStatus: 'success' | 'partial_success' | 'error';
  errorMessage?: string;
}

interface AlertLogsViewerProps {
  limit?: number;
  showFilters?: boolean;
  height?: string | number;
  onLogSelected?: (log: AlertLog) => void;
}

const AlertLogsViewer: React.FC<AlertLogsViewerProps> = ({ 
  limit = 10,
  showFilters = true,
  height = 600,
  onLogSelected
}) => {
  const [logs, setLogs] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(limit);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [tabValue, setTabValue] = useState<number>(0);
  const [detailOpen, setDetailOpen] = useState<string | null>(null);
  const [selectedLog, setSelectedLog] = useState<AlertLog | null>(null);
  const [detailsDialog, setDetailsDialog] = useState<boolean>(false);

  useEffect(() => {
    fetchLogs();
  }, [tabValue]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      // Em um ambiente real, aqui seria uma chamada para a API
      // que retornaria os logs do sistema
      try {
        const token = localStorage.getItem('token');
        const res = await api.get('/alert-logs', {
          headers: { Authorization: `Bearer ${token}` },
          params: { status: getStatusFilter() }
        });
        setLogs(res.data);
      } catch (err) {
        // Se a API falhar, usamos dados mockados para demonstração
        const mockLogs = generateMockLogs(30);
        setLogs(mockLogs);
      }
    } catch (error) {
      console.error('Erro ao carregar logs de alertas:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusFilter = (): string => {
    switch (tabValue) {
      case 0:
        return 'all';
      case 1:
        return 'success';
      case 2:
        return 'partial_success';
      case 3:
        return 'error';
      default:
        return 'all';
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = () => {
    fetchLogs();
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDetails = (log: AlertLog) => {
    setSelectedLog(log);
    setDetailsDialog(true);
    if (onLogSelected) {
      onLogSelected(log);
    }
  };

  const handleCloseDetails = () => {
    setDetailsDialog(false);
  };

  const toggleDetail = (id: string) => {
    setDetailOpen(detailOpen === id ? null : id);
  };

  const getPriorityIcon = (priority?: string) => {
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

  // Função para filtrar logs com base na busca
  const filteredLogs = logs.filter(log => {
    const searchLower = searchTerm.toLowerCase();
    return (
      log.emailSubject.toLowerCase().includes(searchLower) ||
      log.emailSender.toLowerCase().includes(searchLower) ||
      (log.detectedAlertType?.name.toLowerCase() || '').includes(searchLower)
    );
  });

  // Paginação
  const paginatedLogs = filteredLogs.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckIcon color="success" />;
      case 'partial_success':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return null;
    }
  };

  const formatDateTime = (dateStr: string) => {
    try {
      return format(new Date(dateStr), "dd/MM/yyyy HH:mm", { locale: ptBR });
    } catch {
      return dateStr;
    }
  };

  // Gera dados de exemplo para demonstração
  const generateMockLogs = (count: number): AlertLog[] => {
    const alertTypes = [
      { id: '1', name: 'Intrusão', priority: 'critical' as const },
      { id: '2', name: 'Procurado ou Foragido', priority: 'high' as const },
      { id: '3', name: 'Suspeito', priority: 'medium' as const },
      { id: '4', name: 'Teste Facial', priority: 'low' as const }
    ];

    const senders = ['camera@security.com', 'alerta@empresa.com', 'sistema@alarmes.com'];
    const subjects = [
      'INTRUSAO 2025-04-17 09:50:58',
      'URGENTE - Alerta de Procurado ou Foragido',
      'URGENTE - Alerta de Intrusão',
      'ATENÇÃO - Alerta de Suspeito',
      'FACIAL TESTE | 2025-04-17 09:28:32'
    ];

    const contents = [
      'DIVICEGRUPO:Default group DEVICE NAME: NVR LOJA CHANNEL name:Bullet Varifo',
      'Acabamos de detectar pelo sistema de câmeras do comércio que um Alerta de Procurado ou Foragido foi registrado',
      'Sua loja acabou de receber um alerta de Intrusão, acesse a sua câmera e confirma o que está acontecendo',
      'Sua loja acabou de receber um alerta de Suspeito, acesse a sua câmera e confirme o que está acontecendo',
      'time:2025-04-17 09:28:32 DIVICEGRUPO:Default group DEVICE NAME: NVR LOJA CHANNEL name:Bullet 5 MP 1'
    ];

    const statusOptions = ['success', 'partial_success', 'error'];
    
    const users = [
      { id: '1', name: 'João da Silva', chat_id: '123456789' },
      { id: '2', name: 'Maria Oliveira', chat_id: '987654321' },
      { id: '3', name: 'Pedro Santos', chat_id: '456789123' }
    ];

    return Array(count).fill(0).map((_, index) => {
      const alertType = Math.random() > 0.2 ? 
        alertTypes[Math.floor(Math.random() * alertTypes.length)] :
        null;

      const statusIndex = Math.floor(Math.random() * statusOptions.length);
      const status = statusOptions[statusIndex] as 'success' | 'partial_success' | 'error';

      const hasAttachment = Math.random() > 0.3;
      const attachmentType = hasAttachment ? 
        ['image', 'pdf', 'video', 'other'][Math.floor(Math.random() * 4)] as 'image' | 'pdf' | 'video' | 'other' :
        null;

      // Gerando data aleatória recente
      const date = new Date();
      date.setDate(date.getDate() - Math.floor(Math.random() * 7));
      date.setHours(date.getHours() - Math.floor(Math.random() * 24));
      date.setMinutes(date.getMinutes() - Math.floor(Math.random() * 60));

      // Selecionando o assunto e conteúdo correspondente ao tipo de alerta
      let subjectIndex = 0;
      if (alertType) {
        if (alertType.name.includes('Intrusão')) subjectIndex = 0;
        else if (alertType.name.includes('Procurado')) subjectIndex = 1;
        else if (alertType.name.includes('Suspeito')) subjectIndex = 3;
        else if (alertType.name.includes('Facial')) subjectIndex = 4;
      }

      // Gerando destinatários com status de sucesso ou erro
      const recipientUsers = [];
      const userCount = Math.floor(Math.random() * 3) + 1; // 1 a 3 usuários
      
      for (let i = 0; i < userCount; i++) {
        const randomUser = users[Math.floor(Math.random() * users.length)];
        const success = status === 'success' ? true : 
                        status === 'error' ? false :
                        Math.random() > 0.5;
        
        recipientUsers.push({
          ...randomUser,
          notificationSuccess: success
        });
      }

      return {
        id: (index + 1).toString(),
        timestamp: date.toISOString(),
        emailSubject: subjects[subjectIndex],
        emailSender: senders[Math.floor(Math.random() * senders.length)],
        emailContent: contents[subjectIndex],
        detectedAlertType: alertType,
        notificationSent: status !== 'error',
        recipientUsers,
        hasAttachment,
        attachmentType,
        processingStatus: status,
        errorMessage: status === 'error' ? 'Erro ao processar alerta ou enviar notificação' : undefined
      };
    });
  };

  return (
    <Box sx={{ width: '100%', height }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Todos" />
          <Tab label="Processados com Sucesso" />
          <Tab label="Parcialmente Processados" />
          <Tab label="Erros" />
        </Tabs>
      </Box>

      {showFilters && (
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <TextField
            placeholder="Buscar alertas..."
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ width: 300 }}
          />
          <Button
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            color="primary"
            variant="outlined"
          >
            Atualizar
          </Button>
        </Box>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : filteredLogs.length === 0 ? (
        <Alert severity="info" sx={{ mt: 2 }}>
          Nenhum registro de alerta encontrado.
        </Alert>
      ) : (
        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: height ? height - 200 : 400 }}>
            <Table stickyHeader aria-label="sticky table" size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Data/Hora</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Tipo de Alerta</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Assunto</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Remetente</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Notificações</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 'bold' }}>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedLogs.map((log) => (
                  <React.Fragment key={log.id}>
                    <TableRow 
                      hover 
                      onClick={() => toggleDetail(log.id)}
                      sx={{ 
                        cursor: 'pointer',
                        '&:nth-of-type(odd)': { backgroundColor: 'action.hover' },
                        ...(log.processingStatus === 'error' ? { bgcolor: 'error.lightest' } : {})
                      }}
                    >
                      <TableCell>{formatDateTime(log.timestamp)}</TableCell>
                      <TableCell>
                        {log.detectedAlertType ? (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {getPriorityIcon(log.detectedAlertType.priority)}
                            <Typography sx={{ ml: 1 }}>
                              {log.detectedAlertType.name}
                            </Typography>
                          </Box>
                        ) : (
                          <Chip label="Não identificado" size="small" color="default" />
                        )}
                      </TableCell>
                      <TableCell>{log.emailSubject}</TableCell>
                      <TableCell>{log.emailSender}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getStatusIcon(log.processingStatus)}
                          <Typography sx={{ ml: 1 }}>
                            {log.processingStatus === 'success' && 'Sucesso'}
                            {log.processingStatus === 'partial_success' && 'Parcial'}
                            {log.processingStatus === 'error' && 'Erro'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <TelegramIcon fontSize="small" color="primary" sx={{ mr: 0.5 }} />
                          <Typography>
                            {log.recipientUsers.length}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <IconButton size="small" onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDetails(log);
                        }}>
                          {detailOpen === log.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell 
                        style={{ paddingBottom: 0, paddingTop: 0 }} 
                        colSpan={7}
                      >
                        <Collapse in={detailOpen === log.id} timeout="auto" unmountOnExit>
                          <Box sx={{ m: 2 }}>
                            <Grid container spacing={2}>
                              <Grid item xs={12}>
                                <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                                  Detalhes do alerta
                                </Typography>
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <Card variant="outlined">
                                  <CardContent>
                                    <Typography variant="subtitle2">
                                      Conteúdo do e-mail:
                                    </Typography>
                                    <Paper 
                                      variant="outlined" 
                                      sx={{ p: 2, mt: 1, maxHeight: 150, overflow: 'auto', bgcolor: 'grey.50' }}
                                    >
                                      <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                        {log.emailContent}
                                      </Typography>
                                    </Paper>
                                    
                                    {log.hasAttachment && (
                                      <Box sx={{ mt: 2 }}>
                                        <Typography variant="subtitle2">
                                          Anexo:
                                        </Typography>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                          {log.attachmentType === 'image' && <PhotoCameraIcon color="primary" sx={{ mr: 1 }} />}
                                          {log.attachmentType === 'pdf' && <FileDownloadIcon color="primary" sx={{ mr: 1 }} />}
                                          <Typography variant="body2">
                                            {log.attachmentType === 'image' ? 'Imagem' : 
                                             log.attachmentType === 'pdf' ? 'Documento PDF' :
                                             log.attachmentType === 'video' ? 'Vídeo' : 'Arquivo anexado'}
                                          </Typography>
                                        </Box>
                                      </Box>
                                    )}
                                  </CardContent>
                                </Card>
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <Card variant="outlined">
                                  <CardContent>
                                    <Typography variant="subtitle2">
                                      Notificações enviadas:
                                    </Typography>
                                    <Box sx={{ mt: 1 }}>
                                      {log.recipientUsers.length === 0 ? (
                                        <Typography variant="body2">
                                          Nenhum destinatário configurado para este tipo de alerta.
                                        </Typography>
                                      ) : (
                                        <Table size="small">
                                          <TableHead>
                                            <TableRow>
                                              <TableCell>Usuário</TableCell>
                                              <TableCell>Chat ID</TableCell>
                                              <TableCell>Status</TableCell>
                                            </TableRow>
                                          </TableHead>
                                          <TableBody>
                                            {log.recipientUsers.map((user) => (
                                              <TableRow key={user.id}>
                                                <TableCell>{user.name}</TableCell>
                                                <TableCell>{user.chat_id}</TableCell>
                                                <TableCell>
                                                  {user.notificationSuccess ? (
                                                    <Chip 
                                                      label="Enviado" 
                                                      size="small" 
                                                      color="success" 
                                                      icon={<CheckIcon />} 
                                                    />
                                                  ) : (
                                                    <Chip 
                                                      label="Falhou" 
                                                      size="small" 
                                                      color="error" 
                                                      icon={<ErrorIcon />} 
                                                    />
                                                  )}
                                                </TableCell>
                                              </TableRow>
                                            ))}
                                          </TableBody>
                                        </Table>
                                      )}
                                    </Box>
                                    
                                    {log.processingStatus === 'error' && log.errorMessage && (
                                      <Alert severity="error" sx={{ mt: 2 }}>
                                        {log.errorMessage}
                                      </Alert>
                                    )}
                                  </CardContent>
                                </Card>
                              </Grid>
                            </Grid>
                          </Box>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={filteredLogs.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage="Linhas por página:"
            labelDisplayedRows={({ from, to, count }) =>
              `${from}-${to} de ${count}`
            }
          />
        </Paper>
      )}

      <Dialog
        open={detailsDialog}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        {selectedLog && (
          <>
            <DialogTitle>
              Detalhes do Alerta
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="h6">
                      {selectedLog.emailSubject}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Recebido em: {formatDateTime(selectedLog.timestamp)}
                    </Typography>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Informações do E-mail
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>Remetente:</strong> {selectedLog.emailSender}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Tipo de alerta:</strong> {selectedLog.detectedAlertType?.name || 'Não identificado'}
                    </Typography>
                    {selectedLog.detectedAlertType && (
                      <Typography variant="body2">
                        <strong>Prioridade:</strong> {selectedLog.detectedAlertType.priority}
                      </Typography>
                    )}
                  </Box>

                  <Typography variant="subtitle2" gutterBottom>
                    Conteúdo do E-mail
                  </Typography>
                  <Paper 
                    variant="outlined" 
                    sx={{ p: 2, maxHeight: 200, overflow: 'auto', bgcolor: 'grey.50' }}
                  >
                    <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                      {selectedLog.emailContent}
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Processamento
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      icon={getStatusIcon(selectedLog.processingStatus)} 
                      label={
                        selectedLog.processingStatus === 'success' ? 'Processado com sucesso' :
                        selectedLog.processingStatus === 'partial_success' ? 'Parcialmente processado' :
                        'Erro no processamento'
                      }
                      color={
                        selectedLog.processingStatus === 'success' ? 'success' :
                        selectedLog.processingStatus === 'partial_success' ? 'warning' :
                        'error'
                      }
                      sx={{ mb: 1 }}
                    />
                    
                    {selectedLog.processingStatus === 'error' && selectedLog.errorMessage && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        {selectedLog.errorMessage}
                      </Alert>
                    )}
                  </Box>

                  <Typography variant="subtitle2" gutterBottom>
                    Notificações
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Usuário</TableCell>
                          <TableCell>Chat ID</TableCell>
                          <TableCell align="center">Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedLog.recipientUsers.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={3} align="center">
                              Nenhum destinatário configurado
                            </TableCell>
                          </TableRow>
                        ) : (
                          selectedLog.recipientUsers.map((user) => (
                            <TableRow key={user.id}>
                              <TableCell>{user.name}</TableCell>
                              <TableCell>{user.chat_id}</TableCell>
                              <TableCell align="center">
                                {user.notificationSuccess ? (
                                  <CheckIcon color="success" />
                                ) : (
                                  <ErrorIcon color="error" />
                                )}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDetails}>Fechar</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default AlertLogsViewer;