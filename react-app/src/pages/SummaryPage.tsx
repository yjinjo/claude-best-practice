import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Snackbar,
  Paper,
  useTheme,
  alpha,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Share as ShareIcon,
  ContentCopy as CopyIcon,
  Code as DeveloperIcon,
  Business as ProductManagerIcon,
  Palette as DesignerIcon,
  Description as GeneralIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { useApp } from '../context/AppContext';
import apiService from '../services/api';

const SummaryPage: React.FC = () => {
  const theme = useTheme();
  const { summaryData, resetApp, selectedPersona } = useApp();
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleFeedback = async (type: 'positive' | 'negative') => {
    if (!summaryData || !selectedPersona) return;

    try {
      await apiService.submitFeedback(summaryData.url, selectedPersona, type);
      setFeedback(type);
      setFeedbackMessage(
        type === 'positive' 
          ? '피드백을 보내주셔서 감사합니다! 👍' 
          : '소중한 의견 감사합니다. 더 나은 서비스로 개선하겠습니다. 🙏'
      );
    } catch (error) {
      setFeedbackMessage('피드백 전송 중 오류가 발생했습니다.');
    }
  };

  const handleCopy = async () => {
    if (!summaryData) return;

    try {
      const textToCopy = `${summaryData.title}\n\n${summaryData.summary}\n\n출처: ${summaryData.url}`;
      await navigator.clipboard.writeText(textToCopy);
      setCopySuccess(true);
    } catch (error) {
      console.error('복사 실패:', error);
    }
  };

  const getPersonaInfo = () => {
    switch (selectedPersona) {
      case 'general':
        return {
          title: '일반',
          icon: GeneralIcon,
          color: '#6c757d',
          gradient: 'linear-gradient(135deg, #6c757d, #495057)',
        };
      case 'developer':
        return {
          title: '개발자',
          icon: DeveloperIcon,
          color: '#4285f4',
          gradient: 'linear-gradient(135deg, #4285f4, #34a853)',
        };
      case 'product_manager':
        return {
          title: '기획자',
          icon: ProductManagerIcon,
          color: '#ea4335',
          gradient: 'linear-gradient(135deg, #ea4335, #fbbc04)',
        };
      case 'designer':
        return {
          title: '디자이너',
          icon: DesignerIcon,
          color: '#34a853',
          gradient: 'linear-gradient(135deg, #34a853, #4285f4)',
        };
      default:
        return {
          title: '사용자',
          icon: GeneralIcon,
          color: '#6c757d',
          gradient: 'linear-gradient(135deg, #6c757d, #495057)',
        };
    }
  };


  if (!summaryData) {
    return (
      <Container maxWidth="md">
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <Typography variant="h2">요약 데이터를 찾을 수 없습니다.</Typography>
          <Button onClick={resetApp} sx={{ mt: 2 }}>
            홈으로 돌아가기
          </Button>
        </Box>
      </Container>
    );
  }

  const personaInfo = getPersonaInfo();
  const PersonaIcon = personaInfo.icon;

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 3 }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <IconButton onClick={resetApp} sx={{ mr: 2 }}>
              <ArrowBackIcon />
            </IconButton>
            <Typography
              variant="h1"
              sx={{
                fontSize: '1.5rem',
                fontWeight: 400,
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              ConfluSum
            </Typography>
          </Box>
        </motion.div>

        <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
          {/* Main Content */}
          <Box sx={{ flex: 1 }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {/* Document Info */}
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  mb: 3,
                  borderRadius: '12px',
                  border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
                  background: alpha(theme.palette.primary.main, 0.02),
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      background: personaInfo.gradient,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                    }}
                  >
                    <PersonaIcon sx={{ fontSize: 20, color: 'white' }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h2" sx={{ fontSize: '1.25rem', mb: 0.5 }}>
                      {summaryData.title}
                    </Typography>
                    <Chip
                      label={`${personaInfo.title} 관점`}
                      size="small"
                      sx={{
                        background: personaInfo.gradient,
                        color: 'white',
                        fontWeight: 500,
                      }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="요약 복사">
                      <IconButton onClick={handleCopy} size="small">
                        <CopyIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="공유">
                      <IconButton size="small">
                        <ShareIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    color: theme.palette.text.secondary,
                    wordBreak: 'break-all',
                  }}
                >
                  {summaryData.url}
                </Typography>
              </Paper>

              {/* Summary Content */}
              <Card
                elevation={0}
                sx={{
                  borderRadius: '12px',
                  border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box
                    sx={{
                      '& h2': {
                        fontSize: '1.25rem',
                        fontWeight: 600,
                        mt: 3,
                        mb: 1.5,
                        color: theme.palette.text.primary,
                        borderBottom: `2px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                        pb: 0.5,
                        '&:first-of-type': {
                          mt: 0,
                        },
                      },
                      '& h3': {
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        mt: 2.5,
                        mb: 1,
                        color: theme.palette.text.primary,
                      },
                      '& p': {
                        mb: 2,
                        lineHeight: 1.7,
                        fontSize: '1rem',
                      },
                      '& ul, & ol': {
                        mb: 2,
                        pl: 3,
                      },
                      '& li': {
                        mb: 0.5,
                        lineHeight: 1.6,
                      },
                      '& strong': { 
                        color: theme.palette.primary.main,
                        fontWeight: 600,
                      },
                      '& em': {
                        color: theme.palette.secondary.main,
                        fontStyle: 'italic',
                      },
                      '& code': {
                        backgroundColor: alpha(theme.palette.grey[500], 0.1),
                        padding: '2px 4px',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontFamily: 'monospace',
                      },
                      '& blockquote': {
                        borderLeft: `4px solid ${theme.palette.primary.main}`,
                        pl: 2,
                        ml: 0,
                        fontStyle: 'italic',
                        color: theme.palette.text.secondary,
                      },
                    }}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h2: ({ children }) => (
                          <Typography variant="h2" component="h2" sx={{ 
                            fontSize: '1.25rem', 
                            fontWeight: 600, 
                            mt: 3, 
                            mb: 1.5,
                            '&:first-of-type': { mt: 0 }
                          }}>
                            {children}
                          </Typography>
                        ),
                        h3: ({ children }) => (
                          <Typography variant="h3" component="h3" sx={{ 
                            fontSize: '1.1rem', 
                            fontWeight: 600, 
                            mt: 2.5, 
                            mb: 1 
                          }}>
                            {children}
                          </Typography>
                        ),
                        p: ({ children }) => (
                          <Typography variant="body1" component="p" sx={{ mb: 2, lineHeight: 1.7 }}>
                            {children}
                          </Typography>
                        ),
                      }}
                    >
                      {summaryData.summary}
                    </ReactMarkdown>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Box>

          {/* Sidebar */}
          <Box sx={{ width: { xs: '100%', lg: '300px' } }}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              {/* Feedback Section */}
              <Card
                elevation={0}
                sx={{
                  borderRadius: '12px',
                  border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
                  mb: 3,
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h3" sx={{ fontSize: '1.1rem', mb: 2, fontWeight: 500 }}>
                    이 요약이 도움이 되셨나요?
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Button
                      variant={feedback === 'positive' ? 'contained' : 'outlined'}
                      startIcon={<ThumbUpIcon />}
                      onClick={() => handleFeedback('positive')}
                      disabled={!!feedback}
                      size="small"
                      sx={{ flex: 1 }}
                    >
                      좋아요
                    </Button>
                    <Button
                      variant={feedback === 'negative' ? 'contained' : 'outlined'}
                      startIcon={<ThumbDownIcon />}
                      onClick={() => handleFeedback('negative')}
                      disabled={!!feedback}
                      size="small"
                      sx={{ flex: 1 }}
                      color="error"
                    >
                      별로예요
                    </Button>
                  </Box>

                  {feedbackMessage && (
                    <Typography
                      variant="body2"
                      sx={{
                        color: feedback === 'positive' 
                          ? theme.palette.success.main 
                          : theme.palette.text.secondary,
                        textAlign: 'center',
                        fontSize: '0.875rem',
                      }}
                    >
                      {feedbackMessage}
                    </Typography>
                  )}
                </CardContent>
              </Card>

              {/* Actions */}
              <Card
                elevation={0}
                sx={{
                  borderRadius: '12px',
                  border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h3" sx={{ fontSize: '1.1rem', mb: 2, fontWeight: 500 }}>
                    다른 작업
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={resetApp}
                      sx={{ justifyContent: 'flex-start' }}
                    >
                      🔄 새로운 문서 분석
                    </Button>
                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => window.open(summaryData.url, '_blank')}
                      sx={{ justifyContent: 'flex-start' }}
                    >
                      📄 원본 문서 열기
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Box>
      </Box>

      {/* Snackbars */}
      <Snackbar
        open={copySuccess}
        autoHideDuration={3000}
        onClose={() => setCopySuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={() => setCopySuccess(false)}>
          요약이 클립보드에 복사되었습니다! 📋
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default SummaryPage;