#!/usr/bin/env python3

def format_as_markdown(reference, text, include_reference=True, version=None):
    """Format verse text as markdown."""
    if include_reference:
        # Add version to reference if provided
        ref_display = reference
        if version:
            ref_display = f"{reference}({version})"
            
        # Add blockquote to both reference and verse text
        quoted_text = "\n".join([f"> {line}" for line in text.split("\n")])
        return f"> **{ref_display}**\n>\n{quoted_text}"
    else:
        # Add blockquote to the verse text without reference
        quoted_text = "\n".join([f"> {line}" for line in text.split("\n")])
        return quoted_text

def format_parallel_verses(parallel_results, markdown=False):
    """Format parallel verses for display."""
    if not parallel_results:
        return "No results found."
    
    # Get the reference from the first successful result
    reference = next((r["reference"] for r in parallel_results if "error" not in r), "Unknown reference")
    
    if markdown:
        # Don't include version in main title for parallel view since we show multiple versions
        output = [f"> **{reference}**\n>"]
        
        for result in parallel_results:
            version = result["version"]
            if "error" in result:
                output.append(f"> *{version}*: Error - {result['error']}")
            else:
                # Add blockquote to each line of the verse text
                verse_text = result["text"]
                quoted_text = "\n".join([f"> {line}" for line in verse_text.split("\n")])
                output.append(f"> *{version}*:\n{quoted_text}")
        
        return "\n\n".join(output)
    else:
        output = [f"\n{reference}"]
        
        for result in parallel_results:
            version = result["version"]
            if "error" in result:
                output.append(f"\n[{version}] Error: {result['error']}")
            else:
                output.append(f"\n[{version}] {result['text']}")
        
        return "\n".join(output)