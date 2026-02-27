from django.conf import settings


def config(request):
    return {
        'GIT_COMMIT_HASH': settings.GIT_COMMIT_HASH,
        'vue3_entry_script': settings.VUE3_ENTRY_SCRIPT,
    }
