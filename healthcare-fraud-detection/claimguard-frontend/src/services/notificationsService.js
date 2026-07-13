import api, { USE_MOCK, mockDelay } from './api';
import { mockNotifications } from './mockData';

let store = [...mockNotifications];

export async function getNotifications() {
  if (USE_MOCK) return mockDelay([...store], 350);
  const { data } = await api.get('/notifications');
  return data;
}

export async function markAsRead(id) {
  if (USE_MOCK) {
    store = store.map((n) => (n.id === id ? { ...n, read: true } : n));
    return mockDelay(store, 200);
  }
  const { data } = await api.patch(`/notifications/${id}/read`);
  return data;
}

export async function deleteNotification(id) {
  if (USE_MOCK) {
    store = store.filter((n) => n.id !== id);
    return mockDelay(store, 200);
  }
  const { data } = await api.delete(`/notifications/${id}`);
  return data;
}
