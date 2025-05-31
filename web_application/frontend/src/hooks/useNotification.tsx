import React, { useState, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertColor,
  Slide,
  SlideProps
} from '@mui/material';

interface NotificationState {
  open: boolean;
  message: string;
  severity: AlertColor;
  autoHideDuration?: number;
}

interface UseNotificationReturn {
  showNotification: (message: string, severity?: AlertColor, duration?: number) => void;
  hideNotification: () => void;
  NotificationComponent: React.ComponentType;
}

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

export const useNotification = (): UseNotificationReturn => {
  const [notification, setNotification] = useState<NotificationState>({
    open: false,
    message: '',
    severity: 'info',
    autoHideDuration: 6000
  });

  const showNotification = useCallback((
    message: string,
    severity: AlertColor = 'info',
    duration: number = 6000
  ) => {
    setNotification({
      open: true,
      message,
      severity,
      autoHideDuration: duration
    });
  }, []);

  const hideNotification = useCallback(() => {
    setNotification(prev => ({
      ...prev,
      open: false
    }));
  }, []);

  const NotificationComponent = useCallback(() => {
    if (!notification.open) return null;

    return (
      <Snackbar
        open={notification.open}
        autoHideDuration={notification.autoHideDuration}
        onClose={hideNotification}
        anchorOrigin={{ 
          vertical: 'bottom', 
          horizontal: 'right' 
        }}
        TransitionComponent={SlideTransition}
        sx={{
          '& .MuiSnackbarContent-root': {
            minWidth: '300px'
          }
        }}
      >
        <Alert
          onClose={hideNotification}
          severity={notification.severity}
          variant="filled"
          sx={{
            width: '100%',
            fontSize: '0.875rem',
            fontWeight: 500,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            '& .MuiAlert-icon': {
              alignItems: 'center'
            },
            '& .MuiAlert-message': {
              padding: '4px 0',
              display: 'flex',
              alignItems: 'center'
            }
          }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    );
  }, [notification, hideNotification]);

  return {
    showNotification,
    hideNotification,
    NotificationComponent
  };
};

export default useNotification;