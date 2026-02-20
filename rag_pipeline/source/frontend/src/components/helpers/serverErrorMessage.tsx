import { Card } from "react-bootstrap";
interface Params {
  serverError: string;
}

const ServerErrorWindow = (props: Params) => {
  const { serverError } = props;

  return (
    <div className="d-flex h-100 align-items-center justify-content-center">
      <Card className="shadow col col-12 col-md-10 col-lg-6">
        <Card.Header>Error</Card.Header>
        <Card.Body>
          While requesting data from the server we have encountered the
          following error: {serverError}
        </Card.Body>
      </Card>
    </div>
  );
};

export default ServerErrorWindow;
