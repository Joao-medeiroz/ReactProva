"use client";

export default function FilterInput({ value, onChange }) {
  return (
    <input
      type="text"
      placeholder="Filtrar por nome ou email..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}
