from exporter_fe.settings import env, AUTHBROKER_URL


def export_vars(request):
    data = {
        "AUTHBROKER_URL": AUTHBROKER_URL,
    }
    return data
