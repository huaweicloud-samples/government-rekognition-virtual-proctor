import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import { Alert, Button, Col, Form, Row } from "react-bootstrap";

import gateway from "./utils/gateway";
import { clearAuth, isAuthenticated } from "./utils/auth";
import { login } from "./utils/request";

import CameraHelp from "./components/CameraHelp";
import EngagementSummary from "./components/EngagementsSummary";
import Header from "./components/Header";
import SettingsHelp from "./components/SettingsHelp";
import ConsentModal from "./components/ConsentModal";

const App = () => {
  const [signedIn, setSignedIn] = useState(isAuthenticated());
  const [readyToStream, setReadyToStream] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [loginError, setLoginError] = useState(null);
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const iterating = useRef(false);
  const webcam = useRef(undefined);

  const addUser = (params) => gateway.addUser(params);

  const getSnapshot = () => {
    const image = webcam.current.getScreenshot();
    const b64Encoded = image.split(",")[1];

    gateway.processImage(b64Encoded).then((response) => {
      if (response) setTestResults(response);
      if (iterating.current) setTimeout(getSnapshot, 300);
      else setTestResults([]);
    });
  };

  const setupWebcam = (instance) => {
    webcam.current = instance;

    const checkIfReady = () => {
      if (
        webcam.current &&
        webcam.current.state &&
        webcam.current.state.hasUserMedia
      ) {
        setReadyToStream(true);
      } else setTimeout(checkIfReady, 250);
    };

    checkIfReady();
  };

  const toggleProctor = () => {
    iterating.current = !iterating.current;

    if (iterating.current) {
      getSnapshot();
    } else setTestResults([]);
  };

  const signIn = (e) => {
    e.preventDefault();
    setLoginError(null);
    login(loginForm.username, loginForm.password)
      .then(() => setSignedIn(true))
      .catch((err) => setLoginError(err.message || "Authentication failed"));
  };

  const signOut = () => {
    clearAuth();
    iterating.current = false;
    setTestResults([]);
    setSignedIn(false);
  };

  const onFieldChange = (field) => (e) =>
    setLoginForm({ ...loginForm, [field]: e.target.value });

  return (
    <div className="App">
      <Header
        addUser={addUser}
        readyToStream={readyToStream}
        signedIn={signedIn}
        toggleProctor={toggleProctor}
        signOut={signOut}
      />
      <ConsentModal />
      {signedIn ? (
        <>
          <SettingsHelp show={!window.proctorSettings} />
          <CameraHelp show={!readyToStream} />
          <Row>
            <Col md={8} sm={6}>
              <Webcam
                ref={setupWebcam}
                screenshotFormat="image/jpeg"
                videoConstraints={{
                  width: 1280,
                  height: 640,
                  facingMode: "user",
                }}
                style={{ width: "100%", marginTop: "10px" }}
              />
            </Col>
            <Col md={4} sm={6}>
              <EngagementSummary testResults={testResults} />
            </Col>
          </Row>
        </>
      ) : (
        <div className="auth-container">
          <Form className="auth-form" onSubmit={signIn}>
            <h3>Sign in</h3>
            <p className="auth-hint">
              Use the account created in the deployment configuration.
            </p>
            {loginError && <Alert variant="danger">{loginError}</Alert>}
            <Form.Group controlId="username">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                value={loginForm.username}
                onChange={onFieldChange("username")}
                autoComplete="username"
              />
            </Form.Group>
            <Form.Group controlId="password">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                value={loginForm.password}
                onChange={onFieldChange("password")}
                autoComplete="current-password"
              />
            </Form.Group>
            <Button
              variant="primary"
              type="submit"
              disabled={!loginForm.username || !loginForm.password}
            >
              Sign in
            </Button>
          </Form>
        </div>
      )}
    </div>
  );
};

export default App;
