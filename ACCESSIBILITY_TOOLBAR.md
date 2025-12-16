# Accessibility Toolbar Configuration

WikiAccess includes an accessibility toolbar in converted HTML pages that provides users with various accessibility options:

- **Theme**: Light/Dark mode toggle
- **Text Size**: Adjustable font size (14-20px)
- **Line Spacing**: Adjustable line height (1.4-2.0)
- **Letter Spacing**: Adjustable letter spacing
- **Font Family**: Multiple accessible font options (Atkinson Hyperlegible, OpenDyslexic, Lexend, Luciole)
- **High Contrast**: Toggle high contrast mode
- **Reset**: Reset all settings to defaults

## How to Hide the Toolbar

If you want to generate HTML files without the accessibility toolbar, you can disable it using the `include_accessibility_toolbar` parameter:

### Option 1: Using the Python API

```python
from wikiaccess import convert_wiki_page, convert_multiple_pages

# Convert a single page without toolbar
result = convert_wiki_page(
    wiki_url="https://your-wiki.org",
    page_name="your_page_id",
    include_accessibility_toolbar=False  # Disable toolbar
)

# Convert multiple pages without toolbar
results = convert_multiple_pages(
    wiki_url="https://your-wiki.org",
    page_names=["page1", "page2", "page3"],
    include_accessibility_toolbar=False  # Disable toolbar
)
```

### Option 2: Modifying convert_from_file_list.py

Edit `convert_from_file_list.py` and add the parameter:

```python
results = convert_multiple_pages(
    wiki_url=wiki_url,
    page_names=page_ids,
    output_dir=OUTPUT_DIR,
    formats=['html', 'docx'],
    check_accessibility=True,
    include_accessibility_toolbar=False  # Add this line
)
```

## Default Behavior

By default, `include_accessibility_toolbar=True`, so the toolbar will be included unless you explicitly disable it.

## Note on Accessibility

While hiding the toolbar can create a cleaner appearance, the toolbar provides valuable accessibility features for users with visual impairments, dyslexia, or other reading difficulties. Consider your audience's needs when deciding whether to disable it.

The toolbar:
- Saves user preferences in localStorage (persistent across sessions)
- Includes ARIA labels for screen reader compatibility
- Provides keyboard shortcuts (Alt+T for theme, Alt+R for reset)
- Supports system dark mode detection
- Includes specialized fonts for dyslexia and visual impairments
