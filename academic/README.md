# Entregáveis acadêmicos

Esta pasta separa o registro acadêmico oficial do documento que continua em evolução científica.

| Entregável | Status | Fonte | PDF |
|---|---|---|---|
| Monografia aprovada | Registro histórico imutável | Não alterado/publicado | [`monografia-aprovada-2025.pdf`](monografia/monografia-aprovada-2025.pdf) |
| Artigo científico V1.0 | Versão congelada em 13/08/2026; revisões futuras recebem nova versão | [`artigo/main.tex`](artigo/main.tex) | [`artigo/releases/article-v1.pdf`](artigo/releases/article-v1.pdf) |
| Bibliografia do artigo | Fonte compartilhada | [`shared/referencias.bib`](shared/referencias.bib) | — |

## Identificação

- **Título:** Aplicação de Inteligência Artificial na Identificação de Vulnerabilidades em Redes Locais com Integração a Firewall
- **Autores:** João Vitor Ielen e Vinicius Mota Favaro
- **Curso:** Engenharia de Software — Centro Universitário UniOpet
- **Local e ano:** Curitiba, 2025
- **Aprovação:** 19 de novembro de 2025
- **Orientador:** Michel Cesar dos Santos
- **Banca:** Pedro Eckel e Claudio Bylik

## Política documental

A monografia pública é uma cópia byte a byte do PDF apresentado e aprovado em 2025. Ela não recebe correções editoriais, científicas ou tipográficas posteriores. Seu SHA-256 é:

```text
DCACE3DBCFC0B6FDD6E549B686AD76DA1C9072933DE1579E37BDF8430BCCD898
```

O artigo é um trabalho derivado e pode ser refinado conforme método científico, revisão por pares e requisitos do periódico, desde que não seja confundido com a monografia histórica.

A V1.0 do artigo é identificada no fonte, nos metadados do PDF e pelo arquivo
nomeado `artigo/releases/article-v1.pdf`. O histórico Git preserva seu estado;
alterações científicas posteriores devem incrementar `artigo/VERSION` e gerar
um novo PDF nomeado, sem sobrescrever o snapshot V1.

Todos os arquivos desta pasta estão excluídos da licença MIT do software e permanecem com [todos os direitos reservados](LICENSE.md). Citação acadêmica não concede, por si só, autorização de reprodução, alteração ou redistribuição.

## Compilação do artigo

XeLaTeX é necessário para empregar Arial. Em `artigo/`, execute:

```sh
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

Também é possível usar `latexmk -xelatex main.tex`. Arquivos auxiliares são ignorados pelo Git; o PDF final permanece versionável. Antes de uma submissão real, o artigo precisa ser adaptado ao template, limite de páginas e metadados do periódico escolhido.

Consulte a [política completa](../docs/DOCUMENT_POLICY.md) e o [contexto acadêmico](../docs/ACADEMIC_CONTEXT.md).
