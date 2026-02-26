import { LeafFill } from "react-bootstrap-icons";
import SideBarContent from "./dashboardSidebarContent";
import type {
  AppAction,
  AppState,
} from "./dashboard_wripper/helpers/appReducer";

interface Props {
  sideBarWidth: number;
  navBarHeight: number;
  iconRowWidth: number;
  appState: AppState;
  appDispatch: React.ActionDispatch<[action: AppAction]>;
}

const DashboartSidebarDesktop = (props: Props) => {
  const { sideBarWidth, navBarHeight, iconRowWidth, appState, appDispatch } =
    props;

  const paramsSideBarContent = {
    iconRowWidth,
    appState,
    appDispatch,
  };

  return (
    <div
      className="text-bg-dark fixed-top h-100"
      style={{ maxWidth: sideBarWidth }}
    >
      <div
        style={{
          height: navBarHeight,
        }}
        className="d-flex align-items-center p-2 ps-3 bg-extra-dark border-grey-bottom"
      >
        <div>
          <LeafFill
            className="text-success ms-2 me-2 mb-1"
            width="20"
            height="20"
          />
        </div>
        <div>Light Agents AI</div>
      </div>
      <div className="d-flex align-items-stretch h-100">
        <SideBarContent {...paramsSideBarContent} />
      </div>
    </div>
  );
};

export default DashboartSidebarDesktop;
