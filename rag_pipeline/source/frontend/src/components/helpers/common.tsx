import type { Method } from "./types";

export type Result<T = unknown> = {
  data: T | null;
  error: string | null;
  notAuthenticated: boolean | null;
};

type QueryParams = Record<
  string,
  string | number | boolean | string[] | number[] | boolean[]
>;

type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export const requestServer = async <T = unknown,>(
  url: string,
  options: {
    method: Method;
    body?: QueryParams | FormData | JsonValue; // placeholder body placeholder query
    token?: string | null; // bearer placeholder
  },
): Promise<Result<T>> => {
  const headers: HeadersInit = {};

  // Bearer token
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  let body: BodyInit | undefined = undefined;

  let finalUrl = url;

  if (options.body !== undefined) {
    if (options.method === "GET") {
      // restored comment from original Russian source
      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(options.body as QueryParams)) {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      }
      finalUrl += `?${params.toString()}`;
    } else {
      // restored comment from original Russian source
      if (options.body instanceof FormData) {
        body = options.body; // Content-Type placeholder
      } else {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(options.body);
      }
    }
  }

  const response = await fetch(finalUrl, {
    method: options.method,
    headers,
    body,
  });

  const data = await response.json().catch(() => null);

  if (response.ok) {
    return {
      data,
      error: null,
      notAuthenticated: false,
    };
  }

  if (response.status === 401) {
    return {
      data: null,
      error: data?.detail ?? "Unauthorized",
      notAuthenticated: true,
    };
  }

  // restored comment from original Russian source
  const error = data?.detail ?? "Unknown error";

  return {
    data: null,
    error: typeof error === "object" ? JSON.stringify(error) : String(error),
    notAuthenticated: false,
  };
};

export const formatDate = (iso: string) => {
  const date = new Date(iso);

  const day = String(date.getDate()).padStart(2, "0");
  const month = date.toLocaleString("en-US", { month: "short" }).toLowerCase();
  const year = String(date.getFullYear());

  return `${day}-${month}-${year}`;
};

export const scrollToTopInstant = () => {
  document.documentElement.style.scrollBehavior = "auto";
  window.scrollTo(0, 0);

  // restored comment from original Russian source
  document.documentElement.style.scrollBehavior = "";
};

export const isDeepEqual = (
  a: Record<string, unknown>,
  b: Record<string, unknown>,
): boolean => {
  return JSON.stringify(a) === JSON.stringify(b);
};

export const renderJsonCodeBlock = (jsonObj: unknown) => (
  <pre className="mb-0">
    <code>{JSON.stringify(jsonObj, null, 2)}</code>
  </pre>
);
