import { apiClient } from './client';

export interface SearchResultItem {
  title: string;
  url: string;
  snippet: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
}

class SearchApi {
  async search(query: string, maxResults: number = 10): Promise<SearchResponse> {
    return await apiClient.post<SearchResponse>('/search', {
      query,
      max_results: maxResults,
    });
  }
}

export const searchApi = new SearchApi();
export default SearchApi;
