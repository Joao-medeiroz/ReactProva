"use client";

import { useState } from "react";

const ContactForm = ({ onAdd }) => {
    const [form, setForm] = useState({nome: "", email: "", telefone: "",});

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({...prev, [name]: value,}));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onAdd(form);
        setForm({nome: "", email: "", telefone: "",})
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label htmlFor="nome">Nome</label>

                <input
                    id="nome"
                    name="nome"
                    value={form.nome}
                    onChange={handleChange}
                />
            </div>

            <div>
                <label htmlFor="email">Email</label>

                <input
                    id="email"
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                />
            </div>

            <div>
                <label htmlFor="telefone">Telefone</label>

                <input
                    id="telefone"
                    name="telefone"
                    value={form.telefone}
                    onChange={handleChange}
                />
            </div>

            <button type="submit">
                Adicionar Contato
            </button>
        </form>
    );
};

export default ContactForm;
