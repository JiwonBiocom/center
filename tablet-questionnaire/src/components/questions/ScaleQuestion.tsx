import React from 'react';
import {View, StyleSheet} from 'react-native';
import {Text} from 'react-native-paper';
import Slider from '@react-native-community/slider';
import {theme} from '../../theme';
import type {Question} from '../../types/questionnaire';

interface ScaleQuestionProps {
  question: Question;
  value: number | null;
  onChange: (value: number) => void;
}

const ScaleQuestion: React.FC<ScaleQuestionProps> = ({
  question,
  value,
  onChange,
}) => {
  const min = question.validation_rules?.min ?? 0;
  const max = question.validation_rules?.max ?? 10;
  const currentValue = value ?? min;

  const getScaleLabel = (value: number): string => {
    const percentage = (value - min) / (max - min);
    
    if (percentage === 0) return '매우 나쁨';
    if (percentage <= 0.2) return '나쁨';
    if (percentage <= 0.4) return '보통 이하';
    if (percentage <= 0.6) return '보통';
    if (percentage <= 0.8) return '좋음';
    return '매우 좋음';
  };

  const getScaleColor = (value: number): string => {
    const percentage = (value - min) / (max - min);
    
    if (percentage <= 0.3) return '#EF4444'; // Red
    if (percentage <= 0.6) return '#F59E0B'; // Amber
    return '#10B981'; // Green
  };

  return (
    <View style={styles.container}>
      <Text style={styles.questionText}>{question.question_text}</Text>
      {question.question_subtext && (
        <Text style={styles.subText}>{question.question_subtext}</Text>
      )}
      
      <View style={styles.sliderContainer}>
        <View style={styles.valueContainer}>
          <Text style={[styles.valueText, {color: getScaleColor(currentValue)}]}>
            {currentValue}
          </Text>
          <Text style={styles.valueLabel}>{getScaleLabel(currentValue)}</Text>
        </View>
        
        <Slider
          style={styles.slider}
          minimumValue={min}
          maximumValue={max}
          step={1}
          value={currentValue}
          onValueChange={onChange}
          minimumTrackTintColor={getScaleColor(currentValue)}
          maximumTrackTintColor="#E5E7EB"
          thumbTintColor={theme.colors.primary}
        />
        
        <View style={styles.labelsContainer}>
          <Text style={styles.labelText}>{min}</Text>
          <Text style={styles.labelText}>{max}</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 24,
  },
  questionText: {
    fontSize: 20,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
    lineHeight: 28,
  },
  subText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginBottom: 32,
    lineHeight: 22,
  },
  sliderContainer: {
    paddingHorizontal: 16,
  },
  valueContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  valueText: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  valueLabel: {
    fontSize: 18,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
  slider: {
    height: 60,
    marginVertical: 16,
  },
  labelsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 8,
  },
  labelText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
});

export default ScaleQuestion;