"use client"

import Link from "next/link"

const ContactItem = ({contact, onRemove}) => {
    const Details = `contact/${contact.id}` +
    `?nome=${encodeURIComponent(contact.nome)}`+
    `&email=${encodeURIComponent(contact.email)}`+
    `&idade=${encodeURIComponent(contact.idade)}`


    return(
        <li>
            <Link href={Details}>{contact.nome}</Link>
            <p>{contact.idade}</p>
            <p>{contact.email}</p>

            <button onClick={() => onRemove(contact.id)}>Remover</button>
        </li>
    )
}

export default ContactItem;