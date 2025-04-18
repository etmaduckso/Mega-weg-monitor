import { Drawer, List, ListItem, ListItemIcon, ListItemText, ListItemButton } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Email as EmailIcon,
  Settings as SettingsIcon,
  Storage as StorageIcon,
  Notifications as NotificationsIcon,
  RouteRounded as RouteIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  drawerWidth?: number;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Monitoramento', icon: <RouteIcon />, path: '/monitoring' },
  { text: 'Configuração IMAP', icon: <EmailIcon />, path: '/config/imap' },
  { text: 'Notificações', icon: <NotificationsIcon />, path: '/config/notifications' },
  { text: 'Logs', icon: <StorageIcon />, path: '/logs' },
  { text: 'Configurações', icon: <SettingsIcon />, path: '/settings' },
];

export const Sidebar = ({ open, onClose, drawerWidth = 240 }: SidebarProps) => {
  const navigate = useNavigate();

  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

  return (
    <Drawer
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <List sx={{ mt: 8 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton onClick={() => handleNavigation(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};