"""
Prompt templates for the Simplified Attribute Enrichment service
"""
from typing import Dict, List, Any, Optional

# -------------------- Base Template --------------------

class BaseTemplate:
    """Base template for all product categories"""
    
    def generate_prompt(self, data: Dict[str, Any], attribute_list: List[str]) -> str:
        """
        Generate a prompt for the given data and attribute list
        
        Args:
            data: Dictionary containing product data (MPN, manufacturer, etc.)
            attribute_list: List of attributes to extract
            
        Returns:
            str: The generated prompt text
        """
        # This should be overridden by specific templates
        return self._generate_generic_prompt(data, attribute_list)
    
    def format_attribute_list(self, attribute_list: List[str]) -> str:
        """Format a list of attributes for inclusion in the prompt"""
        return ", ".join(attribute_list)
    
    def _generate_generic_prompt(self, data: Dict[str, Any], attribute_list: List[str]) -> str:
        """Generate a generic prompt for any product category"""
        # Extract required fields from data
        mpn = data.get('mfg_part_number', '')
        manufacturer = data.get('manufacturer_name', '')
        cat_subcat = data.get('cat_subcat', '')
        
        # Format the attribute list
        formatted_attributes = self.format_attribute_list(attribute_list)
        
        # Generic prompt template
        prompt = f"""
Extract comprehensive information about this product by searching MULTIPLE SOURCES and websites:

PRODUCT MPN: {mpn}
MANUFACTURER: {manufacturer}
CATEGORY & SUBCATEGORY: {cat_subcat}
ATTRIBUTES TO EXTRACT: {formatted_attributes}

MULTI-SOURCE SEARCH STRATEGY:
1. Search manufacturer's official website first ({manufacturer}.com) for authoritative specifications
2. Search at least 5 major distributors and retailers for this product
3. Locate PDF technical datasheets and installation manuals for complete specifications
4. Cross-reference information across all sources for accuracy

SEARCH EFFICIENCY GUIDELINES:
1. Use specific search strings: "[MPN] [manufacturer] specifications"
2. Search for datasheets using "[MPN] datasheet pdf technical specifications" 
3. Use industry-specific search terms for this product category

VERIFICATION REQUIREMENTS:
✓ Information comes from multiple independent sources
✓ Data specifically references the exact MPN {mpn}
✓ All technical specifications include proper units of measurement
✓ No speculative information is included

RESPONSE FORMAT:
Return ONLY a single valid JSON object with these requirements:
1. Use double quotes for all keys and string values
2. No trailing commas
3. Ensure all special characters in strings are properly escaped
4. CRITICAL: For any unavailable information, use "" (empty string) without any explanatory text

CRITICAL REQUIREMENTS:
- Return ONLY the JSON object with no additional text before or after
- Never duplicate the JSON in the response
- NO NEWLINES at the beginning of your response
- For ANY attribute where information cannot be definitively determined, use "" (empty string)
- NEVER use phrases like "Information Not Available", "Unknown", or "Not Specified" - use "" instead
- Include complete specifications with proper units for available information
- If information conflicts between sources, use the most authoritative source
"""
        return prompt

# -------------------- Electrical Template --------------------

