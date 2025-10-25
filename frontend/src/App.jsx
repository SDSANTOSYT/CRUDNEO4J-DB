import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import NavigationTab from "./components/NavigationTab";
import modeloER from "./assets/modeloER.jpg";
import { Table } from "./components/Table";
import { Modal } from "./components/Modal";

function App() {

  const [modalOpen, setModalOpen] = useState(false);

  const [selectedTab, setSelection] = useState(0);

  const [rows, setRows] = useState([
    { idu: 1, nombre: "Juan" },
    { idu: 2, nombre: "Sebas" },
    { idu: 3, nombre: "Carlos" },
  ]);

  const [rowToEdit, setRowToEdit] = useState(null);

  const handleEditRow = (idx) => {
    setRowToEdit(idx);
    setModalOpen(true);
  }

  const handleDeleteRow = (targetIndex) => {
    setRows(rows.filter((row, index) => index !== targetIndex));
  }

  const handleSubmit = (newRow) => {
    rowToEdit === null ?
      setRows([...rows, newRow]) :
      setRows(
        rows.map((currRow, idx) => {
          if (idx !== rowToEdit) return currRow;
          return newRow;
        }))
  };

  return (
    <div className="page">
      <h1>CRUD NEO4J</h1>
      <div className="img-container">
        <h2>Modelo Entidad Relación</h2>
        <img src={modeloER} />
      </div>
      <NavigationTab selection={selectedTab} setSelection={setSelection} />

      <div className="table-container">
        <Table rows={rows} deleteRow={handleDeleteRow} editRow={handleEditRow} />
        <button className="btn"
          onClick={() => {
            setModalOpen(true);
            setRowToEdit(null);
          }} >Agregar Nuevo</button>
        {modalOpen &&
          <Modal closeModal={() =>
            setModalOpen(false)}
            onSubmit={handleSubmit}
            defaultValue={rowToEdit !== null && rows[rowToEdit]}
          />}
      </div>

    </div>
  );
}

export default App;
