import { Folder2, GraphUp, Headset, PersonCircle } from "react-bootstrap-icons";

const isDebug = true;

export const layerNames = {
  documents: "Documents",
  documentEdit: "documentEdit",
  chat: "Chat",
  dummyMenu1: "Dummy Menu 1",
  dummyMenu2: "Dummy Menu 2",
  dummyMenu3: "Dummy Menu 3",
  dummyMenu4: "Dummy Menu 4",
  dummyMenu5: "Dummy Menu 5",
};

const baseURL = isDebug ? "http://localhost:8000" : "https://myfrontend.com";
export const baseWebSocketURL = isDebug
  ? "ws://localhost:8000"
  : "ws://myfrontend.com";
const apiPrefix = "/api/v1";

export const menuStructure = [
  {
    icon: <Folder2 />,
    items: {
      [layerNames.documents]: {
        visible: true,
        disabled: false,
        activeFor: [layerNames.documents, layerNames.documentEdit],
      },
      [layerNames.documentEdit]: {
        visible: false,
        disabled: true,
        activeFor: [],
      },
      [layerNames.chat]: {
        visible: true,
        disabled: false,
        activeFor: [layerNames.chat],
      },
    },
  },
  {
    icon: <GraphUp />,
    items: {
      [layerNames.dummyMenu1]: {
        visible: true,
        disabled: true,
        activeFor: [],
      },
      [layerNames.dummyMenu2]: {
        visible: true,
        disabled: true,
        activeFor: [],
      },
    },
  },
  {
    icon: <Headset />,
    items: {
      [layerNames.dummyMenu3]: {
        visible: true,
        disabled: true,
        activeFor: [],
      },
    },
  },
  {
    icon: <PersonCircle />,
    items: {
      [layerNames.dummyMenu4]: {
        visible: true,
        disabled: true,
        activeFor: [],
      },
      [layerNames.dummyMenu5]: {
        visible: true,
        disabled: true,
        activeFor: [],
      },
    },
  },
];

export const APIs = {
  login: `${baseURL}${apiPrefix}/auth/login/`,
  fetchDocs: `${baseURL}${apiPrefix}/documents/`,
  searchDocsContext: `${baseURL}${apiPrefix}/documents/search/context/`,
  searchDocsKeyword: `${baseURL}${apiPrefix}/documents/search/keyword/`,
  patchDocContent: (ID: number) =>
    `${baseURL}${apiPrefix}/documents/update/content/${ID}/`,
  progress: (ID: number) => `${baseURL}${apiPrefix}/documents/status/${ID}/`,
  deleteDocument: (ID: number) =>
    `${baseURL}${apiPrefix}/documents/delete/${ID}/`,
  requestChatPassport: `${baseURL}${apiPrefix}/chat/init/`,
};
