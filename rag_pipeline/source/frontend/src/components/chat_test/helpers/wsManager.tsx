import { useCallback, useEffect, type ReactNode } from "react";
import { APIs, baseWebSocketURL } from "../../helpers/constants";
import type {
  ChatAction,
  ChatState,
} from "../../dashboard_wripper/helpers/chatReducer";
import { renderJsonCodeBlock, requestServer } from "../../helpers/common";
import { Method } from "../../helpers/types";
import type { AppAction } from "../../dashboard_wripper/helpers/appReducer";

export const useWebScoketManager = (
  chatSocketRef: React.RefObject<WebSocket | null>,
  setIsSocketOpen: (flag: boolean) => void,
  setIsloading: (flag: boolean) => void,
  setServerError: (msg: string) => void,
  chatState: ChatState,
  appDispatch: React.ActionDispatch<[action: AppAction]>,
  chatDispatch: (action: ChatAction) => void,
) => {
  type DebuggerData =
    | {
        message?: string;
        tokens?: number;
        chunks?: string[];
        bot_shortname?: string;
        json_obj?: unknown;
        search_query?: string;
      }
    | string;

  const addMessage = useCallback(
    (role: string, content: ReactNode) => {
      const next =
        role === "debugger" ? (
          <div
            className="overflow-x-auto w-100 bg-success-subtle py-2 px-3 border rounded text-success-emphasis opacity-75"
            style={{ fontSize: "0.9em" }}
          >
            {content}
          </div>
        ) : (
          <div>
            <strong className="me-2">{role}:</strong>
            {content}
          </div>
        );
      chatDispatch({ type: "ADD_MESSAGE", message: next });
    },
    [chatDispatch],
  );

  const proceedDebugData = useCallback(
    (role: string, message: DebuggerData) => {
      // restored comment from original Russian source
      if (typeof message === "object" && message !== null) {
        // restored comment from original Russian source
        if ("tokens" in message) {
          const tokens = (message as { tokens?: number }).tokens;
          if (typeof tokens === "number") {
            chatDispatch({ type: "ADD_SPENT_TOKENS", tokens });
            return;
          }
        }

        // restored comment from original Russian source
        else if ("bot_shortname" in message) {
          const content = (
            <span>
              <b>Comment:</b> {message.message} <b>{message.bot_shortname}</b>.
              This bot starts extracting the missing request details
            </span>
          );
          addMessage(String(role), content);
        }

        // restored comment from original Russian source
        else if ("json_obj" in message) {
          const content = (
            <>
              <div>
                <b>Comment:</b> {message.message}
              </div>
              <div>{renderJsonCodeBlock(message.json_obj)}</div>
            </>
          );
          addMessage(String(role), content);
        }

        // restored comment from original Russian source
        else if ("chunks" in message) {
          const chunks = message.chunks!;
          const content = (
            <>
              <div>
                <b>Comment:</b> {message.message}
              </div>
              <div>{renderJsonCodeBlock(chunks)}</div>
              <p></p>
            </>
          );
          addMessage(String(role), content);
        }

        // restored comment from original Russian source
        else if ("search_query" in message) {
          const content = (
            <>
              <div>
                <b>Comment:</b> {message.message} <b>{message.search_query}</b>
              </div>
            </>
          );
          addMessage(String(role), content);
        }

        // restored comment from original Russian source
        else if ("message" in message) {
          const content = (
            <div>
              <b>Comment:</b> {message.message}
            </div>
          );
          addMessage(String(role), content);
        }
      }

      // restored comment from original Russian source
      else addMessage(String(role), String(message));
    },
    [addMessage, chatDispatch],
  );

  useEffect(() => {
    const connectChatWebSocket = (webSockerURL: string) => {
      if (
        chatSocketRef.current &&
        (chatSocketRef.current.readyState === WebSocket.OPEN ||
          chatSocketRef.current.readyState === WebSocket.CONNECTING)
      ) {
        return;
      }

      const finalUrl = `${baseWebSocketURL}${webSockerURL}&is_test_mode=1`;

      chatSocketRef.current = new WebSocket(finalUrl);

      chatSocketRef.current.onopen = () => {
        console.log("WebSocket connected");
        setIsSocketOpen(true);
        setIsloading(false);
      };

      chatSocketRef.current.onclose = () => {
        console.log("WebSocket closed");
        setIsSocketOpen(false);
      };

      chatSocketRef.current.onmessage = (event) => {
        const raw = event.data;
        if (typeof raw === "string") {
          try {
            const parsed = JSON.parse(raw);
            const isJsonObject =
              parsed !== null &&
              typeof parsed === "object" &&
              !Array.isArray(parsed);
            const role = isJsonObject
              ? "debugger"
              : (parsed?.role ?? "assistant");
            const message =
              parsed?.message ?? parsed?.content ?? parsed?.text ?? raw;

            if (role === "debugger") {
              proceedDebugData(role, isJsonObject ? parsed : message);
            } else {
              addMessage(String(role), String(message));
            }

            return;
          } catch {
            addMessage("assistant", raw);
            return;
          }
        }
        addMessage("assistant", String(raw));
      };

      chatSocketRef.current.onerror = (err) => {
        console.error("WebSocket error", err);
        setServerError(String(err));
        setIsSocketOpen(false);
      };
    };

    const requestChatPassport = async () => {
      const result = await requestServer<{
        chat_passport_id: string;
        ws_url: string;
      }>(APIs.requestChatPassport, {
        method: Method.POST,
        body: {
          id: null,
          source: "web",
        },
      });

      if (result.error) {
        console.log(result.error);
        if (result.error === "Invalid chat passport id") {
          localStorage.removeItem("chat_passport_id");
          chatDispatch({ type: "SET_WS_URL", url: "" });
          return;
        } else {
          setServerError(String(result.error));
          setIsloading(false);
          return;
        }
      } else if (result.notAuthenticated) {
        setServerError("");
        appDispatch({ type: "SET_UNAUTH" });
        setIsloading(false);
        return;
      } else if (result.data) {
        chatDispatch({ type: "SET_WS_URL", url: result.data.ws_url });
        setIsloading(false);

        // restored comment from original Russian source
        connectChatWebSocket(result.data.ws_url);
      }
    };

    if (chatState.wsURL === "") {
      requestChatPassport();
      return;
    }

    if (chatState.wsURL) {
      connectChatWebSocket(chatState.wsURL);
    }
    return () => {
      if (
        chatSocketRef.current &&
        chatSocketRef.current.readyState === WebSocket.OPEN
      ) {
        chatSocketRef.current.close();
      }
      setIsSocketOpen(false);
    };
  }, [
    appDispatch,
    addMessage,
    chatState.wsURL,
    proceedDebugData,
    chatDispatch,
    chatSocketRef,
    setIsSocketOpen,
    setIsloading,
    setServerError,
  ]);

  return addMessage;
};
