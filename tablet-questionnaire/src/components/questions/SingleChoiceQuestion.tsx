import React from 'react';
import {View, StyleSheet, TouchableOpacity} from 'react-native';
import {Text, RadioButton} from 'react-native-paper';
import {theme} from '../../theme';
import type {Question, QuestionOption} from '../../types/questionnaire';

interface SingleChoiceQuestionProps {
  question: Question;
  value: string | null;
  onChange: (value: string) => void;
}

const SingleChoiceQuestion: React.FC<SingleChoiceQuestionProps> = ({
  question,
  value,
  onChange,
}) => {
  return (
    <View style={styles.container}>
      <Text style={styles.questionText}>{question.question_text}</Text>
      {question.question_subtext && (
        <Text style={styles.subText}>{question.question_subtext}</Text>
      )}
      
      <View style={styles.optionsContainer}>
        {question.options?.map((option: QuestionOption) => (
          <TouchableOpacity
            key={option.value}
            style={[
              styles.optionItem,
              value === option.value && styles.selectedOption,
            ]}
            onPress={() => onChange(option.value)}>
            <RadioButton
              value={option.value}
              status={value === option.value ? 'checked' : 'unchecked'}
              onPress={() => onChange(option.value)}
              color={theme.colors.primary}
            />
            <Text
              style={[
                styles.optionLabel,
                value === option.value && styles.selectedLabel,
              ]}>
              {option.label}
            </Text>
          </TouchableOpacity>
        ))}
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
    marginBottom: 24,
    lineHeight: 22,
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
});

export default SingleChoiceQuestion;