class ElectricalTemplate(BaseTemplate):
    """Template for electrical category products"""
    
    def generate_prompt(self, data: Dict[str, Any], attribute_list: List[str]) -> str:
        """Generate a prompt for electrical products"""
        # Extract required fields from data
        mpn = data.get('mfg_part_number', '')
        manufacturer = data.get('manufacturer_name', '')
        cat_subcat = data.get('cat_subcat', '')
        
        # Format the attribute list
        formatted_attributes = self.format_attribute_list(attribute_list)
        
        # Electrical-specific prompt template
        prompt = f"""
Extract comprehensive information about this electrical part by searching MULTIPLE SOURCES and websites:

PRODUCT MPN: {mpn}
MANUFACTURER: {manufacturer}
CATEGORY & SUBCATEGORY: {cat_subcat}
ATTRIBUTES TO EXTRACT: {formatted_attributes}

MULTI-SOURCE SEARCH STRATEGY:
1. Search manufacturer's official website first ({manufacturer}.com) for authoritative specifications
2. Search at least 5 major electrical distributors (Grainger, Home Depot, Lowe's, Eaton, Schneider Electric)
3. Locate PDF technical datasheets and installation manuals for complete specifications
4. Check specialized electrical forums for professional insights
5. Cross-reference information across all sources for accuracy

MATERIAL IDENTIFICATION REQUIREMENTS:
1. CRITICAL: Determine definitive material composition (plastic, metal, copper, aluminum, etc.)
2. Find exact material specifications without using qualifiers like "likely" or "probably"
3. Look for specific material descriptions: "made of", "constructed from", "material:", "composition:"
4. Check material codes in specs: "AL" (aluminum), "Cu" (copper), "PVC", "ABS"
5. Examine product photos and technical diagrams for visual material identification
6. If material cannot be definitively determined, use empty string "" for Material field

SEARCH EFFICIENCY GUIDELINES:
1. Use specific search strings: "[MPN] [manufacturer] specifications material"
2. Search for datasheets using "[MPN] datasheet pdf technical specifications" 
3. Use industry-specific search terms for electrical components

VERIFICATION REQUIREMENTS:
✓ Information comes from multiple independent sources
✓ Data specifically references the exact MPN {mpn}
✓ Material type is definitively identified
✓ All technical specifications include proper units of measurement
✓ No speculative information is included

RESPONSE FORMAT:
Return ONLY a single valid JSON object with these requirements:
1. Use double quotes for all keys and string values
2. No trailing commas
3. Ensure all special characters in strings are properly escaped
4. CRITICAL: For any unavailable information, use "" (empty string) without any explanatory text

CRITICAL REQUIREMENTS:
- Return ONLY the JSON object with no additional text before or after
- Never duplicate the JSON in the response
- NO NEWLINES at the beginning of your response
- For ANY attribute where information cannot be definitively determined, use "" (empty string)
- NEVER use phrases like "Information Not Available", "Unknown", or "Not Specified" - use "" instead
- Include complete specifications with proper units for available information
- If information conflicts between sources, use the most authoritative source
"""
        return prompt

# -------------------- HVAC Template --------------------

class HVACTemplate(BaseTemplate):
    """Template for HVAC category products"""
    
    def generate_prompt(self, data: Dict[str, Any], attribute_list: List[str]) -> str:
        """Generate a prompt for HVAC products"""
        # Extract required fields from data
        mpn = data.get('mfg_part_number', '')
        manufacturer = data.get('manufacturer_name', '')
        cat_subcat = data.get('cat_subcat', '')
        
        # Format the attribute list
        formatted_attributes = self.format_attribute_list(attribute_list)
        
        # HVAC-specific prompt template
        prompt = f"""
Extract comprehensive information about this HVAC component by searching MULTIPLE SOURCES and websites:

PRODUCT MPN: {mpn}
MANUFACTURER: {manufacturer}
CATEGORY & SUBCATEGORY: {cat_subcat}
ATTRIBUTES TO EXTRACT: {formatted_attributes}

MULTI-SOURCE SEARCH STRATEGY:
1. Search manufacturer's official website first ({manufacturer}.com) for authoritative specifications
2. Search at least 5 major HVAC distributors (Grainger, Ferguson, Johnstone Supply, Carrier, Trane)
3. Locate PDF technical datasheets, installation manuals, and engineering specifications
4. Check specialized HVAC forums and contractor resources
5. Cross-reference information across all sources for accuracy

TECHNICAL SPECIFICATIONS FOCUS:
1. CRITICAL: Find exact capacity/BTU/tonnage ratings with proper units
2. Determine precise electrical requirements (voltage, phase, amperage)
3. Identify refrigerant type and compatibility (R-410A, R-32, etc.)
4. Find exact physical dimensions and installation requirements
5. Determine energy efficiency ratings (SEER, EER, HSPF) where applicable

SEARCH EFFICIENCY GUIDELINES:
1. Use specific search strings: "[MPN] [manufacturer] specifications technical data"
2. Search for datasheets using "[MPN] datasheet pdf technical specifications" 
3. Use industry-specific search terms for HVAC components

VERIFICATION REQUIREMENTS:
✓ Information comes from multiple independent sources
✓ Data specifically references the exact MPN {mpn}
✓ All technical specifications include proper units of measurement
✓ No speculative information is included

RESPONSE FORMAT:
Return ONLY a single valid JSON object with these requirements:
1. Use double quotes for all keys and string values
2. No trailing commas
3. Ensure all special characters in strings are properly escaped
4. CRITICAL: For any unavailable information, use "" (empty string) without any explanatory text

CRITICAL REQUIREMENTS:
- Return ONLY the JSON object with no additional text before or after
- Never duplicate the JSON in the response
- NO NEWLINES at the beginning of your response
- For ANY attribute where information cannot be definitively determined, use "" (empty string)
- NEVER use phrases like "Information Not Available", "Unknown", or "Not Specified" - use "" instead
- Include complete specifications with proper units for available information
- If information conflicts between sources, use the most authoritative source
"""
        return prompt

