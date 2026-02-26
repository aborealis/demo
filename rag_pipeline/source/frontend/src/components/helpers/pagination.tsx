import Pagination from "react-bootstrap/Pagination";
import type {
  DocAction,
  DocState,
} from "../dashboard_wripper/helpers/docReducer";

interface Props {
  docState: DocState;
  docDispatch: React.ActionDispatch<[action: DocAction]>;
  setIsLoading: (flag: boolean) => void;
}

const MyPagination = (props: Props) => {
  const { docState, docDispatch, setIsLoading } = props;
  const nPages = Math.ceil(
    docState.documents.total_count / docState.docsPerPage,
  );
  const pageNumbers = [...Array(nPages + 1).keys()].slice(1);

  const nextPage = () => {
    if (docState.currentPage !== nPages)
      docDispatch({ type: "SET_CURRENT_PAGE", page: docState.currentPage + 1 });
  };
  const prevPage = () => {
    if (docState.currentPage !== 1)
      docDispatch({ type: "SET_CURRENT_PAGE", page: docState.currentPage - 1 });
  };

  const handleClick = (page: number) => {
    docDispatch({ type: "SET_CURRENT_PAGE", page });
    setIsLoading(true);
  };

  return (
    <Pagination>
      <Pagination.Prev onClick={prevPage} />
      {pageNumbers.map((n) => {
        const button = (
          <Pagination.Item
            key={n}
            onClick={() => handleClick(n)}
            active={n === docState.currentPage}
          >
            {n}
          </Pagination.Item>
        );

        // restored comment from original Russian source
        if ([1, nPages].includes(n)) return button;

        // restored comment from original Russian source
        if (n === 2) {
          if (nPages > 7 && docState.currentPage >= 5)
            return <Pagination.Ellipsis key={n} />;
          return button;
        }

        // restored comment from original Russian source
        if (n === nPages - 1) {
          if (nPages > 7 && docState.currentPage <= nPages - 4)
            return <Pagination.Ellipsis key={n} />;
          return button;
        }

        // restored comment from original Russian source
        if (nPages > 7) {
          if (docState.currentPage <= 3 && n <= 5) return button;
          if (docState.currentPage >= nPages - 2 && n >= nPages - 4)
            return button;
          if (Math.abs(docState.currentPage - n) < 2) return button;
        } else return button;

        return null;
      })}
      <Pagination.Next onClick={nextPage} />
    </Pagination>
  );
};

export default MyPagination;
