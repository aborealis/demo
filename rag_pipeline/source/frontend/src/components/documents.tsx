import { useEffect, useRef, useState } from "react";
import Login from "./helpers/loginWindow";
import { APIs, layerNames } from "./helpers/constants";
import {
  isDeepEqual,
  requestServer,
  scrollToTopInstant,
} from "./helpers/common";
import Loader from "./helpers/loader";
import ServerErrorWindow from "./helpers/serverErrorMessage";
import {
  Button,
  Col,
  Dropdown,
  Form,
  InputGroup,
  Modal,
  ProgressBar,
  Row,
  SplitButton,
  Table,
} from "react-bootstrap";
import MyPagination from "./helpers/pagination";
import { PencilSquare, Search, Trash3, XLg } from "react-bootstrap-icons";
import {
  Method,
  SearchType,
  type DocProgress,
  type DocsServerType,
  type OneDocType,
  type RequestOptions,
} from "./helpers/types";
import type {
  AppAction,
  AppState,
} from "./dashboard_wripper/helpers/appReducer";
import type {
  DocAction,
  DocState,
} from "./dashboard_wripper/helpers/docReducer";

interface Params {
  appState: AppState;
  docState: DocState;
  appDispatch: React.ActionDispatch<[action: AppAction]>;
  docDispatch: React.ActionDispatch<[action: DocAction]>;
}

