# AI Virtual Assistant

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A sophisticated virtual assistant powered by Google Gemini with real-time audio streaming. The assistant can interact with users via voice and has access to various tools through function calling, including Google Search, file management, Google Suite integration, and more.

*Inspired by Iron Man's JARVIS assistant*

</div>

## ✨ Features

- 🎤 **Real-time audio streaming** with Gemini Live API
- 🔍 **Google Search integration** for web queries
- 🛠️ **Extensible tool system** for function calling
- 📹 **Camera and screen capture support** (optional)
- 🇪🇸 **Spanish/Andalusian culture customization**
- ⚙️ **Meta commands** to control assistant behavior (sarcasm, humor, response length, formality)
- 💾 **Persistent configuration** stored in SQLite database
- 🔇 **Echo cancellation** (experimental) to prevent feedback loops

## 🏗️ Project Structure

```
Assistant/
├── src/
│   ├── main.py                    # Entry point
│   ├── audio/                     # Audio module
│   │   ├── audio_loop.py         # Main audio streaming loop
│   │   ├── audio_handler.py      # Audio I/O handling
│   │   └── echo_cancellation.py  # Echo cancellation (experimental)
│   ├── agent/                     # Agent orchestrator
│   │   ├── orchestrator.py       # Main agent
│   │   └── config.py             # Agent configuration
│   ├── tools/                     # Tool system
│   │   ├── base.py               # Base tool class
│   │   ├── assistant_config.py   # Meta commands tool
│   │   ├── google_search.py      # Google Search
│   │   ├── google_suite.py       # Google Suite (prepared)
│   │   ├── file_manager.py       # File management (prepared)
│   │   └── shopping_list.py      # Shopping list (prepared)
│   ├── database/                  # Database module
│   │   └── config_db.py          # SQLite configuration storage
│   └── utils/                     # Utilities
├── docs/                          # Documentation
│   └── ECHO_CANCELLATION_OPTIONS.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Microphone
- Speakers/headphones
- Camera (optional, for camera mode)
- Google Gemini API key

### System Dependencies

**macOS (with Homebrew):**
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Linux (Fedora):**
```bash
sudo dnf install portaudio-devel
```

### Python Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd Assistant
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get your API key at: https://makersuite.google.com/app/apikey

## 📖 Usage

### Basic Execution
```bash
python -m src.main
```

### Options
```bash
# Camera mode (default)
python -m src.main --mode camera

# Screen capture mode
python -m src.main --mode screen

# Audio only (no video)
python -m src.main --mode none

# Specify API key directly
python -m src.main --api-key your_api_key
```

### During Execution
- Speak to the assistant through your microphone
- Type "q" and press Enter to exit
- The assistant will respond with voice

### Meta Commands

You can control the assistant's behavior using voice commands:

- **"Set sarcasm level to 8"** - Adjust sarcasm (0-10)
- **"Set humor level to 6"** - Adjust humor (0-10)
- **"Make responses shorter"** - Change response length (short/medium/long)
- **"Use formal language"** - Change formality (informal/formal/very_formal)
- **"Address me as 'usted'"** - Change treatment (tú/usted/señor/señora)
- **"Show me your configuration"** - Get current settings
- **"Reset configuration"** - Reset to defaults

All settings are saved in `~/.assistant_config.db` and persist across sessions.

## 🛠️ Tool System

The project is designed to be easily extensible with new tools through function calling:

### ✅ Implemented
- **Google Search**: Web search (natively integrated)
- **Assistant Config**: Meta commands to control assistant behavior

### 🚧 Prepared for Implementation
- **Google Suite**: 
  - Read and modify Google Docs
  - Manage Google Calendar meetings
  - Summarize documents
  
- **File Manager**:
  - Read local files
  - List directories
  - Search files

- **Shopping List**:
  - Add/remove items from shopping list
  - Get complete list
  - Recommend products

## 🔧 Development

### Adding a New Tool

1. Create a new file in `src/tools/` that inherits from `BaseTool`
2. Implement `get_function_declarations()` and `execute()`
3. Register the tool in `src/tools/__init__.py` in the `get_all_tools()` function

Example:
```python
from .base import BaseTool
from typing import List, Dict, Any
from google.genai import types

class MyNewTool(BaseTool):
    def get_function_declarations(self) -> List[types.FunctionDeclaration]:
        return [
            self._create_function_declaration(
                name="my_function",
                description="Description of the function",
                parameters={
                    "param1": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                }
            )
        ]
    
    async def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        if function_name == "my_function":
            # Implement logic
            return {"result": "success"}
        raise ValueError(f"Function {function_name} not found")
```

## 📝 Configuration

The assistant configuration is stored in SQLite at `~/.assistant_config.db`. You can modify it programmatically or through meta commands.

### Default Configuration
- Sarcasm level: 3/10
- Humor level: 5/10
- Response length: medium
- Formality: informal
- Treatment: tú

## 🐛 Troubleshooting

### Audio Issues
- **No audio input**: Check microphone permissions
- **Echo/feedback**: Echo cancellation is experimental and currently disabled by default
- **Assistant cuts off**: Check logs for errors, may be related to turn coverage settings

### API Issues
- **Connection errors**: Verify your `GEMINI_API_KEY` is correct
- **Rate limits**: Check your API quota

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

- [ ] Implement Google Suite integration (Docs, Calendar)
- [ ] Implement file manager tool
- [ ] Implement shopping list tool
- [ ] Improve echo cancellation
- [ ] Add voice activity detection
- [ ] Add conversation history
- [ ] Add multi-language support

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🙏 Acknowledgments

- Built with [Google Gemini API](https://ai.google.dev/)
- Uses [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/) for audio I/O
- Inspired by Iron Man's JARVIS assistant

## 📚 Documentation

- [Echo Cancellation Options](docs/ECHO_CANCELLATION_OPTIONS.md)
- [Google Gemini Live API Documentation](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.py)
