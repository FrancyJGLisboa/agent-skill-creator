# Convenções de Nomenclatura: Sufixo "-cskill"

## 🎯 **Propósito e Visão Geral**

Este documento estabelece a convenção de nomenclatura obrigatória para todas as Claude Skills criadas pelo Agent-Skill-Creator, utilizando o sufixo "-cskill" para garantir identificação clara e consistência profissional.

## 🏷️ **O Sufixo "-cskill"**

### **Significado**
- **CSKILL** = **C**laude **SKILL** (Habilidade Claude)
- Indica que a skill foi criada automaticamente pelo Agent-Skill-Creator
- Diferencia de skills criadas manualmente ou por outras ferramentas

### **Benefícios**

✅ **Identificação Imediata**
- Qualquer pessoa vê "-cskill" e sabe imediatamente que é uma Claude Skill
- Reconhecimento instantâneo da origem (Agent-Skill-Creator)

✅ **Organização Facilitada**
- Fácil filtrar e encontrar skills criadas pelo creator
- Agrupamento lógico em sistemas de arquivos
- Busca eficiente com padrão consistente

✅ **Profissionalismo**
- Convenção de nomenclatura profissional e padronizada
- Clareza na comunicação sobre origem e tipo
- Aparência organizada e intencional

✅ **Evita Confusão**
- Sem ambiguidade sobre o que é uma skill vs plugin
- Distinção clara de skills manuais vs automatizadas
- Prevenção de conflitos de nomes

## 📋 **Regras de Nomenclatura**

### **1. Formato Obrigatório**
```
{descrição-descritiva}-cskill/
```

### **2. Estrutura do Nome Base**

#### **Simple Skills (Objetivo Único)**
```
{ação}-{objeto}-csskill/
```

**Exemplos:**
- `pdf-text-extractor-cskill/`
- `csv-data-cleaner-cskill/`
- `image-converter-cskill/`
- `email-automation-cskill/`
- `report-generator-cskill/`

#### **Complex Skill Suites (Múltiplos Componentes)**
```
{domínio}-analysis-suite-cskill/
{domínio}-automation-cskill/
{domínio}-workflow-cskill/
```

**Exemplos:**
- `financial-analysis-suite-cskill/`
- `e-commerce-automation-cskill/`
- `research-workflow-cskill/`
- `business-intelligence-cskill/`

#### **Component Skills (Dentro de Suites)**
```
{funcionalidade}-{domínio}-cskill/
```

**Exemplos:**
- `data-acquisition-cskill/`
- `technical-analysis-cskill/`
- `reporting-generator-cskill/`
- `user-interface-cskill/`

### **3. Regras de Formatação**

✅ **OBRIGATÓRIO:**
- Sempre minúsculas
- Usar hífens (-) para separar palavras
- Terminar com "-cskill"
- Ser descritivo e claro
- Usar apenas caracteres alfanuméricos e hífens

