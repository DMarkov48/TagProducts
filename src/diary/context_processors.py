from .services import get_progress

def progress_helpers(request):
    # Возвращаем ссылку на функцию, чтобы можно было вызвать из шаблона
    return {"get_progress_func": get_progress}