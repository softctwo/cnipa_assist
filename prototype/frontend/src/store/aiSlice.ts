import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AIMessage {
  id: string;
  content: string;
}

interface AIState {
  messages: AIMessage[];
}

const initialState: AIState = {
  messages: []
};

const aiSlice = createSlice({
  name: 'ai',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<AIMessage>) => {
      state.messages.push(action.payload);
    }
  }
});

export const { addMessage } = aiSlice.actions;
export default aiSlice.reducer;
