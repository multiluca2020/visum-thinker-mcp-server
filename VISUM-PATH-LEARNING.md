# Visum Path Learning and Configuration Persistence

The Sequential Thinking MCP Server now includes intelligent path learning for PTV Visum installations. This feature automatically remembers custom installation paths so users don't need to provide them repeatedly.

## 🧠 How It Works

### Automatic Path Discovery
The server automatically searches for Visum installations in:
1. **Known installations from previous sessions** (prioritized)
2. Standard installation paths:
   - `C:\Program Files\PTV Vision\PTV Visum 202X\Exe\VisumXXX.exe`
   - `C:\Program Files (x86)\PTV Vision\PTV Visum 202X\Exe\VisumXXX.exe`
3. **Custom user-provided paths**

### Path Learning Process

1. **First Time Setup**: When Claude can't find Visum in standard locations, it asks the user for a custom path
2. **Path Validation**: The system validates the custom path to ensure it's a valid Visum executable
3. **Automatic Storage**: Valid paths are automatically saved to `visum-config.json`
4. **Smart Prioritization**: Stored paths are checked first in future sessions
5. **Persistent Memory**: Configuration survives server restarts

### Configuration File Structure

The server creates a `visum-config.json` file with the following structure:

```json
{
  "knownInstallations": [
    {
      "path": "D:\\MyPrograms\\PTV\\Visum2024\\Exe\\Visum240.exe",
      "version": "Visum 24.0",
      "lastVerified": "2025-01-20T10:30:00.000Z"
    }
  ],
  "preferredPath": "D:\\MyPrograms\\PTV\\Visum2024\\Exe\\Visum240.exe",
  "lastUpdated": "2025-01-20T10:30:00.000Z"
}
```

## 🔧 Usage Examples

### Scenario 1: First Time with Custom Installation
```
User: "Check if Visum is available"
Claude: "❌ Visum not found in standard locations. If installed elsewhere, 
         please provide the full path to Visum executable."

User: "D:\Software\PTV\Visum\Exe\Visum240.exe"
Claude: "✅ Visum found and saved! Future checks will automatically use this path."
```

### Scenario 2: Subsequent Uses
```
User: "Check if Visum is available"
Claude: "✅ Visum Available
         Path: D:\Software\PTV\Visum\Exe\Visum240.exe
         Version: Visum 24.0
         Ready for transportation analysis!"
```

## 🎯 Benefits

### For Users
- **No Repetition**: Provide custom path only once
- **Automatic Detection**: System remembers and prioritizes known installations
- **Multiple Installations**: Supports and tracks multiple Visum versions
- **Seamless Experience**: Works transparently across server restarts

### For Claude
- **Intelligent Prompting**: Only asks for paths when truly needed
- **Context Awareness**: Knows about previous user setups
- **Error Reduction**: Validates paths before storing
- **Efficient Operation**: Checks known paths first

## 🔍 Technical Features

### Path Validation
- Verifies file existence
- Checks executable permissions
- Validates Visum-specific naming patterns
- Extracts version information

### Configuration Management
- Automatic backup on updates
- JSON format for easy inspection
- Timestamp tracking for verification
- Cleanup of invalid paths

### Demo Mode Integration
- Graceful fallback when Visum unavailable
- Full functionality testing without installation
- Realistic simulation data

## 📁 File Locations

- **Configuration**: `visum-config.json` (in server root directory)
- **Example Config**: `visum-config-example.json`
- **Logs**: Written to stderr for MCP compatibility

## 🛠️ Advanced Usage

### Manual Configuration
You can manually edit `visum-config.json` to:
- Add multiple known installations
- Set a preferred installation
- Update version information
- Remove outdated paths

### Troubleshooting
If experiencing path issues:
1. Delete `visum-config.json` to reset
2. Use the `check_visum` tool with `customPath` parameter
3. Check server logs for detailed error information

### API Integration
The learning system works with all Visum tools:
- `check_visum` - Discovery and validation
- `load_visum_model` - Uses preferred path automatically
- `run_visum_calculation` - Leverages stored configuration
- All other Visum tools benefit from the learned paths

## 🚀 Future Enhancements

Planned improvements include:
- Network path support for shared Visum installations
- Version compatibility checking
- Performance optimization for large installations
- Integration with Visum license management

---

This intelligent path learning system ensures that once you set up your Visum installation path, Claude will remember it permanently, making your transportation planning workflow seamless and efficient!
