"use client";

import ContactItem from "./ContactItem";

export default function ContactList({contacts, onRemove,}) {
    return (
        <section >
            <h2>Lista de Contatos</h2>
            {contacts.length === 0 ? (
                <p>Nenhum contato encontrado.</p>
            ) : (
                <ul>
                    {contacts.map((contact) => (
                        <ContactItem key={contact.id} contact={contact} onRemove={onRemove}/>
                        ))}
                </ul>
            )}
        </section>
    );
}
