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
  type DocViewState,
  type OneDocType,
  type RequestOptions,
} from "./helpers/types";

interface Params {
  isAuthenticated: boolean;
  setIsAuthenticated: (flag: boolean) => void;
  docsViewState: DocViewState;
  setDocsViewState: React.Dispatch<React.SetStateAction<DocViewState>>;
  setActiveLayer: (layer: string) => void;
}

const Documents = (params: Params) => {
  const {
    isAuthenticated,
    setIsAuthenticated,
    docsViewState,
    setDocsViewState,
    setActiveLayer,
  } = params;

  const [serverError, setServerError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const prevDocsViewStateRef = useRef<DocViewState | null>(null);

  useEffect(() => {
    scrollToTopInstant();

    if (prevDocsViewStateRef.current) {
      const prevDocViewState = prevDocsViewStateRef.current;
      const {
        documents: _val1,
        ...triggerKeysPrev
      } = prevDocViewState;
      const {
        documents: _val2,
        ...triggerKeysCurent
      } = docsViewState;

      void _val1;
      void _val2;

      if (isDeepEqual(triggerKeysPrev, triggerKeysCurent)) return;
    }

    const setDocuments = (documents: DocsServerType) =>
      setDocsViewState((prev) => ({ ...prev, documents }));

    let API = "";
    const docsRequestOptions: RequestOptions = {
      method: Method.GET,
      token: localStorage.getItem("AuthToken") ?? undefined,
      body: {
        offset: (docsViewState.currentPage - 1) * docsViewState.docsPerPage,
        limit: docsViewState.docsPerPage,
      },
    };

    const fetchDocuments = async () => {
      if (!docsViewState.searchQuery) {
        API = APIs.fetchDocs;
      } else if (docsViewState.searchType == SearchType.context) {
        API = APIs.searchDocsContext;
        docsRequestOptions.method = Method.POST;
        docsRequestOptions.body = {
          query: docsViewState.searchQuery,
          top_k: 5,
        };
      } else {
        API = APIs.searchDocsKeyword;
        docsRequestOptions.method = Method.POST;
        docsRequestOptions.body = {
          ...docsRequestOptions.body,
          query: docsViewState.searchQuery,
        };
      }

      const result = await requestServer<DocsServerType>(
        API,
        docsRequestOptions,
      );

      setIsLoading(false);
      if (result.notAuthenticated) {
        setIsAuthenticated(false);
        setServerError("");
      } else if (result.error) {
        setServerError(result.error);
      } else if (result.data) {
        setServerError("");
        setDocuments(result.data);
      }
    };

    fetchDocuments();
    prevDocsViewStateRef.current = docsViewState;
  }, [docsViewState, setIsAuthenticated, setDocsViewState, isAuthenticated]);

  const [searchDraft, setSearchDraft] = useState(
    docsViewState.searchQuery ?? "",
  );

  const setDocsPerPage = (n: number) =>
    setDocsViewState((prev) => ({ ...prev, docsPerPage: n }));

  const setCurrentPage = (n: number) =>
    setDocsViewState((prev) => ({ ...prev, currentPage: n }));

  const setSearchType = (sType: string) =>
    setDocsViewState((prev) => ({ ...prev, searchType: sType }));

  const setSearchQuery = (query: string | null) => {
    setIsLoading(true);
    setDocsViewState((prev) => ({
      ...prev,
      searchQuery: query,
      currentPage: 1,
    }));
  };

  const resetSearchQuery = () => {
    setSearchDraft("");
    setSearchQuery(null);
  };

  const isPaginationVisible =
    docsViewState.documents.total_count > docsViewState.docsPerPage;

  const paramsPaginator = {
    nPages: Math.ceil(
      docsViewState.documents.total_count / docsViewState.docsPerPage,
    ),
    docsViewState,
    setDocsViewState,
    setIsLoading,
  };

  const handleChangeDocsPerPage = (n: number) => {
    setIsLoading(true);
    setDocsPerPage(n);
    setCurrentPage(1);
  };

  const setDocToEdit = (doc: OneDocType) =>
    setDocsViewState((prev) => ({ ...prev, documentToEdit: doc }));

  const handleEditDoc = (doc: OneDocType) => {
    setDocToEdit(doc);
    setActiveLayer(layerNames.documentEdit);
  };

  const [progresses, setProgresses] = useState<DocProgress>({});
  const progressIntervalsRef = useRef<Map<number, number>>(new Map());

  useEffect(() => {
    const intervals = progressIntervalsRef.current;
    const queuedIds = new Set<number>();
    for (const doc of docsViewState.documents.documents) {
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
          setIsAuthenticated(false);
          return;
        }

        if (result.error) {
          setServerError(result.error);
          return;
        }

        if (result.data) {
          const data = result.data;

          if (data.status === "ready") {
            setDocsViewState((prev) => ({
              ...prev,
              documents: {
                ...prev.documents,
                documents: prev.documents.documents.map((doc) =>
                  doc.id === docId ? { ...doc, status: "ready" } : doc,
                ),
              },
            }));

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
  }, [docsViewState.documents.documents, setDocsViewState, setIsAuthenticated]);

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
      setIsAuthenticated(false);
      setServerError("");
    } else if (result.error) {
      setServerError(result.error);
    } else {
      setServerError("");
      setDocsViewState((prev) => ({
        ...prev,
        documents: {
          ...prev.documents,
          documents: prev.documents.documents.filter(
            (doc) => doc.id !== docIDtoDelete,
          ),
          total_count: prev.documents.total_count - 1,
        },
      }));
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
        <InputGroup.Text id="ipp-val">
          {docsViewState.docsPerPage}
        </InputGroup.Text>
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

  if (!isAuthenticated) {
    return <Login setIsAuthenticated={setIsAuthenticated} />;
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
              placeholder={docsViewState.searchType}
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
                  onClick={() => setSearchType(item)}
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
            {docsViewState.documents.documents.map((item) => (
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
