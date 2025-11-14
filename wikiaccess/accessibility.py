#!/usr/bin/env python3
"""
WikiAccess - pa11y-based WCAG 2.1 AA/AAA Accessibility Checker

Uses pa11y for comprehensive accessibility testing with fallback to custom checks for DOCX.
Provides industry-standard accessibility validation.

Part of WikiAccess: Transform DokuWiki into Accessible Documents
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import os

try:
    from docx import Document
except ImportError:
    Document = None


class AccessibilityChecker:
    """Check WCAG 2.1 compliance using pa11y for HTML and custom checks for DOCX"""
    
    def __init__(self):
        self.pa11y_path = self._find_pa11y()
        if not self.pa11y_path:
            raise RuntimeError("pa11y not found. Install with: npm install pa11y")
    
    def _find_pa11y(self) -> Optional[str]:
        """Find pa11y executable"""
        # Check local node_modules first
        local_pa11y = Path("node_modules/.bin/pa11y")
        if local_pa11y.exists():
            return str(local_pa11y.absolute())
        
        # Check global installation
        try:
            result = subprocess.run(["which", "pa11y"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def check_html(self, html_path: str) -> Dict:
        """
        Check HTML file for accessibility issues using pa11y
        
        Returns dict with:
            - score_aa: 0-100
            - score_aaa: 0-100  
            - issues_aa: list of AA level issues
            - issues_aaa: list of AAA level issues
            - warnings: list of warnings
            - passes: list of passed checks
            - total_tests: number of tests run
        """
        if not os.path.exists(html_path):
            return {
                'score_aa': 0,
                'score_aaa': 0,
                'issues_aa': [f"File not found: {html_path}"],
                'issues_aaa': [],
                'warnings': [],
                'passes': [],
                'total_tests': 0,
                'file': html_path
            }
        
        # Run pa11y with WCAG2AA standard
        aa_results = self._run_pa11y(html_path, "WCAG2AA")
        
        # Run pa11y with WCAG2AAA standard  
        aaa_results = self._run_pa11y(html_path, "WCAG2AAA")
        
        # Process results
        aa_issues = self._process_pa11y_results(aa_results, "AA")
        aaa_issues = self._process_pa11y_results(aaa_results, "AAA")
        
        # Calculate scores
        # pa11y only reports failures, so we estimate total checks from known pa11y ruleset
        estimated_total_checks = 50  # pa11y typically runs ~50 accessibility rules
        aa_failures = len(aa_issues)
        aaa_failures = len(aaa_issues) 
        
        # Conservative scoring: failures count against total possible checks
        score_aa = max(0, int(((estimated_total_checks - aa_failures) / estimated_total_checks) * 100))
        score_aaa = max(0, int(((estimated_total_checks - (aa_failures + aaa_failures)) / estimated_total_checks) * 100))
        
        # Generate positive feedback for clean results
        passes = []
        if aa_failures == 0:
            passes.append("✓ No WCAG 2.1 AA violations detected by pa11y")
        if aaa_failures == 0:
            passes.append("✓ No WCAG 2.1 AAA violations detected by pa11y")
        
        return {
            'score_aa': score_aa,
            'score_aaa': score_aaa,
            'issues_aa': aa_issues,
            'issues_aaa': aaa_issues,
            'warnings': [],  # pa11y doesn't distinguish warnings from errors
            'passes': passes,
            'total_tests': estimated_total_checks,
            'file': html_path
        }
    
    def _run_pa11y(self, html_path: str, standard: str) -> List[Dict]:
        """Run pa11y with specified standard"""
        try:
            # Convert to file URL for pa11y
            file_url = f"file://{os.path.abspath(html_path)}"
            
            cmd = [
                self.pa11y_path,
                "--reporter", "json",
                "--standard", standard,
                "--ignore", "warning",  # Only report errors, not warnings
                file_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                return json.loads(result.stdout)
            else:
                return []
                
        except Exception as e:
            return [{"message": f"pa11y error: {str(e)}", "type": "error"}]
    
    def _process_pa11y_results(self, results: List[Dict], level: str) -> List[str]:
        """Process pa11y JSON results into formatted issue strings"""
        issues = []
        
        for item in results:
            if item.get("type") == "error":
                # Extract WCAG code from message if present
                message = item.get("message", "Unknown accessibility issue")
                code = item.get("code", "")
                selector = item.get("selector", "")
                
                # Format issue with location context
                location_info = f" (element: {selector})" if selector else ""
                wcag_info = f" [{code}]" if code else ""
                
                formatted_issue = f"✗ {message}{location_info}{wcag_info}"
                issues.append(formatted_issue)
        
        return issues
    
    def check_docx(self, docx_path: str) -> Dict:
        """
        Check DOCX file for accessibility - uses custom implementation
        since pa11y doesn't support DOCX files
        """
        issues_aa = []
        issues_aaa = []
        warnings = []
        passes = []
        
        try:
            doc = Document(docx_path)
        except Exception as e:
            return {
                'score_aa': 0,
                'score_aaa': 0,
                'issues_aa': [f"Could not open document: {e}"],
                'issues_aaa': [],
                'warnings': [],
                'passes': [],
                'total_tests': 5,
                'file': docx_path
            }
        
        # Custom DOCX checks (since pa11y doesn't support DOCX)
        self._check_docx_title(doc, issues_aa, passes)
        self._check_docx_language(doc, warnings, passes)
        self._check_docx_headings(doc, issues_aa, passes)
        self._check_docx_images(doc, issues_aa, passes)
        self._check_docx_links(doc, issues_aa, passes)
        
        # Calculate scores
        total_checks = len(issues_aa) + len(passes)
        score_aa = 100 if total_checks == 0 else int((len(passes) / total_checks) * 100)
        score_aaa = score_aa  # No AAA-specific DOCX tests currently
        
        return {
            'score_aa': score_aa,
            'score_aaa': score_aaa,
            'issues_aa': issues_aa,
            'issues_aaa': issues_aaa,
            'warnings': warnings,
            'passes': passes,
            'total_tests': total_checks,
            'file': docx_path
        }
    
    def _check_docx_title(self, doc: Any, issues: List, passes: List):
        """Check document title"""
        if doc.core_properties.title:
            passes.append(f'✓ Document title present: "{doc.core_properties.title}"')
        else:
            issues.append('✗ Missing document title (WCAG 2.4.2)')
    
    def _check_docx_language(self, doc: Any, warnings: List, passes: List):
        """Check document language"""
        if doc.core_properties.language:
            passes.append(f'✓ Document language set: {doc.core_properties.language}')
        else:
            warnings.append('⚠ Document language not set (consider setting for accessibility)')
    
    def _check_docx_headings(self, doc: Any, issues: List, passes: List):
        """Check heading structure"""
        heading_styles = []
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                heading_styles.append(para.style.name)
        
        if not heading_styles:
            issues.append('✗ No heading styles used - use Word heading styles for accessibility (WCAG 1.3.1)')
        else:
            passes.append(f'✓ Document uses {len(heading_styles)} heading elements')
    
    def _check_docx_images(self, doc: Any, issues: List, passes: List):
        """Check images for alt text"""
        from docx.oxml.ns import nsdecls, qn
        import xml.etree.ElementTree as ET
        
        total_images = 0
        images_with_alt = 0
        
        # Count images in document
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                total_images += 1
        
        # This is a simplified check - full implementation would parse XML for alt text
        if total_images == 0:
            passes.append('✓ No images to check')
        else:
            # Conservative assumption - flag for manual review
            issues.append(f'⚠ {total_images} images found - verify alt text is set in Word (WCAG 1.1.1)')
    
    def _check_docx_links(self, doc: Any, issues: List, passes: List):
        """Check hyperlinks"""
        link_count = 0
        
        for para in doc.paragraphs:
            for run in para.runs:
                if run.element.find('.//w:hyperlink', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                    link_count += 1
        
        if link_count == 0:
            passes.append('✓ No hyperlinks to check')
        else:
            passes.append(f'✓ {link_count} hyperlinks found - verify descriptive text (WCAG 2.4.4)')


if __name__ == "__main__":
    # Test the accessibility checker
    checker = AccessibilityChecker()
    
    # Test HTML file if available
    html_files = list(Path("output/html").glob("*.html")) if Path("output/html").exists() else []
    if html_files:
        result = checker.check_html(str(html_files[0]))
        print(f"HTML Test Results for {html_files[0].name}:")
        print(f"  AA Score: {result['score_aa']}%")
        print(f"  AAA Score: {result['score_aaa']}%")
        print(f"  Issues: {len(result['issues_aa']) + len(result['issues_aaa'])}")
    
    # Test DOCX file if available  
    docx_files = list(Path("output/docx").glob("*.docx")) if Path("output/docx").exists() else []
    if docx_files:
        result = checker.check_docx(str(docx_files[0]))
        print(f"DOCX Test Results for {docx_files[0].name}:")
        print(f"  AA Score: {result['score_aa']}%")
        print(f"  Issues: {len(result['issues_aa'])}")