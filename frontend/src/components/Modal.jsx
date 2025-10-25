import React, { useState } from 'react'

import './Modal.css'

export const Modal = ({ closeModal, onSubmit, defaultValue }) => {

    const [formState, setFormState] = useState(defaultValue || {
        idu: '',
        nombre: ''
    });

    const[errors, setErrors] = useState("");

    const validateForm = () => {
        if(formState.idu && formState.nombre){
            setErrors("");
            return true;
        } else {
            let errorFields = [];
            for(const [key, value] of Object.entries(formState)){
                if(!value) errorFields.push(key);
            }

            setErrors(errorFields.join(", "));
            return false;
        }
    }

    const handleChange = (e) => {
        setFormState({
            ...formState,
            [e.target.name]: e.target.value
        });
    }

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!validateForm()) return;

        onSubmit(formState);

        closeModal();
    }

    return (
        <div className="modal-container" onClick={(e) => {
            if (e.target.className === 'modal-container') {
                closeModal()
            }
        }}>
            <div className="modal">
                <form>
                    <div className='form-group'>
                        <label htmlFor='idu'>Idu</label>
                        <input type="text" name='idu' value={formState.idu}
                            onChange={handleChange} />
                    </div>
                    <div className='form-group'>
                        <label htmlFor='nombre'>Nombre</label>
                        <input type="text" name='nombre' value={formState.nombre}
                            onChange={handleChange} />
                    </div>
                    {errors && <div className='error'>
                        {"Complete: " + errors}
                        </div>}
                    <button type='submit' className='btn' onClick={handleSubmit}>Guardar</button>
                </form>
            </div>
        </div>
    )
}
