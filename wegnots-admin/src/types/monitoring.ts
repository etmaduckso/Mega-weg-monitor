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