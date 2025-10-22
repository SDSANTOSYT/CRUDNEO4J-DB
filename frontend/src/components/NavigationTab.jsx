import "../static/CustomButton.css";
import CustomButton from "./CustomButton";
import "../static/NavigationTab.css";

function NavigationTab({ label, onClick }) {
  return (
    <ul>
      <li>
        <CustomButton
          label={"Usuario"}
          onClick={() => {
            console.log("hola");
          }}
        />
      </li>
      <li>
        <CustomButton
          label={"Post"}
          onClick={() => {
            console.log("hola");
          }}
        />
      </li>
      <li>
        <CustomButton
          label={"Comentario"}
          onClick={() => {
            console.log("hola");
          }}
        />
      </li>
    </ul>
  );
}

export default NavigationTab;
