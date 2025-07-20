# GitHub & NPM Publishing Guide

## 📂 **Step 1: Create GitHub Repository**

1. **Go to GitHub.com** and sign in
2. **Click "New repository"** (green button)
3. **Repository settings:**
   - Name: `visum-thinker-mcp-server`
   - Description: `Visum Thinker - MCP server for sequential thinking and PDF analysis`
   - ✅ Public (so others can use it)
   - ❌ Don't initialize with README (we already have one)

4. **Click "Create repository"**

## 🚀 **Step 2: Push to GitHub**

Your local git repo is ready! Run these commands:

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOURUSERNAME/visum-thinker-mcp-server.git

# Push your code to GitHub  
git branch -M main
git push -u origin main
```

**Replace `YOURUSERNAME` with your actual GitHub username!**

## 📦 **Step 3: Publish to NPM (Optional but Recommended)**

### Create NPM Account
1. Go to [npmjs.com](https://www.npmjs.com/)
2. Sign up for a free account
3. Verify your email

### Publish Your Package
```bash
# Login to npm
npm login

# Build your package
npm run build

# Publish to npm (make sure name is unique!)
npm publish
```

**Note:** The package name `visum-thinker-mcp-server` might be taken. If so, try:
- `@yourusername/visum-thinker-mcp-server`
- `visum-thinker-v2`
- `your-visum-thinker`

## 🎯 **Step 4: Update Package URLs**

After creating your GitHub repo, update `package.json`:

```json
{
  "homepage": "https://github.com/YOURUSERNAME/visum-thinker-mcp-server#readme",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/YOURUSERNAME/visum-thinker-mcp-server.git"
  },
  "bugs": {
    "url": "https://github.com/YOURUSERNAME/visum-thinker-mcp-server/issues"
  }
}
```

Then commit and push the changes:
```bash
git add package.json
git commit -m "Update repository URLs"
git push
```

## 📥 **Step 5: Installation on Other Machines**

Once published, anyone can install your server:

### From NPM:
```bash
# Install globally
npm install -g visum-thinker-mcp-server

# Or use with npx (no installation)
npx visum-thinker-mcp-server
```

### From GitHub:
```bash
# Clone and install
git clone https://github.com/YOURUSERNAME/visum-thinker-mcp-server.git
cd visum-thinker-mcp-server
npm install
npm run build
npm run dev
```

### Claude Desktop Configuration:
```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "npx",
      "args": ["-y", "visum-thinker-mcp-server"]
    }
  }
}
```

## 🔄 **Step 6: Updates and Versions**

### Update Your Server:
1. Make changes to your code
2. Update version in `package.json`:
   ```json
   {
     "version": "1.0.1"  // Increment version
   }
   ```
3. Commit and push:
   ```bash
   git add .
   git commit -m "Version 1.0.1: Added new features"
   git push
   ```
4. Publish to NPM:
   ```bash
   npm run build
   npm publish
   ```

### Users Update:
```bash
npm update -g visum-thinker-mcp-server
```

## 🌟 **Benefits of GitHub + NPM Publishing**

### ✅ **Easy Installation**
- `npm install -g visum-thinker-mcp-server` on any machine
- No need to copy files manually
- Automatic dependency management

### ✅ **Version Control**  
- Track all changes and improvements
- Users can install specific versions
- Easy rollbacks if needed

### ✅ **Community**
- Others can contribute improvements
- Issue tracking and bug reports
- Documentation hosting on GitHub Pages

### ✅ **Professional Distribution**
- Proper package management
- Semantic versioning (1.0.0, 1.0.1, etc.)
- Automated builds and testing

## 📋 **Checklist**

- [ ] Create GitHub repository
- [ ] Push local code to GitHub
- [ ] Update package.json with correct URLs  
- [ ] Test installation from GitHub
- [ ] (Optional) Create NPM account
- [ ] (Optional) Publish to NPM
- [ ] Test installation from NPM
- [ ] Update documentation with install instructions
- [ ] Share your server with others!

## 🎯 **Example Claude Desktop Config for Published Server**

Once published, users just need this simple config:

```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "npx",
      "args": ["-y", "visum-thinker-mcp-server"]
    }
  }
}
```

**No paths, no manual setup - just works!** 🚀

Your Visum Thinker will be available for download and use on any machine with Node.js installed. Perfect for sharing with colleagues, students, or the broader community!
