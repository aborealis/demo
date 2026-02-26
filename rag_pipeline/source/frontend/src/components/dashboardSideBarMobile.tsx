import { Offcanvas } from "react-bootstrap";
import { LeafFill } from "react-bootstrap-icons";
import SideBarContent from "./dashboardSidebarContent";
import type {
  AppAction,
  AppState,
} from "./dashboard_wripper/helpers/appReducer";

interface Props {
  appState: AppState;
  appDispatch: React.ActionDispatch<[action: AppAction]>;
  sideBarResponsiveViewBreakpoint: string;
  sideBarWidth: number;
  iconRowWidth: number;
}

const DashboardSideBarMobile = (props: Props) => {
  const {
    appState,
    appDispatch,
    sideBarResponsiveViewBreakpoint,
    sideBarWidth: sideBarWidthPixels,
    iconRowWidth,
  } = props;

  const paramsSideBarContent = {
    iconRowWidth,
    appState,
    appDispatch,
  };

  return (
    <Offcanvas
      show={appState.showSideBar}
      onHide={() => appDispatch({ type: "HIDE_SIDEBAR" })}
      className={`text-bg-dark d-${sideBarResponsiveViewBreakpoint}-none`}
      style={{ width: sideBarWidthPixels }}
    >
      <Offcanvas.Header
        className="bg-extra-dark border-grey-bottom"
        closeButton
        closeVariant="white"
        style={{
          height: 50,
        }}
      >
        <Offcanvas.Title className="fs-6">
          <div className="d-flex align-items-center">
            <div>
              <LeafFill
                className="text-success ms-2 me-2 mb-1"
                width="20"
                height="20"
              />
            </div>
            <div>Light Agents AI</div>
          </div>
        </Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body
        className="h-100 p-0"
        style={{ width: sideBarWidthPixels }}
      >
        <div className="d-flex d-align-items-stretch h-100">
          <SideBarContent {...paramsSideBarContent} />
        </div>
      </Offcanvas.Body>
    </Offcanvas>
  );
};

export default DashboardSideBarMobile;
