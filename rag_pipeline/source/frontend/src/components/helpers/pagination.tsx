import Pagination from "react-bootstrap/Pagination";
import type { DocViewState } from "./types";

interface Props {
  nPages: number;
  docsViewState: DocViewState;
  setDocsViewState: React.Dispatch<React.SetStateAction<DocViewState>>;
  setIsLoading: (flag: boolean) => void;
}

const MyPagination = (props: Props) => {
  const { nPages, docsViewState, setDocsViewState, setIsLoading } = props;
  const pageNumbers = [...Array(nPages + 1).keys()].slice(1);

  const setCurrentPage = (page: number) => {
    setDocsViewState((prev) => ({ ...prev, currentPage: page }));
  };
  const nextPage = () => {
    if (docsViewState.currentPage !== nPages)
      setCurrentPage(docsViewState.currentPage + 1);
  };
  const prevPage = () => {
    if (docsViewState.currentPage !== 1)
      setCurrentPage(docsViewState.currentPage - 1);
  };

  const handleClick = (page: number) => {
    setCurrentPage(page);
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
            active={n === docsViewState.currentPage}
          >
            {n}
          </Pagination.Item>
        );

        // restored comment from original Russian source
        if ([1, nPages].includes(n)) return button;

        // restored comment from original Russian source
        if (n === 2) {
          if (nPages > 7 && docsViewState.currentPage >= 5)
            return <Pagination.Ellipsis key={n} />;
          return button;
        }

        // restored comment from original Russian source
        if (n === nPages - 1) {
          if (nPages > 7 && docsViewState.currentPage <= nPages - 4)
            return <Pagination.Ellipsis key={n} />;
          return button;
        }

        // restored comment from original Russian source
        if (nPages > 7) {
          if (docsViewState.currentPage <= 3 && n <= 5) return button;
          if (docsViewState.currentPage >= nPages - 2 && n >= nPages - 4)
            return button;
          if (Math.abs(docsViewState.currentPage - n) < 2) return button;
        } else return button;

        return null;
      })}
      <Pagination.Next onClick={nextPage} />
    </Pagination>
  );
};

export default MyPagination;
