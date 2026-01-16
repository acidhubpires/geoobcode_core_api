# GeoOBCode Core API — PoC (FastAPI)

O **GeoOBCode Core API** é o núcleo de uma tecnologia de **codificação espaço-temporal estruturada**, voltada à **integridade, rastreabilidade e governança de processos**, decisões e estados — com horizonte de longo prazo.

Este repositório nasce a partir de um **baseline técnico** do projeto *AgentIA Hub*, mas **segue um caminho próprio**, com propósito, modelo conceitual e aplicações distintas.

> **GeoOBCode não é um chatbot, nem um sistema de agentes.**  
> É uma **infraestrutura base** para representar, selar e verificar estados e eventos complexos de forma determinística e auditável.

---

## Origem e Linhagem

- **Autor / Base Cognitiva**: PIRESAAO  
- **Baseline Técnico**: PIRESAAO AgentIA Hub (FastAPI)
- **Commit inicial**:  
  `chore: initialize GeoOBCode API from PIRESAAO AgentIA Hub Baseline`

A base de conhecimento e os princípios estruturais são **pessoais (PIRESAAO)**, porém o desenvolvimento se bifurca em dois caminhos claros:

| Caminho | Propósito |
|------|---------|
| **ACIDHUB / Geotoken Engine** | Infraestrutura cognitiva, agentes, tokens, negócios |
| **GeoOBCode** | Codificação estrutural, prova de processo, integridade espaço-temporal |

Essa separação é **intencional e estratégica**.

---

## O que é o GeoOBCode

O **GeoOBCode** é um **framework de codificação e selagem** que permite:

- representar **eventos, estados e decisões** como estruturas verificáveis,
- manter **delimitação semântica explícita** (fato, hipótese, inferência),
- gerar **provas de execução e processo**, não apenas de documentos,
- sustentar governança, auditoria e reversibilidade.

Ele pode operar:
- isoladamente (off-chain),
- ancorado criptograficamente (quando fizer sentido),
- interoperável com outras infraestruturas (ex.: Geotoken Engine).

---

## Princípios Arquiteturais

- **Estado explícito > memória implícita**
- **Contrato formal > prompt heurístico**
- **Determinismo onde importa**
- **Separação entre conteúdo e integridade**
- **Evolução incremental, sem reescrita**

Este projeto privilegia **robustez sistêmica**, não velocidade de demo.

---

## Estrutura do Projeto

```text
app/
 ├─ api/        # Contratos HTTP (PoC)
 ├─ core/       # Configuração, segurança, governança
 ├─ services/   # Codificação, validação, selagem
 ├─ infra/      # Persistência local (PoC)
 └─ domain/     # Schemas e contratos tipados
````

A estrutura é **neutra e reutilizável**, preservada do baseline técnico.

---

## Status Atual (PoC)

* ✔ Estrutura FastAPI funcional
* ✔ Persistência local (JSON) para validação de fluxo
* ✔ Contratos claros de entrada/saída
* ✔ Linhagem técnica preservada
* ⏳ Implementação específica do GeoOBCode (em progresso)

---

## O que este repositório **não é**

* ❌ Não é um chatbot
* ❌ Não é um sistema de agentes autônomos
* ❌ Não é um produto de engajamento
* ❌ Não é um repositório de documentos

Ele é **infraestrutura base**.

---

## Roadmap Conceitual (alto nível)

### Fase 1 — Núcleo Estrutural

* Definição formal do **Case / Cell / Seal**
* Codificação determinística de estados
* Versionamento e integridade

### Fase 2 — Governança e Prova

* Trilhas de eventos
* Verificação e consistência
* Reversibilidade controlada

### Fase 3 — Interoperabilidade

* Integração opcional com Geotoken Engine
* Selagem visual (GeoOBCode)
* Ancoragem criptográfica (quando aplicável)

---

## Nota Final

O **GeoOBCode** é pensado como tecnologia de **horizonte longo**, com baixa dívida técnica e alto rigor conceitual.

Ele compartilha **origem intelectual** com outros projetos do ecossistema PIRESAAO, mas **não compartilha destino**.

---

© PIRESAAO — todos os direitos reservados




