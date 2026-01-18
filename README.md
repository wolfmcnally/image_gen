# image-gen

Generate or edit images using OpenAI GPT or Google Gemini APIs.

## Installation

### From source (pre-publication)

This package is not yet published to PyPI. Install from the local source:

```bash
# Clone and install as a CLI tool (requires Python 3.11+)
git clone https://github.com/wolf/image-gen.git
cd image-gen
uv tool install --python 3.11 ".[all]"

# To update after code changes (clear cache to ensure fresh install)
uv cache clean image-gen && uv tool install --force --python 3.11 ".[all]"
```

Or run directly without installing:

```bash
cd image-gen
uv run image-gen -p "your prompt"
```

### From PyPI (after publication)

Once published, install with:

```bash
# Install as a CLI tool with uv (recommended)
uv tool install "image-gen[all]"

# Or with pip
pip install "image-gen[all]"

# With specific backends only
uv tool install "image-gen[openai]"   # OpenAI only
uv tool install "image-gen[gemini]"   # Gemini only
```

### Adding as a project dependency

If you want to use image-gen as a library in your own project:

```bash
uv add "image-gen[all]"
```

## Usage

### Generate images from text prompts

```bash
# Generate with OpenAI (default)
image-gen -p "A cat in a spacesuit" -o space_cat.png

# Generate with Gemini
image-gen --api gemini -p "A mountain landscape" -q high --size 16:9

# Generate multiple variations
image-gen -p "Abstract art" -n 3
```

### Edit existing images

```bash
# Single image edit
image-gen photo.jpg -p "Make it look like a painting"

# Multi-image composition
image-gen style.jpg photo.jpg -p "Apply the style of Image 1 to Image 2"
```

### Output filenames

When no output path is specified with `-o`:

- **Generation (no input images):** saves to `generated_1.png`, `generated_2.png`, etc.
- **Editing (with input images):** uses the last input filename as the base (e.g., `photo.jpg` → `photo_1.png`, `photo_2.png`, etc.)

The tool always appends a number suffix and finds the next available number to avoid overwriting existing files.

```bash
# Outputs: generated_1.png
image-gen -p "A sunset"

# Outputs: generated_1.png, generated_2.png, generated_3.png
image-gen -p "A sunset" -n 3

# Outputs: photo_1.png
image-gen photo.jpg -p "Add a rainbow"

# Outputs: photo_1.png, photo_2.png
image-gen photo.jpg -p "Add a rainbow" -n 2
```

### Options

| Option              | Description                                              | Default         |
|---------------------|----------------------------------------------------------|-----------------|
| `-p, --prompt`      | Text prompt (appended to `-f` if both provided)          | -               |
| `-f, --prompt-file` | Read prompt from file                                    | -               |
| `--api`             | API backend: `gpt` or `gemini`                           | `gpt`           |
| `-o, --output`      | Output file path                                         | `generated.png` |
| `-q, --quality`     | Quality: `high`, `medium`, `low`                         | `high`          |
| `--size`            | Size: `WxH` or aspect ratio like `16:9`                  | `1024x1024`     |
| `-n, --count`       | Number of variations to generate                         | `1`             |
| `--transparent`     | Transparent background (GPT only)                        | `false`         |
| `--moderation`      | Moderation level: `auto`, `low`                          | `low`           |

At least one of `-p` or `-f` is required. If both are provided, the file content and prompt are concatenated.

### Environment Variables

```bash
# For OpenAI backend
export OPENAI_API_KEY='your-key-here'

# For Gemini backend
export GEMINI_API_KEY='your-key-here'
# or
export GOOGLE_API_KEY='your-key-here'
```

## Development

```bash
# Clone the repository
git clone https://github.com/wolf/image-gen.git
cd image-gen

# Install with dev dependencies
uv sync --all-extras --dev
```

### Running locally

To run the CLI during development (picks up code changes automatically):

```bash
# Option 1: Use uv run (simplest)
uv run image-gen -p "test prompt"

# Add a shell alias for convenience (add to .zshrc or .bashrc)
alias image-gen='uv run --directory /path/to/image-gen image-gen'
```

```bash
# Option 2: Editable install with global PATH access
uv pip install -e ".[all]"

# Add the venv bin to your PATH (add to .zshrc or .bashrc)
export PATH="/path/to/image-gen/.venv/bin:$PATH"

# Now image-gen is available globally and picks up source changes
image-gen -p "test prompt"
```

### Linting and testing

```bash
# Run linting
uv run ruff check src/ tests/

# Run formatting
uv run ruff format src/ tests/

# Run type checking
uv run mypy src/

# Run tests
uv run pytest

# Run all checks
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run mypy src/ && uv run pytest
```

## License

MIT
