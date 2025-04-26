export interface MonitoredEmail {
  id: string;
  email: string;
  description: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TelegramConfig {
  id: string;
  chatId: string;
  description: string;
  isActive: boolean;
}

export interface NotificationRouting {
  id: string;
  emailId: string;
  telegramChatIds: string[];
  useRocketChat: boolean;
  rocketChatChannel?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CentralServer {
  email: string;
  chatId: string;
  isActive: boolean;
}

export interface SystemStatus {
  imap: {
    status: 'connected' | 'disconnected' | 'error';
    lastCheck: string;
    error?: string;
  };
  telegram: {
    status: 'connected' | 'disconnected' | 'error';
    lastMessage: string;
    error?: string;
  };
  mongodb: {
    status: 'connected' | 'disconnected' | 'error';
    error?: string;
  };
  monitoring: {
    isActive: boolean;
    lastAlert: string;
    processedEmails: number;
    sentAlerts: number;
  };
}

export interface MonitoringConfig {
  checkInterval: number;
  retryAttempts: number;
  retryDelay: number;
  alertLevels: {
    critical: string[];
    moderate: string[];
    low: string[];
  };
  telegramConfig: {
    retryAttempts: number;
    retryDelay: number;
  };
  rocketChatConfig: {
    enabled: boolean;
    defaultChannel: string;
  };
}