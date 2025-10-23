# Claude Skills Architecture: Guia Completo

## 🎯 **Propósito**

Este documento elimina a confusão entre diferentes tipos de Skills Claude Code e estabelece terminologia consistente.

## 📚 **Terminologia Padrão**

### **Skill**
Uma **Skill** é uma capacidade completa do Claude Code implementada como uma pasta contendo:
- Arquivo `SKILL.md` (obrigatório)
- Recursos opcionais (scripts/, references/, assets/)
- Funcionalidade específica para um domínio

**Exemplo:** `minha-skill/` contendo análise de dados financeiros

### **Component Skill**
Uma **Component Skill** é uma sub-skill especializada que é parte de uma Skill Suite maior.
- Tem seu próprio `SKILL.md`
- Foca em uma funcionalidade específica
- Compartilha recursos com outras component skills

**Exemplo:** `data-acquisition/SKILL.md` dentro de uma suite de análise financeira

### **Skill Suite**
Uma **Skill Suite** é uma coleção integrada de Component Skills que trabalham juntas.
- Tem `marketplace.json` como manifest
- Múltiplas component skills especializadas
- Recursos compartilhados entre skills

**Exemplo:** Suite completa de análise financeira com skills para data acquisition, analysis, e reporting.

### **Marketplace Plugin**
Um **Marketplace Plugin** é o arquivo `marketplace.json` que hospeda e organiza uma ou mais Skills.
- **NÃO é uma skill** - é um manifest organizacional
- Define como as skills devem ser carregadas
- Pode hospedar skills simples ou suites complexas

## 🏗️ **Tipos de Arquitetura**

### **Arquitetura 1: Simple Skill**
```
minha-skill/
├── SKILL.md              ← Single skill file
├── scripts/              ← Optional supporting code
├── references/           ← Optional documentation
└── assets/               ← Optional templates/resources
```

**Quando usar:**
- Funcionalidade focada e única
- Workflow simples
- Menos de 1000 linhas de código total
- Um objetivo principal

**Exemplos:**
- Gerador de propostas comerciais
- Extrator de dados de PDFs
- Calculadora de ROI

### **Arquitetura 2: Complex Skill Suite**
```
minha-suite/                    ← Skill Suite completa
├── .claude-plugin/
│   └── marketplace.json        ← Manifest das skills
├── componente-1/               ← Component Skill 1
│   ├── SKILL.md
│   └── scripts/
├── componente-2/               ← Component Skill 2
│   ├── SKILL.md
│   └── references/
├── componente-3/               ← Component Skill 3
│   ├── SKILL.md
│   └── assets/
└── shared/                     ← Recursos compartilhados
    ├── utils/
    ├── config/
    └── templates/
```

**Quando usar:**
- Múltiplos workflows relacionados
- Funcionalidades complexas que precisam ser separadas
- Mais de 2000 linhas de código total
- Vários objetivos interconectados

**Exemplos:**
- Suite completa de análise financeira
- Sistema de gestão de projetos
- Plataforma de e-commerce analytics

### **Arquitetura 3: Hybrid (Simple + Components)**
```
minha-skill-hibrida/           ← Simple skill principal
├── SKILL.md                   ← Orquestração principal
├── scripts/
│   ├── main.py               ← Lógica principal
│   └── components/           ← Componentes especializados
├── references/
└── assets/
```

**Quando usar:**
- Funcionalidade principal com sub-componentes
- Complexidade moderada
- Orquestração centralizada necessária

## 🔍 **Decidindo Qual Arquitetura Usar**

### **Use Simple Skill quando:**
- ✅ Um objetivo principal claro
- ✅ Workflow linear e sequencial
- ✅ Menos de 3 subprocessos distintos
- ✅ Código < 1000 linhas
- ✅ Uma pessoa pode manter facilmente

### **Use Complex Skill Suite quando:**
- ✅ Múltiplos objetivos relacionados
- ✅ Workflows independentes mas conectados
- ✅ Mais de 3 subprocessos distintos
- ✅ Código > 2000 linhas
- ✅ Equipe ou manutenção complexa

### **Use Hybrid quando:**
- ✅ Orquestração central é crítica
- ✅ Componentes são opcionais/configuráveis
- ✅ Workflow principal com sub-tarefas especializadas

## 📋 **Marketplace.json Explicado**

O `marketplace.json` **NÃO É** uma skill. É um **manifest organizacional**:

```json
{
  "name": "minha-suite",
  "plugins": [
    {
      "name": "componente-1",
      "source": "./componente-1/",
      "skills": ["./SKILL.md"]     ← Aponta para a skill real
    },
    {
      "name": "componente-2",
      "source": "./componente-2/",
      "skills": ["./SKILL.md"]     ← Aponta para outra skill
    }
  ]
}
```

