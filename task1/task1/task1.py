from shutil import SameFileError
import sys
import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
from argparse import ArgumentParser
from colorama import Fore


def parse_arguments():
    parser = ArgumentParser(description="Copy files by extension to new directory structure")
    parser.add_argument("source_dir", type=str, help="Path to the source directory")
    parser.add_argument("target_dir", type=str, nargs='?', default="extensions", help="Path to the target directory (default: extensions)")
    args = parser.parse_args()
    return args


# Let's do a generator which recursively returns the content of a folder and its subfolders
async def read_folder(apath: AsyncPath):
    async for item in apath.iterdir():      
        if not await item.is_file():
            async for subitem in read_folder(item):
                yield subitem
        else:
            yield item


async def copy_file(file: AsyncPath, destination: AsyncPath):
    '''
    The function copies a file to the directory named as a file extension. The extension directory is in 'destination'
    '''
    # Check if item is a directory or not. It should be not, but just in a case.
    try:
        if await file.is_dir():
            raise IsADirectoryError
    except IsADirectoryError:
        print(Fore.RED + "\nSomething went wrong inside " + Fore.YELLOW + "'read_folder'" + Fore.RED + " generator.")
        print(Fore.CYAN + f"{file.name}" + Fore.RED + " is a directory and it is tried to be copied, not its content.\n" + Fore.RESET)
        sys.exit()

    # Obtain the file extension
    if '.' not in file.name:
        extension = 'no_extension'
    else:
        extension = file.name.split('.')[-1]
    
    # Create a directory to store files
    ext_dir = destination / extension
    await ext_dir.mkdir(exist_ok=True)
    
    new_destination = ext_dir / file.name

    try:
        # We avoid copying files into themselves
        # It's useful when we try to run   task1.py .   second time
        # First time the directory 'extensions' was created. Second time it tries to be copied into itself.
        if file != new_destination:
            await copyfile(file, new_destination)
    except SameFileError:
        print("You try to copy file into the same file")
    except PermissionError:
        print("The problem with permission. Probably, you forgot to add a file name to the path")


async def main():
    # Let's get arguments from the command line:
    args = parse_arguments()
    
    # Define a folder where are we copying FROM:
    apath_outdir = AsyncPath(args.source_dir)

    try:
        if not await apath_outdir.exists():
            raise FileNotFoundError
    except FileNotFoundError:
        print(Fore.RED + "There is no such file or directory what you want to copy: " + Fore.RESET + f"{apath_outdir}\n")
        sys.exit()
    
    # Create (if there is not) a folder where are we copying TO:
    apath_todir = AsyncPath(args.target_dir)
    await apath_todir.mkdir(exist_ok=True)
    
    # Copy files
    async for item in read_folder(apath_outdir):
        await copy_file(item, apath_todir)


if __name__ == "__main__":
    asyncio.run(main())
