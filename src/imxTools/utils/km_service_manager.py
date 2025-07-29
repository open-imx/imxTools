KM_SERVICE_INSTANCE = None


async def start_km_service():
    global KM_SERVICE_INSTANCE, km_service_starting

    if KM_SERVICE_INSTANCE is not None:
        return
    else:
        from kmService import KmService

        KM_SERVICE_INSTANCE = await KmService.factory()


def is_km_service_running():
    global KM_SERVICE_INSTANCE
    return KM_SERVICE_INSTANCE is not None


def get_km_service():
    global KM_SERVICE_INSTANCE
    return KM_SERVICE_INSTANCE
