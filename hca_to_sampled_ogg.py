from typing import Tuple

import pydub
import os
import subprocess

hca_location = r"D:\DRO Raw Files\Danganronpa 1 2 Full Music Package\Raw\DRV3\_vgmt_awb_ext_BGM"
ogg_location = r"D:\DRO Raw Files\Danganronpa 1 2 Full Music Package\DRV3 Music"
vgmstream_location = r"D:\DRO Raw Files\Danganronpa 1 2 Full Music Package\vgmstream"
ffmpeg_location = r"D:\Location\of\your\ffmpeg\exe" # Should finish in ".exe"
ffprobe_location = r"D:\Location\of\your\ffprobe\exe" # Should finish in ".exe"

pydub.AudioSegment.ffmpeg = ffmpeg_location
pydub.AudioSegment.converted = ffmpeg_location
pydub.AudioSegment.ffprobe = ffprobe_location
os.chdir(vgmstream_location)


def get_hca_file_directory(file_name):
    hca_file_name = file_name.replace('.bin', '.hca')
    return rf'{hca_location}\{hca_file_name}'


def get_ogg_file_directory(file_name):
    ogg_file = rf"{ogg_location}\{file_name.replace('.bin', '.ogg')}"
    return ogg_file


def rename_file(bin_name):
    bin_file_name = rf'{hca_location}\{bin_name}'
    hca_file_name = bin_file_name.replace('.bin', '.hca')
    os.rename(bin_file_name, hca_file_name)


def get_samples_for_file(hca_file_name: str) -> Tuple[int, int]:
    hca_file = get_hca_file_directory(hca_file_name)
    process = subprocess.Popen([r'.\test.exe', '-m', hca_file],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    process.kill()
    parsed_stdout = stdout.decode('utf-8').split('\r\n')
    parsed_stderr = stderr.decode('utf-8').split('\r\n')
    if parsed_stderr[0]:
        raise RuntimeError(parsed_stderr)

    loop_start, loop_end = -1, -1
    for line in parsed_stdout:
        if 'loop start' in line:
            loop_start = int(line.split(' ')[2])
        elif 'loop end' in line:
            loop_end = int(line.split(' ')[2])

    return loop_start, loop_end


def convert_hca_to_ogg(hca_file_name: str) -> None:
    hca_file = get_hca_file_directory(hca_file_name)
    ogg_file = get_ogg_file_directory(hca_file_name)
    process = subprocess.Popen([r'.\test.exe', '-o', ogg_file, hca_file],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    process.kill()
    parsed_stdout = stdout.decode('utf-8').split('\r\n')
    parsed_stderr = stderr.decode('utf-8').split('\r\n')
    if parsed_stderr[0]:
        raise RuntimeError(parsed_stderr)

    return


def add_samples_to_file(hca_file_name: str, loop_start: int, loop_end: int) -> None:
    ogg_file = get_ogg_file_directory(hca_file_name)
    sound = pydub.AudioSegment.from_file(ogg_file)
    if loop_start == -1 and loop_end == -1:
        print(hca_file_name, 'has no loop information')
        sound.export(ogg_file, format="ogg")
    else:
        sound.export(ogg_file, format="ogg", tags={'LoopStart': loop_start, 'LoopEnd': loop_end})


def do_drae_file(hca_file_name: str) -> None:
    print(f'*Processing {hca_file_name}...')

    loop_start, loop_end = get_samples_for_file(hca_file_name)
    convert_hca_to_ogg(hca_file_name)
    add_samples_to_file(hca_file_name, loop_start, loop_end)
    print(f'Processed {hca_file_name}...')


def do_drae_files() -> None:
    for file in os.listdir(hca_location):
        do_drae_file(file)


def do_drv3_file(hca_file_name: str) -> None:
    print(f'*Processing {hca_file_name}...')

    loop_start, loop_end = -1, -1
    rename_file(hca_file_name)
    convert_hca_to_ogg(hca_file_name)
    add_samples_to_file(hca_file_name, loop_start, loop_end)
    print(f'Processed {hca_file_name}...')


def do_drv3_files() -> None:
    for file in os.listdir(hca_location):
        do_drv3_file(file)


if __name__ == '__main__':
    do_drv3_files()