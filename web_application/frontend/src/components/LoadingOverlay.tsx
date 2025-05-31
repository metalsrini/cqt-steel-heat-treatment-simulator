import React from 'react';
import {
  Backdrop,
  Box,
  CircularProgress,
  Typography,
  LinearProgress,
  Paper,
  Fade
} from '@mui/material';
import {
  Science as ScienceIcon,
  Calculate as CalculateIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';

interface LoadingOverlayProps {
  open: boolean;
  message?: string;
  progress?: number;
  stage?: string;
  subMessage?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  open,
  message = 'Processing simulation...',
  progress,
  stage,
  subMessage
}) => {
  const getStageIcon = () => {
    if (stage?.includes('carburiz')) return <ScienceIcon sx={{ fontSize: 32, color: 'primary.main' }} />;
    if (stage?.includes('quench')) return <TimelineIcon sx={{ fontSize: 32, color: 'primary.main' }} />;
    if (stage?.includes('temper')) return <CalculateIcon sx={{ fontSize: 32, color: 'primary.main' }} />;
    return <ScienceIcon sx={{ fontSize: 32, color: 'primary.main' }} />;
  };

  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(4px)'
      }}
      open={open}
    >
      <Fade in={open} timeout={300}>
        <Paper
          elevation={8}
          sx={{
            padding: 4,
            borderRadius: 3,
            backgroundColor: 'background.paper',
            color: 'text.primary',
            minWidth: 320,
            maxWidth: 480,
            textAlign: 'center',
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
          }}
        >
          <Box sx={{ marginBottom: 3 }}>
            {getStageIcon()}
          </Box>

          <Typography 
            variant="h6" 
            gutterBottom
            sx={{ 
              fontWeight: 600,
              color: 'primary.main'
            }}
          >
            {message}
          </Typography>

          {stage && (
            <Typography 
              variant="body2" 
              color="textSecondary"
              sx={{ marginBottom: 2 }}
            >
              Current Stage: {stage}
            </Typography>
          )}

          {subMessage && (
            <Typography 
              variant="body2" 
              color="textSecondary"
              sx={{ 
                marginBottom: 3,
                fontStyle: 'italic'
              }}
            >
              {subMessage}
            </Typography>
          )}

          <Box sx={{ marginY: 3 }}>
            {progress !== undefined ? (
              <Box>
                <LinearProgress 
                  variant="determinate" 
                  value={progress}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(0,0,0,0.1)',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 4
                    }
                  }}
                />
                <Typography 
                  variant="body2" 
                  color="textSecondary"
                  sx={{ marginTop: 1 }}
                >
                  {Math.round(progress)}% Complete
                </Typography>
              </Box>
            ) : (
              <CircularProgress 
                size={48}
                thickness={4}
                sx={{
                  color: 'primary.main'
                }}
              />
            )}
          </Box>

          <Typography 
            variant="caption" 
            color="textSecondary"
            sx={{
              display: 'block',
              marginTop: 2,
              opacity: 0.8
            }}
          >
            C-Q-T Heat Treatment Simulation
          </Typography>

          <Box
            sx={{
              marginTop: 2,
              display: 'flex',
              justifyContent: 'center',
              gap: 0.5
            }}
          >
            {[0, 1, 2].map((index) => (
              <Box
                key={index}
                sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  backgroundColor: 'primary.main',
                  opacity: 0.3,
                  animation: `pulse 1.5s ease-in-out ${index * 0.2}s infinite`,
                  '@keyframes pulse': {
                    '0%, 100%': {
                      opacity: 0.3,
                      transform: 'scale(1)'
                    },
                    '50%': {
                      opacity: 1,
                      transform: 'scale(1.2)'
                    }
                  }
                }}
              />
            ))}
          </Box>
        </Paper>
      </Fade>
    </Backdrop>
  );
};

export default LoadingOverlay;