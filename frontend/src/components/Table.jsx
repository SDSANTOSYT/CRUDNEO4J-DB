import React from 'react'
import { BsFillTrashFill, BsFillPencilFill } from 'react-icons/bs'
import './Table.css'

export const Table = ({ rows, deleteRow, editRow }) => {
    return (
        <div className="table-wrapper">
            <table className='table-generals table'>
                <thead>
                    <tr>
                        <th>idu</th>
                        <th className="expand" >nombre</th>
                        <th>Accion</th>
                    </tr>
                </thead>
                <tbody>
                    {
                        rows.map((row, idx) => {
                            return <tr key={idx}>
                                <td>{row.idu}</td>
                                <td className="expand" >{row.nombre}</td>
                                <td>
                                    <span className="actions">
                                        <BsFillTrashFill className="delete-btn" onClick={()=> deleteRow(idx)} />
                                        <BsFillPencilFill onClick= {() => editRow(idx)} />
                                    </span>
                                </td>
                            </tr>
                        })
                    }
                </tbody>
            </table>
        </div>
    )
}
