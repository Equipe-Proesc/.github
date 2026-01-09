## 📝 Descrição
- **O que mudou:** - **Contexto técnico:** **Issue Relacionada:** # (ou link para o Jira/PED-XXXX)

---

## ✅ Autorevisão do Desenvolvedor
- [ ] Revisei meu próprio código e ele está claro e organizado?
- [ ] Todas as funcionalidades foram testadas adequadamente (manuais/locais)?
- [ ] O código foi simplificado ou refatorado para melhor legibilidade?
- [ ] Removi códigos mortos (dead code) ou dependências desnecessárias?

---

## 🛠 Checklist de Padronização

### 1. 🔍 Clareza e Rastreabilidade
- [ ] O título do PR é claro e a descrição detalha o que e como foi feito?
- [ ] A issue de origem foi referenciada na descrição?
- [ ] A mudança é autoexplicativa para o revisor?

### 2. 🎯 Escopo e Foco
- [ ] O PR foca em uma única responsabilidade (feature, bug ou refatoração)?
- [ ] O PR não mistura diferentes tipos de mudanças (evitou o "PR Monstro")?

### 3. 🏛️ Arquitetura e Padrões
- [ ] O código está no local arquitetural correto (services, repositories, actions, etc.)?
- [ ] O código segue as convenções e padrões de design da equipe?

### 4. 🧪 Cobertura e Qualidade dos Testes
- [ ] O novo código possui testes correspondentes e os antigos continuam passando?
- [ ] Os testes validam comportamentos significativos (não apenas detalhes)?
- [ ] Foram testados o "caminho feliz" e os casos de falha/exceção?
- [ ] O design do código facilita a escrita de testes (sem estado global excessivo)?

### 5. 🛠️ Análise Técnica e Otimização
- [ ] O pipeline de CI e o Linter passaram com sucesso?
- [ ] Novas dependências são estritamente necessárias e seguras?
- [ ] Foram verificados possíveis problemas de N+1 (uso de eager loading)?
- [ ] O código evita carregar dados excessivos em memória (uso de chunks/generators)?
- [ ] Operações lentas foram movidas para background jobs ou cache?

### 6. 🚀 Processo de Deploy e Homologação
- [ ] Foi providenciado um ambiente para que QA/Produto possa testar?
- [ ] O processo de release e comunicação de deploy foi seguido?
