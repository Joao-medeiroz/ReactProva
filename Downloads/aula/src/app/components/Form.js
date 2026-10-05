"use client"

import { useState } from "react"

const Form = ({Add}) => {
    const [form, setform] = useState({nome: "", idade: "", email: ""})

    const handleSubmit = (e) => {
        e.preventDefault()
        if(!form.nome.trim())return;

        Add({...form, id: Date.now()})
        setform({nome: "", idade: "", email: ""})

        console.log(form)
    }

    const handleChange = (e) => {
        const {name,  value} = e.target
        setform((prev) => ({...prev, [name]: value}))
    }
    return(
        <div> 
            <form onSubmit={handleSubmit}>
                <label>Nome</label>
                <input name="nome" value={form.nome} onChange={handleChange} ></input>

                <label>Idade</label>
                <input name="idade" value={form.idade} onChange={handleChange} ></input>

                <label>Email</label>
                <input name="email" value={form.email} onChange={handleChange} ></input><br/>

                <button type="submit">Enviar</button>
            </form>
        </div>
    )
}

export default Form;