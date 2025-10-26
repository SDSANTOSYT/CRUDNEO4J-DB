import React from "react";
import { BsFillTrashFill, BsFillPencilFill } from "react-icons/bs";
import "./Table.css";

export const Table = ({ rows, deleteRow, editRow }) => {
  return (
    <div className="table-wrapper">
      <table className="table-generals table">
        <thead>
          <tr>
            {Object.keys(rows[0]).map((column) => {
              return <th key={column}>{column}</th>;
            })}
            <th>Accion</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => {
            return (
              <tr key={idx}>
                {Object.entries(row).map(([column, value]) => {
                  return column == Object.keys(row)[0] ? (
                    <td key={[Object.keys(row)[0], value]}>{value}</td>
                  ) : (
                    <td key={[Object.keys(row)[0], value]} className="expand">
                      {value}
                    </td>
                  );
                })}
                <td>
                  <span className="actions">
                    <BsFillTrashFill
                      className="delete-btn"
                      onClick={() => deleteRow(idx)}
                    />
                    <BsFillPencilFill onClick={() => editRow(idx)} />
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
