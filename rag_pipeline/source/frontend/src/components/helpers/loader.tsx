import Spinner from "react-bootstrap/Spinner";

const Loader = () => {
  return (
    <div className="d-flex justify-content-center align-items-center h-100">
      <div className="text-center">
        <Spinner animation="border" variant="success" />
        <p>Loading</p>
      </div>
    </div>
  );
};

export default Loader;
