"use client";

import Link from "next/link";

const ContactItem = ({ contact, onRemove }) => {
    return (
        <li >
            <div>
                <Link href={`/contact/${contact.id}`}>{contact.nome}</Link>

                <p>{contact.email} • {contact.telefone}</p>
            </div>
            <button onClick={() => onRemove(contact.id)}>Excluir</button>
        </li>
    );
};

export default ContactItem;
