export type FormState = {
  titleDraft: string;
  contentDraft: string;
};

type Action =
  | { type: "SET_TITLE"; title: string }
  | { type: "SET_CONTENT"; content: string };

export const formReducer = (state: FormState, action: Action) => {
  switch (action.type) {
    case "SET_TITLE":
      return { ...state, titleDraft: action.title };
    case "SET_CONTENT":
      return { ...state, contentDraft: action.content };
    default:
      return state;
  }
};
