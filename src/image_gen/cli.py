"""CLI interface for image-gen."""

import argparse
import os
import sys
import time
from pathlib import Path

from image_gen.backends import ImageGenConfig, get_backend

VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_QUALITY = "high"
DEFAULT_SIZE = "1024x1024"


def validate_image_path(path: Path) -> None:
    """Validate that the path exists and has a valid image extension."""
    if not path.exists():
        sys.stderr.write(f"[!] File not found: {path}\n")
        sys.exit(1)
    if path.suffix.lower() not in VALID_EXTENSIONS:
        sys.stderr.write(f"[!] Invalid image format: {path.suffix}\n")
        sys.stderr.write(f"    Supported formats: {', '.join(VALID_EXTENSIONS)}\n")
        sys.exit(1)


def check_api_key(api: str) -> None:
    """Check that the required API key is set for the selected backend."""
    if api == "gpt" and not os.environ.get("OPENAI_API_KEY"):
        sys.stderr.write("[!] OPENAI_API_KEY environment variable not set.\n")
        sys.stderr.write("    Set it with: export OPENAI_API_KEY='your-key-here'\n")
        sys.exit(1)
    if (
        api == "gemini"
        and not os.environ.get("GEMINI_API_KEY")
        and not os.environ.get("GOOGLE_API_KEY")
    ):
        sys.stderr.write("[!] GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set.\n")
        sys.stderr.write("    Set it with: export GEMINI_API_KEY='your-key-here'\n")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate or edit images using OpenAI GPT or Google Gemini APIs."
    )
    parser.add_argument(
        "images",
        nargs="*",
        type=Path,
        help="Input images (referenced as Image 1, Image 2, etc. in prompt)",
    )
    parser.add_argument(
        "--api",
        choices=["gpt", "gemini"],
        default="gpt",
        help="API backend to use (default: gpt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path (default: last input filename with _n suffix, or 'generated.png')",
    )
    parser.add_argument(
        "-q",
        "--quality",
        choices=["high", "medium", "low"],
        default=DEFAULT_QUALITY,
        help="Image quality (default: high)",
    )
    parser.add_argument(
        "--size",
        default=DEFAULT_SIZE,
        help="Output size - WxH pixels or aspect ratio like 16:9 (default: 1024x1024)",
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("-p", "--prompt", help="Prompt describing the image or edit")
    prompt_group.add_argument(
        "-f", "--prompt-file", type=Path, help="Path to file containing the prompt"
    )
    parser.add_argument(
        "-n", "--count", type=int, default=1, help="Number of variations to generate (default: 1)"
    )
    parser.add_argument(
        "--transparent",
        action="store_true",
        help="Generate with transparent background (GPT only)",
    )
    parser.add_argument(
        "--moderation",
        choices=["auto", "low"],
        default="low",
        help="Content moderation level (GPT only, default: low)",
    )
    args = parser.parse_args()

    # Resolve prompt from file if specified
    if args.prompt_file:
        if not args.prompt_file.exists():
            sys.stderr.write(f"[!] Prompt file not found: {args.prompt_file}\n")
            sys.exit(1)
        args.prompt = args.prompt_file.read_text().strip()

    # Validate image count (GPT limit is 4, Gemini supports more)
    max_images = 4 if args.api == "gpt" else 14
    if len(args.images) > max_images:
        sys.stderr.write(f"[!] Maximum of {max_images} input images allowed for {args.api}.\n")
        sys.exit(1)

    # Check for API key
    check_api_key(args.api)

    # Validate input files
    for img in args.images:
        validate_image_path(img)

    # Determine mode
    generation_mode = len(args.images) == 0

    # Default output path
    if args.output:
        output_base = args.output
    elif generation_mode:
        output_base = Path("generated.png")
    else:
        output_base = args.images[-1]

    # Build configuration
    config = ImageGenConfig(
        prompt=args.prompt,
        images=args.images,
        quality=args.quality,
        size=args.size,
        count=args.count,
        transparent=args.transparent,
        moderation=args.moderation,
    )

    start_time = time.time()
    try:
        # Get backend and print any warnings
        backend = get_backend(args.api)
        for warning in backend.validate_config(config):
            sys.stderr.write(f"[!] Warning: {warning}\n")

        if generation_mode:
            print(f"Generating image with {args.api}...")
            results = backend.generate(config)
        else:
            print(f"Processing image edit with {args.api}...")
            for i, img in enumerate(args.images, start=1):
                print(f"  Image {i}: {img}")
            results = backend.edit(config)

        if not results:
            sys.stderr.write("[!] No image data returned from API.\n")
            sys.exit(1)

        # Save each generated image
        base_name = output_base.stem
        output_dir = output_base.parent or Path()

        # Find next available suffix number (check all image extensions)
        suffix_num = 1
        all_extensions = {".png", ".jpg", ".jpeg", ".webp"}
        while any(
            (output_dir / f"{base_name}_{suffix_num}{ext}").exists() for ext in all_extensions
        ):
            suffix_num += 1

        for result in results:
            # Normalize format: use .jpg not .jpeg
            fmt = result.format if result.format else "png"
            out_ext = ".jpg" if fmt == "jpeg" else f".{fmt}"

            # Find next available suffix number for this file
            while any(
                (output_dir / f"{base_name}_{suffix_num}{ext}").exists() for ext in all_extensions
            ):
                suffix_num += 1

            output_path = output_dir / f"{base_name}_{suffix_num}{out_ext}"
            output_path.write_bytes(result.image_data)
            print(f"  Output: {output_path}")
            suffix_num += 1

        elapsed = time.time() - start_time
        print(f"Done in {elapsed:.1f}s.")

    except Exception as e:
        sys.stderr.write(f"[!] Error: {e}\n")
        sys.exit(1)
