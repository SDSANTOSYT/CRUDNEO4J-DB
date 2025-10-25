import CustomButton from "./CustomButton";
import "../static/NavigationTab.css";


function NavigationTab({ selection, setSelection }) {
  const isUserSelected = selection == 1 ? true : false;
  const isPostSelected = selection == 2 ? true : false;
  const isCommentSelected = selection == 3 ? true : false;

  let selectUser = () => {
    setSelection(1);
    console.log(selection);
  };
  let selectPost = () => {
    setSelection(2);
    console.log(selection);
  };
  let selectComment = () => {
    setSelection(3);
    console.log(selection);
  };

  return (
    <ul>
      <li>
        <CustomButton
          label={"Usuario"}
          onClick={selectUser}
          selected={isUserSelected}
        />
      </li>
      <li>
        <CustomButton
          label={"Post"}
          onClick={selectPost}
          selected={isPostSelected}
        />
      </li>
      <li>
        <CustomButton
          label={"Comentario"}
          onClick={selectComment}
          selected={isCommentSelected}
        />
      </li>    

    </ul>

  );
}

export default NavigationTab;
