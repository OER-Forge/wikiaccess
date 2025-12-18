"""
Helper functions for managing static files (CSS, JS, etc.)
"""

from pathlib import Path
import shutil


def copy_static_files(output_dir: str):
    """
    Copy static CSS and JS files to output directory.

    Args:
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    static_root = Path(__file__).parent / 'static'

    # Copy CSS files
    css_src = static_root / 'css'
    css_dest = output_path / 'reports' / 'css'
    css_dest.mkdir(parents=True, exist_ok=True)

    if css_src.exists():
        for css_file in css_src.glob('*.css'):
            shutil.copy2(css_file, css_dest / css_file.name)
    else:
        print(f"Warning: CSS directory not found: {css_src}")

    # Copy JavaScript files
    js_src = static_root / 'js'
    js_dest = output_path / 'reports' / 'js'
    js_dest.mkdir(parents=True, exist_ok=True)

    if js_src.exists():
        for js_file in js_src.glob('*.js'):
            shutil.copy2(js_file, js_dest / js_file.name)
    else:
        print(f"Warning: JS directory not found: {js_src}")

    return css_dest


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
        'accessibility.css',
        'report-inline-styles.css'  # Consolidated inline styles from Python code
    ]

    links = []
    for css_file in css_files:
        links.append(f'    <link rel="stylesheet" href="css/{css_file}">')

    return '\n'.join(links)
