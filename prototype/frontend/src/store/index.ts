/**
 * Redux Store配置
 */
import { configureStore } from '@reduxjs/toolkit';
import documentsReducer from './documentsSlice';
import examinationReducer from './examinationSlice';
import aiReducer from './aiSlice';

export const store = configureStore({
  reducer: {
    documents: documentsReducer,
    examination: examinationReducer,
    ai: aiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;