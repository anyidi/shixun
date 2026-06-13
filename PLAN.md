# PyQt6 Manga Translator Desktop Application - Implementation Plan

## Project Overview
Create a PyQt6 desktop application for translating Japanese manga images to Chinese, based on the manga-image-translator project architecture.

## Key Requirements
1. Use manga-image-translator's core logic unchanged
2. Use Baidu translator for translations
3. Simple UI: select image → translate → display result
4. Clean, minimalist design without gradients
5. Maintain project's modular architecture

## Architecture Analysis

### Core Components (from manga-image-translator)
1. **MangaTranslator** (`manga_translator.py`)
   - Main translation orchestrator
   - Handles detection, OCR, translation, inpainting, rendering pipeline
   - Uses async/await pattern
   - Supports config-based initialization

2. **MangaTranslatorLocal** (`mode/local.py`)
   - Local file mode handler
   - `translate_path()` - main entry point for file translation
   - `translate_file()` - single file processing
   - Returns results to `result/final.png`

3. **Config System** (`config.py`)
   - Pydantic-based configuration
   - TranslatorConfig with translator type and target_lang
   - JSON/TOML config file support

4. **Translation Flow**:
   ```
   Image Input → Detection → OCR → Translation → Inpainting → Rendering → Output
   ```

### Existing UI Reference (MangaStudio_Data/app)
- Uses PySide6 (Qt for Python)
- Has Pipeline class for backend integration
- Uses threading for async operations
- Signal/slot pattern for UI updates

## Implementation Strategy

### 1. Project Structure
```
F:\6176\
├── main.py                    # Application entry point
├── ui/
│   ├── __init__.py
│   ├── main_window.py         # Main window UI
│   └── widgets.py             # Custom widgets
├── core/
│   ├── __init__.py
│   ├── translator_wrapper.py # Wrapper for manga-translator
│   └── config_manager.py      # Config file management
├── resources/
│   └── styles.qss            # Qt stylesheet
├── config.json               # Default Baidu translator config
└── requirements.txt          # Dependencies
```

### 2. Core Integration Approach

**translator_wrapper.py**:
- Import `MangaTranslatorLocal` from manga-image-translator
- Create wrapper class that:
  - Initializes translator with Baidu config
  - Provides `translate_image(input_path)` method
  - Runs async code using `asyncio.run()`
  - Returns result image path
- Handle environment variables for Baidu API keys

**config_manager.py**:
- Create default config with Baidu translator
- Read/write Baidu API credentials
- Generate config dict for MangaTranslatorLocal

### 3. UI Design (PyQt6)

**Main Window Layout**:
```
┌─────────────────────────────────────────┐
│  Manga Translator - 日译中              │
├─────────────────────────────────────────┤
│  [选择图片...]  [开始翻译]  [保存结果]  │
├─────────────────────────────────────────┤
│  ┌─────────────┐      ┌─────────────┐  │
│  │   原图      │      │  翻译结果   │  │
│  │  (预览)     │      │  (预览)     │  │
│  │             │      │             │  │
│  └─────────────┘      └─────────────┘  │
├─────────────────────────────────────────┤
│  进度条: [████████░░░░] 80%            │
│  状态: 正在翻译...                      │
└─────────────────────────────────────────┘
```

**Features**:
- Two QLabel widgets for image display (original + result)
- QProgressBar for translation progress
- QTextEdit for status/log messages
- QPushButton for actions
- Simple toolbar for settings (API keys)

### 4. Threading Strategy

**Worker Thread**:
- Run translation in separate QThread to avoid UI freeze
- Emit signals for progress updates
- Use QRunnable + QThreadPool pattern

**Progress Reporting**:
- Hook into manga-translator's progress system
- Emit signals back to main thread
- Update progress bar and status text

### 5. Configuration

**config.json**:
```json
{
  "translator": {
    "translator": "baidu",
    "target_lang": "CHS"
  },
  "detector": {
    "detector": "default",
    "detection_size": 2048
  },
  "ocr": {
    "ocr": "48px"
  },
  "inpainter": {
    "inpainter": "lama_large"
  }
}
```

**API Key Storage**:
- Store in user settings file or environment variables
- Settings dialog to input BAIDU_APP_ID and BAIDU_SECRET_KEY

### 6. UI Styling (No Gradients)

**Color Scheme**:
- Background: #f5f5f5 (light gray)
- Panels: #ffffff (white)
- Borders: #d0d0d0 (medium gray)
- Primary button: #4CAF50 (flat green)
- Text: #333333 (dark gray)
- Accent: #2196F3 (flat blue)

**QSS Stylesheet**:
- Flat design with solid colors
- Subtle borders and shadows
- Clean typography
- Consistent padding/margins

### 7. Error Handling

- Validate image file before translation
- Check Baidu API credentials
- Display user-friendly error messages
- Log detailed errors to file
- Graceful degradation on failures

## Implementation Steps

### Phase 1: Core Setup
1. Create project structure
2. Set up virtual environment
3. Install dependencies (PyQt6, manga-image-translator libs)
4. Create basic config.json

### Phase 2: Backend Integration
1. Implement translator_wrapper.py
   - Import MangaTranslatorLocal
   - Create async wrapper
   - Handle Baidu API credentials
2. Implement config_manager.py
   - Load/save config
   - Manage API keys
3. Test translation standalone (CLI)

### Phase 3: UI Development
1. Create main_window.py
   - Basic window structure
   - Layout components
2. Implement image selection
   - File dialog
   - Image preview
3. Create worker thread
   - Translation in background
   - Signal/slot connections
4. Add progress reporting
   - Progress bar
   - Status messages

### Phase 4: Styling & Polish
1. Create styles.qss
   - Flat design theme
   - Consistent styling
2. Add icons (optional)
3. Error dialogs
4. Settings dialog for API keys

### Phase 5: Testing & Refinement
1. Test with various manga images
2. Handle edge cases
3. Performance optimization
4. User experience improvements

## Technical Considerations

### Dependencies
```
PyQt6>=6.6.0
manga-image-translator (reference existing installation)
Pillow>=10.0.0
```

### Path Management
- Reference manga-image-translator at `f:\shixun\manga-image-translator`
- Add to Python path or install as editable package
- Store results in application directory

### Async Integration
```python
import asyncio
from manga_translator.mode.local import MangaTranslatorLocal

def run_translation(input_path, config):
    """Run async translation in sync context"""
    translator = MangaTranslatorLocal({
        'use_gpu': True,
        'verbose': True
    })
    return asyncio.run(
        translator.translate_path(input_path, None, config)
    )
```

### Environment Variables
```python
import os
os.environ['BAIDU_APP_ID'] = app_id
os.environ['BAIDU_SECRET_KEY'] = secret_key
```

## Open Questions
1. Should we copy models to app directory or reference original location?
   - **Decision**: Reference original to avoid duplication
2. Show intermediate images (detection, inpainting)?
   - **Decision**: Start simple, add later if needed
3. Batch processing support?
   - **Decision**: Single image first, batch as enhancement

## Success Criteria
- [x] Application launches without errors
- [ ] Can select and preview manga image
- [ ] Translation completes successfully with Baidu
- [ ] Result displays correctly
- [ ] UI is clean and responsive
- [ ] No crashes during translation
- [ ] Proper error messages shown
