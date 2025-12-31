# Phase 5 Quick Start Guide 🚀

## New Features at a Glance

Phase 5 adds **4 major UI enhancements** to Apex Aurum - Claude Edition:

---

## 1. 🌙 Dark Mode Theme

**What**: Professional dark theme automatically applied

**How to verify**:
- Launch the app: `streamlit run main.py`
- Should see dark background immediately
- No configuration needed - it's the default!

**Colors**:
- Background: Dark charcoal
- Sidebar: Slate gray
- Accent: Coral red
- Text: Off-white

---

## 2. 📚 Conversation Browser

**What**: Load and manage previous conversations

**Location**: Sidebar → "Browse Conversations" expander

**How to use**:
```
1. Click "Browse Conversations" in sidebar
2. See list of all past chats
3. Click "📂 Load" to restore a conversation
4. Click "🗑️ Delete" to remove one permanently
```

**Example**:
```
Dec 29, 01:08 (12 messages)
Preview: "Hello, can you help me with..."
[📂 Load] [🗑️ Delete]
```

---

## 3. 📁 File Browser

**What**: View and manage files created by Claude

**Location**: Sidebar → "Browse Sandbox Files" expander

**How to use**:
```
1. Click "Browse Sandbox Files" in sidebar
2. See all files in ./sandbox/ directory
3. Click "👁️ View" to see file contents
4. Click "🗑️ Delete" to remove (non-system files)
```

**Protected files** (cannot delete):
- `conversations.json`
- `memory.json`
- `agents.json`

**Example**:
```
test.txt (0.02 KB) • Modified: Dec 29, 01:00
[👁️ View] [🗑️ Delete]
```

---

## 4. 🧠 Memory Viewer

**What**: See what Claude remembers about you

**Location**: Sidebar → "Browse Memory Entries" expander

**How to use**:
```
1. Click "Browse Memory Entries" in sidebar
2. See all stored key-value pairs
3. Click "🗑️ Delete" to remove an entry
4. For long values, click expander to see full content
```

**Example**:
```
favorite_color
Value: blue
Stored: Dec 29, 01:00
[🗑️ Delete]
```

---

## 5. 🎛️ Advanced Settings

**What**: Fine-tune Claude's behavior

**Location**: Sidebar → "Model Parameters" expander

**Controls**:

### Temperature (0.0 - 1.0)
- **Lower (0.3)**: Focused, consistent responses
- **Medium (0.7)**: Balanced creativity
- **Higher (1.0)**: Maximum creativity (default)

### Top P (0.0 - 1.0)
- **Lower (0.8)**: More focused word choices
- **Higher (0.99)**: More diverse responses (default)

### Max Tokens (256 - 8192)
- **Lower**: Shorter responses, faster, cheaper
- **Higher**: Longer responses, more detailed
- **Default**: 4096 (good balance)

**When to adjust**:
- Need consistent output? → Lower temperature
- Want creative ideas? → Higher temperature
- Getting cut-off responses? → Increase max tokens
- Need faster responses? → Decrease max tokens

---

## Quick Testing Checklist

Test the new features:

### Dark Mode
- [ ] Launch app - dark theme active?
- [ ] All text readable?
- [ ] Sidebar looks good?

### Conversation Browser
- [ ] Can you see past conversations?
- [ ] Load button works?
- [ ] Delete button works?

### File Browser
- [ ] Files listed with sizes?
- [ ] View button shows content?
- [ ] Delete works (non-protected files)?
- [ ] Protected files can't be deleted?

### Memory Viewer
- [ ] Memory entries displayed?
- [ ] Can view full values?
- [ ] Delete works?

### Advanced Settings
- [ ] Temperature slider moves?
- [ ] Top P slider moves?
- [ ] Max tokens accepts input?
- [ ] Settings affect responses?

---

## Keyboard Shortcuts

No new shortcuts, but good to know:

- **Enter**: Send message
- **Shift+Enter**: New line in message
- **Ctrl+R**: Refresh page
- **Ctrl+C**: Stop Streamlit server

---

## Common Tasks

### Cleaning Up Old Data

**Delete old conversations**:
```
Sidebar → 📚 Conversation History → Select conversation → 🗑️ Delete
```

**Delete temporary files**:
```
Sidebar → 📁 File Browser → Select file → 🗑️ Delete
```

**Clear memory**:
```
Sidebar → 🧠 Memory Viewer → Select entry → 🗑️ Delete
```

### Loading a Previous Chat

```
1. Sidebar → 📚 Conversation History
2. Find conversation you want
3. Click 📂 Load
4. Conversation appears in main chat
5. Continue where you left off!
```

### Fine-Tuning Responses

**For coding tasks** (need precision):
```
Temperature: 0.3
Top P: 0.9
Max Tokens: 4096
```

**For creative writing** (need variety):
```
Temperature: 0.9
Top P: 0.99
Max Tokens: 8192
```

**For quick answers** (need speed):
```
Temperature: 0.7
Top P: 0.95
Max Tokens: 1024
```

---

## Troubleshooting

### Dark mode not showing
```bash
# Check config exists
ls -la .streamlit/config.toml

# If missing, re-run:
streamlit run main.py
# Should create automatically
```

### Sidebar looks cluttered
```
Solution: All new features are in collapsible expanders
- Close expanders you're not using
- Default: all collapsed (clean look)
```

### Can't delete a file
```
Check: Is it a protected file?
- conversations.json (protected)
- memory.json (protected)
- agents.json (protected)

Other files: should be deletable
If not, check file permissions
```

### Advanced settings not working
```
Check: Settings only affect NEW messages
- Send a new message after changing settings
- Previous messages use their original settings
```

---

## Pro Tips 💡

1. **Collapse expanders** you're not using for a cleaner sidebar
2. **Load conversations** to continue multi-day projects
3. **Check memory regularly** to see what Claude remembers
4. **Use file browser** to verify files Claude creates
5. **Adjust temperature** based on task type (coding vs creative)
6. **Lower max tokens** for faster responses
7. **Delete old conversations** to keep storage clean

---

## Need Help?

### Documentation
- `PHASE5_COMPLETE.md` - Full technical details
- `README.md` - General project info
- `IMPLEMENTATION_PLAN.md` - Architecture details

### Testing
```bash
# Run Phase 5 tests
python test_phase5.py

# Should show: 10/10 tests passed ✅
```

### Support
- Check logs: `app.log`
- Report issues: GitHub issues
- Review error messages in UI

---

## What's Changed?

### Before Phase 5
```
Basic features:
- Chat with Claude
- Enable/disable tools
- Change model
- Edit system prompt
```

### After Phase 5
```
Enhanced features:
+ Browse past conversations
+ Manage files visually
+ View stored memory
+ Fine-tune model parameters
+ Professional dark theme
```

**Result**: More powerful, more transparent, better UX! 🎉

---

**Quick Start Complete! Enjoy your enhanced Claude experience!** 🚀

Launch the app:
```bash
cd claude-version
source venv/bin/activate
streamlit run main.py
```

Open: http://localhost:8501

---

*Built with Claude Sonnet 4.5 | December 29, 2025*
