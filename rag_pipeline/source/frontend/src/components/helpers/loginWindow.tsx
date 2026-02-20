import { Button, Card, Form } from "react-bootstrap";
import { useState } from "react";
import { APIs } from "./constants";

interface Params {
  setIsAuthenticated: (flag: boolean) => void;
}

const Login = (params: Params) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string }>(
    {},
  );
  const { setIsAuthenticated } = params;

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(APIs.login, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem("AuthToken", data.access_token);
      setIsAuthenticated(true);
    } else if (response.status === 401) {
      setIsAuthenticated(false);
      const data = await response.json();
      if (data.detail === "Invalid username") {
        setErrors({ email: "Invalid email" });
      } else if (data.detail === "Invalid password") {
        setErrors({ password: "Invalid password" });
      }
    } else {
      setIsAuthenticated(false);
      console.error("Unexpected error", response.status);
    }
  };

  return (
    <div className="d-flex h-100 align-items-center justify-content-center">
      <Card className="shadow col col-12 col-md-10 col-lg-6">
        <Card.Header>Log in</Card.Header>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Email address</Form.Label>
              <Form.Control
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                isInvalid={!!errors.email}
              />
              <Form.Control.Feedback type="invalid">
                {errors.email}
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                isInvalid={!!errors.password}
              />
              <Form.Control.Feedback type="invalid">
                {errors.password}
              </Form.Control.Feedback>
            </Form.Group>

            <Button
              type="submit"
              variant="success"
              size="lg"
              className="w-100 mt-2"
            >
              Log in
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default Login;
