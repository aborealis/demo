import { Offcanvas } from "react-bootstrap";
import { LeafFill } from "react-bootstrap-icons";
import SideBarContent from "./dashboardSidebarContent";

interface Props {
  showSideBar: boolean;
  sideBarClose: () => void;
  sideBarResponsiveViewBreakpoint: string;
  sideBarWidth: number;
  iconRowWidth: number;
  activeLayer: string;
  setActiveLayer: (layerName: string) => void;
}

const DashboardSideBarMobile = (props: Props) => {
  const {
    showSideBar,
    sideBarClose,
    sideBarResponsiveViewBreakpoint,
    sideBarWidth: sideBarWidthPixels,
    iconRowWidth,
    activeLayer,
    setActiveLayer,
  } = props;

  const paramsSideBarContent = {
    iconRowWidth,
    activeLayer,
    setActiveLayer,
    sideBarClose,
  };

  return (
    <Offcanvas
      show={showSideBar}
      onHide={sideBarClose}
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
