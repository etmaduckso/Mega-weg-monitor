import { api } from './api';
import type { MonitoredEmail, TelegramConfig, NotificationRouting, CentralServer } from '../types/monitoring';

export const monitoringService = {
  // Servidor Central
  async getCentralServer() {
    const { data } = await api.get<CentralServer>('/api/central-server');
    return data;
  },

  async updateCentralServerStatus(active: boolean) {
    const { data } = await api.put('/api/central-server/status', { active });
    return data;
  },

  async updateCentralServerConfig(email: string) {
    const { data } = await api.put('/api/central-server', { email });
    return data;
  },

  // E-mails monitorados
  async getMonitoredEmails() {
    const { data } = await api.get<MonitoredEmail[]>('/api/emails');
    return data;
  },

  async createMonitoredEmail(email: Omit<MonitoredEmail, 'id' | 'createdAt' | 'updatedAt'>) {
    const { data } = await api.post<MonitoredEmail>('/api/emails', email);
    return data;
  },

  async updateMonitoredEmail(id: string, email: Partial<MonitoredEmail>) {
    const { data } = await api.put<MonitoredEmail>(`/api/emails/${id}`, email);
    return data;
  },

  async deleteMonitoredEmail(id: string) {
    await api.delete(`/api/emails/${id}`);
  },

  // Configurações do Telegram
  async getTelegramConfigs() {
    const { data } = await api.get<TelegramConfig[]>('/api/telegram/configs');
    return data;
  },

  async createTelegramConfig(config: Omit<TelegramConfig, 'id'>) {
    const { data } = await api.post<TelegramConfig>('/api/telegram/configs', config);
    return data;
  },

  async updateTelegramConfig(id: string, config: Partial<TelegramConfig>) {
    const { data } = await api.put<TelegramConfig>(`/api/telegram/configs/${id}`, config);
    return data;
  },

  async deleteTelegramConfig(id: string) {
    await api.delete(`/api/telegram/configs/${id}`);
  },

  // Roteamento de notificações
  async getNotificationRoutings() {
    const { data } = await api.get<NotificationRouting[]>('/api/routing-rules');
    return data;
  },

  async createNotificationRouting(routing: Omit<NotificationRouting, 'id' | 'createdAt' | 'updatedAt'>) {
    const { data } = await api.post<NotificationRouting>('/api/routing-rules', routing);
    return data;
  },

  async updateNotificationRouting(id: string, routing: Partial<NotificationRouting>) {
    const { data } = await api.put<NotificationRouting>(`/api/routing-rules/${id}`, routing);
    return data;
  },

  async deleteNotificationRouting(id: string) {
    await api.delete(`/api/routing-rules/${id}`);
  },

  // Teste de conexão Telegram
  async testTelegramConnection(chatId: string) {
    const { data } = await api.post<{ success: boolean; message: string }>('/api/telegram/test', { chatId });
    return data;
  },

  // Configurações gerais
  async getMonitoringConfig() {
    const { data } = await api.get('/api/monitoring/config');
    return data;
  },

  async updateMonitoringConfig(config: any) {
    const { data } = await api.put('/api/monitoring/config', config);
    return data;
  },
  
  // Status do sistema
  async getSystemStatus() {
    const { data } = await api.get('/api/monitoring/status');
    return data;
  },

  // Configuração do sistema
  async getSystemConfig() {
    const { data } = await api.get('/api/config');
    return data;
  }
};