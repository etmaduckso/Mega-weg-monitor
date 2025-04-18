import React from 'react';
import { useMsal } from '@azure/msal-react';

export const Logout = () => {
  const { instance } = useMsal();

  const handleLogout = () => {
    instance.logoutRedirect();
  };

  return (
    <div>
      <button onClick={handleLogout}>Sair</button>
    </div>
  );
};
