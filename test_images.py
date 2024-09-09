#!/usr/bin/env python
import argparse
import base64
import csv
import itertools
import json
import os
import sys
import time
from PIL import Image
import openai
import torch

client = openai.Client(base_url='http://localhost:5005/v1', api_key='sk-ip')

not_enhanced = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"
csvwriter = None
torch_memory_baseline = 0

def get_total_gpu_mem_used():
    device_count = torch.cuda.device_count()
    total_mem_used = 0.0
    for i in range(device_count):
        allocated_memory, total_memory,  = torch.cuda.mem_get_info(device=i)
        total_mem_used += total_memory - allocated_memory
    return total_mem_used / (1024 ** 3) - torch_memory_baseline  # convert bytes to gigabytes
    
def unload():
    response = client.images.generate(prompt="unload", model="unload")
    torch_memory_baseline = get_total_gpu_mem_used()
    print(f"Baseline CUDA memory: {torch_memory_baseline:0.1f}GB")

def preamble(model, f):
    unload()
    print(f"Starting pre: {model}")
    start = time.time()
    response = client.images.generate(prompt=not_enhanced + 'preamble', model=model, size="256x256", response_format='b64_json')
    end = time.time()
    print(f"# {model} First Image Latency (load time): {int(end - start)} seconds", file=f)
    if csvwriter:
        csvwriter.writerow([args.tag, "first image time", model, 'preamble', "256x256", 1, 'standard', get_total_gpu_mem_used(), end-start])
    mem_update(model, f, "start")
    print(f"Starting: {model}")

def mem_update(model, f, string):
    print(f"> {model} Memory used ({string}) {get_total_gpu_mem_used():0.1f} GB", file=f)

def generate_image(folder, prompt, model, res, f, n = 1, quality='standard'):
    start = time.time()
    response = client.images.generate(prompt=prompt, model=model, size=res, response_format='b64_json', n=n, quality=quality)
    #image = Image.open(io.BytesIO(base64.b64decode(response.data[0].b64_json)))
    #image.show()
    end = time.time()
    print(f"> {model} {quality} {res} took {end-start:.1f} seconds", file=f)

    for i, img in enumerate(response.data, 1):
        fname = f"{response.created}-{model}-{res}-{quality}-{i}.png"
        with open(os.path.join(folder, fname), 'wb') as png:
            png.write(base64.b64decode(img.b64_json))
        # markdown record the details of the test, including any extra revised_prompt
        print(f"\n\n![{prompt}]({fname})\n\n", file=f)
        if img.revised_prompt:
            print("revised_prompt: " + img.revised_prompt, file=f)
        print("\n", file=f, flush=True)

    print("-"*50, file=f)
    print("\n", file=f, flush=True)

    return end - start

def generic_test(folder, filename, models, prompt = "A cute baby sea otter", resolutions = ['1024x1024'], qualities = ['standard'], n=1, rounds=1):
    with open(os.path.join(folder, filename), "w") as f:
        for model in models:
            preamble(model, f)
            print(f"## Prompt\n```\n{prompt}\n```", file=f)

            for res in resolutions:
                for quality in qualities:
                    for i in range(rounds):
                        t = generate_image(folder, prompt, model, res, f, n, quality)
                        if csvwriter:
                            csvwriter.writerow([args.tag, folder, model, prompt, res, n, quality, get_total_gpu_mem_used(), t])
            
            mem_update(model, f, f"end")

def parse_args(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('prompt', action='store', type=str, default="A cute baby sea otter")
    parser.add_argument('-c', '--config', type=str, default="config.default.json")
    parser.add_argument('-m', '--models', type=str, default='all')
    parser.add_argument('-q', '--quick', action='store_true')
    parser.add_argument('-s', '--smoke', action='store_true')
    parser.add_argument('-p', '--perf', action='store_true')
    parser.add_argument('-f', '--full', action='store_true')
    parser.add_argument('-o', '--official', action='store_true')
    parser.add_argument('-x', '--extended', action='store_true')
    parser.add_argument('-n', '--batch', action='store', type=int, default=1)
    parser.add_argument('-t', '--test-dir', action='store', type=str, default='test')
    parser.add_argument('-T', '--tag', action='store', type=str, default='generic')
    parser.add_argument('--csv', action='store', type=str, default=None)

    return parser.parse_args()

def test_dir(root, test_type):
    t = time.localtime()
    dir = os.path.join(root, test_type + f"-{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}T{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}")
    os.makedirs(dir, exist_ok=True)
    return dir

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if args.models == 'all':
        with open(args.config) as f:
            config = json.load(f)

        models = list(config['models'])
    else:
        models = args.models.split(',')

    if args.csv:
        csvwriter = csv.writer(open(args.csv, "+a"))
        #[ tag, folder, model, prompt, res, n, quality, mem, time])

    if args.quick:
        TEST_DIR = test_dir(args.test_dir, 'quick')
        generic_test(TEST_DIR, "README.md", 'dall-e-2', args.prompt)
        generic_test(TEST_DIR, "README.md", 'dall-e-3', args.prompt)
    if args.smoke:
        TEST_DIR = test_dir(args.test_dir, 'smoke')
        generic_test(TEST_DIR, "README.md", models, args.prompt)
    if args.perf:
        TEST_DIR = test_dir(args.test_dir, 'perf')
        generic_test(TEST_DIR, "README.md", models, args.prompt, resolutions = ['256x256', '512x512', '1024x1024', "1536x1536"], qualities = ['standard', 'hd'], rounds=args.batch)
    if args.official:
        TEST_DIR = test_dir(args.test_dir, 'official')
        generic_test(TEST_DIR, "dall-e-2.md", 'dall-e-2', args.prompt, resolutions = ['256x256', '512x512', '1024x1024'], qualities = ['standard', 'hd'], n=10)
        generic_test(TEST_DIR, "dall-e-3-not-enhanced.md", 'dall-e-3', not_enhanced + args.prompt, resolutions = ['256x256', '512x512', '1024x1024', '1024x1796', '1796x1024'], qualities = ['standard', 'hd'])
        generic_test(TEST_DIR, "dall-e-3.md", 'dall-e-3', args.prompt, resolutions = ['256x256', '512x512', '1024x1024', '1024x1796', '1796x1024'], qualities = ['standard', 'hd'])
    if args.full:
        TEST_DIR = test_dir(args.test_dir, 'full')
        generic_test(TEST_DIR, "README.md", models, args.prompt, resolutions = ['256x256', '512x512', '1024x1024', "1536x1536"], qualities = ['standard', 'hd'], n=args.batch)
    if args.extended:
        TEST_DIR = test_dir(args.test_dir, 'extended')
        full_res = [ 256, 320, 448, 512, 640, 768, 896, 1024, 1080, 1152, 1280, 1344, 1408, 1536, 1664, 1728, 1796, 1920, 2176]
        all_res = [ f"{x}x{y}" for x, y in itertools.product(full_res, full_res) ]
        generic_test(TEST_DIR, "README.md", models, args.prompt, resolutions = ['256x256', '512x512', '1024x1024', "1536x1536"], qualities = ['standard', 'hd'], n=args.batch)


['256x256', '512x512', '1024x1024', "1536x1536"]