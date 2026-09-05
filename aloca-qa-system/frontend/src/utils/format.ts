// Query String Helper Functions
// Utility functions for building, parsing, and formatting query strings

export interface QueryParams {
  [key: string]: string | number | boolean | string[] | undefined;
}

export function buildQueryString(params: QueryParams): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) return;

    if (Array.isArray(value)) {
      value.forEach(v => searchParams.append(key, String(v)));
    } else {
      searchParams.set(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

export function parseQueryString(search: string): QueryParams {
  const params: QueryParams = {};
  const searchParams = new URLSearchParams(search);

  searchParams.forEach((value, key) => {
    if (params[key]) {
      if (Array.isArray(params[key])) {
        (params[key] as string[]).push(value);
      } else {
        params[key] = [params[key] as string, value];
      }
    } else {
      params[key] = value;
    }
  });

  return params;
}

export function getQueryParam(search: string, key: string): string | null {
  const params = new URLSearchParams(search);
  return params.get(key);
}

export function updateQueryParam(search: string, key: string, value: string): string {
  const params = new URLSearchParams(search);
  params.set(key, value);
  return `?${params.toString()}`;
}

export function removeQueryParam(search: string, key: string): string {
  const params = new URLSearchParams(search);
  params.delete(key);
  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

export function formatAPIUrl(
  baseURL: string,
  endpoint: string,
  filters?: QueryParams
): string {
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const query = filters ? buildQueryString(filters) : '';
  return `${baseURL}${path}${query}`;
}

export function buildFilterQuery(filters: {
  status?: string;
  severity?: string;
  module?: string;
  search?: string;
}): QueryParams {
  const params: QueryParams = {};

  if (filters.status) params.status = filters.status;
  if (filters.severity) params.severity = filters.severity;
  if (filters.module) params.module = filters.module;
  if (filters.search) params.search = filters.search;

  return params;
}

export function encodePath(path: string): string {
  return encodeURIComponent(path);
}

export function decodePath(path: string): string {
  return decodeURIComponent(path);
}

export default {
  buildQueryString,
  parseQueryString,
  getQueryParam,
  updateQueryParam,
  removeQueryParam,
  formatAPIUrl,
  buildFilterQuery,
  encodePath,
  decodePath,
};
