import { Button, Form, InputGroup } from "react-bootstrap";
import { useReducer, useState } from "react";
import { layerNames } from "../helpers/constants";
import Login from "../helpers/loginWindow";
import ServerErrorWindow from "../helpers/serverErrorMessage";
import type { DocState } from "../dashboard_wripper/helpers/docReducer";
import type {
  AppAction,
  AppState,
} from "../dashboard_wripper/helpers/appReducer";
import { formReducer, type FormState } from "./helpers/formReducer";
import { useServerSend } from "./helpers/submitter";

interface Props {
  appState: AppState;
  docState: DocState;
  appDispatch: React.ActionDispatch<[action: AppAction]>;
}

const DocumentEdit = (param: Props) => {
  const { docState, appState, appDispatch } = param;

  const formInitState: FormState = {
    titleDraft: docState.documentToEdit?.name ?? "",
    contentDraft: docState.documentToEdit?.content ?? "",
  };

  const [formState, formDispatch] = useReducer(formReducer, formInitState);
  const [serverError, setServerError] = useState("");

  const handleSubmit = useServerSend(
    formState,
    docState,
    setServerError,
    appDispatch,
  );

  if (!appState.isAuthenticated) {
    return <Login appDispatch={appDispatch} />;
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
          value={formState.titleDraft}
          onChange={(e) =>
            formDispatch({ type: "SET_TITLE", title: e.target.value })
          }
        />
      </InputGroup>
      <InputGroup className="mb-3">
        <Form.Control
          as="textarea"
          rows={15}
          aria-label="With textarea"
          value={formState.contentDraft}
          onChange={(e) =>
            formDispatch({ type: "SET_CONTENT", content: e.target.value })
          }
        />
      </InputGroup>
      <div className="d-flex justify-content-end">
        <Button
          variant="secondary"
          className="mt-3 me-2"
          size="lg"
          onClick={() =>
            appDispatch({ type: "SET_LAYER", layer: layerNames.documents })
          }
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
