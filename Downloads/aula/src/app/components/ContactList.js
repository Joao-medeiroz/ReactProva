import ContactItem from "./ContactItem"

const ContactList = ({items, onRemove}) => {
    return(
        <ul>
            <h2>Contatos {items.length}
                </h2>
                {(items.length === 0) ? (
                    <h2> Nenhum Contato encontrado</h2>
                ) : (
                    items.map((c) => (
                        <ContactItem key={c.id} contact={c} onRemove={onRemove}></ContactItem>
                    ))
                )}
        </ul>
    )
}

export default ContactList