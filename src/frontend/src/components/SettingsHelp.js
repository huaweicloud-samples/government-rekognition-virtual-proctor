import React from "react";
import { Alert, Row } from "react-bootstrap";

const SettingsHelp = ({ show }) => {
  if (show) {
    return (
      <Row>
        <Alert variant="danger">
          There is an issue with your settings configuration. Make sure the
          deployment writes a <code>settings.js</code> file (defining{" "}
          <code>window.proctorSettings.apiEndpoint</code>) next to the static
          files, then reload this page.
        </Alert>
      </Row>
    );
  }
  return "";
};

export default SettingsHelp;
