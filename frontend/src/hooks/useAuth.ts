// HealthFit AI - useAuth Hook
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { loginThunk, logoutThunk, registerThunk, clearError } from '../store/slices/authSlice';
import { LoginPayload, RegisterPayload } from '../services/auth.service';

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user, token, isAuthenticated, loading, error } = useSelector((s: RootState) => s.auth);

  return {
    user, token, isAuthenticated, loading, error,
    login:      (p: LoginPayload)    => dispatch(loginThunk(p)),
    register:   (p: RegisterPayload) => dispatch(registerThunk(p)),
    logout:     ()                   => dispatch(logoutThunk()),
    clearError: ()                   => dispatch(clearError()),
  };
};
