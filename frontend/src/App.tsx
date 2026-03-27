// HealthFit AI - Root Application Component
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { fetchCurrentUserThunk } from './store/slices/authSlice';
import { AppDispatch } from './store/store';
import { useAuth } from './hooks/useAuth';

import Layout        from './components/Layout';
import PrivateRoute  from './components/PrivateRoute';
import Login         from './pages/Login';
import Dashboard     from './pages/Dashboard';
import HealthPage    from './pages/HealthPage';
import AppointmentsPage from './pages/AppointmentsPage';
import NutritionPage from './pages/NutritionPage';
import FitnessPage   from './pages/FitnessPage';
import AIInsightsPage from './pages/AIInsightsPage';
import ProfilePage   from './pages/ProfilePage';

const App: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { isAuthenticated } = useAuth();

  // Refresh user data on app load if we have a token
  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchCurrentUserThunk());
    }
  }, [dispatch, isAuthenticated]);

  return (
<BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
        } />

        {/* Protected routes wrapped in Layout */}
        <Route path="/" element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"    element={<Dashboard />} />
          <Route path="health"       element={<HealthPage />} />
          <Route path="appointments" element={<AppointmentsPage />} />
          <Route path="nutrition"    element={<NutritionPage />} />
          <Route path="fitness"      element={<FitnessPage />} />
          <Route path="ai-insights"  element={<AIInsightsPage />} />
          <Route path="profile"      element={<ProfilePage />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
