import React from "react";

function DragAndDrop({ children, onDrop, onDragOver }) {
  return <div onDrop={onDrop} onDragOver={onDragOver}>{children}</div>;
}

export default DragAndDrop;
