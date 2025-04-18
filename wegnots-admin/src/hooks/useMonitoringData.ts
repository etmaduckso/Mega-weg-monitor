import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { monitoringService } from '../services/monitoring';
import type { MonitoredEmail, TelegramConfig, NotificationRouting } from '../types/monitoring';

export const useMonitoringData = () => {
  const queryClient = useQueryClient();

  // Queries
  const emails = useQuery({
    queryKey: ['monitoredEmails'],
    queryFn: monitoringService.getMonitoredEmails,
  });

  const telegramConfigs = useQuery({
    queryKey: ['telegramConfigs'],
    queryFn: monitoringService.getTelegramConfigs,
  });

  const routings = useQuery({
    queryKey: ['notificationRoutings'],
    queryFn: monitoringService.getNotificationRoutings,
  });

  // Mutations
  const createEmail = useMutation({
    mutationFn: monitoringService.createMonitoredEmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoredEmails'] });
    },
  });

  const updateEmail = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<MonitoredEmail> }) =>
      monitoringService.updateMonitoredEmail(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoredEmails'] });
    },
  });

  const deleteEmail = useMutation({
    mutationFn: monitoringService.deleteMonitoredEmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoredEmails'] });
    },
  });

  const createTelegramConfig = useMutation({
    mutationFn: monitoringService.createTelegramConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['telegramConfigs'] });
    },
  });

  const updateTelegramConfig = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TelegramConfig> }) =>
      monitoringService.updateTelegramConfig(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['telegramConfigs'] });
    },
  });

  const deleteTelegramConfig = useMutation({
    mutationFn: monitoringService.deleteTelegramConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['telegramConfigs'] });
    },
  });

  const createRouting = useMutation({
    mutationFn: monitoringService.createNotificationRouting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificationRoutings'] });
    },
  });

  const updateRouting = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<NotificationRouting> }) =>
      monitoringService.updateNotificationRouting(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificationRoutings'] });
    },
  });

  const deleteRouting = useMutation({
    mutationFn: monitoringService.deleteNotificationRouting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificationRoutings'] });
    },
  });

  const testTelegram = useMutation({
    mutationFn: monitoringService.testTelegramConnection,
  });

  return {
    // Queries
    emails,
    telegramConfigs,
    routings,
    // Mutations
    createEmail,
    updateEmail,
    deleteEmail,
    createTelegramConfig,
    updateTelegramConfig,
    deleteTelegramConfig,
    createRouting,
    updateRouting,
    deleteRouting,
    testTelegram,
  };
};