# PDF Problem-Solving Workflow

This guide shows how to use the Sequential Thinking MCP Server to analyze complex problems from PDF documents.

## Workflow Overview

1. **Load PDF** → 2. **Analyze Content** → 3. **Sequential Thinking** → 4. **Iterate & Refine**

## Example: Analyzing a Research Paper or Technical Document

### Step 1: Load Your PDF

```json
{
  "tool": "load_pdf",
  "arguments": {
    "filePath": "/Users/yourname/Documents/research_paper.pdf"
  }
}
```

**Expected Response:**
- PDF metadata (pages, text length)
- Content preview
- Confirmation that PDF is loaded for analysis

### Step 2: Analyze Specific Sections

```json
{
  "tool": "analyze_pdf_section",
  "arguments": {
    "query": "methodology experimental design",
    "searchTerms": ["methodology", "experiment", "hypothesis", "results"]
  }
}
```

**This will:**
- Search for relevant content sections
- Highlight key terms and their frequency  
- Extract relevant paragraphs
- Prepare content for sequential analysis

### Step 3: Start Sequential Thinking

```json
{
  "tool": "sequential_thinking",
  "arguments": {
    "thought": "Based on the PDF content, I need to understand the research problem first. The paper discusses [specific topic from PDF]. Let me identify the main research question being addressed.",
    "nextThoughtNeeded": true,
    "thoughtNumber": 1,
    "totalThoughts": 5
  }
}
```

### Step 4: Continue Analysis

```json
{
  "tool": "sequential_thinking",
  "arguments": {
    "thought": "Now I'll examine the methodology section. The authors used [specific method from PDF]. I can see potential strengths: [list], and possible limitations: [list].",
    "nextThoughtNeeded": true,
    "thoughtNumber": 2,
    "totalThoughts": 5
  }
}
```

### Step 5: Revision if Needed

```json
{
  "tool": "sequential_thinking",
  "arguments": {
    "thought": "Wait, I think I misunderstood the experimental design. Let me re-read that section. Actually, they used a different approach...",
    "nextThoughtNeeded": true,
    "thoughtNumber": 4,
    "totalThoughts": 6,
    "isRevision": true,
    "revisesThought": 2
  }
}
```

### Step 6: Get Summary

```json
{
  "tool": "get_thinking_summary",
  "arguments": {}
}
```

## Common Use Cases

### 📚 Academic Research
- Analyze research papers methodology
- Compare different theoretical approaches
- Identify gaps in literature reviews

### 📊 Business Analysis  
- Review financial reports or market research
- Break down complex business cases
- Analyze competitor strategies

### 🔧 Technical Documentation
- Understand complex system architectures
- Debug technical specifications
- Learn new technologies step-by-step

### 📖 Educational Material
- Break down complex textbook chapters
- Solve mathematical proofs
- Understand scientific concepts

## Pro Tips

1. **Start Broad, Then Narrow**: First get overview, then dive into specifics
2. **Use Search Terms**: Include relevant keywords to find the right sections  
3. **Iterate**: Use revisions when you discover new insights
4. **Branch**: Explore alternative interpretations when needed
5. **Reset**: Clear state between different documents or problem types

## Example Queries for Different Document Types

### Research Papers
- "research methodology experimental design"
- "results statistical analysis findings"
- "limitations future work recommendations"

### Technical Manuals
- "installation setup configuration"
- "troubleshooting error handling"
- "API endpoints authentication"

### Business Documents
- "financial performance revenue analysis"
- "market trends competitive analysis" 
- "strategic recommendations implementation"

## Integration with Learning

This server is perfect for:
- **Active Reading**: Engage deeply with complex texts
- **Problem Decomposition**: Break down multi-step problems
- **Critical Analysis**: Question assumptions and explore alternatives
- **Knowledge Synthesis**: Connect ideas across different sections

Start with simpler documents to get comfortable with the workflow, then tackle more complex materials as you build proficiency with the sequential thinking approach!
