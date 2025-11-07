import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';

// Redux store setup
const store = configureStore({
  reducer: {
    auth: authReducer,
    // ... baaki reducers (agar hain)
  },
});

export default store;