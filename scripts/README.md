# Context Auto-Update Scripts

Automated system for keeping your project documentation up-to-date as the Twitter News Curator grows.

## 📁 Files

- **`update-context.ps1`** - Main script that scans and updates context
- **`setup-scheduler.ps1`** - Configures automatic scheduling
- **`README.md`** - This file

## 🚀 Quick Start

### One-Time Setup

1. **Set Execution Policy** (if needed):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Run the scheduler setup** (as Administrator):
   ```powershell
   cd "x:\Projects\Twitter News Curator\scripts"
   .\setup-scheduler.ps1
   ```

   This creates a daily scheduled task that runs at 9:00 AM.

### Manual Update

To update the context file immediately:

```powershell
.\update-context.ps1
```

With verbose output:

```powershell
.\update-context.ps1 -VerboseOutput
```

Force update (even if no changes):

```powershell
.\update-context.ps1 -Force -VerboseOutput
```

## ⚙️ Configuration

Edit `.context-config.json` in the project root to customize:

```json
{
  "contextFile": "context for the news curator.md",
  "excludePatterns": ["node_modules", ".git", "__pycache__"],
  "includeFileTypes": [".py", ".js", ".json", ".md"],
  "autoSections": {
    "architecture": true,
    "structure": true,
    "dependencies": true
  },
  "trackChanges": true
}
```

### Options

- **`contextFile`** - Name of your context markdown file
- **`excludePatterns`** - Folders/files to ignore during scanning
- **`includeFileTypes`** - File extensions to analyze
- **`autoSections`** - Which sections to auto-generate
- **`trackChanges`** - Show recently modified files

## 📋 What Gets Updated

The script automatically generates:

### Project Statistics
- Total files and size
- Code files count
- Lines of code

### Project Structure
- Visual folder tree (max 3 levels deep)
- File sizes

### Dependencies
- Python packages (from `requirements.txt`)
- Node packages (from `package.json`)

### Detected Technologies
- Automatically identifies frameworks and libraries by scanning imports

### Recent Changes
- Last 10 modified files with timestamps

## 🎯 How It Works

1. **Preserves Manual Content** - Everything you write above the `AUTO-GENERATED` marker stays untouched
2. **Scans Project** - Recursively analyzes all files (excluding configured patterns)
3. **Generates Sections** - Creates up-to-date technical documentation
4. **Updates Context** - Replaces only the auto-generated section

### Context File Structure

```markdown
# Your Manual Notes
(This section is preserved)

---

## AUTO-GENERATED CONTENT
(Everything below is regenerated)

## Project Statistics
...

## Project Structure
...
```

## 📅 Scheduling Options

### Daily at Specific Time
```powershell
.\setup-scheduler.ps1 -Schedule Daily -Time "14:30"
```

### On System Startup
```powershell
.\setup-scheduler.ps1 -Schedule OnStartup
```

### Custom Schedule
Open Task Scheduler (`Win + R` → `taskschd.msc`) and modify the task manually.

## 🔧 Management

### Check Task Status
```powershell
Get-ScheduledTask -TaskName "TwitterCurator-ContextUpdate"
```

### Run Task Now
```powershell
Start-ScheduledTask -TaskName "TwitterCurator-ContextUpdate"
```

### Disable Task
```powershell
Disable-ScheduledTask -TaskName "TwitterCurator-ContextUpdate"
```

### Enable Task
```powershell
Enable-ScheduledTask -TaskName "TwitterCurator-ContextUpdate"
```

### Remove Task
```powershell
Unregister-ScheduledTask -TaskName "TwitterCurator-ContextUpdate" -Confirm:$false
```

## 📊 Viewing Logs

Logs are saved to `scripts/update-context.log`:

```powershell
Get-Content .\update-context.log -Tail 20
```

View in real-time:

```powershell
Get-Content .\update-context.log -Wait
```

## 🐛 Troubleshooting

### "Execution Policy" Error

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Access Denied" Error

Run PowerShell as Administrator for scheduler setup.

### Task Not Running

1. Open Task Scheduler (`taskschd.msc`)
2. Find `TwitterCurator-ContextUpdate`
3. Check "Last Run Result" and "History" tab
4. Verify user account has permissions

### Context Not Updating

1. Run manually with verbose flag:
   ```powershell
   .\update-context.ps1 -VerboseOutput
   ```
2. Check the log file for errors
3. Verify `.context-config.json` exists and is valid JSON

### Files Not Being Detected

Check your exclude patterns in `.context-config.json`. Make sure you're not accidentally excluding important directories.

## 🎨 Customization

### Change Update Frequency

Edit the scheduled task in Task Scheduler or re-run `setup-scheduler.ps1` with different parameters.

### Add Custom Sections

Modify `update-context.ps1` to add your own auto-generated sections. Look for the "Build new context" section around line 170.

### Filter Specific File Types

Edit `includeFileTypes` in `.context-config.json`:

```json
"includeFileTypes": [".py", ".js", ".md"]
```

### Exclude More Patterns

Add to `excludePatterns` in `.context-config.json`:

```json
"excludePatterns": ["node_modules", ".git", "temp", "*.tmp"]
```

## 💡 Tips

1. **Keep manual notes at the top** - Write your strategy, ideas, and notes before the AUTO-GENERATED marker
2. **Run after major changes** - Manually update after adding new dependencies or restructuring
3. **Review logs periodically** - Check for any scanning errors
4. **Commit the config** - Keep `.context-config.json` in version control

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the log file for specific errors
3. Ensure all paths are correct in the config file
4. Try running with `-VerboseOutput` flag for detailed information
