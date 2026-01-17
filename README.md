# image-gen

Generate or edit images using OpenAI GPT or Google Gemini APIs.

## Installation

```bash
# Install with uv (recommended)
uv add image-gen

# With OpenAI backend
uv add "image-gen[openai]"

# With Gemini backend
uv add "image-gen[gemini]"

# With all backends
uv add "image-gen[all]"

# Or with pip
pip install "image-gen[all]"
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

### Options

| Option              | Description                             | Default         |
|---------------------|-----------------------------------------|-----------------|
| `-p, --prompt`      | Text prompt describing the image        | (required)      |
| `-f, --prompt-file` | Read prompt from file                   | -               |
| `--api`             | API backend: `gpt` or `gemini`          | `gpt`           |
| `-o, --output`      | Output file path                        | `generated.png` |
| `-q, --quality`     | Quality: `high`, `medium`, `low`        | `high`          |
| `--size`            | Size: `WxH` or aspect ratio like `16:9` | `1024x1024`     |
| `-n, --count`       | Number of variations to generate        | `1`             |
| `--transparent`     | Transparent background (GPT only)       | `false`         |
| `--moderation`      | Moderation level: `auto`, `low`         | `low`           |

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
