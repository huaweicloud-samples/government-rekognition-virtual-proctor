import React, { useEffect, useState } from "react";
import { Button, Nav, Navbar } from "react-bootstrap";

import { getUsername } from "../utils/auth";

import AddUserModal from "./AddUserModal";
import ProctorButton from "./ProctorButton";

import "./Header.css";

const Header = ({ addUser, readyToStream, signedIn, toggleProctor, signOut }) => {
  const [userEmail, setUserEmail] = useState(undefined);

  useEffect(() => {
    if (signedIn) setUserEmail(getUsername());
    else setUserEmail(undefined);
  }, [signedIn]);

  return (
    <Navbar bg="dark" expand="lg">
      <Navbar.Brand>
        <span className="brand-title">Virtual Proctor</span>
      </Navbar.Brand>
      <Navbar.Toggle />
      {userEmail && (
        <Navbar.Collapse className="justify-content-end">
          <Nav>
            <span className="navbar-user">{userEmail}</span>
            <ProctorButton onClick={toggleProctor} enabled={readyToStream} />
            <AddUserModal onSave={addUser} />
            <Button onClick={signOut} variant="warning" size="sm">
              Sign Out
            </Button>
          </Nav>
        </Navbar.Collapse>
      )}
    </Navbar>
  );
};

export default Header;
