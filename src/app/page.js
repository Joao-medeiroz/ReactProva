"use client"

import {useState, useEffect} from "react"
import ContactForm from "./components/ContactForm";
import ContactList from "./components/ContactList";
import FilterInput from "./components/FilterInput";

const HomePage = () => {

  const [contacts, setContacts] = useState([])
  const [isLoad, setIsLoad] = useState(false)
  const [isFilter, setFilter] = useState("")

  useEffect(() => {
    const Salving = localStorage.getItem("contatos")

    if(Salving){
      setContacts(JSON.parse(Salving))
    }

    setIsLoad(true)
  }, [])

  useEffect(() => { 
    if(isLoad){
      localStorage.setItem("contatos", JSON.stringify(contacts))

    }
  }, [contacts, isLoad])

  const handleAdd = (newContact) => {
    setContacts((prev) => ([...prev,{...newContact, id: Date.now()}]))
  }

  const Filtro = contacts.filter(
    (contact) => contact.nome.toLowerCase().includes(isFilter.toLowerCase())
  );

  const Remove = (Id) => {
    setContacts((prev) => prev.filter((c) => c.id !== Id ))
  }

  return(
    <div>
      <ContactForm onAdd={handleAdd}/>
      <ContactList contacts={Filtro} onRemove={Remove}/>
      <FilterInput value={isFilter} onChange={setFilter}/>

    </div>
  )
}

export default HomePage;