import {configureStore} from '@reduxjs/toolkit';
import questionnaireReducer from './slices/questionnaireSlice';
import authReducer from './slices/authSlice';
import syncReducer from './slices/syncSlice';
import inbodyReducer from './slices/inbodySlice';

export const store = configureStore({
  reducer: {
    questionnaire: questionnaireReducer,
    auth: authReducer,
    sync: syncReducer,
    inbody: inbodyReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['questionnaire/setAnswerTimestamp'],
        ignoredPaths: ['questionnaire.currentAnswer.timestamp'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;