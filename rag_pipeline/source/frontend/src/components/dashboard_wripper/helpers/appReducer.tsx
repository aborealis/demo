import { layerNames } from "../../helpers/constants";

export type AppState = {
  activeLayer: string;
  isAuthenticated: boolean;
  showSideBar: boolean;
};

export const appInitState = {
  activeLayer: layerNames.documents,
  isAuthenticated: true,
  showSideBar: false,
};

export type AppAction =
  | { type: "SET_LAYER"; layer: string }
  | { type: "SET_AUTH" }
  | { type: "SET_UNAUTH" }
  | { type: "SHOW_SIDEBAR" }
  | { type: "HIDE_SIDEBAR" };

export const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case "SET_LAYER":
      return { ...state, activeLayer: action.layer };
    case "SHOW_SIDEBAR":
      return { ...state, showSideBar: true };
    case "HIDE_SIDEBAR":
      return { ...state, showSideBar: false };
    case "SET_AUTH":
      return { ...state, isAuthenticated: true };
    case "SET_UNAUTH":
      return { ...state, isAuthenticated: false };
    default:
      return state;
  }
};
