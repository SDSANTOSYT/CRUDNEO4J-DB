import React, { useState } from "react";

import "./Modal.css";

export const Modal = ({ closeModal, onSubmit, defaultValue, formFields }) => {
  const [formState, setFormState] = useState(
    defaultValue || Object.fromEntries(formFields.map((field) => [field, " "]))
  );

  const [errors, setErrors] = useState("");

  const validateForm = () => {
    if (Object.values(formState).every((value) => value && value.tim !== "")) {
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
                <input
                  type="text"
                  name={field}
                  value={formState[field]}
                  onChange={handleChange}
                />
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
