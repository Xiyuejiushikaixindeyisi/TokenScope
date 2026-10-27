export interface StoredSnapshot { key: string; raw: string; etag: string; bytes: number; touched: number }
/** This database contains results only. It never creates/deletes receipt storage. */
export function openSnapshotDb(factory: IDBFactory = indexedDB): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = factory.open('tokenscope-viewer-snapshots-v1', 1);
    request.onupgradeneeded = () => { request.result.createObjectStore('snapshots', { keyPath: 'key' }); };
    request.onerror = () => reject(request.error);
    request.onblocked = () => reject(new Error('CACHE_DB_BLOCKED'));
    request.onsuccess = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains('snapshots')) { db.close(); reject(new Error('CACHE_SCHEMA_INVALID')); return; }
      db.onversionchange = () => db.close(); resolve(db);
    };
  });
}
export async function diskGet(db: IDBDatabase, key: string): Promise<StoredSnapshot | undefined> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('snapshots', 'readonly');
    const request = tx.objectStore('snapshots').get(key);
    tx.oncomplete = () => resolve(request.result as StoredSnapshot | undefined);
    tx.onabort = () => reject(tx.error);
    tx.onerror = () => reject(tx.error);
  });
}
export async function diskPut(db: IDBDatabase, record: StoredSnapshot, budget: number, protectedKey: string | null): Promise<void> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('snapshots', 'readwrite');
    const store = tx.objectStore('snapshots');
    store.put(record);
    const all = store.getAll();
    all.onsuccess = () => {
      const rows = all.result as StoredSnapshot[];
      let total = rows.reduce((sum, row) => sum + row.bytes, 0);
      for (const row of rows.sort((a, b) => a.touched - b.touched)) {
        if (total <= budget) break;
        if (row.key === protectedKey) continue;
        store.delete(row.key); total -= row.bytes;
      }
    };
    tx.oncomplete = () => resolve(); tx.onerror = () => reject(tx.error); tx.onabort = () => reject(tx.error);
  });
}
