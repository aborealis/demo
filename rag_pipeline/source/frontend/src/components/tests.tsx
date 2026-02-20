import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import type { ReactNode } from "react";
import { requestServer, renderJsonCodeBlock } from "./helpers/common";
import { APIs, baseWebSocketURL } from "./helpers/constants";
import { Method } from "./helpers/types";
import Login from "./helpers/loginWindow";
import ServerErrorWindow from "./helpers/serverErrorMessage";
import Loader from "./helpers/loader";
import { Button, ButtonGroup } from "react-bootstrap";

let chatSocket: WebSocket | null = null;
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

interface Props {
  isAuthenticated: boolean;
  setIsAuthenticated: (flag: boolean) => void;
  messages: ReactNode[];
  setMessages: React.Dispatch<React.SetStateAction<ReactNode[]>>;
  spentTokens: number;
  setSpentTokens: React.Dispatch<React.SetStateAction<number>>;
  wsURL: string;
  setWsURL: (arg: string) => void;
}

const Tests = (props: Props) => {
  const {
    isAuthenticated,
    setIsAuthenticated,
    messages,
    setMessages,
    spentTokens,
    setSpentTokens,
    wsURL,
    setWsURL,
  } = props;

  /* ================
   * restored comment from original Russian source
   * ================ */

  const [messageInput, setMessageInput] = useState("");
  const endRef = useRef<HTMLDivElement | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const [isSocketOpen, setIsSocketOpen] = useState(false);

  const resetMessages = () => {
    setMessages([]);
    setSpentTokens(0);
    setIsSocketOpen(false);
    setWsURL("");
  };

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
      setMessages((prev) => [...prev, next]);
    },
    [setMessages],
  );

  const proceedDebugData = useCallback(
    (role: string, message: DebuggerData) => {
      // restored comment from original Russian source
      if (typeof message === "object" && message !== null) {
        // restored comment from original Russian source
        if ("tokens" in message) {
          const tokens = (message as { tokens?: number }).tokens;
          if (typeof tokens === "number") {
            setSpentTokens((prev) => prev + tokens);
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
    [addMessage, setSpentTokens],
  );

  const scrollToBottom = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) return;
    container.scrollTop = container.scrollHeight;
  }, []);

  const scrollToBottomSoon = useCallback(() => {
    const t1 = setTimeout(scrollToBottom, 0);
    const t2 = setTimeout(scrollToBottom, 50);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [scrollToBottom]);

  useLayoutEffect(() => {
    scrollToBottom();
  }, [messages.length, scrollToBottom]);

  useEffect(() => scrollToBottomSoon(), [messages.length, scrollToBottomSoon]);

  const handleSendMessage = () => {
    const text = messageInput.trim();
    if (!text) return;

    setMessageInput("");
    addMessage("user", text);

    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
      chatSocket.send(text);
    } else {
      addMessage("system", "WebSocket is not connected");
    }
  };

  /* ====================================
   * restored comment from original Russian source
   * ==================================== */
  const [isLoading, setIsloading] = useState(wsURL === null);
  const [serverError, setServerError] = useState("");

  useEffect(() => {
    const connectChatWebSocket = (webSockerURL: string) => {
      if (
        chatSocket &&
        (chatSocket.readyState === WebSocket.OPEN ||
          chatSocket.readyState === WebSocket.CONNECTING)
      ) {
        return;
      }

      const finalUrl = `${baseWebSocketURL}${webSockerURL}&is_test_mode=1`;

      chatSocket = new WebSocket(finalUrl);

      chatSocket.onopen = () => {
        console.log("WebSocket connected");
        setIsSocketOpen(true);
        setIsloading(false);
      };

      chatSocket.onclose = () => {
        console.log("WebSocket closed");
        setIsSocketOpen(false);
      };

      chatSocket.onmessage = (event) => {
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

      chatSocket.onerror = (err) => {
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
          setWsURL("");
          return;
        } else {
          setServerError(String(result.error));
          setIsloading(false);
          return;
        }
      } else if (result.notAuthenticated) {
        setServerError("");
        setIsAuthenticated(false);
        setIsloading(false);
        return;
      } else if (result.data) {
        setWsURL(result.data.ws_url);
        setIsloading(false);

        // restored comment from original Russian source
        connectChatWebSocket(result.data.ws_url);
      }
    };

    if (wsURL === "") {
      requestChatPassport();
      return;
    }

    if (wsURL) {
      connectChatWebSocket(wsURL);
    }
    return () => {
      if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.close();
      }
      setIsSocketOpen(false);
    };
  }, [setIsAuthenticated, addMessage, wsURL, proceedDebugData, setWsURL]);

  /* =========
   * restored comment from original Russian source
   * ========= */

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
    <div className="h-100 d-flex flex-column pb-4 tests-root">
      <h1 className="py-3 mt-5 mt-lg-1 fs-4">Chat</h1>
      <p className="text-muted mb-3">
        Update document content in the Documents tab, then ask a question about
        that content here.
      </p>
      <div className="border rounded mb-3 d-flex flex-column flex-grow-1 tests-chat-window">
        <div className="border-bottom bg-light d-flex justify-content-end">
          <div className="px-3">
            <small>Tokens spent: {spentTokens}</small>
          </div>
        </div>
        <div
          ref={scrollContainerRef}
          className="p-3 flex-grow-1 overflow-auto tests-chat-scroll"
        >
          {messages.length === 0 && (
            <div className="text-muted">No messages yet.</div>
          )}
          {messages.map((item, index) => (
            <div key={index} className="mb-2">
              {item}
            </div>
          ))}
          <div ref={endRef} />
        </div>
      </div>
      <form
        className="d-flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          handleSendMessage();
        }}
      >
        <input
          className="form-control"
          type="text"
          placeholder="Type a message..."
          value={messageInput}
          onChange={(event) => setMessageInput(event.target.value)}
        />
        <ButtonGroup>
          <Button variant="outline-success" onClick={resetMessages}>
            Reset
          </Button>
          <Button variant="success" type="submit" disabled={!isSocketOpen}>
            Send
          </Button>
        </ButtonGroup>
      </form>
    </div>
  );
};

export default Tests;
