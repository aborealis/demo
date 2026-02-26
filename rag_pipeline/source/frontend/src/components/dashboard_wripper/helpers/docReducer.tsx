import {
  SearchType,
  type DocsServerType,
  type OneDocType,
} from "../../helpers/types";

export type DocState = {
  currentPage: number;
  docsPerPage: number;
  searchType: string;
  searchQuery: string | null;
  documents: DocsServerType;
  documentToEdit: OneDocType | null;
};

export const docsInitState: DocState = {
  currentPage: 1,
  docsPerPage: 10,
  searchType: SearchType.keyword,
  searchQuery: null,
  documents: { total_count: 0, offset: 0, documents: [] },
  documentToEdit: null,
};

export type DocAction =
  | { type: "SET_CURRENT_PAGE"; page: number }
  | { type: "SET_DOCS_PER_PAGE"; number: number }
  | { type: "SET_SEARCH_TYPE"; searchType: string }
  | { type: "SET_SEARCH_QUERY"; query: string | null }
  | { type: "SET_DOCUMENTS"; documents: DocsServerType }
  | { type: "SET_DOC_TO_EDIT"; document: OneDocType }
  | { type: "SET_DOC_STATUS_READY"; docId: number }
  | { type: "REMOVE_DOC"; docId: number };

export const docReducer = (state: DocState, action: DocAction): DocState => {
  switch (action.type) {
    case "SET_CURRENT_PAGE":
      return { ...state, currentPage: action.page };
    case "SET_DOCS_PER_PAGE":
      return { ...state, docsPerPage: action.number };
    case "SET_SEARCH_TYPE":
      return { ...state, searchType: action.searchType };
    case "SET_SEARCH_QUERY":
      return { ...state, searchQuery: action.query };
    case "SET_DOCUMENTS":
      return { ...state, documents: action.documents };
    case "SET_DOC_TO_EDIT":
      return { ...state, documentToEdit: action.document };
    case "SET_DOC_STATUS_READY": {
      const docList = state.documents.documents;
      const updatedList = docList.map((d) =>
        d.id === action.docId ? { ...d, status: "ready" } : d,
      );
      return {
        ...state,
        documents: { ...state.documents, documents: updatedList },
      };
    }
    case "REMOVE_DOC": {
      const docList = state.documents.documents;
      const updatedList = docList.filter((d) => d.id !== action.docId);
      return {
        ...state,
        documents: {
          ...state.documents,
          total_count: state.documents.total_count - 1,
          documents: updatedList,
        },
      };
    }
    default:
      return state;
  }
};