**Analogia:** Pense no `marketplace.json` como um **índice de livro** - ele não é o conteúdo, apenas organiza e aponta para os capítulos (skills).

## 🚫 **Terminologia a Evitar**

Para evitar confusão:

❌ **"Plugin"** para se referir a skills individuais
✅ **"Component Skill"** ou **"Skill Suite"**

❌ **"Multi-plugin architecture"**
✅ **"Multi-skill suite"**

❌ **"Plugin marketplace"**
✅ **"Skill marketplace"** (quando hospeda skills)

## ✅ **Termos Corretos**

| Situação | Termo Correto | Exemplo (com convenção -cskill) |
|----------|---------------|--------------------------------|
| Arquivo único com habilidade | **Simple Skill** | `gerador-pdf-cskill/SKILL.md` |
| Sub-habilidade especializada | **Component Skill** | `data-extraction-cskill/SKILL.md` |
| Conjunto de habilidades | **Skill Suite** | `financial-analysis-suite-cskill/` |
| Arquivo organizacional | **Marketplace Plugin** | `marketplace.json` |
| Sistema completo | **Skill Ecosystem** | Suite + Marketplace + Recursos |

## 🏷️ **Convenção de Nomenclatura: Sufixo "-cskill"**

### **Propósito do Sufixo "-cskill"**
- **Identificação Clara**: Indica imediatamente que é uma Claude Skill
- **Origem Definida**: Criada pelo Agent-Skill-Creator
- **Padrão Consistente**: Convenção profissional em toda documentação
- **Evita Confusão**: Distingue de skills manuais ou outras fontes
- **Organização Facilitada**: Fácil identificação e agrupamento

### **Regras de Nomenclatura**

**1. Formato Padrão**
```
{descrição-descritiva}-cskill/
```

**2. Simple Skills**
```
pdf-text-extractor-cskill/
csv-data-cleaner-cskill/
weekly-report-generator-cskill/
image-converter-cskill/
```

**3. Complex Skill Suites**
```
financial-analysis-suite-cskill/
e-commerce-automation-cskill/
research-workflow-cskill/
business-intelligence-cskill/
```

**4. Component Skills (dentro de suites)**
```
data-acquisition-cskill/
technical-analysis-cskill/
reporting-generator-cskill/
user-interface-cskill/
```

**5. Formatação**
- ✅ Sempre minúsculas
- ✅ Usar hífens para separar palavras
- ✅ Descritivo e claro
- ✅ Terminar com "-cskill"
- ❌ Sem underscores ou espaços
- ❌ Sem caracteres especiais (exceto hífens)

### **Exemplos de Transformação**

| Requisito do Usuário | Nome Gerado |
|---------------------|-------------|
| "Extract text from PDF documents" | `pdf-text-extractor-cskill/` |
| "Clean CSV data automatically" | `csv-data-cleaner-cskill/` |
| "Complete financial analysis platform" | `financial-analysis-suite-cskill/` |
| "Generate weekly status reports" | `weekly-report-generator-cskill/` |
| "Automate e-commerce workflows" | `e-commerce-automation-cskill/` |

## 🎯 **Regra de Ouro**

**Se tem `SKILL.md` → É uma Skill (simples ou component)
Se tem `marketplace.json` → É um marketplace plugin (organização)**

## 📖 **Exemplos do Mundo Real**

### **Simple Skill: Proposta Comercial**
```
proposta-comercial/
├── SKILL.md              ← "Criar propostas comerciais"
├── references/
│   └── template.md
└── assets/
    └── logo.png
```

### **Complex Skill Suite: Análise Financeira**
```
financial-analysis-suite/
├── .claude-plugin/marketplace.json
├── data-acquisition/SKILL.md    ← "Baixar dados de mercado"
├── technical-analysis/SKILL.md  ← "Analisar indicadores técnicos"
├── portfolio-analysis/SKILL.md  ← "Otimizar portfólio"
└── reporting/SKILL.md          ← "Gerar relatórios"
```

Ambas são **Skills Claude Code legítimas** - apenas com diferentes níveis de complexidade.

---

## 🔄 **Como Este Documento Ajuda**

1. **Terminologia clara** - Todos usam os mesmos termos
2. **Decisões informadas** - Saber quando usar cada arquitetura
3. **Comunicação efetiva** - Sem ambiguidade entre skills e plugins
4. **Documentação consistente** - Padrão em toda documentação do agent-skill-creator

**Resultado:** Menos confusão, mais clareza, melhor desenvolvimento!