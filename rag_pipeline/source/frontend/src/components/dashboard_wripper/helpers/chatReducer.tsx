import type { ReactNode } from "react";

export type ChatState = {
  spentTokens: number;
  messages: ReactNode[];
  wsURL: string;
};

export const chatInitState = {
  spentTokens: 0,
  messages: [],
  wsURL: "",
};

export type ChatAction =
  | { type: "SET_SPENT_TOKENS"; tokens: number }
  | { type: "ADD_SPENT_TOKENS"; tokens: number }
  | { type: "SET_MESSAGES"; messages: ReactNode[] }
  | { type: "ADD_MESSAGE"; message: ReactNode }
  | { type: "SET_WS_URL"; url: string };

export const chatReducer = (
  state: ChatState,
  action: ChatAction,
): ChatState => {
  switch (action.type) {
    case "SET_SPENT_TOKENS":
      return { ...state, spentTokens: action.tokens };
    case "ADD_SPENT_TOKENS":
      return { ...state, spentTokens: state.spentTokens + action.tokens };
    case "SET_MESSAGES":
      return { ...state, messages: action.messages };
    case "ADD_MESSAGE":
      return { ...state, messages: [...state.messages, action.message] };
    case "SET_WS_URL":
      return { ...state, wsURL: action.url };
    default:
      return state;
  }
};
