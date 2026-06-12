import React from "react";

function FileInput({ onFileChange, inputRef, id }) {
  return <input id={id} ref={inputRef} type="file" accept=".exe" onChange={onFileChange} className="sr-only" />;
}

export default FileInput;
