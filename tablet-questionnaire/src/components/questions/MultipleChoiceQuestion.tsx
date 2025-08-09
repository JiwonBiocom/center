import React from 'react';
import {View, StyleSheet, TouchableOpacity} from 'react-native';
import {Text, Checkbox} from 'react-native-paper';
import {theme} from '../../theme';
import type {Question, QuestionOption} from '../../types/questionnaire';

interface MultipleChoiceQuestionProps {
  question: Question;
  value: string[] | null;
  onChange: (value: string[]) => void;
}

const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
  question,
  value,
  onChange,
}) => {
  const currentValues = value || [];
  const maxSelections = question.validation_rules?.maxSelections;

  const handleToggle = (optionValue: string) => {
    if (currentValues.includes(optionValue)) {
      onChange(currentValues.filter(v => v !== optionValue));
    } else {
      if (maxSelections && currentValues.length >= maxSelections) {
        // 최대 선택 수에 도달한 경우
        return;
      }
      onChange([...currentValues, optionValue]);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.questionText}>{question.question_text}</Text>
      {question.question_subtext && (
        <Text style={styles.subText}>{question.question_subtext}</Text>
      )}
      {maxSelections && (
        <Text style={styles.limitText}>
          최대 {maxSelections}개 선택 가능 ({currentValues.length}/{maxSelections})
        </Text>
      )}
      
      <View style={styles.optionsContainer}>
        {question.options?.map((option: QuestionOption) => {
          const isSelected = currentValues.includes(option.value);
          const isDisabled = !isSelected && maxSelections !== undefined && 
                           currentValues.length >= maxSelections;
          
          return (
            <TouchableOpacity
              key={option.value}
              style={[
                styles.optionItem,
                isSelected && styles.selectedOption,
                isDisabled && styles.disabledOption,
              ]}
              onPress={() => !isDisabled && handleToggle(option.value)}
              disabled={isDisabled}>
              <Checkbox
                status={isSelected ? 'checked' : 'unchecked'}
                onPress={() => !isDisabled && handleToggle(option.value)}
                color={theme.colors.primary}
                disabled={isDisabled}
              />
              <Text
                style={[
                  styles.optionLabel,
                  isSelected && styles.selectedLabel,
                  isDisabled && styles.disabledLabel,
                ]}>
                {option.label}
              </Text>
            </TouchableOpacity>
          );
        })}
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
    marginBottom: 16,
    lineHeight: 22,
  },
  limitText: {
    fontSize: 14,
    color: theme.colors.primary,
    marginBottom: 16,
    fontWeight: '500',
  },
  optionsContainer: {
    gap: 12,
  },
  optionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: theme.colors.border,
    backgroundColor: '#FFFFFF',
  },
  selectedOption: {
    borderColor: theme.colors.primary,
    backgroundColor: '#F0F4FF',
  },
  disabledOption: {
    opacity: 0.5,
  },
  optionLabel: {
    flex: 1,
    fontSize: 18,
    color: theme.colors.text,
    marginLeft: 8,
  },
  selectedLabel: {
    color: theme.colors.primary,
    fontWeight: '500',
  },
  disabledLabel: {
    color: theme.colors.textSecondary,
  },
});

export default MultipleChoiceQuestion;