# -------------------- Plumbing Template --------------------

class PlumbingTemplate(BaseTemplate):
    """Template for plumbing category products"""
    
    def generate_prompt(self, data: Dict[str, Any], attribute_list: List[str]) -> str:
        """Generate a prompt for plumbing products"""
        # Extract required fields from data
        mpn = data.get('mfg_part_number', '')
        manufacturer = data.get('manufacturer_name', '')
        cat_subcat = data.get('cat_subcat', '')
        
        # Format the attribute list
        formatted_attributes = self.format_attribute_list(attribute_list)
        
        # Plumbing-specific prompt template
        prompt = f"""
Extract comprehensive information about this plumbing component by searching MULTIPLE SOURCES and websites:

PRODUCT MPN: {mpn}
MANUFACTURER: {manufacturer}
CATEGORY & SUBCATEGORY: {cat_subcat}
ATTRIBUTES TO EXTRACT: {formatted_attributes}

MULTI-SOURCE SEARCH STRATEGY:
1. Search manufacturer's official website first ({manufacturer}.com) for authoritative specifications
2. Search at least 5 major plumbing distributors (Ferguson, Grainger, Home Depot, Lowe's, SupplyHouse)
3. Locate PDF technical datasheets, installation manuals, and specification sheets
4. Check specialized plumbing forums and contractor resources
5. Cross-reference information across all sources for accuracy

MATERIAL AND COMPATIBILITY FOCUS:
1. CRITICAL: Determine exact material composition (brass, copper, PVC, PEX, etc.)
2. Find precise connection types and sizes (NPT, compression, sweat, etc.)
3. Identify pressure and temperature ratings with proper units
4. Determine compatibility with different plumbing systems
5. Find certification information (NSF, ANSI, UPC, etc.)

SEARCH EFFICIENCY GUIDELINES:
1. Use specific search strings: "[MPN] [manufacturer] specifications material"
2. Search for datasheets using "[MPN] datasheet pdf technical specifications" 
3. Use industry-specific search terms for plumbing components

VERIFICATION REQUIREMENTS:
✓ Information comes from multiple independent sources
✓ Data specifically references the exact MPN {mpn}
✓ Material type is definitively identified
✓ All technical specifications include proper units of measurement
✓ No speculative information is included

RESPONSE FORMAT:
Return ONLY a single valid JSON object with these requirements:
1. Use double quotes for all keys and string values
2. No trailing commas
3. Ensure all special characters in strings are properly escaped
4. CRITICAL: For any unavailable information, use "" (empty string) without any explanatory text

CRITICAL REQUIREMENTS:
- Return ONLY the JSON object with no additional text before or after
- Never duplicate the JSON in the response
- NO NEWLINES at the beginning of your response
- For ANY attribute where information cannot be definitively determined, use "" (empty string)
- NEVER use phrases like "Information Not Available", "Unknown", or "Not Specified" - use "" instead
- Include complete specifications with proper units for available information
- If information conflicts between sources, use the most authoritative source
"""
        return prompt

