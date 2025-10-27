import { useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import NavigationTab from "./components/NavigationTab";
import modeloER from "./assets/modeloER.jpg";
import { Table } from "./components/Table";
import { Modal } from "./components/Modal";

function App() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTab, setSelection] = useState(null);
  const [rows, setRows] = useState([]);
  const [rowToEdit, setRowToEdit] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Mapeo de tabs a endpoints y tipos
  const tabConfig = {
    1: { endpoint: "/users", type: "user", label: "User" },
    2: { endpoint: "/posts", type: "post", label: "Post" },
    3: { endpoint: "/comments", type: "comment", label: "Comment" },
  };

  // Fetch data cuando cambia el tab
  useEffect(() => {
    if (selectedTab !== null) {
      fetchData();
    }
  }, [selectedTab]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const config = tabConfig[selectedTab];
      console.log(`Fetching from: http://localhost:5000${config.endpoint}`);

      const response = await fetch(`http://localhost:5000${config.endpoint}`);

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log(` Data received from backend:`, data);

      // Transformar datos según el tipo de entidad
      const transformedData = transformDataByTab(data, selectedTab);
      console.log(`Transformed data:`, transformedData);

      setRows(transformedData);
    } catch (err) {
      setError(err.message);
      console.error("Error fetching data:", err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  // Transformar datos según la estructura esperada
  const transformDataByTab = (data, tab) => {
    // Los datos ya vienen con la estructura correcta desde el backend
    // Solo retornamos los datos tal como están
    return data;
  };

  const handleEditRow = (idx) => {
    setRowToEdit(idx);
    setModalOpen(true);
  };

  const handleDeleteRow = async (targetIndex) => {
    const config = tabConfig[selectedTab];
    const rowToDelete = rows[targetIndex];

    // Obtener el ID correcto según el tipo de entidad
    let nodeId;
    if (selectedTab === 1) {
      nodeId = rowToDelete.idu;
    } else if (selectedTab === 2) {
      nodeId = rowToDelete.idp;
    } else if (selectedTab === 3) {
      nodeId = rowToDelete.consec;
    }

    try {
      const response = await fetch(
        `http://localhost:5000/node/${config.type}/${nodeId}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        throw new Error("Error al eliminar");
      }

      // Actualizar UI
      setRows(rows.filter((row, index) => index !== targetIndex));
    } catch (err) {
      setError(err.message);
      console.error("Error deleting:", err);
    }
  };

  const handleSubmit = async (newRow) => {
    const config = tabConfig[selectedTab];

    // Los datos ya vienen con los campos correctos del formulario
    const dataToSend = { ...newRow };

    try {
      if (rowToEdit === null) {
        // Crear nuevo
        const response = await fetch(
          `http://localhost:5000/node/${config.type}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dataToSend),
          }
        );

        if (!response.ok) {
          throw new Error("Error al crear");
        }

        // Recargar datos
        await fetchData();
      } else {
        // Actualizar existente
        const rowData = rows[rowToEdit];
        let nodeId;

        if (selectedTab === 1) {
          nodeId = rowData.idu;
        } else if (selectedTab === 2) {
          nodeId = rowData.idp;
        } else if (selectedTab === 3) {
          nodeId = rowData.consec;
        }

        const response = await fetch(
          `http://localhost:5000/node/${config.type}/${nodeId}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dataToSend),
          }
        );

        if (!response.ok) {
          throw new Error("Error al actualizar");
        }

        // Recargar datos
        await fetchData();
      }
    } catch (err) {
      setError(err.message);
      console.error("Error submitting:", err);
    }
  };

  // Obtener los campos del formulario según el tab
  const getFormFields = () => {
    if (selectedTab === null) return [];

    if (rows.length > 0) {
      return Object.keys(rows[0]);
    }

    // Retornar campos por defecto según el tab cuando no hay datos
    switch (selectedTab) {
      case 1:
        return ["idu", "nombre"];
      case 2:
        return ["idp", "contenido"];
      case 3:
        return ["consec", "fechorCom", "likeNotLike", "fechorAut", "contenido"];
      default:
        return [];
    }
  };

  return (
    <div className="page">
      <h1>CRUD NEO4J</h1>
      <div className="img-container">
        <h2>Modelo Entidad Relación</h2>
        <img src={modeloER} />
      </div>
      <NavigationTab selection={selectedTab} setSelection={setSelection} />

      {selectedTab === null ? (
        <div className="table-container">
          <p
            style={{
              textAlign: "center",
              padding: "40px",
              color: "#666",
              fontSize: "18px",
            }}
          >
            Selecciona Usuario, Post o Comentario para comenzar
          </p>
        </div>
      ) : (
        <div className="table-container">
          {loading && <p>Cargando datos...</p>}
          {error && <p style={{ color: "red" }}>Error: {error}</p>}

          {!loading && rows.length > 0 && (
            <Table
              rows={rows}
              deleteRow={handleDeleteRow}
              editRow={handleEditRow}
            />
          )}

          {!loading && rows.length === 0 && !error && (
            <p style={{ textAlign: "center", padding: "20px", color: "#666" }}>
              No hay datos para mostrar
            </p>
          )}

          <button
            className="btn"
            onClick={() => {
              setModalOpen(true);
              setRowToEdit(null);
            }}
          >
            Agregar Nuevo
          </button>

          {modalOpen && (
            <Modal
              closeModal={() => setModalOpen(false)}
              onSubmit={handleSubmit}
              defaultValue={rowToEdit !== null && rows[rowToEdit]}
              formFields={getFormFields()}
            />
          )}
        </div>
      )}
    </div>
  );
}

export default App;
