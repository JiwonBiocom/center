import {createSlice, PayloadAction} from '@reduxjs/toolkit';

export interface InBodyData {
  weight?: number;
  height?: number;
  body_fat_percentage?: number;
  skeletal_muscle_mass?: number;
  extracellular_water_ratio?: number;
  phase_angle?: number;
  visceral_fat_level?: number;
  measurement_date?: string;
  is_manual_input: boolean;
}

interface InBodyState {
  currentData: InBodyData | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: InBodyState = {
  currentData: null,
  isConnected: false,
  isLoading: false,
  error: null,
};

const inbodySlice = createSlice({
  name: 'inbody',
  initialState,
  reducers: {
    setInBodyData: (state, action: PayloadAction<InBodyData>) => {
      state.currentData = action.payload;
      state.error = null;
    },
    setManualData: (state, action: PayloadAction<Partial<InBodyData>>) => {
      state.currentData = {
        ...state.currentData,
        ...action.payload,
        is_manual_input: true,
        measurement_date: new Date().toISOString(),
      };
    },
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    resetInBody: (state) => {
      return initialState;
    },
  },
});

export const {
  setInBodyData,
  setManualData,
  setConnected,
  setLoading,
  setError,
  resetInBody,
} = inbodySlice.actions;

export default inbodySlice.reducer;