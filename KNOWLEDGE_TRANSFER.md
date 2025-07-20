# Knowledge Transfer Guide

Your **Visum Thinker MCP Server** now supports **full knowledge persistence and transfer** between servers and sessions!

## 🔄 **How Knowledge Persistence Works**

### Auto-Save Features
- **Every thought** is automatically saved to disk
- **PDF context** persists across server restarts  
- **State recovery** happens automatically on startup
- **Local storage** in `.thinking-storage/thinking-state.json`

### Knowledge Transfer
- **Export** your complete knowledge base
- **Import** to any other Sequential Thinking server
- **Backup** your thinking sessions
- **Share** knowledge with collaborators

## 📦 **Export/Import Workflow**

### Step 1: Export Your Knowledge

```json
{
  "tool": "export_knowledge",
  "arguments": {
    "exportPath": "/Users/uovo/Documents/my-research-session.json"
  }
}
```

**This exports:**
- ✅ All thinking thoughts and progression
- ✅ PDF content and metadata
- ✅ Thinking session state
- ✅ Export timestamp and version info

### Step 2: Transfer the File

Move the exported JSON file to your new server:
```bash
# Copy to another machine
scp my-research-session.json user@newserver:/path/to/destination/

# Copy to cloud storage
cp my-research-session.json ~/Dropbox/thinking-sessions/

# Email, USB, whatever works for you
```

### Step 3: Import on New Server

```json
{
  "tool": "import_knowledge", 
  "arguments": {
    "importPath": "/path/to/my-research-session.json"
  }
}
```

**This restores:**
- ✅ Complete thinking history
- ✅ PDF context (no need to reload PDF!)
- ✅ Session progress and status
- ✅ Ready to continue where you left off

## 🌟 **Use Cases**

### 📚 **Academic Collaboration**
```bash
1. Student exports analysis of research paper
2. Professor imports to review thinking process  
3. Professor adds thoughts and exports back
4. Collaborative learning and feedback
```

### 💼 **Team Problem Solving**
```bash
1. Team member A analyzes business document
2. Exports thinking session with insights
3. Team member B imports and continues analysis
4. Knowledge builds incrementally across team
```

### 🖥️ **Multi-Device Workflow**
```bash
1. Start analysis on laptop (home)
2. Export knowledge session
3. Continue on desktop (office)
4. Move seamlessly between environments
```

### 🔄 **Backup & Recovery**
```bash
1. Regular exports as "thinking backups"
2. Server crashes? No problem!
3. Import last backup and continue
4. Never lose your analysis progress
```

## 📁 **File Structure**

### Local Storage
```
sequential_thinking/
├── .thinking-storage/
│   └── thinking-state.json     # Auto-saved state
├── build/
└── src/
```

### Export File Format
```json
{
  "thoughts": [...],
  "currentThoughtNumber": 5,
  "totalThoughts": 8,
  "isComplete": false,
  "pdfContext": {
    "filename": "research-paper.pdf",
    "content": "full PDF text...",
    "pageCount": 25,
    "loadedAt": "2025-07-20T..."
  },
  "exportedAt": "2025-07-20T...",
  "serverVersion": "1.0.0"
}
```

## 🛡️ **Best Practices**

### 📋 **Regular Exports**
- Export after major thinking milestones
- Use descriptive filenames: `research-methodology-analysis.json`
- Date your exports: `project-analysis-2025-07-20.json`

### 🗂️ **Organization**
```bash
~/thinking-exports/
├── research-projects/
│   ├── paper1-analysis.json
│   └── paper2-critique.json
├── business-analysis/
│   ├── q3-report-review.json
│   └── competitor-analysis.json
└── learning-sessions/
    ├── machine-learning-textbook-ch3.json
    └── statistics-problem-set.json
```

### 🔄 **Version Control**
- Keep multiple versions of complex analyses
- Name with progress indicators: `analysis-v1-initial.json`, `analysis-v2-revised.json`
- Export before major revisions or branching

### 🤝 **Sharing**
- Clean up sensitive paths before sharing
- Include README with context when sharing
- Version control collaborative exports

## ⚡ **Migration Scenarios**

### 🖥️ **New Server Setup**
```bash
1. Install Sequential Thinking server on new machine
2. Import your knowledge file
3. Instantly ready with all PDF context and thinking history
```

### 🔄 **Server Updates**
```bash
1. Export knowledge before updating server
2. Update server software
3. Import knowledge to restore state
4. Continue with enhanced capabilities
```

### 💾 **Backup Strategy**
```bash
# Daily backup script
export_knowledge → daily-backup-$(date).json

# Weekly archive
export_knowledge → weekly-archive-$(date).json

# Project milestones
export_knowledge → project-phase1-complete.json
```

## 🎯 **Pro Tips**

1. **Auto-Recovery**: Server remembers everything automatically
2. **Clean Exports**: Export includes full PDF text - no external files needed
3. **Cross-Platform**: JSON exports work on any system
4. **Incremental**: Import overwrites current state, so export first if needed
5. **Collaboration**: Perfect for peer review and team analysis

Your knowledge is now **truly portable** - analyze anywhere, continue everywhere! 🚀
