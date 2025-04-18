import * as yup from 'yup';

export const emailSchema = yup.object({
  email: yup
    .string()
    .email('E-mail inválido')
    .required('E-mail é obrigatório'),
  description: yup
    .string()
    .required('Descrição é obrigatória')
    .min(3, 'Descrição deve ter pelo menos 3 caracteres')
    .max(100, 'Descrição deve ter no máximo 100 caracteres'),
});

export const telegramSchema = yup.object({
  chatId: yup
    .string()
    .required('Chat ID é obrigatório')
    .matches(/^-?\d+$/, 'Chat ID deve conter apenas números'),
  description: yup
    .string()
    .required('Descrição é obrigatória')
    .min(3, 'Descrição deve ter pelo menos 3 caracteres')
    .max(100, 'Descrição deve ter no máximo 100 caracteres'),
});

export const routingSchema = yup.object({
  emailId: yup
    .string()
    .required('E-mail é obrigatório'),
  telegramChatIds: yup
    .array()
    .of(yup.string())
    .min(1, 'Selecione pelo menos um destinatário')
    .required('Selecione pelo menos um destinatário'),
  useRocketChat: yup
    .boolean(),
  rocketChatChannel: yup
    .string()
    .when('useRocketChat', {
      is: true,
      then: (schema) => schema.matches(/^[a-zA-Z0-9_-]*$/, 'Canal inválido. Use apenas letras, números, _ e -'),
    }),
});