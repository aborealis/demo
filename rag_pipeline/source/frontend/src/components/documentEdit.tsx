import { Button, Form, InputGroup } from "react-bootstrap";
import { Method, type DocViewState } from "./helpers/types";
import { useState } from "react";
import { requestServer } from "./helpers/common";
import { APIs, layerNames } from "./helpers/constants";
import Login from "./helpers/loginWindow";
import ServerErrorWindow from "./helpers/serverErrorMessage";

interface Props {
  docsViewState: DocViewState;
  isAuthenticated: boolean;
  setActiveLayer: (layer: string) => void;
  setIsAuthenticated: (flag: boolean) => void;
}

const DocumentEdit = (param: Props) => {
  const { docsViewState, isAuthenticated, setIsAuthenticated, setActiveLayer } =
    param;

  const [titleDraft, setTitleDraft] = useState<string>(
    docsViewState.documentToEdit?.name ?? "",
  );

  const [contentDraft, setContentDraft] = useState<string>(
    docsViewState.documentToEdit?.content ?? "",
  );

  const [serverError, setServerError] = useState("");

  const handleSubmit = async () => {
    const documentID = docsViewState.documentToEdit?.id;
    if (!documentID) return;

    const payload = {
      name: titleDraft,
      content: contentDraft,
    };

    const result = await requestServer(APIs.patchDocContent(documentID), {
      method: Method.PATCH,
      body: payload,
      token: localStorage.getItem("AuthToken") ?? undefined,
    });

    if (result.error) {
      setServerError(result.error);
      return;
    }

    if (result.notAuthenticated) {
      setIsAuthenticated(false);
      return;
    }

    setActiveLayer(layerNames.documents);
  };

  if (!isAuthenticated) {
    return <Login setIsAuthenticated={setIsAuthenticated} />;
  }

  if (serverError) {
    return <ServerErrorWindow serverError={serverError} />;
  }

  return (
    <>
      <h1 className="py-3 mt-5 mt-lg-1 fs-4">Edit Document</h1>
      <InputGroup className="mb-3">
        <InputGroup.Text id="title">Title</InputGroup.Text>
        <Form.Control
          placeholder="Title"
          aria-label="Title"
          aria-describedby="title"
          value={titleDraft}
          onChange={(e) => setTitleDraft(e.target.value)}
        />
      </InputGroup>
      <InputGroup className="mb-3">
        <Form.Control
          as="textarea"
          rows={15}
          aria-label="With textarea"
          value={contentDraft}
          onChange={(e) => setContentDraft(e.target.value)}
        />
      </InputGroup>
      <div className="d-flex justify-content-end">
        <Button
          variant="secondary"
          className="mt-3 me-2"
          size="lg"
          onClick={() => setActiveLayer(layerNames.documents)}
        >
          Cancel
        </Button>
        <Button
          variant="success"
          className="mt-3"
          size="lg"
          onClick={handleSubmit}
        >
          Update
        </Button>
      </div>
    </>
  );
};

export default DocumentEdit;
