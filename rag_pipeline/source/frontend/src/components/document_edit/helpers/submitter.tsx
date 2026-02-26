import type { AppAction } from "../../dashboard_wripper/helpers/appReducer";
import type { DocState } from "../../dashboard_wripper/helpers/docReducer";
import { requestServer } from "../../helpers/common";
import { APIs, layerNames } from "../../helpers/constants";
import { Method } from "../../helpers/types";
import type { FormState } from "./formReducer";

export const useServerSend = (
  formState: FormState,
  docState: DocState,
  setServerError: (msg: string) => void,
  appDispatch: React.ActionDispatch<[action: AppAction]>,
) => {
  const handleSubmit = async () => {
    const documentID = docState.documentToEdit?.id;
    if (!documentID) return;

    const payload = {
      name: formState.titleDraft,
      content: formState.contentDraft,
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
      appDispatch({ type: "SET_UNAUTH" });
      return;
    }

    appDispatch({ type: "SET_LAYER", layer: layerNames.documents });
  };

  return handleSubmit;
};
