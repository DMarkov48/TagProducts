from .services import get_progress

def progress_helpers(request):
    progress = None
    if request.user.is_authenticated:
        try:
            progress = get_progress(request.user)  # вернёт (unique, target, passed, total)
        except Exception:
            progress = None
    return {"progress": progress}