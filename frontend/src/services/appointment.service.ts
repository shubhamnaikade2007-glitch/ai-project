// HealthFit AI - Appointment Service
import api from './api';
import { Appointment, Doctor } from '../types';

const AppointmentService = {
  async getAppointments(params?: {
    status?: string; upcoming_only?: boolean; limit?: number;
  }) {
    const { data } = await api.get<{ appointments: Appointment[]; count: number }>('/appointments/', { params });
    return data;
  },

  async bookAppointment(payload: {
    doctor_id: number; appointment_date: string; appointment_time: string;
    type?: string; reason?: string; duration_min?: number;
  }) {
    const { data } = await api.post<{ appointment: Appointment; message: string }>('/appointments/', payload);
    return data;
  },

  async getAppointment(id: number) {
    const { data } = await api.get<{ appointment: Appointment }>(`/appointments/${id}`);
    return data;
  },

  async updateAppointment(id: number, payload: Partial<Appointment>) {
    const { data } = await api.put<{ appointment: Appointment; message: string }>(`/appointments/${id}`, payload);
    return data;
  },

  async cancelAppointment(id: number): Promise<void> {
    await api.delete(`/appointments/${id}`);
  },

  async getDoctors(specialization?: string) {
    const { data } = await api.get<{ doctors: Doctor[]; count: number }>('/appointments/doctors', {
      params: specialization ? { specialization } : undefined,
    });
    return data;
  },

  async getAvailableSlots(doctor_id: number, date: string) {
    const { data } = await api.get<{ date: string; available: string[]; booked: string[] }>(
      '/appointments/available-slots',
      { params: { doctor_id, date } }
    );
    return data;
  },
};

export default AppointmentService;
