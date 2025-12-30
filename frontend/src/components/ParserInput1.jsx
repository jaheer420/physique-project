// frontend/src/components/ParserInput1.jsx
import React, { useState } from "react";

export default function ParserInput1({ onSubmit }) {
  const [text, setText] = useState("");

  const handleClick = () => {
    onSubmit(text);
    setText("");
  };

  return (
    <div style={{ marginBottom: 20 }}>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="e.g. I ate 4 idlis"
        style={{ width: 280, padding: 8, marginRight: 10 }}
      />
      <button onClick={handleClick}>Submit</button>
    </div>
  );
}
