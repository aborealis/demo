import type {
  AppAction,
  AppState,
} from "./dashboard_wripper/helpers/appReducer";
import { menuStructure } from "./helpers/constants";

interface Params {
  iconRowWidth: number;
  appState: AppState;
  appDispatch: React.ActionDispatch<[action: AppAction]>;
}

const SideBarContent = (props: Params) => {
  const { iconRowWidth, appState, appDispatch } = props;

  const handleOnClick = (submenu: string, disabled = false) => {
    if (disabled) return;
    appDispatch({ type: "SET_LAYER", layer: submenu });
    appDispatch({ type: "HIDE_SIDEBAR" });
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
                Object.keys(menu.items).includes(appState.activeLayer)
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
            Object.keys(menu.items).includes(appState.activeLayer) &&
            Object.keys(menu.items).map((submenu) => {
              if (!menu.items[submenu].visible) return null;

              const isDisabled = menu.items[submenu].disabled;
              const isActive = menu.items[submenu].activeFor.includes(
                appState.activeLayer,
              );

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
