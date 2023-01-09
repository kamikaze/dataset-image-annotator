import argparse
import asyncio
from pathlib import Path

from dataset_image_annotator.api_clients import annotator


def get_parsed_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-a', '--annotator-server-address', type=str)
    parser.add_argument('-d', '--data-root', type=str)

    args, args_other = parser.parse_known_args()

    return args


async def main():
    args = get_parsed_args()
    annotator_server_address = args.annotator_server_address
    data_root_path = Path(args.data_root).expanduser()

    for raw_image in data_root_path:
        await annotator.upload_raw_file(annotator_server_address, raw_image)

    return True


if __name__ == '__main__':
    asyncio.run(main())
