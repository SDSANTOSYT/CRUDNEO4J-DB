import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import NavigationTab from "./components/NavigationTab";
import modeloER from "./assets/modeloER.jpg";

function App() {
  const [selectedTab, setSelection] = useState(0);
  return (
    <div className="page">
      <h1>CRUD NEO4J</h1>
      <div className="img-container">
        <h2>Modelo Entidad Relación</h2>
        <img src={modeloER} />
      </div>
      <NavigationTab selection={selectedTab} setSelection={setSelection} />
      <div className="table-container"></div>
    </div>
  );
}

export default App;
