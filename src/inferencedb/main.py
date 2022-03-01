import asyncio
from asyncio.subprocess import PIPE, STDOUT
import json
import os
from signal import SIGTERM

from inferencedb.config.factory import create_config_provider
from inferencedb.config.providers.kubernetes_config_provider import KubernetesConfigProvider
from inferencedb.utils.asyncio_utils import cancling_background_task
from inferencedb.settings import Settings


async def main():
    settings = Settings()

    config_provider = create_config_provider(
        name=settings.config_provider,
        params=settings.config_provider_args,
    )

    with cancling_background_task(config_provider.run()): 
         # Wait for the first configuration.
        await config_provider.wait_for_update() 

        while True:        
            config = config_provider.get_config()
            
            # Create the worker process.
            process = await asyncio.create_subprocess_exec(
                "faust", "-A", "inferencedb.app", "worker", "-l", "info",
                env={
                    **os.environ, 
                    "CONFIG": json.dumps(config)
                },
            )

            # Wait for a configuration update and for the process to exit simultaneously.
            wait_for_process_task = asyncio.create_task(process.communicate())
            config_update_task = asyncio.create_task(config_provider.wait_for_update())

            done, pending = await asyncio.wait(
                [wait_for_process_task, config_update_task], 
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            # If there is a configuration update, terminate the process and relaunch it.
            if config_update_task in done:
                # Warm shutdown, wait for tasks to complete.
                # https://faust.readthedocs.io/en/latest/userguide/workers.html
                process.send_signal(SIGTERM)
                await process.wait()


if __name__ == "__main__":
    asyncio.run(main())
