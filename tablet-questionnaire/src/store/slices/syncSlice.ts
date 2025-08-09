import {createSlice, PayloadAction} from '@reduxjs/toolkit';

interface SyncState {
  pendingSync: number;
  lastSyncTime: string | null;
  isSyncing: boolean;
  syncError: string | null;
  isOffline: boolean;
}

const initialState: SyncState = {
  pendingSync: 0,
  lastSyncTime: null,
  isSyncing: false,
  syncError: null,
  isOffline: false,
};

const syncSlice = createSlice({
  name: 'sync',
  initialState,
  reducers: {
    setPendingSync: (state, action: PayloadAction<number>) => {
      state.pendingSync = action.payload;
    },
    incrementPendingSync: (state) => {
      state.pendingSync += 1;
    },
    decrementPendingSync: (state) => {
      if (state.pendingSync > 0) {
        state.pendingSync -= 1;
      }
    },
    setSyncing: (state, action: PayloadAction<boolean>) => {
      state.isSyncing = action.payload;
      if (!action.payload) {
        state.lastSyncTime = new Date().toISOString();
      }
    },
    setSyncError: (state, action: PayloadAction<string | null>) => {
      state.syncError = action.payload;
    },
    setOffline: (state, action: PayloadAction<boolean>) => {
      state.isOffline = action.payload;
    },
  },
});

export const {
  setPendingSync,
  incrementPendingSync,
  decrementPendingSync,
  setSyncing,
  setSyncError,
  setOffline,
} = syncSlice.actions;

export default syncSlice.reducer;