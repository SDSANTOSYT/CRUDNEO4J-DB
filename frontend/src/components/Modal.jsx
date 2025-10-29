import React, { useState } from "react";

import "./Modal.css";

export const Modal = ({ closeModal, onSubmit, defaultValue, formFields, entityType }) => {
  const [formState, setFormState] = useState(
    defaultValue || Object.fromEntries(formFields.map((field) => [field, ""]))
  );

  const [errors, setErrors] = useState("");

  const validateForm = () => {
    if (Object.values(formState).every((value) => value && value.trim !== "")) {
      setErrors("");
      return true;
    } else {
      let errorFields = [];
      for (const [key, value] of Object.entries(formState)) {
        if (!value) errorFields.push(key);
      }

      setErrors(errorFields.join(", "));
      return false;
    }
  };

  const handleChange = (e) => {
    setFormState({
      ...formState,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    onSubmit(formState);

    closeModal();
  };

  // Función para determinar el tipo de input
  const getInputType = (field) => {
    if (field === "fechorCom" || field === "fechorAut") {
      return "datetime-local";
    }
    return "text";
  };

  return (
    <div
      className="modal-container"
      onClick={(e) => {
        if (e.target.className === "modal-container") {
          closeModal();
        }
      }}
    >
      <div className="modal">
        <form>
          {formFields.map((field) => {
            return (
              <div key={field} className="form-group">
                <label htmlFor={field}>{field}</label>
                
                {/* Select especial para likeNotLike */}
                {field === "likeNotLike" ? (
                  <select
                    name={field}
                    value={formState[field] || ""}
                    onChange={handleChange}
                    style={{
                      padding: "10px",
                      borderRadius: "10px",
                      border: "1px solid #ddd",
                      width: "100%",
                      fontFamily: "Arial, Helvetica, sans-serif",
                      fontSize: "14px"
                    }}
                  >
                    <option value="">Selecciona una opción...</option>
                    <option value="megusta">👍 Me gusta</option>
                    <option value="nomegusta">👎 No me gusta</option>
                  </select>
                ) : (
                  <input
                    type={getInputType(field)}
                    name={field}
                    value={formState[field] || ""}
                    onChange={handleChange}
                    placeholder={
                      field === "fechorCom" ? "Fecha del comentario" :
                      field === "fechorAut" ? "Fecha de autorización" : ""
                    }
                    style={{
                      fontFamily: "Arial, Helvetica, sans-serif"
                    }}
                  />
                )}
              </div>
            );
          })}
          {errors && <div className="error">{"Complete: " + errors}</div>}
          <button type="submit" className="btn" onClick={handleSubmit}>
            Guardar
          </button>
        </form>
      </div>
    </div>
  );
};