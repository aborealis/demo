import { menuStructure } from "./helpers/constants";

interface Params {
  iconRowWidth: number;
  activeLayer: string;
  setActiveLayer: (layerName: string) => void;
  sideBarClose: () => void;
}

const SideBarContent = (props: Params) => {
  const { iconRowWidth, activeLayer, setActiveLayer, sideBarClose } = props;

  const handleOnClick = (submenu: string, disabled = false) => {
    if (disabled) return;
    setActiveLayer(submenu);
    sideBarClose();
  };

  return (
    <>
      <div className="border-grey-right" style={{ width: iconRowWidth }}>
        {menuStructure.map((menu, index) => {
          const firstEnabledSubmenu = Object.keys(menu.items).find(
            (submenu) =>
              menu.items[submenu].visible && !menu.items[submenu].disabled,
          );

          return (
            <div
              key={index}
              className={
                Object.keys(menu.items).includes(activeLayer)
                  ? `fs-4 menu-icon active`
                  : `fs-4 menu-icon`
              }
              onClick={() => {
                if (!firstEnabledSubmenu) return;
                handleOnClick(firstEnabledSubmenu);
              }}
            >
              {menu.icon}
            </div>
          );
        })}
      </div>
      <div className="p-3">
        {menuStructure.map((menu) => {
          return (
            Object.keys(menu.items).includes(activeLayer) &&
            Object.keys(menu.items).map((submenu) => {
              if (!menu.items[submenu].visible) return null;

              const isDisabled = menu.items[submenu].disabled;
              const isActive = menu.items[submenu].activeFor.includes(activeLayer);

              return (
                <p
                  className={
                    isDisabled
                      ? "submenu text-secondary opacity-50"
                      : isActive
                        ? "submenu active"
                        : "submenu"
                  }
                  style={isDisabled ? { cursor: "not-allowed" } : undefined}
                  onClick={() => handleOnClick(submenu, isDisabled)}
                  key={submenu}
                >
                  <small>{submenu}</small>
                </p>
              );
            })
          );
        })}
      </div>
    </>
  );
};

export default SideBarContent;
