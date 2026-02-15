import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <HashRouter basename={import.meta.env.BASE_URL}>
      <App />
    </HashRouter>
  </React.StrictMode>
);
