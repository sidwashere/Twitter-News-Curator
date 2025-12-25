# Twitter News Curator - Context Auto-Update System

## 🎯 Quick Start

Your project now has an **automated context management system**! Here's what you need to know:

### ✅ What's Set Up

1. **Auto-Update Script** - `scripts/update-context.ps1` scans your project and updates the context file
2. **Scheduler Setup** - `scripts/setup-scheduler.ps1` creates a daily Windows scheduled task
3. **Quick Update** - `UPDATE-CONTEXT.ps1` in the root for easy manual updates
4. **Configuration** - `.context-config.json` controls what gets scanned

### 🚀 How to Use

#### Manual Update (Right Now)

Double-click **`UPDATE-CONTEXT.ps1`** in the project root, or run:

```powershell
.\scripts\update-context.ps1
```

#### Automatic Daily Updates

Run this **once** as Administrator to set up daily auto-updates:

```powershell
.\scripts\setup-scheduler.ps1
```

This creates a Windows scheduled task that runs daily at 9:00 AM.

### 📋 What Gets Auto-Generated

Every time the script runs, it updates:

- **📊 Project Statistics** - File counts, lines of code, total size
- **📁 Project Structure** - Visual folder tree showing all files
- **📦 Dependencies** - Python packages, Node packages
- **🔧 Detected Technologies** - Frameworks and libraries found in code
- **📝 Recent Changes** - Last 10 modified files with timestamps

### 📝 Your Manual Notes Are Safe

Everything you write **above** the `AUTO-GENERATED CONTENT` marker stays untouched. The script only updates the technical sections at the bottom.

### ⚙️ Customization

Edit `.context-config.json` to:
- Add file/folder exclusions
- Change which file types to scan
- Enable/disable sections
- Configure tracking options

### 📚 Full Documentation

See `scripts/README.md` for:
- Detailed usage instructions
- Scheduling options
- Troubleshooting guide
- Advanced customization

### 🎬 Next Steps

1. **Set up the scheduler** (one-time):
   ```powershell
   .\scripts\setup-scheduler.ps1
   ```

2. **Start coding!** As you add files, dependencies, or restructure the project, the context will automatically update daily.

3. **Manual updates anytime**: Just double-click `UPDATE-CONTEXT.ps1`

### 🔍 Example Context Output

After running the script, your context file will look like:

```
# Your Manual Notes & Strategy
(Everything you write here is preserved)

---

## AUTO-GENERATED CONTENT
Last Updated: 2025-12-25 08:03:10

## 📊 Project Statistics
- Total Files: 5
- Code Files: 5
- Total Lines of Code: 876

## 📁 Project Structure
├── 📁 scripts/
  ├── 📄 README.md
  ├── 📄 setup-scheduler.ps1
  ├── 📄 update-context.ps1
...
```

---

**Need help?** Check `scripts/README.md` or review the script comments.

Happy coding! 🚀
