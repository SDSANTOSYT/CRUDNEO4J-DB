import "../static/CustomButton.css";

function CustomButton({ label, onClick }) {
  return (
    <div>
      <button onClick={onClick}>
        <h3>{label.toUpperCase()}</h3>
      </button>
    </div>
  );
}

export default CustomButton;
