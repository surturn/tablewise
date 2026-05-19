import { apiClient } from '../api/client';

const DB_NAME = 'grandplatform-offline';
const STORE = 'orders';

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(STORE);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function idbSet(key: string, value: unknown) {
  const db = await openDb();
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    tx.objectStore(STORE).put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function idbGet<T>(key: string): Promise<T | undefined> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly');
    const req = tx.objectStore(STORE).get(key);
    req.onsuccess = () => resolve(req.result as T | undefined);
    req.onerror = () => reject(req.error);
  });
}

async function idbDel(key: string) {
  const db = await openDb();
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    tx.objectStore(STORE).delete(key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

const QUEUE_KEY = 'queued-order';

export async function queueOrderWhenOffline(payload: unknown) {
  await idbSet(QUEUE_KEY, payload);
}

export async function flushQueuedOrder(showToast: (message: string) => void = window.alert) {
  const payload = await idbGet(QUEUE_KEY);
  if (!payload || !navigator.onLine) return;
  try {
    await apiClient.post('/orders/', payload);
    await idbDel(QUEUE_KEY);
    showToast('Queued GrandPlatform order was submitted after reconnecting.');
  } catch (error) {
    console.error('Unable to flush queued order', error);
  }
}

window.addEventListener('online', () => {
  void flushQueuedOrder();
});
