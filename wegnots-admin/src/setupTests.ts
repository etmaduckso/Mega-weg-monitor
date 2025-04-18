// setupTests.ts
// Esse arquivo é executado antes de cada teste e configura o ambiente de testes

// Importação da biblioteca de testes
import '@testing-library/jest-dom';

// Mock global de fetch
global.fetch = jest.fn();

// Limpa todos os mocks após cada teste
afterEach(() => {
  jest.clearAllMocks();
});

// Mock do localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock do sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Suprimir erros de console durante os testes
const originalConsoleError = console.error;
console.error = (...args) => {
  // Não exibir erros esperados de testes
  if (args[0]?.includes && args[0].includes('Warning: ReactDOM.render')) {
    return;
  }
  originalConsoleError(...args);
};

// Mock de ResizeObserver que não é suportado no ambiente de teste
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserverMock;