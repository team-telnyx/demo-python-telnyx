from aiohttp import web


def add_domains(connection_data: dict) -> dict:
    uris = {}
    for connection in connection_data:
            uris[str(connection["id"])] = connection["user_name"]
    return uris


def change_files(uris: dict, ngrok_url: str) -> None:
    """
    Takes list of uris to change the inbound and busy XML files to different dial.

    """

    uri_dials = ""
    uri_str = (
        "<Sip statusCallback='{ngrok_url}/TeXML/events' "
        "statusCallbackEvent='initiated answered completed'>sip:{connection}@sip.telnyx.com</Sip>"
    )
    for conn_id in uris.keys():
        uri_dial = uri_str.format(ngrok_url=ngrok_url, connection=uris[conn_id])
        uri_dials += "        " + uri_dial + "\n"

    inbound_file = open("call_center/infrastructure/TeXML/inbound_template.xml", "r")
    inbound_xml = inbound_file.read()
    inbound_file.close()

    busy_file = open("call_center/infrastructure/TeXML/busy_template.xml", "r")
    busy_xml = busy_file.read()
    busy_file.close()

    inbound_xml = inbound_xml.format(uris=uri_dials.strip(), ngrok_url=ngrok_url)
    busy_xml = busy_xml.format(uris=uri_dials.strip(), ngrok_url=ngrok_url)
    inbound_file = open("call_center/infrastructure/TeXML/inbound.xml", "w")
    busy_file = open("call_center/infrastructure/TeXML/busy.xml", "w")
    inbound_file.write(inbound_xml)
    busy_file.write(busy_xml)
    inbound_file.close()
    busy_file.close()


async def get_connections(app: web.Application) -> None:
    """
    Get the list of connections on call-center account and their corresponding
    username. If these have changed since last job, change XML.

    """

    connection_data = await app["telnyx_client"].get_connections()
    connection_data = connection_data["data"]
    connection_data = add_domains(connection_data)

    try:
        cached_data = app["connection_data"]
        if connection_data != cached_data:
            change_files(connection_data, app["ngrok_url"])
            app["connection_data"] = connection_data

    except KeyError:
        app["connection_data"] = connection_data
        change_files(connection_data, app["ngrok_url"])
