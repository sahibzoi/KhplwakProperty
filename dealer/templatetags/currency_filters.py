from django import template

register = template.Library()

@register.filter
def afn(value):
    """
    Format numeric value in AFN with commas.
    Usage: {{ some_number|afn }}
    Output: ؋ 2,500,000
    """
    if value in (None, ""):
        return ""

    try:
        number_value = float(value)
    except (TypeError, ValueError):
        # If it's not a number (like text), just show it raw
        return value

    # format with thousand separators, no decimals
    return f"؋ {number_value:,.0f}"
