import { LeafFill } from "react-bootstrap-icons";
import SideBarContent from "./dashboardSidebarContent";

interface Props {
  sideBarWidth: number;
  navBarHeight: number;
  iconRowWidth: number;
  activeLayer: string;
  setActiveLayer: (layerName: string) => void;
  sideBarClose: () => void;
}

const DashboartSidebarDesktop = (props: Props) => {
  const {
    sideBarWidth,
    navBarHeight,
    iconRowWidth,
    activeLayer,
    setActiveLayer,
    sideBarClose,
  } = props;

  const paramsSideBarContent = {
    iconRowWidth,
    activeLayer,
    setActiveLayer,
    sideBarClose,
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
