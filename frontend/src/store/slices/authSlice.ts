// HealthFit AI - Auth Redux Slice
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import AuthService, { LoginPayload, RegisterPayload } from '../../services/auth.service';
import { AuthState, User } from '../../types';

const initialState: AuthState = {
  user:            AuthService.getStoredUser(),
  token:           AuthService.getToken(),
  isAuthenticated: AuthService.isAuthenticated(),
  loading:         false,
  error:           null,
};

// ── Async thunks ───────────────────────────────────────────

export const loginThunk = createAsyncThunk(
  'auth/login',
  async (payload: LoginPayload, { rejectWithValue }) => {
    try {
      return await AuthService.login(payload);
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error || 'Login failed');
    }
  }
);

export const registerThunk = createAsyncThunk(
  'auth/register',
  async (payload: RegisterPayload, { rejectWithValue }) => {
    try {
      return await AuthService.register(payload);
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error || 'Registration failed');
    }
  }
);

export const logoutThunk = createAsyncThunk('auth/logout', async () => {
  await AuthService.logout();
});

export const fetchCurrentUserThunk = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      return await AuthService.getCurrentUser();
    } catch (err: any) {
      return rejectWithValue('Session expired');
    }
  }
);

// ── Slice ──────────────────────────────────────────────────

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError(state) {
      state.error = null;
    },
    setUser(state, action: PayloadAction<User>) {
      state.user = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginThunk.pending, (state) => {
        state.loading = true; state.error = null;
      })
      .addCase(loginThunk.fulfilled, (state, { payload }) => {
        state.loading = false;
        state.user    = payload.user;
        state.token   = payload.access_token;
        state.isAuthenticated = true;
      })
      .addCase(loginThunk.rejected, (state, { payload }) => {
        state.loading = false;
        state.error   = payload as string;
      });

    // Register
    builder
      .addCase(registerThunk.pending, (state) => {
        state.loading = true; state.error = null;
      })
      .addCase(registerThunk.fulfilled, (state, { payload }) => {
        state.loading = false;
        state.user    = payload.user;
        state.token   = payload.access_token;
        state.isAuthenticated = true;
      })
      .addCase(registerThunk.rejected, (state, { payload }) => {
        state.loading = false;
        state.error   = payload as string;
      });

    // Logout
    builder.addCase(logoutThunk.fulfilled, (state) => {
      state.user = null; state.token = null; state.isAuthenticated = false;
    });

    // Fetch user
    builder
      .addCase(fetchCurrentUserThunk.fulfilled, (state, { payload }) => {
        state.user = payload;
      })
      .addCase(fetchCurrentUserThunk.rejected, (state) => {
        state.user = null; state.token = null; state.isAuthenticated = false;
      });
  },
});

export const { clearError, setUser } = authSlice.actions;
export default authSlice.reducer;
