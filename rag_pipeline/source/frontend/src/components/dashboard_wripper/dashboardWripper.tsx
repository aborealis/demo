import { Col, Row } from "react-bootstrap";
import DashboardNavBar from "../dashboardNavBar";
import { useReducer, useState } from "react";
import DashboardSideBarMobile from "../dashboardSideBarMobile";
import DashboartSidebarDesktop from "../dashboardSideBarDesktop";
import Documents from "../documents";
import { layerNames } from "../helpers/constants";
import DocumentEdit from "../document_edit/documentEdit";
import ChatTest from "../chat_test/chatTest";
import { appInitState, appReducer } from "./helpers/appReducer";
import { docReducer, docsInitState } from "./helpers/docReducer";
import { chatInitState, chatReducer } from "./helpers/chatReducer";

function DashBoardWripper() {
  const sideBarResponsiveViewBreakpoint = "lg";
  const sideBarWidth = 230;
  const navBarHeight = 50;
  const iconRowWidth = 50;

  const [showSideBar, setSideBarShow] = useState(false);
  const sideBarClose = () => setSideBarShow(false);
  const sideBarShow = () => setSideBarShow(true);

  const [appState, appDispatch] = useReducer(appReducer, appInitState);
  const [docState, docDispatch] = useReducer(docReducer, docsInitState);
  const [chatState, chatDispatch] = useReducer(chatReducer, chatInitState);

  const paramsToPass = {
    showSideBar,
    sideBarShow,
    sideBarClose,
    sideBarResponsiveViewBreakpoint,
    navBarHeight,
    sideBarWidth,
    iconRowWidth,
    appState,
    docState,
    chatState,
    appDispatch,
    docDispatch,
    chatDispatch,
  };

  const renderLayers = () => {
    switch (appState.activeLayer) {
      case layerNames.documentEdit:
        return <DocumentEdit {...paramsToPass} />;
      case layerNames.documents:
        return <Documents {...paramsToPass} />;
      case layerNames.chat:
        return <ChatTest {...paramsToPass} />;
    }
  };

  return (
    <div className="d-flex flex-column vh-100">
      <header>
        <DashboardNavBar {...paramsToPass} />
      </header>
      <main className="d-flex flex-column flex-grow-1" style={{ minHeight: 0 }}>
        <DashboardSideBarMobile {...paramsToPass} />
        <Row className="m-0 h-100" style={{ minHeight: 0 }}>
          <Col
            className={`text-bg-dark d-none d-${sideBarResponsiveViewBreakpoint}-block d-flex flex-column h-100`}
            style={{
              maxWidth: sideBarWidth,
              zIndex: 100,
              minHeight: 0,
            }}
          >
            <DashboartSidebarDesktop {...paramsToPass} />
          </Col>
          <Col
            className="d-flex flex-column h-100"
            style={{ minWidth: 0, minHeight: 0 }}
          >
            {renderLayers()}
          </Col>
        </Row>
      </main>
    </div>
  );
}

export default DashBoardWripper;
