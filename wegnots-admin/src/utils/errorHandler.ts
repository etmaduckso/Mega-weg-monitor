import { AxiosError } from 'axios';

interface ApiError {
  message: string;
  code?: string;
}

export const getErrorMessage = (error: unknown): string => {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as ApiError | undefined;
    if (apiError) {
      return apiError.message || 'Erro na comunicação com o servidor';
    }
    return 'Erro desconhecido na comunicação com o servidor';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Ocorreu um erro inesperado';
};

export const handleApiError = (error: unknown, fallbackMessage: string): string => {
  console.error('API Error:', error);
  const errorMessage = getErrorMessage(error);
  if (errorMessage !== fallbackMessage) {
    console.error(`Fallback message: ${fallbackMessage}`);
  }
  return errorMessage || fallbackMessage;
};