❌ **PROIBIDO:**
- Letras maiúsculas
- Underscores (_)
- Espaços em branco
- Caracteres especiais (!@#$%&*)
- Números no início
- Abreviações não-padrão

### **4. Comprimento Recomendado**

- **Mínimo:** 10 caracteres (ex: `pdf-tool-cskill`)
- **Ideal:** 20-40 caracteres (ex: `financial-analysis-suite-cskill`)
- **Máximo:** 60 caracteres (exceções justificadas)

## 🔧 **Processo de Geração de Nomes**

### **Lógica Automática do Agent-Skill-Creator**

```python
def generate_skill_name(user_requirements, complexity):
    """
    Gera nome da skill seguindo convenção -cskill
    """

    # 1. Extrair conceitos-chave do input do usuário
    concepts = extract_key_concepts(user_requirements)

    # 2. Criar nome base baseado na complexidade
    if complexity == "simple":
        base_name = create_simple_name(concepts)
    elif complexity == "complex_suite":
        base_name = create_suite_name(concepts)
    else:  # hybrid
        base_name = create_hybrid_name(concepts)

    # 3. Sanitizar e formatar
    base_name = sanitize_name(base_name)

    # 4. Aplicar convenção -cskill
    skill_name = f"{base_name}-cskill"

    return skill_name

def create_simple_name(concepts):
    """Cria nome para skills simples"""
    if len(concepts) == 1:
        return f"{concepts[0]}-tool"
    elif len(concepts) == 2:
        return f"{concepts[1]}-{concepts[0]}"
    else:
        return "-".join(concepts[:2])

def create_suite_name(concepts):
    """Cria nome para suites complexas"""
    if len(concepts) <= 2:
        return f"{concepts[0]}-automation"
    else:
        return f"{concepts[0]}-{'-'.join(concepts[1:3])}-suite"

def sanitize_name(name):
    """Sanitiza nome para formato válido"""
    # Converter para minúsculas
    name = name.lower()
    # Substituir espaços e underscores por hífens
    name = re.sub(r'[\s_]+', '-', name)
    # Remover caracteres especiais
    name = re.sub(r'[^a-z0-9-]', '', name)
    # Remover hífens múltiplos
    name = re.sub(r'-+', '-', name)
    # Remover hífens no início/fim
    name = name.strip('-')
    return name
```

### **Exemplos de Transformação**

| Input do Usuário | Tipo | Conceitos Extraídos | Nome Gerado |
|------------------|------|-------------------|-------------|
| "Extract text from PDF" | Simple | ["extract", "text", "pdf"] | `pdf-text-extractor-cskill/` |
| "Clean CSV data automatically" | Simple | ["clean", "csv", "data"] | `csv-data-cleaner-cskill/` |
| "Complete financial analysis platform" | Suite | ["financial", "analysis", "platform"] | `financial-analysis-suite-cskill/` |
| "Automate e-commerce workflows" | Suite | ["automate", "ecommerce", "workflows"] | `ecommerce-automation-cskill/` |
| "Generate weekly status reports" | Simple | ["generate", "weekly", "reports"] | `weekly-report-generator-cskill/` |

## 📚 **Exemplos Práticos por Domínio**

### **Finanças e Investimentos**
```
financial-analysis-suite-cskill/
portfolio-optimizer-cskill/
market-data-fetcher-cskill/
risk-calculator-cskill/
trading-signal-generator-cskill/
```

### **Análise de Dados**
```
data-visualization-cskill/
statistical-analysis-cskill/
etl-pipeline-cskill/
data-cleaner-cskill/
dashboard-generator-cskill/
```

### **Automação de Documentos**
```
pdf-processor-cskill/
word-automation-cskill/
excel-report-generator-cskill/
presentation-creator-cskill/
document-converter-cskill/
```

### **E-commerce e Vendas**
```
inventory-tracker-cskill/
sales-analytics-cskill/
customer-data-processor-cskill/
order-automation-cskill/
price-monitor-cskill/
```

### **Pesquisa e Academia**
```
literature-review-cskill/
citation-manager-cskill/
research-data-collector-cskill/
academic-paper-generator-cskill/
survey-analyzer-cskill/
```

### **Produtividade e Escritório**
```
email-automation-cskill/
calendar-manager-cskill/
task-tracker-cskill/
note-organizer-cskill/
meeting-scheduler-cskill/
```

## 🔍 **Validação e Qualidade**

### **Verificação Automática**
```python
def validate_skill_name(skill_name):
    """
    Valida se o nome segue a convenção -cskill
    """

    # 1. Verificar sufixo -cskill
    if not skill_name.endswith("-cskill"):
        return False, "Missing -cskill suffix"

    # 2. Verificar formato minúsculas
    if skill_name != skill_name.lower():
        return False, "Must be lowercase"

    # 3. Verificar caracteres válidos
    if not re.match(r'^[a-z0-9-]+-cskill$', skill_name):
        return False, "Contains invalid characters"

    # 4. Verificar comprimento
    if len(skill_name) < 10 or len(skill_name) > 60:
        return False, "Invalid length"

    # 5. Verificar hífens consecutivos
    if '--' in skill_name:
        return False, "Contains consecutive hyphens"

    return True, "Valid naming convention"
```

### **Checklist de Qualidade**

Para cada nome gerado, verificar:

- [ ] **Termina com "-cskill"** ✓
- [ ] **Está em minúsculas** ✓
- [ ] **Usa apenas hífens como separadores** ✓
- [ ] **É descritivo e claro** ✓
- [ ] **Não tem caracteres especiais** ✓
- [ ] **Comprimento adequado (10-60 caracteres)** ✓
- [ ] **Fácil de pronunciar e lembrar** ✓
- [ ] **Reflete a funcionalidade principal** ✓
- [ ] **É único no ecossistema** ✓

## 🚀 **Boas Práticas**

### **1. Seja Descritivo**
```
✅ bom: pdf-text-extractor-cskill
❌ ruim: tool-cskill

✅ bom: financial-analysis-suite-cskill
❌ ruim: finance-cskill
```

### **2. Mantenha Simplicidade**
```
✅ bom: csv-data-cleaner-cskill
❌ ruim: automated-csv-data-validation-and-cleaning-tool-cskill

✅ bom: email-automation-cskill
❌ ruim: professional-email-marketing-automation-workflow-cskill
```

### **3. Seja Consistente**
```
✅ bom: data-acquisition-cskill, data-processing-cskill, data-visualization-cskill
❌ ruim: get-data-cskill, process-cskill, visualize-cskill
```

### **4. Pense no Usuário**
```
✅ bom: weekly-report-generator-cskill (claro o que faz)
❌ ruim: wrk-gen-cskill (abreviado, confuso)
```

## 🔄 **Migração e Legado**

### **Skills Existentes Sem "-cskill"**
Se você tem skills existentes sem o sufixo:

1. **Adicione o sufixo imediatamente**
   ```bash
   mv old-skill-name old-skill-name-cskill
   ```

2. **Atualize referências internas**
   - Atualize SKILL.md
   - Modifique marketplace.json
   - Atualize documentação

3. **Teste funcionamento**
   - Verifique que a skill ainda funciona
   - Confirme instalação correta

### **Documentação de Migração**
Para cada skill migrada, documente:
```markdown
## Migration History
- **Original Name**: `old-name`
- **New Name**: `old-name-cskill`
- **Migration Date**: YYYY-MM-DD
- **Reason**: Apply -cskill naming convention
- **Impact**: None, purely cosmetic change
```

## 📖 **Guia Rápido de Referência**

### **Para Criar Novo Nome:**
1. **Identificar objetivo principal** (ex: "extract PDF text")
2. **Extrair conceitos-chave** (ex: extract, pdf, text)
3. **Montar nome base** (ex: pdf-text-extractor)
4. **Adicionar sufixo** (ex: pdf-text-extractor-cskill)

### **Para Validar Nome Existente:**
1. **Verificar sufixo "-cskill"**
2. **Confirmar formato minúsculas**
3. **Checar caracteres válidos**
4. **Avaliar descritividade**

### **Para Solucionar Problemas:**
- **Nome muito curto**: Adicionar descritor
- **Nome muito longo**: Remover palavras secundárias
- **Nome confuso**: Usar sinônimos mais claros
- **Conflito de nomes**: Adicionar diferenciador

## ✅ **Resumo da Convenção**

**Fórmula:** `{descrição-descritiva}-cskill/`

**Regras Essenciais:**
- ✅ Sempre terminar com "-cskill"
- ✅ Sempre minúsculas
- ✅ Usar hífens como separadores
- ✅ Ser descritivo e claro

**Resultados:**
- 🎯 Identificação imediata como Claude Skill
- 🏗️ Origem clara (Agent-Skill-Creator)
- 📁 Organização facilitada
- 🔍 Busca eficiente
- 💬 Comunicação clara

**Esta convenção garante consistência profissional e elimina qualquer confusão sobre a origem e tipo das skills criadas!**