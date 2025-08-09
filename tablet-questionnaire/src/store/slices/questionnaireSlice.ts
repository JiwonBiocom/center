import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import type {
  QuestionnaireTemplate,
  QuestionnaireResponse,
  Question,
  Answer,
  QuestionnaireProgress,
} from '../../types/questionnaire';

interface QuestionnaireState {
  currentTemplate: QuestionnaireTemplate | null;
  currentResponse: QuestionnaireResponse | null;
  currentQuestion: Question | null;
  progress: QuestionnaireProgress | null;
  answers: {[questionId: number]: Answer};
  isLoading: boolean;
  error: string | null;
  questionStartTime: number | null;
}

const initialState: QuestionnaireState = {
  currentTemplate: null,
  currentResponse: null,
  currentQuestion: null,
  progress: null,
  answers: {},
  isLoading: false,
  error: null,
  questionStartTime: null,
};

const questionnaireSlice = createSlice({
  name: 'questionnaire',
  initialState,
  reducers: {
    setTemplate: (state, action: PayloadAction<QuestionnaireTemplate>) => {
      state.currentTemplate = action.payload;
    },
    setResponse: (state, action: PayloadAction<QuestionnaireResponse>) => {
      state.currentResponse = action.payload;
      // 기존 답변 로드
      action.payload.answers.forEach(answer => {
        state.answers[answer.question_id] = answer;
      });
    },
    setCurrentQuestion: (state, action: PayloadAction<Question>) => {
      state.currentQuestion = action.payload;
      state.questionStartTime = Date.now();
    },
    setProgress: (state, action: PayloadAction<QuestionnaireProgress>) => {
      state.progress = action.payload;
    },
    saveAnswer: (state, action: PayloadAction<{questionId: number; answer: Answer}>) => {
      const {questionId, answer} = action.payload;
      if (state.questionStartTime) {
        answer.time_spent_seconds = Math.floor((Date.now() - state.questionStartTime) / 1000);
      }
      state.answers[questionId] = answer;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    resetQuestionnaire: (state) => {
      return initialState;
    },
  },
});

export const {
  setTemplate,
  setResponse,
  setCurrentQuestion,
  setProgress,
  saveAnswer,
  setLoading,
  setError,
  resetQuestionnaire,
} = questionnaireSlice.actions;

export default questionnaireSlice.reducer;