import React from "react";
import { Button, Modal } from "react-bootstrap";
import useLocalStorage from "../hooks/useLocalStorage";

const ConsentModal = () => {
  const [hasConsent, setHasConsent] = useLocalStorage(
    "virtualProctorConsent",
    false
  );

  const onClick = () => {
    setHasConsent(true);
  };

  return (
    <Modal show={!hasConsent} backdrop="static" centered>
      <Modal.Header>
        <Modal.Title>Notice</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        This feature uses a cloud face recognition service. Biometric
        identifiers and biometric information ("biometric data") may be
        collected, stored, and processed by the service provider for the
        purpose of comparing the image of an individual with a stored image for
        identity verification, fraud prevention, and security purposes.
        Biometric information generated as part of this process will be
        retained in line with the service provider's privacy policy. You hereby
        provide your express, informed, written release and consent for the
        service to collect, use, and store your biometric data as described
        herein.
      </Modal.Body>
      <Modal.Footer>
        <Button variant="primary" onClick={onClick}>
          Accept
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ConsentModal;
