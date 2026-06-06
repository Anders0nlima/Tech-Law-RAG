# 🧠 Notas de Aprendizado (Learning Notes)

A construção do **Tech-Law RAG** não foi apenas sobre empilhar ferramentas, mas sim sobre solucionar problemas complexos com arquitetura profissional. Abaixo estão os principais aprendizados e justificativas técnicas, documentadas de forma ideal para apresentação em um portfólio.

---

## 1. Arquitetura Desacoplada e O Padrão de API Isolada

Um dos grandes saltos qualitativos foi entender a importância da divisão entre Frontend (React/Vite) e Backend (FastAPI).
* **O Problema:** Muito se ensina sobre construir aplicações RAG em uma única camada (ex: Streamlit) para entregar rápido, porém isso sacrifica a manutenibilidade, a escala e a experiência do usuário.
* **A Solução:** Ao isolar o Python no backend e fornecer a interface via endpoints HTTP limpos, o sistema adota um padrão "headless". 
* **O Ganho:** O backend pode vir a ser consumido por um app mobile no futuro e o frontend pode ser hospedado de forma ultrabarata (edge networks como a Vercel) enquanto o backend roda em containers escaláveis. 

## 2. Processamento Assíncrono para UX Fluida

Uma chamada complexa para a OpenAI para gerar um dossiê jurídico completo, juntamente à indexação do documento usando Embeddings, pode levar alguns segundos ou mais.
* **O Problema:** Travar a interface do usuário (HTTP blocking) até o dossiê ficar pronto gera uma UX terrível, arrisca timeout em serviços de deploy (ex: Render pode derrubar conexões longas) e passa percepção de lentidão.
* **A Solução:** A requisição HTTP apenas agenda a análise em uma tarefa de background (`BackgroundTasks` do FastAPI) e retorna imediatamente com um `status: pending`.
* **O Ganho:** O frontend pode usar um mecanismo de Polling simples para verificar periodicamente quando o documento finalizou, mostrando uma tela de _loading_ iterativa e engajadora ao usuário, sem travar o navegador.

## 3. Bancos Vetoriais Modernos: `pgvector` e Supabase

Em vez de usar bancos vetoriais isolados na nuvem ou sistemas in-memory (como Pinecone, FAISS, ou ChromaDB local), este projeto adotou o PostgreSQL com `pgvector` por meio do Supabase.
* **O Motivo:** A grande maioria das aplicações comerciais já usa bancos de dados relacionais (Postgres/MySQL) como fonte da verdade. O `pgvector` permite que a persistência dos metadados de um contrato (ID, data de upload, status da análise, URL do PDF) viva na mesma base e nas mesmas transações atômicas que as fatias (_chunks_) de embeddings.
* **O Ganho:** Isso reduz imensamente o trabalho de infraestrutura (menos plataformas a assinar e manter), reduz chances de inconsistência entre bases, e mostra profunda competência em gerenciamento de banco de dados e SQL moderno.

## 4. Observabilidade do LLM com Langfuse

A "caixa preta" dos modelos de Inteligência Artificial é frequentemente o motivo de medo em times de engenharia no mundo real, especialmente no aspecto de custos e latência.
* **O Problema:** Como saber exatamente quantos tokens o sistema gastou em uma chamada? A IA alucinou por causa de um prompt ruim ou porque o texto extraído do PDF estava sujo? Quanto custou essa requisição?
* **A Solução:** Implementar o SDK do Langfuse (`langfuse.openai.AsyncOpenAI` e `@observe`) criando um singleton inteligente de observabilidade, para registrar todas as traces.
* **O Ganho:** O sistema atinge nível de produção (Enterprise Ready). Mostrar em portfólio a capacidade de depurar LLMs e otimizar tokens agrega imenso valor frente a projetos "Hello World" de RAG.

## 5. Structured Outputs (Geração Estruturada) em vez de Texto Livre

Muitos projetos usam a IA apenas para cuspir um grande bloco de texto formatado em Markdown que é vomitado na tela para o usuário final ler.
* **A Solução:** Usamos Pydantic models para definir e forçar (através de function calling / JSON mode) o LLM a retornar a análise como uma estrutura de dados real, separando a lista de cláusulas perigosas, a severidade delas e a recomendação de correção.
* **O Ganho:** O Frontend tem o poder total de decidir **como renderizar** essas informações. O resultado prático é um Dashboard que interage com os dados: exibe badges vermelhos para riscos altos, modais bonitos com a recomendação da reescrita da cláusula, e possibilita filtragem ou agregação de análises futuras.

---

### Resumo para Entrevistas Técnicas
**O que este projeto prova que você sabe?**
* "Não apenas conecto uma IA no sistema; eu sei torná-la observável para redução de custos (Langfuse)."
* "Consigo criar aplicações tolerantes a demoras usando pipelines assíncronas em Python/FastAPI."
* "Entendo a teoria de busca semântica em nível de banco de dados (PostgreSQL/pgvector)."
* "Sei provisionar uma infraestrutura distribuída na nuvem (Docker / Vercel / Render)."
* "Sei converter uma resposta bruta de LLM numa experiência rica (Dashboard Estruturado) na interface web."
