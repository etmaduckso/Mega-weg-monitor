import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormHelperText
} from '@mui/material';
import {
  CheckCircleOutline as CheckIcon,
  ErrorOutline as ErrorIcon,
  AddCircleOutline as AddIcon,
  PlayArrow as TestIcon,
  Save as SaveIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { api } from '../services/api';
import PageLayout from '../layouts/PageLayout';

interface AlertType {
  id: string;
  name: string;
  description?: string;
  priority: 'critical' | 'high' | 'medium' | 'low' | 'info';
  patterns: {
    senderPattern: string;
    subjectPattern: string;
    contentPattern: string;
  }[];
}

interface TestResult {
  matches: boolean;
  matchedType: AlertType | null;
  matchDetails: {
    senderMatch: boolean;
    subjectMatch: boolean;
    contentMatch: boolean;
    matchedPattern?: number;
  };
}

const AlertPatternTesterPage: React.FC = () => {
  const [alertTypes, setAlertTypes] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [sender, setSender] = useState('camera@security.com');
  const [subject, setSubject] = useState('INTRUSAO 2025-04-17 09:50:58');
  const [content, setContent] = useState('time:2025-04-17 09:50:58 DIVICEGRUPO:Default group DEVICE NAME: NVR LOJA CHANNEL name:Bullet Varifo');
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [openTemplateDialog, setOpenTemplateDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  // Exemplos de templates de e-mail para teste
  const emailTemplates = [
    {
      id: 'intrusao',
      name: 'Alerta de Intrusão',
      sender: 'camera@security.com',
      subject: 'INTRUSAO 2025-04-17 09:50:58',
      content: 'time:2025-04-17 09:50:58 DIVICEGRUPO:Default group DEVICE NAME: NVR LOJA CHANNEL name:Bullet Varifo'
    },
    {
      id: 'procurado',
      name: 'Alerta de Procurado/Foragido',
      sender: 'alerta@sistema.com',
      subject: 'URGENTE - Alerta de Procurado ou Foragido',
      content: 'Acabamos de detectar pelo sistema de câmeras do comércio que um Alerta de Procurado ou Foragido foi registrado'
    },
    {
      id: 'suspeito',
      name: 'Alerta de Suspeito',
      sender: 'vigilancia@security.com',
      subject: 'ATENÇÃO - Alerta de Suspeito',
      content: 'Sua loja acabou de receber um alerta de Suspeito, acesse a sua câmera e confirme o que está acontecendo'
    },
    {
      id: 'facial',
      name: 'Teste Facial',
      sender: 'biometria@sistema.com',
      subject: 'FACIAL TESTE | 2025-04-17 09:28:32',
      content: 'time:2025-04-17 09:28:32 DIVICEGRUPO:Default group DEVICE NAME: NVR LOJA CHANNEL name:Bullet 5 MP 1'
    }
  ];

  useEffect(() => {
    fetchAlertTypes();
  }, []);

  const fetchAlertTypes = async () => {
    setLoading(true);
    try {
      // Em um ambiente real, aqui seria uma chamada para a API
      try {
        const token = localStorage.getItem('token');
        const res = await api.get('/alert-types', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAlertTypes(res.data);
      } catch (err) {
        // Se a API falhar, usamos dados mockados para demonstração
        const mockAlertTypes = [
          {
            id: '1',
            name: 'Intrusão',
            description: 'Alertas de invasão ou intrusão detectados por câmeras de segurança',
            priority: 'critical' as const,
            patterns: [
              {
                senderPattern: '.*@security\\.com',
                subjectPattern: '.*INTRUSAO.*',
                contentPattern: '.*DEVICE NAME.*CHANNEL.*'
              }
            ]
          },
          {
            id: '2',
            name: 'Procurado ou Foragido',
            description: 'Alertas de reconhecimento facial de indivíduos procurados',
            priority: 'high' as const,
            patterns: [
              {
                senderPattern: '.*@sistema\\.com',
                subjectPattern: '.*Procurado ou Foragido.*',
                contentPattern: '.*Alerta de Procurado.*'
              }
            ]
          },
          {
            id: '3',
            name: 'Suspeito',
            description: 'Alertas de atividades suspeitas',
            priority: 'medium' as const,
            patterns: [
              {
                senderPattern: '.*@security\\.com',
                subjectPattern: '.*Suspeito.*',
                contentPattern: '.*alerta de Suspeito.*'
              }
            ]
          },
          {
            id: '4',
            name: 'Teste Facial',
            description: 'Testes do sistema de reconhecimento facial',
            priority: 'low' as const,
            patterns: [
              {
                senderPattern: '.*@sistema\\.com',
                subjectPattern: '.*FACIAL TESTE.*',
                contentPattern: '.*CHANNEL name:Bullet.*MP.*'
              }
            ]
          }
        ];
        setAlertTypes(mockAlertTypes);
      }
    } catch (error) {
      console.error('Erro ao carregar tipos de alertas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTest = () => {
    setTestLoading(true);
    
    // Simulando uma pausa para dar a impressão de processamento
    setTimeout(() => {
      const result = testAlertPatterns(sender, subject, content, alertTypes);
      setTestResult(result);
      setTestLoading(false);
    }, 500);
  };

  const handleOpenTemplateDialog = () => {
    setOpenTemplateDialog(true);
  };

  const handleCloseTemplateDialog = () => {
    setOpenTemplateDialog(false);
  };

  const handleSelectTemplate = () => {
    const template = emailTemplates.find(t => t.id === selectedTemplate);
    if (template) {
      setSender(template.sender);
      setSubject(template.subject);
      setContent(template.content);
    }
    handleCloseTemplateDialog();
  };

  const testAlertPatterns = (
    emailSender: string, 
    emailSubject: string, 
    emailContent: string, 
    types: AlertType[]
  ): TestResult => {
    // Testando cada tipo de alerta
    for (const alertType of types) {
      // Testando cada padrão dentro do tipo de alerta
      for (let i = 0; i < alertType.patterns.length; i++) {
        const pattern = alertType.patterns[i];
        
        try {
          // Criando expressões regulares para os padrões
          const senderRegex = new RegExp(pattern.senderPattern, 'i');
          const subjectRegex = new RegExp(pattern.subjectPattern, 'i');
          const contentRegex = new RegExp(pattern.contentPattern, 'i');
          
          // Testando cada campo
          const senderMatch = senderRegex.test(emailSender);
          const subjectMatch = subjectRegex.test(emailSubject);
          const contentMatch = contentRegex.test(emailContent);
          
          // Se todas as condições corresponderem, temos uma correspondência
          if (senderMatch && subjectMatch && contentMatch) {
            return {
              matches: true,
              matchedType: alertType,
              matchDetails: {
                senderMatch,
                subjectMatch,
                contentMatch,
                matchedPattern: i
              }
            };
          }
        } catch (e) {
          console.error(`Erro ao testar padrão de expressão regular: ${e}`);
          // Continua testando outros padrões mesmo se um falhar
        }
      }
    }
    
    // Se nenhum tipo de alerta corresponder, retorna resultado negativo
    return {
      matches: false,
      matchedType: null,
      matchDetails: {
        senderMatch: false,
        subjectMatch: false,
        contentMatch: false
      }
    };
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  return (
    <PageLayout title="Testador de Padrões de Alerta">
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              E-mail de Teste
            </Typography>
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                variant="outlined" 
                startIcon={<AddIcon />} 
                onClick={handleOpenTemplateDialog}
                sx={{ mb: 2 }}
              >
                Carregar Modelo
              </Button>
            </Box>
            
            <TextField
              label="Remetente"
              fullWidth
              margin="normal"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              helperText="Campo 'From' do e-mail"
              inputProps={{ style: { fontFamily: 'monospace' } }}
            />
            
            <TextField
              label="Assunto"
              fullWidth
              margin="normal"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              helperText="Campo 'Subject' do e-mail"
              inputProps={{ style: { fontFamily: 'monospace' } }}
            />
            
            <TextField
              label="Conteúdo"
              fullWidth
              margin="normal"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              multiline
              rows={6}
              helperText="Corpo do e-mail (texto)"
              inputProps={{ style: { fontFamily: 'monospace' } }}
            />
            
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                variant="contained" 
                color="primary"
                startIcon={testLoading ? <CircularProgress size={20} color="inherit" /> : <TestIcon />}
                onClick={handleTest}
                disabled={testLoading}
              >
                Testar Padrões
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Resultado do Teste
            </Typography>
            
            {testResult ? (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {testResult.matches ? (
                    <CheckIcon color="success" sx={{ mr: 1, fontSize: 30 }} />
                  ) : (
                    <ErrorIcon color="error" sx={{ mr: 1, fontSize: 30 }} />
                  )}
                  <Typography variant="h6">
                    {testResult.matches
                      ? 'Padrão correspondente encontrado!'
                      : 'Nenhum padrão correspondente.'}
                  </Typography>
                </Box>
                
                {testResult.matches && testResult.matchedType && (
                  <Card variant="outlined" sx={{ mb: 3 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">{testResult.matchedType.name}</Typography>
                        <Chip 
                          label={testResult.matchedType.priority} 
                          color={getPriorityColor(testResult.matchedType.priority) as any} 
                          size="small" 
                        />
                      </Box>
                      
                      {testResult.matchedType.description && (
                        <Typography color="text.secondary" variant="body2" sx={{ mb: 2 }}>
                          {testResult.matchedType.description}
                        </Typography>
                      )}
                      
                      <Divider sx={{ my: 2 }} />
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Padrão correspondente:
                      </Typography>
                      
                      {testResult.matchDetails.matchedPattern !== undefined && (
                        <Box sx={{ mt: 1 }}>
                          <Grid container spacing={1}>
                            <Grid item xs={4}>
                              <Typography variant="body2" color="text.secondary">
                                Remetente:
                              </Typography>
                            </Grid>
                            <Grid item xs={8}>
                              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                {testResult.matchedType.patterns[testResult.matchDetails.matchedPattern].senderPattern}
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={4}>
                              <Typography variant="body2" color="text.secondary">
                                Assunto:
                              </Typography>
                            </Grid>
                            <Grid item xs={8}>
                              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                {testResult.matchedType.patterns[testResult.matchDetails.matchedPattern].subjectPattern}
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={4}>
                              <Typography variant="body2" color="text.secondary">
                                Conteúdo:
                              </Typography>
                            </Grid>
                            <Grid item xs={8}>
                              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                {testResult.matchedType.patterns[testResult.matchDetails.matchedPattern].contentPattern}
                              </Typography>
                            </Grid>
                          </Grid>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                )}
                
                {!testResult.matches && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    O e-mail de teste não corresponde a nenhum padrão configurado no sistema. 
                    Verifique o conteúdo do e-mail ou ajuste os padrões na página de tipos de alerta.
                  </Alert>
                )}
                
                <Divider sx={{ my: 3 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Detalhes da correspondência
                </Typography>
                
                <Grid container spacing={1} sx={{ mt: 1 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2">Correspondência de remetente:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    {testResult.matchDetails.senderMatch ? (
                      <Typography variant="body2" color="success.main">Correspondente</Typography>
                    ) : (
                      <Typography variant="body2" color="error.main">Não correspondente</Typography>
                    )}
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2">Correspondência de assunto:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    {testResult.matchDetails.subjectMatch ? (
                      <Typography variant="body2" color="success.main">Correspondente</Typography>
                    ) : (
                      <Typography variant="body2" color="error.main">Não correspondente</Typography>
                    )}
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2">Correspondência de conteúdo:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    {testResult.matchDetails.contentMatch ? (
                      <Typography variant="body2" color="success.main">Correspondente</Typography>
                    ) : (
                      <Typography variant="body2" color="error.main">Não correspondente</Typography>
                    )}
                  </Grid>
                </Grid>
              </Box>
            ) : (
              <Alert severity="info">
                Use o formulário à esquerda para testar um e-mail contra os padrões configurados.
                Os resultados aparecerão aqui após o teste.
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      <Dialog
        open={openTemplateDialog}
        onClose={handleCloseTemplateDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Selecione um modelo de e-mail
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Modelo de E-mail</InputLabel>
            <Select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              label="Modelo de E-mail"
            >
              {emailTemplates.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  {template.name}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>
              Selecione um modelo de e-mail para preencher automaticamente os campos de teste
            </FormHelperText>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseTemplateDialog}>Cancelar</Button>
          <Button 
            onClick={handleSelectTemplate} 
            variant="contained"
            color="primary"
            disabled={!selectedTemplate}
          >
            Selecionar
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default AlertPatternTesterPage;