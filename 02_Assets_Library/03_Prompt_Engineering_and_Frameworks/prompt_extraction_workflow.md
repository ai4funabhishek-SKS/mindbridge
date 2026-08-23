# Prompt Extraction Workflow Guide

## Overview
This document outlines the systematic process for extracting, validating, and organizing prompts from WhatsApp content.

## Extraction Process

### 1. Initial Content Review
- Scan WhatsApp messages for prompt-like content
- Look for:
  - Explicit prompt templates
  - System instructions
  - Conversation patterns
  - Command structures

### 2. Content Classification
- Categorize identified prompts:
  - AI Tools prompts
  - Trading analysis prompts
  - Workflow automation prompts
  - General utility prompts

### 3. Prompt Extraction
1. Copy the original prompt text
2. Identify and mark variable elements
3. Document context and prerequisites
4. Note any specific formatting requirements

### 4. Standardization
Transform extracted content into standard template format:

```markdown
# Original Context
[WhatsApp message or conversation context]

# Extracted Prompt
[Clean prompt text with variables marked]

# Usage Notes
- Original purpose/context
- Required inputs
- Expected outputs
```

## Validation Process

### 1. Quality Checks
- Verify prompt completeness
- Check for context preservation
- Validate variable marking
- Confirm formatting consistency

### 2. Documentation Review
- Complete all template fields
- Add relevant examples
- Include source references
- Tag appropriately

### 3. Test Implementation
- Test with sample inputs
- Verify expected outputs
- Document any limitations
- Note improvement opportunities

## Organization

### File Structure
```
sources/prompts/
├── ai_tools/
├── trading/
├── workflow/
└── templates/
```

### Naming Convention
- Format: `[category]_[purpose]_[version].md`
- Example: `trading_market_analysis_v1.md`

### Metadata Requirements
- Creation date
- Last modified date
- Source reference
- Version number
- Author/contributor

## Version Control

### Change Tracking
- Document all modifications
- Keep original versions
- Track improvements
- Note testing results

### Quality Metrics
- Prompt effectiveness
- Consistency with original
- Reusability
- Documentation completeness

## Best Practices

1. Preserve Context
   - Maintain original intent
   - Document assumptions
   - Note specific conditions

2. Enhance Reusability
   - Identify common patterns
   - Abstract where appropriate
   - Document variations

3. Maintain Documentation
   - Keep examples current
   - Update test cases
   - Record improvements

## Review Cycle

1. Regular Reviews
   - Check for outdated content
   - Update examples
   - Refresh documentation

2. Improvement Process
   - Collect user feedback
   - Test variations
   - Document enhancements

## Tags
#prompt-extraction #workflow #documentation #quality-control