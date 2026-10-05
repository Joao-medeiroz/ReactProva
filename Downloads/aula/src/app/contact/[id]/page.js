"use client"

import {useRouter, useParams, useSearchParams} from "next/navigation"

const UserDetails = () => {

    const Router = useRouter();
    const Params = useParams();
    const SearchParams = useSearchParams();

    const DetailsUsers = {
        id: Params.id,
        nome: SearchParams.get("nome"),
        idade: SearchParams.get("idade"),
        email: SearchParams.get("email")
    }

    return(
        <li>
            <h2>Pagina de Detalhes</h2>

            <p>{DetailsUsers.nome}</p>
            <p>{DetailsUsers.idade}</p>
            <p>{DetailsUsers.email}</p>

            <button onClick={() => Router.back()}>Voltar</button>
        </li>
    )
}

export default UserDetails;