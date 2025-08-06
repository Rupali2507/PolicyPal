import React from "react";
import "./Main.css";
import DocumentQA from "../DocumentQA/DocumentQA";

const Main = () => {
  return (
    <div className="main">
      <div className="nav">
        <p>PolicyPal</p>
        <img
          src="https://cdn3.iconfinder.com/data/icons/avatars-9/145/Avatar_Dog-512.png"
          alt="User Avatar"
        />
      </div>

      {/* This container will center everything */}
      <div className="main-content-area">
        <div className="main-header">
          <h1>Welcome to PolicyPal</h1>
          <p className="subtitle">Ask questions about any policy document</p>
        </div>

        {/* This is the new home for our component */}
        <DocumentQA />
      </div>
    </div>
  );
};

export default Main;
