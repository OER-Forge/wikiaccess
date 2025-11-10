# WikiAccess - Accessibility Compliance Guide

**Transform DokuWiki into Accessible Documents**

This guide helps you verify that documents created with WikiAccess meet WCAG 2.1 AA/AAA accessibility standards.

## Quick Accessibility Checklist

### ✅ Document Structure
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] Document has a title
- [ ] Language is set correctly

### ✅ Content
- [ ] All links have descriptive text (not "click here")
- [ ] All images have alt text
- [ ] Lists are properly formatted
- [ ] Text is readable and well-formatted

### ✅ Navigation
- [ ] Can navigate by headings using screen reader
- [ ] Links are announced properly
- [ ] Document structure makes sense without visual formatting

## Testing Tools

### 1. Microsoft Word Accessibility Checker

**Steps:**
1. Open your generated Word document
2. Go to **File → Info**
3. Click **Check for Issues**
4. Select **Check Accessibility**
5. Review and address any issues found

**What it checks:**
- Missing alt text
- Duplicate heading text
- Missing table headers
- Color contrast issues
- And more...

### 2. Screen Reader Testing

#### macOS - VoiceOver

**Enable VoiceOver:**
- Press `Cmd + F5`
- Or System Settings → Accessibility → VoiceOver

**Basic Commands:**
- `Ctrl + Option + Right/Left Arrow` - Navigate elements
- `Ctrl + Option + Cmd + H` - Jump to next heading
- `Ctrl + Option + U` - Open rotor (for navigation)
- `Ctrl + Option + A` - Start reading

**Test checklist:**
- [ ] Document title is announced
- [ ] Headings are announced with level (e.g., "Heading 1, The Momentum Principle")
- [ ] Links announce their purpose
- [ ] Image descriptions are read
- [ ] Document flows logically

#### Windows - NVDA (Free)

**Download:** https://www.nvaccess.org/download/

**Basic Commands:**
- `Ctrl` - Stop reading
- `NVDA + Down Arrow` - Start reading
- `H` - Next heading
- `Shift + H` - Previous heading
- `K` - Next link
- `NVDA + F7` - Elements list

**Test checklist:**
- [ ] Document properties are announced correctly
- [ ] Can navigate by headings
- [ ] Links are descriptive
- [ ] Images have proper descriptions

#### Windows - JAWS (Commercial)

**Basic Commands:**
- `Insert + Down Arrow` - Start reading
- `H` - Next heading
- `Shift + H` - Previous heading
- `Insert + F6` - Headings list
- `Insert + F7` - Links list

### 3. Keyboard Navigation

Test navigation without a mouse:

**Test checklist:**
- [ ] `Tab` - Navigate through all interactive elements
- [ ] `Shift + Tab` - Navigate backwards
- [ ] `Enter` - Activate links
- [ ] All content is accessible via keyboard

### 4. Visual Inspection

**Check for:**
- [ ] Sufficient color contrast
- [ ] Clear visual hierarchy
- [ ] Readable font sizes
- [ ] Proper spacing
- [ ] Logical reading order

## Common Issues and Fixes

### Issue: "Heading levels skip"
**Fix:** Ensure heading hierarchy doesn't skip levels (e.g., don't go from H1 to H3)
**In DokuWiki:** Use proper heading syntax (===== H1, ==== H2, === H3, == H4)

### Issue: "Link text is not descriptive"
**Fix:** Use meaningful link text instead of URLs
**In DokuWiki:** Use `[[url|descriptive text]]` format

### Issue: "Image missing alternative text"
**Fix:** The converter generates alt text from filenames
**Enhancement:** Consider renaming image files to be more descriptive

### Issue: "Document has no title"
**Fix:** Provide `document_title` parameter to the converter:
```python
convert_dokuwiki_to_word(
    'input.txt', 
    'output.docx',
    document_title='Your Descriptive Title'
)
```

## Standards Compliance

### WCAG 2.1 Level AA

The converter aims to meet these success criteria:

**Perceivable:**
- 1.1.1 Non-text Content (Level A) - Alt text provided
- 1.3.1 Info and Relationships (Level A) - Proper heading structure
- 1.3.2 Meaningful Sequence (Level A) - Logical reading order
- 1.4.3 Contrast (Minimum) (Level AA) - Default Word styles used

**Operable:**
- 2.4.1 Bypass Blocks (Level A) - Heading navigation available
- 2.4.2 Page Titled (Level A) - Document title set
- 2.4.4 Link Purpose (Level A) - Descriptive link text
- 2.4.6 Headings and Labels (Level AA) - Clear headings

**Understandable:**
- 3.1.1 Language of Page (Level A) - Document language set
- 3.1.2 Language of Parts (Level AA) - Configurable

**Robust:**
- 4.1.2 Name, Role, Value (Level A) - Semantic structure

### Section 508

Relevant standards addressed:
- 1194.21(d) - Document structure
- 1194.21(l) - No information conveyed by color alone
- 1194.22(a) - Text equivalent for non-text elements
- 1194.22(f) - Descriptive links
- 1194.22(o) - Skip navigation method

## Exporting to PDF

When exporting your Word document to PDF, maintain accessibility:

### In Microsoft Word:
1. **File → Export → Create PDF/XPS**
2. Check **"Document structure tags for accessibility"**
3. Click **Options**
4. Ensure **"ISO 19005-1 compliant (PDF/A)"** is checked (optional but recommended)
5. Click **OK** then **Publish**

### Verify PDF Accessibility:
- Adobe Acrobat: **Accessibility → Full Check**
- PAC (PDF Accessibility Checker) - Free tool from Access for All

## Resources

### Standards
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Section 508 Standards](https://www.section508.gov/)
- [PDF/UA Standard](https://www.pdfa.org/publication/pdfua-in-a-nutshell/)

### Tools
- [NVDA Screen Reader](https://www.nvaccess.org/) - Free for Windows
- [PAC PDF Accessibility Checker](https://www.access-for-all.ch/en/pdf-lab/pdf-accessibility-checker-pac.html) - Free
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Learning Resources
- [WebAIM: Web Accessibility In Mind](https://webaim.org/)
- [Microsoft Accessibility Training](https://www.microsoft.com/en-us/accessibility)
- [W3C Web Accessibility Tutorials](https://www.w3.org/WAI/tutorials/)

## Reporting Issues

If you find accessibility issues with the converter:
1. Document the specific WCAG criterion that fails
2. Provide steps to reproduce
3. Include sample input if possible
4. Open an issue on the project repository

Remember: **Accessibility is everyone's responsibility!** Regular testing ensures your documents are usable by all.
