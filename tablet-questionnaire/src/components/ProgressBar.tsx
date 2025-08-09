import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import {ProgressBar as PaperProgressBar} from 'react-native-paper';
import {theme} from '../theme';

interface ProgressBarProps {
  current: number;
  total: number;
  estimatedTime?: number; // seconds
  section?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  current,
  total,
  estimatedTime,
  section,
}) => {
  const progress = total > 0 ? current / total : 0;
  const percentage = Math.round(progress * 100);

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    if (minutes === 0) return '1분 미만';
    return `약 ${minutes}분`;
  };

  const getSectionLabel = (section?: string): string => {
    const sectionLabels: {[key: string]: string} = {
      basic: '기본 정보',
      health_status: '건강 상태',
      goals: '목표 설정',
      stress_mental: '스트레스/정신건강',
      digestive: '소화기 건강',
      hormone: '호르몬/대사',
      musculoskeletal: '근골격계',
    };
    return section ? sectionLabels[section] || section : '';
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.sectionText}>
          {section && getSectionLabel(section)}
        </Text>
        <Text style={styles.progressText}>
          {current} / {total} ({percentage}%)
        </Text>
      </View>
      
      <PaperProgressBar
        progress={progress}
        color={theme.colors.primary}
        style={styles.progressBar}
      />
      
      {estimatedTime !== undefined && estimatedTime > 0 && (
        <Text style={styles.timeText}>
          남은 시간: {formatTime(estimatedTime)}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 24,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  progressText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
  },
  timeText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 8,
    textAlign: 'right',
  },
});

export default ProgressBar;