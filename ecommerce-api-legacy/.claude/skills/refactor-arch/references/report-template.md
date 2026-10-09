# Audit Report Template (Phase 2)

## Header
- Project: <nome>
- Stack: <linguagem + framework>
- Date: <YYYY-MM-DD>
- Files analyzed: <n>

## Summary
- CRITICAL: <n>
- HIGH: <n>
- MEDIUM: <n>
- LOW: <n>
- Total findings: <n>

## Architecture Snapshot
- Current architecture: <monolitica/parcialmente em camadas/etc>
- Persistence: <sqlite/postgres/etc>
- Main domain: <descricao curta>

## Findings (ordenados por severidade)

### [CRITICAL|HIGH|MEDIUM|LOW] <titulo>
- File: <caminho>:<linha ou intervalo>
- Category: <security | code smell | deprecated api | architecture>
- Evidence: <trecho observado no codigo>
- Impact: <risco tecnico/negocio>
- Recommendation: <acao objetiva>

### [CRITICAL|HIGH|MEDIUM|LOW] <titulo>
- File: <caminho>:<linha ou intervalo>
- Category: <...>
- Evidence: <...>
- Impact: <...>
- Recommendation: <...>

## Deprecated API Notes
- API/Pattern: <nome>
- Location: <arquivo:linha>
- Why obsolete/risky: <justificativa>
- Modern equivalent: <substituicao recomendada>

## Quick Wins
- 1) <acao de baixo risco e alto impacto>
- 2) <acao>
- 3) <acao>

## Refactoring Readiness
- Blocking issues before refactor: <lista>
- Estimated complexity: <low|medium|high>
- Suggested order: <sequencia de execucao>

## Mandatory Checkpoint Output
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
