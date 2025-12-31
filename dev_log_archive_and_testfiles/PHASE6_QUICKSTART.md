# Phase 6 Quick Start: Using Vision 📸

## How to Use Image Support

### Quick Steps

1. **Launch the app**
   ```bash
   streamlit run main.py
   ```

2. **Upload images**
   - Click the "📎 Upload images (optional)" button
   - Select one or more images (JPG, PNG, WebP, GIF)
   - See thumbnails appear

3. **Add your message** (optional)
   - Type a question or instruction
   - Or leave blank to let Claude describe the image

4. **Send**
   - Press Enter or click outside the chat input
   - Claude will analyze your images!

---

## Examples to Try

### 1. Single Image Description
```
Upload: photo.jpg
Message: "What's in this image?"
```

### 2. Multiple Image Comparison
```
Upload: image1.jpg, image2.jpg
Message: "Compare these images"
```

### 3. Image-Only Query
```
Upload: diagram.png
Message: (leave blank)
```

### 4. Code Screenshot
```
Upload: error_screenshot.png
Message: "Fix this error"
```

### 5. Data Extraction
```
Upload: chart.png
Message: "Extract the data from this chart"
```

---

## Supported Formats

✅ **JPG/JPEG** - Most common, good compression
✅ **PNG** - Lossless, supports transparency
✅ **WebP** - Modern format, efficient
✅ **GIF** - Animations supported

❌ **Not supported**: SVG, BMP, TIFF

---

## Size Limits

**Maximum**: 5MB per image (after encoding)
**Recommended**: Under 3MB for best performance

If image is too large:
- Compress before uploading
- Resize to smaller dimensions
- Convert to JPG with lower quality

---

## Tips & Tricks

### Best Practices
1. **Clear images work best** - Good lighting, focus
2. **Higher resolution = better OCR** - For text extraction
3. **Multiple angles help** - For 3D object recognition
4. **Describe what you want** - Be specific in your message

### Cost Optimization
- Use **Haiku** for simple vision tasks (cheapest)
- Use **Sonnet** for balanced performance
- Use **Opus** only for complex visual analysis

### Common Use Cases
- **Screenshots** - Debug errors, analyze UI
- **Documents** - Extract text, analyze structure
- **Photos** - Identify objects, describe scenes
- **Diagrams** - Explain flowcharts, interpret charts
- **Comparisons** - Before/after, side-by-side

---

## Troubleshooting

### "Image too large" error
**Problem**: Image exceeds 5MB limit
**Solution**: Compress or resize the image

### Image won't upload
**Problem**: Unsupported format
**Solution**: Convert to JPG, PNG, WebP, or GIF

### No response from Claude
**Problem**: API error or timeout
**Solution**: Check internet connection, try smaller image

### Images disappeared
**Problem**: Expected - images cleared after sending
**Solution**: This is normal behavior, re-upload if needed

---

## Model Selection

**All models support vision!**

- **Claude Opus 4.5** - Best vision analysis
- **Claude Sonnet 4.5** - Balanced (recommended)
- **Claude Sonnet 3.7** - Fast vision
- **Claude Haiku 3.5** - Fastest, cheapest

Choose based on:
- **Complexity** of image
- **Accuracy** needed
- **Cost** constraints
- **Speed** requirements

---

## Example Workflows

### Workflow 1: Code Review
```
1. Take screenshot of code
2. Upload to chat
3. Ask: "Review this code for issues"
4. Get detailed analysis
```

### Workflow 2: Data Analysis
```
1. Upload chart/graph image
2. Ask: "What trends do you see?"
3. Get insights and interpretation
```

### Workflow 3: Design Feedback
```
1. Upload mockup or wireframe
2. Ask: "Suggest improvements"
3. Get UX/UI recommendations
```

### Workflow 4: Document Processing
```
1. Upload document photo
2. Ask: "Extract the key information"
3. Get structured summary
```

---

## Advanced Usage

### Multiple Images
Upload up to 10+ images in one message for:
- Comparisons
- Sequences
- Multiple perspectives
- Related content

### Mixed Content
Combine text and images:
```
Upload: diagram.png
Message: "Explain step 3 of this diagram"
```

### Follow-up Questions
After Claude analyzes an image:
```
You: "What's the car model?"
Claude: "It's a Tesla Model 3"
You: "What year?"
Claude: [references image] "Based on the design..."
```

Note: Images not persisted between sessions!

---

## Performance

**Upload time**: ~100-500ms (depends on size)
**Processing time**: +2-5 seconds (vs text-only)
**Token cost**: +85-170 tokens per image

**Total response time**:
- Small image + simple query: 3-5 seconds
- Large image + complex query: 10-15 seconds

---

## Privacy & Security

**What happens to your images**:
- ✅ Processed in-session only
- ✅ Sent to Claude API
- ✅ Not saved to disk
- ✅ Cleared after sending
- ⚠️ Not persisted in conversation history

**Recommendations**:
- Don't upload sensitive/confidential images
- Remove EXIF data if needed (use external tool)
- Be aware images sent to Claude API

---

## Limitations

**Current Phase 6 limitations**:
- No image persistence (lost on restart)
- No image editing (crop, resize, rotate)
- No automatic compression
- No URL support (must upload files)
- No drag-and-drop (yet)
- Preview shows max 4 images

**Workarounds**:
- Edit images externally before upload
- Use image compression tools
- Keep original files for reference

---

## What's Different from Phase 5?

**Phase 5** (before):
```
- Text-only chat
- No vision support
- Model selection without vision indicators
```

**Phase 6** (now):
```
+ Vision support on all models
+ Image upload UI
+ Image previews
+ Multi-image messages
+ Enhanced model labels
+ "Vision support 👁️" in caption
```

---

## Need Help?

### Documentation
- `PHASE6_COMPLETE.md` - Full technical details
- `PHASE6_PLAN.md` - Original implementation plan
- `test_phase6.py` - Test suite

### Testing
```bash
# Run Phase 6 tests
python test_phase6.py

# Should show 15/15 tests passed
```

### Common Issues
- Image not uploading → Check format and size
- API error → Check internet and API key
- No response → Image may be too complex, try Opus

---

## Quick Reference

| Feature | Status | Notes |
|---------|--------|-------|
| JPG upload | ✅ | Most common |
| PNG upload | ✅ | Transparency OK |
| WebP upload | ✅ | Modern format |
| GIF upload | ✅ | Animations OK |
| Multiple images | ✅ | No limit |
| Image preview | ✅ | Max 4 shown |
| Size validation | ✅ | 5MB max |
| All models | ✅ | Vision enabled |
| Persistence | ❌ | Session only |
| Editing | ❌ | External tools |

---

## Ready to Try!

**Launch the app and upload your first image:**

```bash
cd claude-version
source venv/bin/activate
streamlit run main.py
```

Open http://localhost:8501 and start analyzing images! 📸✨

---

*Phase 6 Quick Start | December 29, 2025*
