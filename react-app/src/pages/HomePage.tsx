import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Alert,
  Snackbar,
  Paper,
  Chip,
  useTheme,
  alpha,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';

import { useApp, PersonaType } from '../context/AppContext';
import PersonaSelector from '../components/PersonaSelector';
import apiService from '../services/api';

const HomePage: React.FC = () => {
  const theme = useTheme();
  const {
    confluenceUrl,
    setConfluenceUrl,
    selectedPersona,
    setSelectedPersona,
    setCurrentPage,
    setSummaryData,
    setIsLoading,
    error,
    setError,
  } = useApp();

  const [urlError, setUrlError] = useState<string | null>(null);
  const [showPersonaSelector, setShowPersonaSelector] = useState(false);

  const handleUrlSubmit = async () => {
    if (!confluenceUrl.trim()) {
      setUrlError('Confluence URL을 입력해주세요.');
      return;
    }

    if (!confluenceUrl.includes('atlassian.net') && !confluenceUrl.includes('/wiki/')) {
      setUrlError('올바른 Confluence URL을 입력해주세요.');
      return;
    }

    try {
      setIsLoading(true);
      setUrlError(null);
      
      const validation = await apiService.validateUrl(confluenceUrl);
      
      if (validation.valid) {
        setShowPersonaSelector(true);
      } else {
        setUrlError(validation.message || '문서에 접근할 수 없습니다.');
      }
    } catch (error) {
      console.error('URL 검증 API 호출 오류:', error);
      setUrlError(`URL 검증 중 오류가 발생했습니다: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePersonaSelect = async (persona: PersonaType) => {
    setSelectedPersona(persona);
    
    try {
      setIsLoading(true);
      setError(null);
      
      const summary = await apiService.generateSummary(confluenceUrl, persona);
      
      setSummaryData({
        title: summary.title,
        url: summary.url,
        persona: persona,
        summary: summary.summary,
        isLoading: false,
      });
      
      setCurrentPage('summary');
    } catch (error) {
      setError('요약 생성 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !showPersonaSelector) {
      handleUrlSubmit();
    }
  };

  const exampleUrls = [
    'https://company.atlassian.net/wiki/spaces/PROJ/pages/123456/API+Documentation',
    'https://team.atlassian.net/wiki/spaces/DEV/pages/789012/Sprint+Planning',
    'https://org.atlassian.net/wiki/spaces/UX/pages/345678/Design+System',
  ];

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          py: 4,
        }}
      >
        {/* Logo and Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          <Typography
            variant="h1"
            component="h1"
            sx={{
              fontSize: { xs: '3rem', sm: '4rem', md: '5rem' },
              fontWeight: 400,
              mb: 1,
              textAlign: 'center',
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.02em',
            }}
          >
            ConfluSum
          </Typography>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: 'easeOut' }}
        >
          <Typography
            variant="body1"
            sx={{
              color: theme.palette.text.secondary,
              mb: 4,
              textAlign: 'center',
              fontSize: '1.1rem',
            }}
          >
            AI 기반 개인화 Confluence 문서 요약 서비스
          </Typography>
        </motion.div>

        {/* Search Box */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
          style={{ width: '100%', maxWidth: '600px' }}
        >
          <Paper
            elevation={0}
            sx={{
              p: 1,
              borderRadius: '24px',
              border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
              '&:hover': {
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              },
              '&:focus-within': {
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SearchIcon sx={{ color: theme.palette.text.secondary, ml: 2 }} />
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Confluence 문서 URL을 입력하세요..."
                value={confluenceUrl}
                onChange={(e) => setConfluenceUrl(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={showPersonaSelector}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    border: 'none',
                    backgroundColor: 'transparent',
                    '&:hover': {
                      backgroundColor: 'transparent',
                      boxShadow: 'none',
                    },
                    '&.Mui-focused': {
                      backgroundColor: 'transparent',
                      boxShadow: 'none',
                    },
                  },
                }}
              />
              {!showPersonaSelector && (
                <Button
                  variant="contained"
                  onClick={handleUrlSubmit}
                  disabled={!confluenceUrl.trim()}
                  sx={{
                    mr: 1,
                    minWidth: '100px',
                    background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                  }}
                >
                  분석하기
                </Button>
              )}
            </Box>
          </Paper>

          {urlError && (
            <Alert severity="error" sx={{ mt: 2, borderRadius: '8px' }}>
              {urlError}
            </Alert>
          )}
        </motion.div>

        {/* Example URLs */}
        {!showPersonaSelector && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Typography
                variant="body2"
                sx={{ mb: 1.5, color: theme.palette.text.secondary }}
              >
                예시 URL:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                {exampleUrls.map((url, index) => (
                  <Chip
                    key={index}
                    label={url.split('/').pop()?.replace(/\+/g, ' ') || `예시 ${index + 1}`}
                    variant="outlined"
                    size="small"
                    onClick={() => setConfluenceUrl(url)}
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.04),
                      },
                    }}
                  />
                ))}
              </Box>
            </Box>
          </motion.div>
        )}

        {/* Persona Selector */}
        {showPersonaSelector && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{ width: '100%', marginTop: '2rem' }}
          >
            <PersonaSelector onPersonaSelect={handlePersonaSelect} />
          </motion.div>
        )}

        {/* Features */}
        {!showPersonaSelector && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Box sx={{ mt: 6, display: 'flex', gap: 4, flexWrap: 'wrap', justifyContent: 'center' }}>
              {[
                { icon: '🧠', title: 'AI 기반 요약', desc: 'Claude AI가 핵심만 추출' },
                { icon: '👤', title: '개인화', desc: '역할별 맞춤 관점' },
                { icon: '⚡', title: '빠른 분석', desc: '30초 내 결과 제공' },
              ].map((feature, index) => (
                <Box
                  key={index}
                  sx={{
                    textAlign: 'center',
                    maxWidth: '150px',
                    opacity: 0.8,
                  }}
                >
                  <Typography sx={{ fontSize: '2rem', mb: 1 }}>{feature.icon}</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
                    {feature.desc}
                  </Typography>
                </Box>
              ))}
            </Box>
          </motion.div>
        )}
      </Box>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default HomePage;