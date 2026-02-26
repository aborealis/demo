export const Method = {
  GET: "GET",
  POST: "POST",
  PATCH: "PATCH",
  DELETE: "DELETE",
};

export const SearchType = {
  keyword: "Keyword Search",
  context: "Context Search",
};

export type Method = (typeof Method)[keyof typeof Method];
export type SearchType = (typeof SearchType)[keyof typeof SearchType];

export type RequestOptions = {
  method: Method;
  body?: Record<string, string | number | boolean>;
  token?: string | null;
};

export type OneDocType = {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  updated_by: string;
  content: string;
  status: string;
};

export type DocsServerType = {
  total_count: number;
  offset: number;
  documents: OneDocType[];
};

export type DocProgress = Record<number, { progress: number }>;
