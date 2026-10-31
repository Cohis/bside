# Graph Report - jogo  (2026-10-27)

## Corpus Check
- 2 files · ~1,055,701 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .s 2, .a 1)

## Summary
- 10 nodes · 8 edges · 2 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a8d5d25a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Planta da loja, câmera e colisões
- B-Side — loja isométrica

## God Nodes (most connected - your core abstractions)
1. `Planta da loja, câmera e colisões` - 4 edges
2. `B-Side — loja isométrica` - 4 edges
3. `Planta e câmera` - 1 edges
4. `Tipos da matriz` - 1 edges
5. `Movimento e conferência` - 1 edges
6. `Compilar e executar` - 1 edges
7. `Controles` - 1 edges
8. `Arquivos` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities (2 total, 0 thin omitted)

### Community 0 - "Planta da loja, câmera e colisões"
Cohesion: 0.40
Nodes (4): Movimento e conferência, Planta da loja, câmera e colisões, Planta e câmera, Tipos da matriz

### Community 1 - "B-Side — loja isométrica"
Cohesion: 0.40
Nodes (4): Arquivos, B-Side — loja isométrica, Compilar e executar, Controles

## Knowledge Gaps
- **6 isolated node(s):** `Planta e câmera`, `Tipos da matriz`, `Movimento e conferência`, `Compilar e executar`, `Controles` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 8 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Planta e câmera`, `Tipos da matriz`, `Movimento e conferência` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._