import { Button, Navbar } from "react-bootstrap";
import { LeafFill, List } from "react-bootstrap-icons";

interface Props {
  sideBarShow: () => void;
  sideBarResponsiveViewBreakpoint: string;
  navBarHeight: number;
}

const DashboardNavBar = (props: Props) => {
  const { sideBarShow, sideBarResponsiveViewBreakpoint, navBarHeight } = props;

  return (
    <Navbar
      fixed="top"
      className={`text-bg-dark d-${sideBarResponsiveViewBreakpoint}-none`}
      style={{ height: navBarHeight, zIndex: 99 }}
    >
      <div className="d-flex align-items-center">
        <Button
          variant="transparent text-light"
          className={`d-${sideBarResponsiveViewBreakpoint}-none`}
          onClick={sideBarShow}
        >
          <List width="24" height="24" />
        </Button>
        <div>
          <LeafFill
            className="text-success ms-2 me-2 mb-1"
            width="20"
            height="20"
          />
        </div>
        <div>Light Agents AI</div>
      </div>
    </Navbar>
  );
};

export default DashboardNavBar;
