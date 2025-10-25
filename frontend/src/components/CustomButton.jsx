import "../static/CustomButton.css";

function CustomButton({ label, onClick, selected = false }) {
  return (
    <div>
      <button className={selected ? "selected" : ""} onClick={onClick}>
        <h3>{label.toUpperCase()}</h3>
      </button>
    </div>
  );
}

export default CustomButton;
