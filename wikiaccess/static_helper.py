"""
Helper functions for managing static files (CSS, JS, etc.)
"""

from pathlib import Path
import shutil


def copy_static_files(output_dir: str):
    """
    Copy static CSS files to output directory.

    Args:
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    css_output = output_path / 'reports' / 'css'
    css_output.mkdir(parents=True, exist_ok=True)

    # Get the static directory path
    static_dir = Path(__file__).parent / 'static' / 'css'

    if not static_dir.exists():
        print(f"Warning: Static directory not found: {static_dir}")
        return

    # Copy all CSS files
    for css_file in static_dir.glob('*.css'):
        dest = css_output / css_file.name
        shutil.copy2(css_file, dest)

    return css_output


def get_css_links():
    """
    Get HTML link tags for all CSS files.

    Returns:
        HTML string with link tags
    """
    css_files = [
        'sidebar.css',  # Keep for backward compatibility (temporary)
        'breadcrumb-nav.css',
        'report-base.css',
        'components.css',
        'enhanced-sections.css',
        'accessibility.css'
    ]

    links = []
    for css_file in css_files:
        links.append(f'    <link rel="stylesheet" href="css/{css_file}">')

    return '\n'.join(links)
