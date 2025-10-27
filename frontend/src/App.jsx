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
  
  // Estados para Inciso C
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedPostId, setSelectedPostId] = useState("");
  const [postsUsuario, setPostsUsuario] = useState([]);
  const [comentariosPost, setComentariosPost] = useState([]);
  const [loadingConsulta1, setLoadingConsulta1] = useState(false);
  const [loadingConsulta2, setLoadingConsulta2] = useState(false);

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
      console.log(`🔍 Fetching from: http://localhost:5000${config.endpoint}`);

      const response = await fetch(`http://localhost:5000${config.endpoint}`);

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log(`📦 Data received from backend:`, data);

      // Transformar datos según el tipo de entidad
      const transformedData = transformDataByTab(data, selectedTab);
      console.log(`✨ Transformed data:`, transformedData);

      setRows(transformedData);
    } catch (err) {
      setError(err.message);
      console.error("❌ Error fetching data:", err);
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
    console.log(JSON.stringify(dataToSend));

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

  // Función para consultar posts de un usuario (Inciso C - Consulta 1)
  const consultarPostsUsuario = async () => {
    console.log("=== CONSULTA 1 INICIADA ===");
    console.log("Usuario ID:", selectedUserId);
    
    if (!selectedUserId) {
      alert("Por favor ingresa un ID de Usuario");
      return;
    }

    setLoadingConsulta1(true);
    try {
      const url = `http://localhost:5000/consulta/posts-usuario/${selectedUserId}`;
      console.log("Fetching URL:", url);
      
      const response = await fetch(url);
      console.log("Response status:", response.status);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("✅ Posts del usuario recibidos:", data);
      console.log("Cantidad de posts:", data.length);
      
      setPostsUsuario(data);
    } catch (err) {
      console.error("❌ Error consultando posts del usuario:", err);
      setPostsUsuario([]);
      alert("Error al consultar posts del usuario: " + err.message);
    } finally {
      setLoadingConsulta1(false);
    }
  };

  // Función para consultar comentarios de un POST (Inciso C - Consulta 2)
  const consultarComentariosPost = async () => {
    console.log("=== CONSULTA 2 INICIADA ===");
    console.log("Post ID:", selectedPostId);
    
    if (!selectedPostId) {
      alert("Por favor ingresa un ID de Post");
      return;
    }

    setLoadingConsulta2(true);
    try {
      const url = `http://localhost:5000/consulta/comentarios-post/${selectedPostId}`;
      console.log("Fetching URL:", url);
      
      const response = await fetch(url);
      console.log("Response status:", response.status);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("✅ Comentarios del post recibidos:", data);
      console.log("Cantidad de comentarios:", data.length);
      
      setComentariosPost(data);
    } catch (err) {
      console.error("❌ Error consultando comentarios:", err);
      setComentariosPost([]);
      alert("Error al consultar comentarios del post: " + err.message);
    } finally {
      setLoadingConsulta2(false);
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
          <p>Selecciona Usuario, Post o Comentario para comenzar</p>
        </div>
      ) : (
        <div className="table-container">
          {loading && <p>Cargando datos...</p>}
          {error && <p style={{ color: "var(--color1)" }}>Error: {error}</p>}

          {!loading && rows.length > 0 && (
            <Table
              rows={rows}
              deleteRow={handleDeleteRow}
              editRow={handleEditRow}
            />
          )}

          {!loading && rows.length === 0 && !error && (
            <p>No hay datos para mostrar</p>
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

      {/* Sección Inciso C */}
      <div style={{ marginTop: "60px", marginBottom: "60px" }}>
        <h2 style={{ marginBottom: "40px" }}>Inciso C - Consultas</h2>
        
        {/* Consulta 1: Posts de un Usuario */}
        <div className="table-container" style={{ marginBottom: "40px", minHeight: "auto", height: "auto", padding: "30px" }}>
          <h3 style={{ color: "var(--color4)", fontSize: "24px", marginBottom: "15px", fontFamily: "Arial, Helvetica, sans-serif" }}>
            Consulta 1: Posts de un Usuario
          </h3>
          <p>Muestra los posts que ha creado un usuario específico</p>

          <div style={{ marginBottom: "30px", display: "flex", gap: "15px", alignItems: "center", flexWrap: "wrap" }}>
            <label style={{ color: "var(--color4)", fontWeight: "bold", fontFamily: "Arial, Helvetica, sans-serif" }}>
              ID del Usuario:
            </label>
            <input
              type="text"
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              placeholder="Ej: u1"
              style={{
                padding: "10px",
                borderRadius: "10px",
                border: "none",
                width: "200px",
                fontFamily: "Arial, Helvetica, sans-serif"
              }}
            />
            <button
              className="btn"
              onClick={consultarPostsUsuario}
              disabled={loadingConsulta1}
            >
              {loadingConsulta1 ? "Consultando..." : "Consultar"}
            </button>
          </div>

          {loadingConsulta1 ? (
            <p>Cargando...</p>
          ) : postsUsuario.length > 0 ? (
            <div className="table-wrapper">
              <Table
                rows={postsUsuario}
                deleteRow={() => {}}
                editRow={() => {}}
              />
            </div>
          ) : (
            <p>No hay posts para mostrar. Ingresa un ID de usuario y presiona Consultar.</p>
          )}
        </div>

        {/* Consulta 2: Comentarios de un Post */}
        <div className="table-container" style={{ minHeight: "auto", height: "auto", padding: "30px" }}>
          <h3 style={{ color: "var(--color4)", fontSize: "24px", marginBottom: "15px", fontFamily: "Arial, Helvetica, sans-serif" }}>
            Consulta 2: Comentarios de un POST
          </h3>
          <p>Lista los comentarios de un POST mostrando fecha de creación, fecha de autorización, usuario que lo hizo y si fue "megusta" o "nomegusta"</p>

          <div style={{ marginBottom: "30px", display: "flex", gap: "15px", alignItems: "center", flexWrap: "wrap" }}>
            <label style={{ color: "var(--color4)", fontWeight: "bold", fontFamily: "Arial, Helvetica, sans-serif" }}>
              ID del Post:
            </label>
            <input
              type="text"
              value={selectedPostId}
              onChange={(e) => setSelectedPostId(e.target.value)}
              placeholder="Ej: p1"
              style={{
                padding: "10px",
                borderRadius: "10px",
                border: "none",
                width: "200px",
                fontFamily: "Arial, Helvetica, sans-serif"
              }}
            />
            <button
              className="btn"
              onClick={consultarComentariosPost}
              disabled={loadingConsulta2}
            >
              {loadingConsulta2 ? "Consultando..." : "Consultar"}
            </button>
          </div>

          {loadingConsulta2 ? (
            <p>Cargando...</p>
          ) : comentariosPost.length > 0 ? (
            <div className="table-wrapper">
              <Table
                rows={comentariosPost}
                deleteRow={() => {}}
                editRow={() => {}}
              />
            </div>
          ) : (
            <p>No hay comentarios para mostrar. Ingresa un ID de post y presiona Consultar.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;