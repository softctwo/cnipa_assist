import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ExaminationRecord {
  id: number;
  status: string;
  note?: string;
}

interface ExaminationState {
  records: ExaminationRecord[];
}

const initialState: ExaminationState = {
  records: []
};

const examinationSlice = createSlice({
  name: 'examination',
  initialState,
  reducers: {
    addRecord: (state, action: PayloadAction<ExaminationRecord>) => {
      state.records.push(action.payload);
    }
  }
});

export const { addRecord } = examinationSlice.actions;
export default examinationSlice.reducer;
