# Entregáveis acadêmicos

Esta pasta separa o registro acadêmico oficial do documento que continua em evolução científica.

| Entregável | Status | Fonte | PDF |
|---|---|---|---|
| Monografia aprovada | Registro histórico imutável | Não alterado/publicado | [`monografia-aprovada-2025.pdf`](monografia/monografia-aprovada-2025.pdf) |
| Artigo científico V1.0 | Snapshot congelado em 13/08/2026 | Branch `article-v1` e tag `article-v1.0` | [`artigo/releases/article-v1.pdf`](artigo/releases/article-v1.pdf) |
| Artigo científico V1.1 | Revisão científica concluída | [`artigo/main.tex`](artigo/main.tex) | [`artigo/releases/article-v1.1.pdf`](artigo/releases/article-v1.1.pdf) |
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

O artigo é um trabalho derivado e pode ser refinado conforme método científico
e padrões internacionais de apresentação, desde que não seja confundido com a
monografia histórica. Não há submissão a periódico planejada para a V1.1.

A V1.0 do artigo é identificada pelo arquivo nomeado
`artigo/releases/article-v1.pdf`, pelo branch `article-v1` e pela tag
`article-v1.0`. O arquivo `artigo/VERSION` identifica o fonte ativo. A V1.1 está
congelada em `artigo/releases/article-v1.1.pdf`, sem sobrescrever o snapshot
V1.0.

Todos os arquivos desta pasta estão excluídos da licença MIT do software e permanecem com [todos os direitos reservados](LICENSE.md). Citação acadêmica não concede, por si só, autorização de reprodução, alteração ou redistribuição.

## Compilação do artigo

A V1.1 usa o baseline internacional genérico `IEEEtran` apenas como régua
de qualidade e apresentação. Em `artigo/`,
execute:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Também é possível usar `latexmk -pdf main.tex`. Arquivos auxiliares são
ignorados pelo Git; o PDF final permanece versionável. Uma eventual submissão
futura seria um novo escopo e exigiria nova verificação das regras do venue.

Consulte a [política completa](../docs/DOCUMENT_POLICY.md) e o [contexto acadêmico](../docs/ACADEMIC_CONTEXT.md).
