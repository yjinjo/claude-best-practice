import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Code as DeveloperIcon,
  Business as ProductManagerIcon,
  Palette as DesignerIcon,
  Description as GeneralIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

import { PersonaType } from '../context/AppContext';

interface PersonaSelectorProps {
  onPersonaSelect: (persona: PersonaType) => void;
}

const personas = [
  {
    id: 'general' as PersonaType,
    title: '일반',
    description: '모든 직군이 이해할 수 있는 핵심 내용 중심으로 요약',
    icon: GeneralIcon,
    color: '#6c757d',
    gradient: 'linear-gradient(135deg, #6c757d, #495057)',
  },
  {
    id: 'developer' as PersonaType,
    title: '개발자',
    description: '기술적 요구사항, 구현 사항, API 명세 중심으로 요약',
    icon: DeveloperIcon,
    color: '#4285f4',
    gradient: 'linear-gradient(135deg, #4285f4, #34a853)',
  },
  {
    id: 'product_manager' as PersonaType,
    title: '기획자',
    description: '비즈니스 목표, 일정, 의사결정 포인트 중심으로 요약',
    icon: ProductManagerIcon,
    color: '#ea4335',
    gradient: 'linear-gradient(135deg, #ea4335, #fbbc04)',
  },
  {
    id: 'designer' as PersonaType,
    title: '디자이너',
    description: '사용자 경험, 디자인 요구사항, UI/UX 중심으로 요약',
    icon: DesignerIcon,
    color: '#34a853',
    gradient: 'linear-gradient(135deg, #34a853, #4285f4)',
  },
];

const PersonaSelector: React.FC<PersonaSelectorProps> = ({ onPersonaSelect }) => {
  const theme = useTheme();

  return (
    <Box sx={{ mt: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography
          variant="h2"
          component="h2"
          sx={{
            fontSize: '1.5rem',
            fontWeight: 400,
            textAlign: 'center',
            mb: 1,
            color: theme.palette.text.primary,
          }}
        >
          어떤 관점에서 요약해드릴까요?
        </Typography>
        <Typography
          variant="body2"
          sx={{
            textAlign: 'center',
            color: theme.palette.text.secondary,
            mb: 3,
          }}
        >
          역할에 맞는 맞춤형 요약을 제공합니다
        </Typography>
      </motion.div>

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, 
        gap: 3,
      }}>
        {personas.map((persona, index) => {
          const IconComponent = persona.icon;
          
          return (
            <Box key={persona.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => onPersonaSelect(persona.id)}
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    borderRadius: '16px',
                    border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                      transform: 'translateY(-2px)',
                      borderColor: alpha(persona.color, 0.3),
                    },
                    '&:active': {
                      transform: 'translateY(0)',
                    },
                  }}
                >
                  <CardContent
                    sx={{
                      p: 3,
                      textAlign: 'center',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Box>
                      <Box
                        sx={{
                          width: 64,
                          height: 64,
                          mx: 'auto',
                          mb: 2,
                          borderRadius: '50%',
                          background: persona.gradient,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: `0 4px 12px ${alpha(persona.color, 0.3)}`,
                        }}
                      >
                        <IconComponent
                          sx={{
                            fontSize: 32,
                            color: 'white',
                          }}
                        />
                      </Box>

                      <Typography
                        variant="h3"
                        component="h3"
                        sx={{
                          fontSize: '1.25rem',
                          fontWeight: 500,
                          mb: 2,
                          color: theme.palette.text.primary,
                        }}
                      >
                        {persona.title}
                      </Typography>
                    </Box>

                    <Typography
                      variant="body2"
                      sx={{
                        color: theme.palette.text.secondary,
                        lineHeight: 1.5,
                        fontSize: '0.875rem',
                      }}
                    >
                      {persona.description}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Box>
          );
        })}
      </Box>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Typography
          variant="body2"
          sx={{
            textAlign: 'center',
            color: theme.palette.text.secondary,
            mt: 3,
            fontSize: '0.75rem',
          }}
        >
          💡 각 역할에 맞는 핵심 정보만 추출하여 제공합니다
        </Typography>
      </motion.div>
    </Box>
  );
};

export default PersonaSelector;