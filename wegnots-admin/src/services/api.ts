import axios from 'axios';
import { fetchMonitoringDataMock, sendNotificationMock, getMonitoringConfigMock } from './mockApi';

// Flag para controlar o uso de mocks (alterado para false agora que o backend está disponível)
const USE_MOCK = false; 

// Cria uma instância do Axios com configurações base
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Função para obter dados de monitoramento
export const fetchMonitoringData = async () => {
  if (USE_MOCK) {
    return fetchMonitoringDataMock();
  }
  
  try {
    const response = await api.get('/monitoring');
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar dados de monitoramento:', error);
    throw new Error('Não foi possível carregar os dados de monitoramento. Tente novamente mais tarde.');
  }
};

// Função para enviar notificações
export const sendNotification = async (notificationData: { message: string; channel: string }) => {
  if (USE_MOCK) {
    return sendNotificationMock(notificationData);
  }
  
  try {
    const response = await api.post('/notifications', notificationData);
    return response.data;
  } catch (error) {
    console.error('Erro ao enviar notificação:', error);
    throw new Error('Não foi possível enviar a notificação. Verifique os dados e tente novamente.');
  }
};

// Função para obter configurações de monitoramento
export const getMonitoringConfig = async () => {
  if (USE_MOCK) {
    return getMonitoringConfigMock();
  }
  
  try {
    const response = await api.get('/config');
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar configurações de monitoramento:', error);
    throw new Error('Não foi possível carregar as configurações de monitoramento. Tente novamente mais tarde.');
  }
};

// Função para salvar configurações de monitoramento
export const saveMonitoringConfig = async (config: any) => {
  try {
    const response = await api.post('/config/monitoring', config);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error('Erro ao salvar configurações. Verifique os dados e tente novamente.');
    } else if (error.request) {
      throw new Error('Servidor não respondeu. Verifique sua conexão.');
    } else {
      throw new Error('Erro ao fazer a requisição.');
    }
  }
};

// Função para registrar usuário
export const registerUser = async (data: RegisterUserData) => {
  try {
    const response = await api.post('/register', data);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // O servidor respondeu com um status de erro
      throw new Error('Erro ao registrar usuário. Verifique os dados e tente novamente.');
    } else if (error.request) {
      // A requisição foi feita mas não houve resposta
      throw new Error('Servidor não respondeu. Verifique sua conexão.');
    } else {
      // Erro na configuração da requisição
      throw new Error('Erro ao fazer a requisição.');
    }
  }
};

// Função para login de usuário
export const loginUser = async (data: { email: string; password: string }) => {
  return api.post('/login', data);
};

// Função para salvar configurações do usuário
export const saveUserConfig = async (userId: string, data: any) => {
  try {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error('Erro ao salvar configurações do usuário. Verifique os dados e tente novamente.');
    } else if (error.request) {
      throw new Error('Servidor não respondeu. Verifique sua conexão.');
    } else {
      throw new Error('Erro ao fazer a requisição.');
    }
  }
};
