import { getJson, ApiError } from '../api/client';
import type { Dto } from '../api/types';
export async function loadCatalog(signal?: AbortSignal, read = getJson): Promise<Dto<'CatalogResponse'>> {
  for (let attempt = 0; attempt < 3; attempt++) {
    let first: Dto<'CatalogResponse'> | undefined;
    const items: Dto<'CatalogItem'>[] = [];
    let offset = '0';
    try {
      do {
        const page = await read('CatalogResponse', '/monitoring/catalog', { offset, limit: 100, ...(first ? { catalog_revision: first.catalog_revision } : {}) }, signal ? { signal } : {});
        if (first && (first.service_instance_id !== page.service_instance_id || first.catalog_revision !== page.catalog_revision || first.total !== page.total)) throw new ApiError(409, 'CATALOG_REVISION_CHANGED', '目录版本已变化');
        first ??= page;
        if (page.offset !== offset || page.items.length > page.limit) throw new Error('INVALID_CATALOG_PAGE');
        items.push(...page.items);
        if (page.next_offset !== null && (page.items.length === 0 || BigInt(page.next_offset) !== BigInt(offset) + BigInt(page.items.length))) throw new Error('INVALID_CATALOG_OFFSET');
        offset = page.next_offset ?? '';
      } while (offset);
      if (BigInt(items.length) !== BigInt(first!.total)) throw new Error('INCOMPLETE_CATALOG');
      const keys = new Set(items.map(item => JSON.stringify([item.appid, item.model_id])));
      if (keys.size !== items.length) throw new Error('DUPLICATE_CATALOG_GROUP');
      // The first cursor is safe even when failed events arrive during pagination.
      return { ...first!, items, offset: '0', next_offset: null };
    } catch (error) {
      if (!(error instanceof ApiError && error.code === 'CATALOG_REVISION_CHANGED') || attempt === 2) throw error;
    }
  }
  throw new Error('CATALOG_UNSTABLE');
}
