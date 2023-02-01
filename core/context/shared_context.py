from core.model_enums import AppCategories,Devices


''' Use for share categories for all views '''


def shared_categories_context(request):
    return {'categories': AppCategories}

def shared_devices_context(request):
    return {'devices': Devices}