import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import Login from "../helpers/loginWindow";
import ServerErrorWindow from "../helpers/serverErrorMessage";
import Loader from "../helpers/loader";
import { Button, ButtonGroup } from "react-bootstrap";
import type {
  AppAction,
  AppState,
} from "../dashboard_wripper/helpers/appReducer";
import type {
  ChatAction,
  ChatState,
} from "../dashboard_wripper/helpers/chatReducer";
import { useWebScoketManager } from "./helpers/wsManager";

interface Props {
  appState: AppState;
  chatState: ChatState;
  appDispatch: React.ActionDispatch<[action: AppAction]>;
  chatDispatch: React.ActionDispatch<[action: ChatAction]>;
}

const ChatTest = (props: Props) => {
  const { appState, chatState, appDispatch, chatDispatch } = props;
  const chatSocketRef = useRef<WebSocket | null>(null);

  /* ================
   * Chat Management
   * ================ */
  const [isLoading, setIsloading] = useState(chatState.wsURL === null);
  const [serverError, setServerError] = useState("");

  const [messageInput, setMessageInput] = useState("");
  const endRef = useRef<HTMLDivElement | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const [isSocketOpen, setIsSocketOpen] = useState(false);

  const resetMessages = () => {
    chatDispatch({ type: "SET_MESSAGES", messages: [] });
    chatDispatch({ type: "SET_SPENT_TOKENS", tokens: 0 });
    chatDispatch({ type: "SET_WS_URL", url: "" });
    setIsSocketOpen(false);
  };

  const addMessage = useWebScoketManager(
    chatSocketRef,
    setIsSocketOpen,
    setIsloading,
    setServerError,
    chatState,
    appDispatch,
    chatDispatch,
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
  }, [chatState.messages.length, scrollToBottom]);

  useEffect(
    () => scrollToBottomSoon(),
    [chatState.messages.length, scrollToBottomSoon],
  );

  const handleSendMessage = () => {
    const text = messageInput.trim();
    if (!text) return;

    setMessageInput("");
    addMessage("user", text);

    if (
      chatSocketRef.current &&
      chatSocketRef.current.readyState === WebSocket.OPEN
    ) {
      chatSocketRef.current.send(text);
    } else {
      addMessage("system", "WebSocket is not connected");
    }
  };

  /* =========
   * Rendering
   * ========= */

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
    <div className="h-100 d-flex flex-column pb-4 tests-root">
      <h1 className="py-3 mt-5 mt-lg-1 fs-4">Chat</h1>
      <p className="text-muted mb-3">
        Update document content in the Documents tab, then ask a question about
        that content here.
      </p>
      <div className="border rounded mb-3 d-flex flex-column flex-grow-1 tests-chat-window">
        <div className="border-bottom bg-light d-flex justify-content-end">
          <div className="px-3">
            <small>Tokens spent: {chatState.spentTokens}</small>
          </div>
        </div>
        <div
          ref={scrollContainerRef}
          className="p-3 flex-grow-1 overflow-auto tests-chat-scroll"
        >
          {chatState.messages.length === 0 && (
            <div className="text-muted">No messages yet.</div>
          )}
          {chatState.messages.map((item, index) => (
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

export default ChatTest;
