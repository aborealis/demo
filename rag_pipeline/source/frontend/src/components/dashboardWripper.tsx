import { Col, Row } from "react-bootstrap";
import DashboardNavBar from "./dashboardNavBar";
import { useState, type ReactNode } from "react";
import DashboardSideBarMobile from "./dashboardSideBarMobile";
import DashboartSidebarDesktop from "./dashboardSideBarDesktop";
import Documents from "./documents";
import { layerNames } from "./helpers/constants";
import { docsViewInitState, type DocViewState } from "./helpers/types";
import DocumentEdit from "./documentEdit";
import Tests from "./tests";

function DashBoardWripper() {
  const sideBarResponsiveViewBreakpoint = "lg";
  const sideBarWidth = 230;
  const navBarHeight = 50;
  const iconRowWidth = 50;

  const [showSideBar, setSideBarShow] = useState(false);
  const sideBarClose = () => setSideBarShow(false);
  const sideBarShow = () => setSideBarShow(true);

  const [activeLayer, setActiveLayer] = useState(layerNames.documents);
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [spentTokens, setSpentTokens] = useState(0);
  const [docsViewState, setDocsViewState] =
    useState<DocViewState>(docsViewInitState);
  const [messages, setMessages] = useState<ReactNode[]>([]);
  const [wsURL, setWsURL] = useState("");

  const paramsToPass = {
    showSideBar,
    sideBarShow,
    sideBarClose,
    sideBarResponsiveViewBreakpoint,
    navBarHeight,
    sideBarWidth,
    iconRowWidth,
    activeLayer,
    setActiveLayer,
    isAuthenticated,
    setIsAuthenticated,
    spentTokens,
    setSpentTokens,
    docsViewState,
    setDocsViewState,
    messages,
    setMessages,
    wsURL,
    setWsURL,
  };

  const renderLayers = () => {
    switch (activeLayer) {
      case layerNames.documentEdit:
        return <DocumentEdit {...paramsToPass} />;
      case layerNames.documents:
        return <Documents {...paramsToPass} />;
      case layerNames.chat:
        return <Tests {...paramsToPass} />;
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
