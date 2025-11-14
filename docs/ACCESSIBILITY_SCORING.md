# WikiAccess Accessibility Scoring System Documentation

## Overview

WikiAccess uses a comprehensive WCAG 2.1-based scoring system to evaluate the accessibility of converted HTML and DOCX documents. The system provides both **AA (Level AA)** and **AAA (Level AAA)** compliance scores ranging from 0-100%.

## Scoring Methodology

### Score Calculation Formula

The accessibility scoring uses a **pass/fail ratio** approach:

```
AA Score = (Passed Checks / Total AA Checks) × 100
AAA Score = (Passed Checks / (Total AA Checks + Total AAA Checks)) × 100
```

Where:
- **Passed Checks**: Number of accessibility tests that passed
- **Total AA Checks**: All WCAG AA-level tests performed  
- **Total AAA Checks**: All WCAG AAA-level tests performed
- **Warnings**: Do not count toward pass/fail - informational only

### Score Interpretation

| Score Range | Status | Color | Meaning |
|------------|--------|-------|---------|
| 90-100% | Excellent | 🟢 Green | Highly accessible, minimal issues |
| 70-89% | Good | 🟡 Yellow | Generally accessible, minor issues |
| 50-69% | Fair | 🟠 Orange | Some accessibility barriers present |
| 0-49% | Poor | 🔴 Red | Significant accessibility issues |

## HTML Accessibility Tests

### 1. **HTML Language** (WCAG 3.1.1 - AA)
- **Test**: Checks for `lang` attribute on `<html>` tag
- **Pass**: `<html lang="en">` or similar
- **Fail**: Missing `lang` attribute
- **Impact**: Screen readers need language to pronounce content correctly

### 2. **Page Title** (WCAG 2.4.2 - AA)  
- **Test**: Checks for non-empty `<title>` element
- **Pass**: `<title>Page Name - Site</title>`
- **Fail**: Missing or empty `<title>`
- **Impact**: Essential for navigation, bookmarks, search results

### 3. **Heading Hierarchy** (WCAG 1.3.1, 2.4.6 - AA)
- **Tests**:
  - Single H1 heading present
  - No hierarchy skips (H1→H3 without H2)
- **Pass**: Proper nested heading structure
- **Fail**: Multiple H1s, missing H1, skipped levels
- **Impact**: Screen readers use headings for page navigation

### 4. **Image Alt Text** (WCAG 1.1.1 - AA)
- **Test**: All `<img>` elements have meaningful `alt` attributes
- **Pass**: `<img src="chart.png" alt="Sales increased 25% in Q3">`
- **Fail**: Missing `alt` attribute
- **Warning**: Empty alt (verify if decorative)
- **Impact**: Screen readers cannot describe images without alt text
- **Note**: Displays figcaption text or filename when available

### 5. **Link Accessibility** (WCAG 2.4.4 - AA)
- **Tests**:
  - No "click here" or "here" link text
  - No empty link text
- **Pass**: `<a href="/report">View Q3 Sales Report</a>`
- **Fail**: `<a href="/report">click here</a>` or `<a href="/report"></a>`
- **Impact**: Screen reader users navigate by link text alone

### 6. **Color Contrast** (WCAG 1.4.3 - AA, 1.4.6 - AAA)
- **Test**: Basic check for contrast warnings in CSS
- **Pass**: No obvious low-contrast issues detected
- **Warning**: Potential contrast problems found
- **Impact**: Low vision users need sufficient contrast
- **Note**: This is a simplified check - full testing requires rendering

### 7. **Semantic HTML** (WCAG 1.3.1 - AA)
- **Test**: Proper use of semantic elements
- **Pass**: Uses `<main>`, `<nav>`, `<section>`, `<article>` appropriately
- **Warning**: Only generic `<div>` containers found
- **Impact**: Assistive technology relies on semantic structure

### 8. **Skip Navigation** (WCAG 2.4.1 - AAA)
- **Test**: Presence of skip navigation link
- **Pass**: `<a href="#main">Skip to main content</a>`
- **Fail**: Missing skip link
- **Impact**: Keyboard users need to skip repetitive navigation
- **Level**: AAA requirement (optional for AA compliance)

### 9. **ARIA Labels** (WCAG 4.1.2 - AA)
- **Test**: Interactive elements have accessible names
- **Pass**: Buttons/links have text or ARIA labels
- **Fail**: Interactive elements without accessible names
- **Impact**: Screen readers need element labels

### 10. **Form Labels** (WCAG 1.3.1, 3.3.2 - AA)
- **Test**: Form inputs properly associated with labels
- **Pass**: `<label for="email">Email:</label><input id="email">`
- **Fail**: Inputs without associated labels
- **Impact**: Users need to understand form field purposes

### 11. **Keyboard Access** (WCAG 2.1.1 - AA)
- **Test**: Interactive elements are keyboard accessible
- **Pass**: No keyboard traps or inaccessible elements
- **Warning**: Elements that may block keyboard navigation
- **Impact**: Keyboard-only users must access all functionality

## DOCX Accessibility Tests

### 1. **Document Title** (WCAG 2.4.2 - AA)
- **Test**: Document has title property
- **Pass**: Title set in document properties
- **Fail**: Missing document title
- **Impact**: Screen readers announce document purpose

