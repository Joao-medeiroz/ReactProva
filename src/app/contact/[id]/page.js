"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

const ContactDetailPage = () => {
  const params = useParams();
  const router = useRouter();

  const [contact, setContact] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedContacts = localStorage.getItem("contatos");

    if (savedContacts) {
      const contacts = JSON.parse(savedContacts);

      const foundContact = contacts.find(
        (contact) =>
          contact.id === parseInt(params.id)
      );

      if (foundContact) {
        setContact(foundContact);
      } else {
        router.push("/");
      }
    } else {
      router.push("/");
    }

    setLoading(false);
  }, [params.id, router]);

  if (loading) {
    return (
      <main className="container">
        <section className="card">
          <p>Carregando...</p>
        </section>
      </main>
    );
  }

  if (!contact) {
    return (
      <main className="container">
        <section className="card">
          <p>Contato não encontrado.</p>
        </section>
      </main>
    );
  }

  return (
    <main className="container">
      <section className="card">
        <div className="detail-header">
          <h1>Detalhes do Contato</h1>

          <button onClick={() => router.back()}>
            ← Voltar
          </button>
        </div>

        <div className="details">
          <div>
            <strong>Nome</strong>
            <p>{contact.nome}</p>
          </div>

          <div>
            <strong>Email</strong>
            <p>{contact.email || "—"}</p>
          </div>

          <div>
            <strong>Telefone</strong>
            <p>{contact.telefone || "—"}</p>
          </div>
        </div>
      </section>
    </main>
  );
};

export default ContactDetailPage;
