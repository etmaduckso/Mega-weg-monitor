import React, { useEffect, useState } from 'react';
import { monitoringService } from '../services/monitoring';

const Configurations = () => {
  const [config, setConfig] = useState({
    imap: {},
    telegram: {}
  });

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const data = await monitoringService.getSystemConfig();
        setConfig(data);
      } catch (error) {
        console.error('Erro ao buscar configurações:', error);
      }
    };

    fetchConfig();
  }, []);

  return (
    <div>
      <h1>Configurações do Sistema</h1>
      <h2>Servidor IMAP</h2>
      <p><strong>Servidor:</strong> {config.imap.server}</p>
      <p><strong>Porta:</strong> {config.imap.port}</p>
      <p><strong>Usuário:</strong> {config.imap.username}</p>
      <p><strong>Intervalo de Verificação:</strong> {config.imap.check_interval} segundos</p>

      <h2>Telegram</h2>
      <p><strong>Token do Bot:</strong> {config.telegram.bot_token}</p>
      <p><strong>Chat ID Padrão:</strong> {config.telegram.default_chat_id}</p>
    </div>
  );
};

export default Configurations;