# -------------------- Refrigeration Template --------------------

class RefrigerationTemplate(BaseTemplate):
    """Template for refrigeration category products"""
    
    def generate_prompt(self, data: Dict[str, Any], attribute_list: List[str]) -> str:
        """Generate a prompt for refrigeration products"""
        # Extract required fields from data
        mpn = data.get('mfg_part_number', '')
        manufacturer = data.get('manufacturer_name', '')
        cat_subcat = data.get('cat_subcat', '')
        
        # Format the attribute list
        formatted_attributes = self.format_attribute_list(attribute_list)
        
        # Refrigeration-specific prompt template
        prompt = f"""
Extract comprehensive information about this refrigeration component by searching MULTIPLE SOURCES and websites:

PRODUCT MPN: {mpn}
MANUFACTURER: {manufacturer}
CATEGORY & SUBCATEGORY: {cat_subcat}
ATTRIBUTES TO EXTRACT: {formatted_attributes}

MULTI-SOURCE SEARCH STRATEGY:
1. Search manufacturer's official website first ({manufacturer}.com) for authoritative specifications
2. Search at least 5 major refrigeration distributors (Grainger, Ferguson, Johnstone Supply, United Refrigeration)
3. Locate PDF technical datasheets, installation manuals, and engineering specifications
4. Check specialized refrigeration forums and contractor resources
5. Cross-reference information across all sources for accuracy

TECHNICAL SPECIFICATIONS FOCUS:
1. CRITICAL: Find exact capacity ratings with proper units
2. Determine precise electrical requirements (voltage, phase, amperage)
3. Identify refrigerant type and compatibility (R-134a, R-404A, R-290, etc.)
4. Find exact physical dimensions and installation requirements
5. Determine temperature range and operating conditions

SEARCH EFFICIENCY GUIDELINES:
1. Use specific search strings: "[MPN] [manufacturer] specifications technical data"
2. Search for datasheets using "[MPN] datasheet pdf technical specifications" 
3. Use industry-specific search terms for refrigeration components

VERIFICATION REQUIREMENTS:
✓ Information comes from multiple independent sources
✓ Data specifically references the exact MPN {mpn}
✓ All technical specifications include proper units of measurement
✓ No speculative information is included

RESPONSE FORMAT:
Return ONLY a single valid JSON object with these requirements:
1. Use double quotes for all keys and string values
2. No trailing commas
3. Ensure all special characters in strings are properly escaped
4. CRITICAL: For any unavailable information, use "" (empty string) without any explanatory text

CRITICAL REQUIREMENTS:
- Return ONLY the JSON object with no additional text before or after
- Never duplicate the JSON in the response
- NO NEWLINES at the beginning of your response
- For ANY attribute where information cannot be definitively determined, use "" (empty string)
- NEVER use phrases like "Information Not Available", "Unknown", or "Not Specified" - use "" instead
- Include complete specifications with proper units for available information
- If information conflicts between sources, use the most authoritative source
"""
        return prompt

# -------------------- Template Factory --------------------

def get_template(category: Optional[str] = None) -> BaseTemplate:
    """
    Get the appropriate template for the given category
    
    Args:
        category: Product category name
        
    Returns:
        BaseTemplate: The appropriate template instance
    """
    # Normalize category name
    if category:
        category = category.lower().strip()
    
    # Select template based on category
    if category in ['electrical', 'electric', 'electronics']:
        return ElectricalTemplate()
    elif category in ['hvac', 'heating', 'cooling', 'air conditioning']:
        return HVACTemplate()
    elif category in ['plumbing', 'pipe', 'water']:
        return PlumbingTemplate()
    elif category in ['refrigeration', 'refrigerant', 'cooling']:
        return RefrigerationTemplate()
    else:
        # Default to base template
        return BaseTemplate()