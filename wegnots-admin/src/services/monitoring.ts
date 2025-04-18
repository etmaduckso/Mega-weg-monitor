import { api } from './api';
import type { MonitoredEmail, TelegramConfig, NotificationRouting } from '../types/monitoring';

export const monitoringService = {
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
    const { data } = await api.get<NotificationRouting[]>('/api/notification-routings');
    return data;
  },

  async createNotificationRouting(routing: Omit<NotificationRouting, 'id' | 'createdAt' | 'updatedAt'>) {
    const { data } = await api.post<NotificationRouting>('/api/notification-routings', routing);
    return data;
  },

  async updateNotificationRouting(id: string, routing: Partial<NotificationRouting>) {
    const { data } = await api.put<NotificationRouting>(`/api/notification-routings/${id}`, routing);
    return data;
  },

  async deleteNotificationRouting(id: string) {
    await api.delete(`/api/notification-routings/${id}`);
  },

  // Teste de conexão Telegram
  async testTelegramConnection(chatId: string) {
    const { data } = await api.post<{ success: boolean; message: string }>('/api/telegram/test', { chatId });
    return data;
  },
};