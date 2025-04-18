import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from './Dashboard';
import * as apiService from '../services/api';

// Mock do módulo api
jest.mock('../services/api', () => ({
  fetchMonitoringData: jest.fn(),
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('exibe mensagem de carregamento inicialmente', () => {
    // Mock do retorno da API
    (apiService.fetchMonitoringData as jest.Mock).mockResolvedValue([]);

    render(<Dashboard />);
    
    // Verifica se a mensagem de carregamento é exibida
    expect(screen.getByText(/Carregando dados.../i)).toBeInTheDocument();
  });

  test('exibe dados de monitoramento quando carregados com sucesso', async () => {
    // Mock do retorno da API com dados de exemplo
    const mockData = [
      { id: 1, message: 'Monitoramento ativo', status: 'active' },
      { id: 2, message: 'E-mail importante recebido', status: 'alert' }
    ];
    
    (apiService.fetchMonitoringData as jest.Mock).mockResolvedValue(mockData);

    render(<Dashboard />);
    
    // Espera que os dados sejam carregados
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Monitoramento ativo')).toBeInTheDocument();
      expect(screen.getByText('E-mail importante recebido')).toBeInTheDocument();
    });
    
    // Verifica se a função da API foi chamada
    expect(apiService.fetchMonitoringData).toHaveBeenCalledTimes(1);
  });

  test('exibe mensagem de erro quando falha ao carregar dados', async () => {
    // Mock de erro na API
    (apiService.fetchMonitoringData as jest.Mock).mockRejectedValue(
      new Error('Erro ao carregar dados')
    );

    render(<Dashboard />);
    
    // Espera que a mensagem de erro seja exibida
    await waitFor(() => {
      expect(screen.getByText('Erro ao carregar dados de monitoramento.')).toBeInTheDocument();
    });
    
    // Verifica se a função da API foi chamada
    expect(apiService.fetchMonitoringData).toHaveBeenCalledTimes(1);
  });
});