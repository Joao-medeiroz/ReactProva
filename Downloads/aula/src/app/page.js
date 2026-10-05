"use client"

import {useState} from "react"
import Form from "./components/Form"
import ContactList from "./components/ContactList"

const HomePage = () => {
    const [contact, setContact] = useState([])

    const handleAdd = (newContact) => {
        setContact((prev) => ([...prev, newContact]))
    }

    const onRemove = (Id) => {
        setContact((prev) => (prev.filter((c) => c.id !== Id )))
    }
    
    return(
        <div>
            <header>
                <h1>Candidatos</h1>
            </header>
            <div>
            <Form Add={handleAdd}/>
            <ContactList items={contact} onRemove={onRemove}/>
            </div>
        </div>
    )
}

export default HomePage;