def admin_custom_context(request):
    """
    Custom context processor to handle Python 3.14 compatibility issues
    with Django admin template context copying.
    """
    return {
        'admin_custom_context': True,
    }
