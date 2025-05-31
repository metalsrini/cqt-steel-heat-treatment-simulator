import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  AlertTitle,
  Stack,
  Divider
} from '@mui/material';
import {
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
  errorId: string;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log error to console for development
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // In production, you would send this to your error reporting service
    if (process.env.NODE_ENV === 'production') {
      this.logErrorToService(error, errorInfo);
    }
  }

  private logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
    // Implement error logging service integration here
    // For example: Sentry, LogRocket, etc.
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      errorId: this.state.errorId,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    
    console.log('Error logged:', errorData);
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
      errorId: ''
    });
  };

  private handleReportError = () => {
    const { error, errorInfo, errorId } = this.state;
    const errorReport = {
      errorId,
      message: error?.message,
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      timestamp: new Date().toISOString()
    };

    const subject = `Error Report - C-Q-T Simulator - ${errorId}`;
    const body = `Error Report Details:\n\n${JSON.stringify(errorReport, null, 2)}`;
    const mailtoLink = `mailto:support@example.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    
    window.open(mailtoLink);
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { error, errorInfo, errorId } = this.state;
      const isProduction = process.env.NODE_ENV === 'production';

      return (
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f5f5f5',
            padding: 3
          }}
        >
          <Paper
            elevation={3}
            sx={{
              padding: 4,
              maxWidth: 600,
              width: '100%',
              textAlign: 'center'
            }}
          >
            <ErrorIcon
              sx={{
                fontSize: 64,
                color: 'error.main',
                marginBottom: 2
              }}
            />

            <Typography variant="h4" gutterBottom color="error">
              Something went wrong
            </Typography>

            <Typography variant="body1" color="textSecondary" paragraph>
              An unexpected error occurred in the C-Q-T Steel Heat Treatment Simulator.
              We apologize for the inconvenience.
            </Typography>

            <Alert severity="error" sx={{ marginBottom: 3, textAlign: 'left' }}>
              <AlertTitle>Error Details</AlertTitle>
              <Typography variant="body2" component="div">
                <strong>Error ID:</strong> {errorId}
                <br />
                <strong>Message:</strong> {error?.message || 'Unknown error'}
                {!isProduction && (
                  <>
                    <br />
                    <strong>Stack:</strong>
                    <pre style={{ 
                      fontSize: '0.75rem', 
                      marginTop: '8px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}>
                      {error?.stack}
                    </pre>
                  </>
                )}
              </Typography>
            </Alert>

            <Stack spacing={2} direction="row" justifyContent="center">
              <Button
                variant="contained"
                color="primary"
                startIcon={<RefreshIcon />}
                onClick={this.handleRetry}
              >
                Try Again
              </Button>

              <Button
                variant="outlined"
                color="primary"
                onClick={this.handleReload}
              >
                Reload Page
              </Button>

              <Button
                variant="outlined"
                color="secondary"
                startIcon={<BugReportIcon />}
                onClick={this.handleReportError}
              >
                Report Error
              </Button>
            </Stack>

            {!isProduction && errorInfo && (
              <>
                <Divider sx={{ marginY: 3 }} />
                <Alert severity="info" sx={{ textAlign: 'left' }}>
                  <AlertTitle>Component Stack (Development)</AlertTitle>
                  <pre style={{ 
                    fontSize: '0.75rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    margin: 0
                  }}>
                    {errorInfo.componentStack}
                  </pre>
                </Alert>
              </>
            )}

            <Typography variant="caption" color="textSecondary" sx={{ marginTop: 3, display: 'block' }}>
              If this problem persists, please contact technical support with Error ID: {errorId}
            </Typography>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;