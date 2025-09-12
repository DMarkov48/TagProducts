from .services import get_progress

def progress_helpers(request):
    progress = None
    if request.user.is_authenticated:
        try:
            progress = get_progress(request.user)
        except Exception:
            progress = None
    return {"progress": progress}