const Documents = (params: Params) => {
  const { appState, docState, appDispatch, docDispatch } = params;

  const [serverError, setServerError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const prevDocsStateRef = useRef<DocState | null>(null);

  useEffect(() => {
    scrollToTopInstant();

    if (prevDocsStateRef.current) {
      const prevDocState = prevDocsStateRef.current;
      const { documents: _val1, ...triggerKeysPrev } = prevDocState;
      const { documents: _val2, ...triggerKeysCurent } = docState;

      void _val1;
      void _val2;

      if (isDeepEqual(triggerKeysPrev, triggerKeysCurent)) return;
    }

    let API = "";
    const docsRequestOptions: RequestOptions = {
      method: Method.GET,
      token: localStorage.getItem("AuthToken") ?? undefined,
      body: {
        offset: (docState.currentPage - 1) * docState.docsPerPage,
        limit: docState.docsPerPage,
      },
    };

    const fetchDocuments = async () => {
      if (!docState.searchQuery) {
        API = APIs.fetchDocs;
      } else if (docState.searchType == SearchType.context) {
        API = APIs.searchDocsContext;
        docsRequestOptions.method = Method.POST;
        docsRequestOptions.body = {
          query: docState.searchQuery,
          top_k: 5,
        };
      } else {
        API = APIs.searchDocsKeyword;
        docsRequestOptions.method = Method.POST;
        docsRequestOptions.body = {
          ...docsRequestOptions.body,
          query: docState.searchQuery,
        };
      }

      const result = await requestServer<DocsServerType>(
        API,
        docsRequestOptions,
      );

      setIsLoading(false);
      if (result.notAuthenticated) {
        appDispatch({ type: "SET_UNAUTH" });
        setServerError("");
      } else if (result.error) {
        setServerError(result.error);
      } else if (result.data) {
        setServerError("");
        docDispatch({ type: "SET_DOCUMENTS", documents: result.data });
      }
    };

    fetchDocuments();
    prevDocsStateRef.current = docState;
  }, [docState, appState.isAuthenticated, docDispatch, appDispatch]);

  const [searchDraft, setSearchDraft] = useState(docState.searchQuery ?? "");

  const setSearchQuery = (query: string | null) => {
    setIsLoading(true);
    docDispatch({ type: "SET_SEARCH_QUERY", query });
    docDispatch({ type: "SET_CURRENT_PAGE", page: 1 });
  };

  const resetSearchQuery = () => {
    setSearchDraft("");
    setSearchQuery(null);
  };

  const isPaginationVisible =
    docState.documents.total_count > docState.docsPerPage;

  const paramsPaginator = {
    docState,
    docDispatch,
    setIsLoading,
  };

  const handleChangeDocsPerPage = (n: number) => {
    setIsLoading(true);
    docDispatch({ type: "SET_DOCS_PER_PAGE", number: n });
    docDispatch({ type: "SET_CURRENT_PAGE", page: 1 });
  };

  const handleEditDoc = (doc: OneDocType) => {
    docDispatch({ type: "SET_DOC_TO_EDIT", document: doc });
    appDispatch({ type: "SET_LAYER", layer: layerNames.documentEdit });
  };

  const [progresses, setProgresses] = useState<DocProgress>({});
  const progressIntervalsRef = useRef<Map<number, number>>(new Map());

  useEffect(() => {
    const intervals = progressIntervalsRef.current;
    const queuedIds = new Set<number>();
    for (const doc of docState.documents.documents) {
      if (doc.status === "queued") {
        queuedIds.add(doc.id);
      }
    }

    const startPolling = (docId: number) => {
      const poll = async () => {
        const result = await requestServer<{
          status: string;
          progress: number;
        }>(APIs.progress(docId), {
          method: Method.GET,
          token: localStorage.getItem("AuthToken") ?? undefined,
        });

        if (result.notAuthenticated) {
          appDispatch({ type: "SET_UNAUTH" });
          return;
        }

        if (result.error) {
          setServerError(result.error);
          return;
        }

        if (result.data) {
          const data = result.data;

          if (data.status === "ready") {
            docDispatch({ type: "SET_DOC_STATUS_READY", docId });

            setProgresses((prev) => {
              const next = { ...prev };
              delete next[docId];
              return next;
            });

            const intervalId = intervals.get(docId);
            if (intervalId !== undefined) {
              window.clearInterval(intervalId);
              intervals.delete(docId);
            }

            return;
          }

          setProgresses((prev) => ({
            ...prev,
            [docId]: { progress: data.progress },
          }));
        }
      };

      const intervalId = window.setInterval(() => {
        void poll();
      }, 1000);

      intervals.set(docId, intervalId);
      void poll();
    };

    for (const docId of queuedIds) {
      if (!intervals.has(docId)) {
        startPolling(docId);
      }
    }

    for (const [docId, intervalId] of intervals) {
      if (!queuedIds.has(docId)) {
        window.clearInterval(intervalId);
        intervals.delete(docId);
      }
    }

    return () => {
      for (const intervalId of intervals.values()) {
        window.clearInterval(intervalId);
      }
      intervals.clear();
    };
  }, [docState.documents.documents, docDispatch, appDispatch]);

  const [showModal, setShowModal] = useState(false);
  const [docIDtoDelete, setDocIDtoDelete] = useState<number | null>(null);

  const handleCloseModal = () => {
    setShowModal(false);
    setDocIDtoDelete(null);
  };
  const handleShowModal = (ID: number) => {
    setDocIDtoDelete(ID);
    setShowModal(true);
  };

  const handleDeleteDoc = async () => {
    if (!docIDtoDelete) return;

    const result = await requestServer(APIs.deleteDocument(docIDtoDelete), {
      method: Method.DELETE,
      token: localStorage.getItem("AuthToken") ?? undefined,
    });

    if (result.notAuthenticated) {
      appDispatch({ type: "SET_UNAUTH" });
      setServerError("");
    } else if (result.error) {
      setServerError(result.error);
    } else {
      setServerError("");
      docDispatch({ type: "REMOVE_DOC", docId: docIDtoDelete });
      handleCloseModal();
    }
  };

  const modalWindow = (
    <Modal show={showModal} onHide={handleCloseModal}>
      <Modal.Header closeButton>
        <Modal.Title>Delete Document?</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        You are abouut to delete this document. Are you sure?
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleCloseModal}>
          Cancel
        </Button>
        <Button variant="danger" onClick={handleDeleteDoc}>
          Delete
        </Button>
      </Modal.Footer>
    </Modal>
  );

  const paginationTop = (
    <div className="d-flex justify-content-center d-sm-none">
      <MyPagination {...paramsPaginator} />
    </div>
  );

  const paginationBottom = (
    <div className="d-none d-sm-flex justify-content-end">
      <InputGroup className="mb-3">
        <InputGroup.Text id="ipp-txt" className="border-0 bg-white">
          Items per page
        </InputGroup.Text>
        <InputGroup.Text id="ipp-val">{docState.docsPerPage}</InputGroup.Text>
        <Dropdown className="d-inline-block ms-2">
          <Dropdown.Toggle
            variant="outline-secondary"
            id="dropdown-category"
            size="sm"
          ></Dropdown.Toggle>

          <Dropdown.Menu>
            {[10, 20, 50, 100].map((item) => (
              <Dropdown.Item
                key={item}
                href="#"
                onClick={() => handleChangeDocsPerPage(item)}
              >
                {item}
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
      </InputGroup>
      <div>
        <MyPagination {...paramsPaginator} />
      </div>
    </div>
  );

  if (isLoading) {
    return <Loader />;
  }

  if (!appState.isAuthenticated) {
    return <Login appDispatch={appDispatch} />;
  }

  if (serverError) {
    return <ServerErrorWindow serverError={serverError} />;
  }

  return (
    <div>
      <Row xs={1} md={2} className="py-3 mt-5 mt-lg-1">
        <Col xs={12} md={3} xl={5}>
          <h1 className="fs-4">Documents</h1>
        </Col>
        <Col xs={12} md={9} xl={7}>
          <InputGroup>
            <Form.Control
              aria-label="Search documents"
              placeholder={docState.searchType}
              onChange={(e) => setSearchDraft(e.target.value)}
              value={searchDraft}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  setSearchQuery(searchDraft);
                }
              }}
            />
            <Button variant="outline-secondary" onClick={resetSearchQuery}>
              <XLg />
            </Button>
            <SplitButton
              variant="outline-secondary"
              title={<Search />}
              id="search button"
              onClick={() => setSearchQuery(searchDraft)}
            >
              {[SearchType.keyword, SearchType.context].map((item) => (
                <Dropdown.Item
                  key={item}
                  href="#"
                  onClick={() =>
                    docDispatch({ type: "SET_SEARCH_TYPE", searchType: item })
                  }
                >
                  {item}
                </Dropdown.Item>
              ))}
            </SplitButton>
          </InputGroup>
        </Col>
      </Row>
      {isPaginationVisible && paginationTop}
      <div className="table-responsive">
        <Table hover>
          <thead>
            <tr>
              <th>Name</th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {docState.documents.documents.map((item) => (
              <tr key={item.id}>
                <td className={item.status == "queued" ? "text-secondary" : ""}>
                  <div>{item.name.slice(0, 150)}</div>
                  {item.status == "queued" && (
                    <ProgressBar
                      animated
                      variant="success"
                      now={progresses[item.id]?.progress ?? 0}
                    />
                  )}
                </td>
                <td>
                  {item.status == "queued" ? (
                    <span className="text-secondary fs-5">
                      <PencilSquare />
                    </span>
                  ) : (
                    <a
                      href="#"
                      className="text-muted fs-5"
                      onClick={() => handleEditDoc(item)}
                    >
                      {<PencilSquare />}
                    </a>
                  )}
                </td>
                <td>
                  {item.status == "queued" ? (
                    <span className="text-secondary fs-5">{<Trash3 />}</span>
                  ) : (
                    <a
                      href="#"
                      className="text-muted fs-5"
                      onClick={() => handleShowModal(item.id)}
                    >
                      {<Trash3 />}
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
        {modalWindow}
      </div>

      {isPaginationVisible && paginationBottom}
    </div>
  );
};

export default Documents;
