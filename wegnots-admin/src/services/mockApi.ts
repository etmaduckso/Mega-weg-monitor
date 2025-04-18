/**
 * Mock API para desenvolvimento sem backend
 * 
 * Este arquivo fornece simulações de respostas da API para permitir
 * o desenvolvimento do frontend sem dependência do backend.
 */

// Mock para dados de monitoramento
export const fetchMonitoringDataMock = async () => {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return [
    { 
      id: 1, 
      message: "Monitoramento ativo", 
      status: "active", 
      lastCheck: new Date().toISOString() 
    },
    { 
      id: 2, 
      message: "E-mail importante recebido", 
      status: "alert", 
      lastCheck: new Date(Date.now() - 3600000).toISOString(),
      sender: "contato@empresa.com",
      subject: "Servidor em manutenção"
    },
    { 
      id: 3, 
      message: "Notificação enviada com sucesso", 
      status: "info", 
      lastCheck: new Date(Date.now() - 7200000).toISOString() 
    }
  ];
};

// Mock para envio de notificações
export const sendNotificationMock = async (notificationData: { message: string; channel: string }) => {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 700));
  
  // Simula uma resposta bem-sucedida
  return { 
    success: true, 
    message: `Notificação "${notificationData.message}" enviada para o canal "${notificationData.channel}"` 
  };
};

// Mock para configurações de monitoramento
export const getMonitoringConfigMock = async () => {
  await new Promise(resolve => setTimeout(resolve, 300));
  
  return {
    checkInterval: 60,
    reconnectAttempts: 5,
    reconnectDelay: 30,
    reconnectBackoffFactor: 1.5,
    logLevel: "INFO",
    emailSettings: {
      server: "imap.titan.email",
      port: 993,
      user: "monitoramento@empresa.com"
    },
    notificationChannels: {
      telegram: true,
      rocketChat: true,
      email: false
    }
  };
};