### 2. **Document Language** (WCAG 3.1.1 - AA)  
- **Test**: Document language property set
- **Pass**: Language specified in document properties
- **Warning**: Language property not set
- **Impact**: Screen readers need language for pronunciation

### 3. **Heading Structure** (WCAG 1.3.1, 2.4.6 - AA)
- **Tests**:
  - Built-in heading styles used (not just bold text)
  - Proper heading hierarchy maintained
- **Pass**: Uses Word heading styles (Heading 1, 2, 3...)
- **Fail**: Text styled as headings without using heading styles
- **Impact**: Screen readers cannot navigate by headings

### 4. **Image Alt Text** (WCAG 1.1.1 - AA)
- **Test**: Images have alternative text
- **Pass**: All images have alt text descriptions
- **Fail**: Images missing alt text
- **Impact**: Screen readers cannot describe images
- **Note**: Attempts to resolve actual image filenames

### 5. **Link Accessibility** (WCAG 2.4.4 - AA)
- **Test**: Hyperlinks have descriptive text
- **Pass**: Meaningful link text
- **Fail**: "Click here" or empty link text  
- **Impact**: Screen readers navigate by link lists

## Score Aggregation

### Page-Level Scores
Each page receives individual scores for:
- **HTML AA Score**: Based on HTML-specific tests
- **HTML AAA Score**: Includes AAA-level requirements  
- **DOCX AA Score**: Based on Word document tests
- **DOCX AAA Score**: Currently same as AA (no DOCX AAA tests)

### Report-Level Scores  
The accessibility dashboard shows:
- **Average HTML AA/AAA**: Mean of all page HTML scores
- **Average DOCX AA/AAA**: Mean of all page DOCX scores
- **Overall Statistics**: Total pages, issues, passes

### Score Calculation Example

**Example Page with:**
- ✅ 8 passed tests
- ❌ 2 AA failures 
- ❌ 1 AAA failure

**Calculations:**
```
Total AA checks = 8 passed + 2 failed = 10
Total AAA checks = 1 failed = 1
Total all checks = 10 + 1 = 11

AA Score = 8/10 × 100 = 80%
AAA Score = 8/11 × 100 = 73%
```

## Scoring Edge Cases

### No Issues Found
- If no accessibility tests apply: Score = 100%
- Example: Document with no images, links, or forms

### Critical Failures
- Document cannot be opened: Score = 0%
- Complete absence of required elements: Significant score reduction

### Warnings vs. Failures
- **Failures**: Count against score (red ✗)
- **Warnings**: Informational only (yellow ⚠)  
- **Passes**: Count toward score (green ✓)

## WCAG 2.1 Standards Mapped

| WCAG Guideline | Level | WikiAccess Test | HTML | DOCX |
|---------------|-------|----------------|------|------|
| 1.1.1 Non-text Content | AA | Image alt text | ✅ | ✅ |
| 1.3.1 Info and Relationships | AA | Headings, forms, semantic HTML | ✅ | ✅ |
| 2.1.1 Keyboard | AA | Keyboard access | ✅ | ➖ |
| 2.4.1 Bypass Blocks | AAA | Skip links | ✅ | ➖ |
| 2.4.2 Page Titled | AA | Page/document title | ✅ | ✅ |
| 2.4.4 Link Purpose | AA | Descriptive links | ✅ | ✅ |
| 2.4.6 Headings and Labels | AA | Heading hierarchy | ✅ | ✅ |
| 3.1.1 Language of Page | AA | Language attributes | ✅ | ✅ |
| 3.3.2 Labels or Instructions | AA | Form labels | ✅ | ➖ |
| 4.1.2 Name, Role, Value | AA | ARIA labels | ✅ | ➖ |
| 1.4.3 Contrast (Minimum) | AA | Color contrast | ⚠️ | ➖ |
| 1.4.6 Contrast (Enhanced) | AAA | Enhanced contrast | ⚠️ | ➖ |

**Legend:**
- ✅ Full automated test
- ⚠️ Basic/warning-level test  
- ➖ Not applicable to format

## Limitations and Notes

### Automated Testing Limits
- **Color contrast**: Basic CSS parsing only, not full rendering
- **Cognitive accessibility**: Not measurable through automation
- **User testing**: Scores don't replace human accessibility evaluation

### Format-Specific Considerations
- **HTML**: More comprehensive testing possible
- **DOCX**: Limited to document structure and properties
- **Images**: Alt text quality not evaluated (only presence)

### Scoring Philosophy
- **Conservative approach**: Missing elements score as failures
- **Pass-focused**: Scores reward accessibility implementation
- **Actionable results**: Each failure links to specific WCAG criteria

## Using the Scores

### Development Guidance
- **90%+**: Ready for production, excellent accessibility
- **70-89%**: Minor improvements needed
- **50-69%**: Moderate accessibility work required  
- **<50%**: Significant accessibility review needed

### Compliance Interpretation
- **AA compliance**: Focus on AA scores
- **Legal requirements**: May require AAA in some jurisdictions
- **Best practices**: Aim for high scores in both AA and AAA

The scoring system provides objective, measurable accessibility feedback while following established WCAG 2.1 guidelines, helping ensure WikiAccess produces truly accessible content.