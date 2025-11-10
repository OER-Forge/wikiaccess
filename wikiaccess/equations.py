"""
WikiAccess - LaTeX to Word OMML Equation Converter

Converts LaTeX equations to Word's native format:
1. LaTeX → MathML (using latex2mathml)
2. MathML → OMML (Office Math Markup Language)
3. Insert as editable equation objects in Word documents

OMML equations are fully editable in Word's equation editor.

Part of WikiAccess: Transform DokuWiki into Accessible Documents
https://github.com/yourusername/wikiaccess
"""

from latex2mathml.converter import convert as latex_to_mathml
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from xml.etree import ElementTree as ET


def insert_mathml_equation(paragraph, latex, inline=False):
    """
    Insert equation as native Word OMML
    
    Args:
        paragraph: python-docx paragraph object
        latex: LaTeX string
        inline: If True, inline equation; if False, display equation
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert LaTeX to MathML
        mathml = latex_to_mathml(latex)
        
        # Convert MathML to OMML
        omml = mathml_to_omml(mathml)
        
        if omml is None:
            return False
        
        # For display equations, wrap in oMathPara
        if not inline:
            math_para = OxmlElement('m:oMathPara')
            math_para_pr = OxmlElement('m:oMathParaPr')
            jc = OxmlElement('m:jc')
            jc.set(qn('m:val'), 'center')
            math_para_pr.append(jc)
            math_para.append(math_para_pr)
            math_para.append(omml)
            
            # Insert into paragraph
            run = paragraph.add_run()
            run._element.append(math_para)
        else:
            # Inline equation - just insert oMath
            run = paragraph.add_run()
            run._element.append(omml)
        
        return True
        
    except Exception as e:
        print(f"  ⚠ Equation conversion failed: {e}")
        print(f"    LaTeX: {latex}")
        import traceback
        traceback.print_exc()
        return False


def mathml_to_omml(mathml_str):
    """
    Convert MathML to OMML using direct conversion
    """
    try:
        # Remove namespace declarations from parsing
        mathml_clean = mathml_str.replace(' xmlns="http://www.w3.org/1998/Math/MathML"', '')
        mathml = ET.fromstring(mathml_clean)
        
        # Create OMML root
        oMath = OxmlElement('m:oMath')
        
        # Convert MathML elements to OMML
        _convert_mathml_node(mathml, oMath)
        
        return oMath
        
    except Exception as e:
        print(f"  ⚠ MathML to OMML conversion failed: {e}")
        return None


def _convert_mathml_node(mathml_node, omml_parent):
    """
    Recursively convert MathML nodes to OMML nodes
    """
    tag = mathml_node.tag.split('}')[-1]  # Remove namespace
    
    if tag == 'math':
        # Root node, process children
        for child in mathml_node:
            _convert_mathml_node(child, omml_parent)
    
    elif tag == 'mrow':
        # Group of elements
        for child in mathml_node:
            _convert_mathml_node(child, omml_parent)
    
    elif tag == 'mi' or tag == 'mn' or tag == 'mo':
        # Identifier, number, or operator
        _add_text_element(omml_parent, mathml_node.text or '')
    
    elif tag == 'mfrac':
        # Fraction
        frac = OxmlElement('m:f')
        num = OxmlElement('m:num')
        den = OxmlElement('m:den')
        
        children = list(mathml_node)
        if len(children) >= 2:
            _convert_mathml_node(children[0], num)
            _convert_mathml_node(children[1], den)
        
        frac.append(num)
        frac.append(den)
        omml_parent.append(frac)
    
    elif tag == 'msup':
        # Superscript
        sup = OxmlElement('m:sSup')
        base = OxmlElement('m:e')
        supScript = OxmlElement('m:sup')
        
        children = list(mathml_node)
        if len(children) >= 2:
            _convert_mathml_node(children[0], base)
            _convert_mathml_node(children[1], supScript)
        
        sup.append(base)
        sup.append(supScript)
        omml_parent.append(sup)
    
    elif tag == 'msub':
        # Subscript
        sub = OxmlElement('m:sSub')
        base = OxmlElement('m:e')
        subScript = OxmlElement('m:sub')
        
        children = list(mathml_node)
        if len(children) >= 2:
            _convert_mathml_node(children[0], base)
            _convert_mathml_node(children[1], subScript)
        
        sub.append(base)
        sub.append(subScript)
        omml_parent.append(sub)
    
    elif tag == 'msqrt':
        # Square root
        rad = OxmlElement('m:rad')
        deg = OxmlElement('m:deg')  # Empty for square root
        base = OxmlElement('m:e')
        
        for child in mathml_node:
            _convert_mathml_node(child, base)
        
        rad.append(deg)
        rad.append(base)
        omml_parent.append(rad)
    
    elif tag == 'mover':
        # Over (like vector arrow)
        acc = OxmlElement('m:acc')
        accPr = OxmlElement('m:accPr')
        chr_elem = OxmlElement('m:chr')
        
        # Get the accent character
        children = list(mathml_node)
        if len(children) >= 2:
            accent_char = children[1].text or '→'
            chr_elem.set(qn('m:val'), accent_char)
        
        accPr.append(chr_elem)
        base = OxmlElement('m:e')
        
        if len(children) >= 1:
            _convert_mathml_node(children[0], base)
        
        acc.append(accPr)
        acc.append(base)
        omml_parent.append(acc)
    
    else:
        # Unknown tag, process children
        for child in mathml_node:
            _convert_mathml_node(child, omml_parent)


def _add_text_element(omml_parent, text):
    """
    Add a text run to OMML
    """
    r = OxmlElement('m:r')
    t = OxmlElement('m:t')
    t.text = text
    r.append(t)
    omml_parent.append(r)
