#!/usr/bin/env python
import base64
import time
import argparse
import sys
import os
import io
import itertools
import json
from PIL import Image
import openai
import torch

client = openai.Client(base_url='http://localhost:5005/v1', api_key='sk-ip')

TEST_DIR = 'test'
not_enhanced = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"

torch_memory_baseline = 0

def get_total_gpu_mem_used():
    device_count = torch.cuda.device_count()
    total_mem_used = 0.0
    for i in range(device_count):
        allocated_memory, total_memory,  = torch.cuda.mem_get_info(device=i)
        total_mem_used += total_memory - allocated_memory
    return total_mem_used / (1024 ** 3) - torch_memory_baseline  # convert bytes to gigabytes
    
torch_memory_baseline = get_total_gpu_mem_used()
print(f"Baseline CUDA memory: {torch_memory_baseline:0.1f}GB")

def preamble(model, f):
    start = time.time()
    response = client.images.generate(prompt=not_enhanced + 'test', model=model, size="256x256", response_format='b64_json')
    end = time.time()
    print(f"# {model} First Image Latency (load time): {int(end - start)} seconds", file=f)
    mem_update(model, f, "start")

def mem_update(model, f, string):
    print(f"> {model} Memory used ({string}) {get_total_gpu_mem_used():0.1f} GB", file=f)

def generate_image(prompt, model, res, f, n = 1, suffix='', quality='standard'):
    start = time.time()
    response = client.images.generate(prompt=prompt, model=model, size=res, response_format='b64_json', n=n, quality=quality)
    #image = Image.open(io.BytesIO(base64.b64decode(response.data[0].b64_json)))
    #image.show()
    end = time.time()
    print(f"> {model} {quality} {res} took {end-start:.1f} seconds", file=f)

    for i, img in enumerate(response.data, 1):
        fname = f"{response.created}-{model}-{res}-{quality}-{i}.png"
        with open(f'{TEST_DIR}/{fname}', 'wb') as png:
            png.write(base64.b64decode(img.b64_json))
        # markdown record the details of the test, including any extra revised_prompt
        print(f"![{prompt}]({fname})", file=f)
        if img.revised_prompt:
            print("revised_prompt: " + img.revised_prompt, file=f)
        print("\n", file=f, flush=True)

    print("-"*50, file=f)
    print("\n", file=f, flush=True)

def extended_test(models, prompt, n=1):
    for model in models:
        if 'enhancer' not in config['models'][model]:
            with open(f"{TEST_DIR}/test_images-{model}.md", "w") as f:

                preamble(model, f)
                print(f"## Prompt\n```{prompt}```", file=f)

                full_res = [ 256, 320, 448, 512, 640, 768, 896, 1024, 1080, 1152, 1280, 1344, 1408, 1536, 1664, 1728, 1796, 1920, 2176]
                for x, y in itertools.product(full_res, full_res):
                    res = f"{x}x{y}"
                    mem_update(model, f, f"{res}")
                    for quality in ['standard', 'hd']:
                        generate_image(prompt, model, res, f, n=n, quality=quality)

                mem_update(model, f, f"end")

def full_test(models, prompt, n=1):
    for model in models:
        with open(f"{TEST_DIR}/full_test-{model}.md", "w") as f:
            preamble(model, f)
            print(f"## Prompt\n```{prompt}```", file=f)

            for res in ['256x256', '512x512', '1024x1024', "1536x1536"]:
                mem_update(model, f, f"{res}")
                for quality in ['standard', 'hd']:
                    generate_image(prompt, model, res, f, n=n, quality=quality)

            mem_update(model, f, f"end")

def official_test(prompt, n=1):
    for model in ['dall-e-2', 'dall-e-3']:
        with open(f"{TEST_DIR}/official_test-{model}.md", "w") as f:
            preamble(model, f)
            print(f"## Prompt\n```{prompt}```", file=f)

            for res in ['256x256', '512x512', '1024x1024'] + ['1024x1796', '1796x1024'] if model == 'dall-e-3' else []:
                mem_update(model, f, f"{res}")
                for quality in ['standard', 'hd']:
                    generate_image(prompt, model, res, f, n=n, quality=quality)

            mem_update(model, f, f"end")

def smoke_test(models, prompt):
    with open(f"{TEST_DIR}/smoke_test.md", "w") as f:
        for model in models:
            preamble(model, f)
            print(f"## Prompt\n```{prompt}```", file=f)

            res='1024x1024'
            mem_update(model, f, f"{res}")
            generate_image(prompt, model, res, f)
            mem_update(model, f, f"end")

def quick_test(models, prompt, n=1):
    with open(f"{TEST_DIR}/quick_test.md", "w") as f:
        preamble("dall-e-2", f)
        print(f"# {prompt}", file=f)
        generate_image(prompt, "dall-e-2", "1024x1024", f, n=n)
        mem_update("dall-e-2", f, f"end")

        preamble("dall-e-3", f)
        print(f"# {prompt}", file=f)
        generate_image(not_enhanced + prompt, "dall-e-3", "1024x1024", f, n=n, suffix='-not-enhanced')
        generate_image(prompt, "dall-e-3", "1024x1024", f, n=n)
        mem_update("dall-e-3", f, f"end")

def parse_args(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', '--prompt', action='store', type=str, default="A cute baby sea otter")
    parser.add_argument('-c', '--config', type=str, default="config.default.json")
    parser.add_argument('-m', '--models', type=str, default='all')
    parser.add_argument('-q', '--quick', action='store_true')
    parser.add_argument('-s', '--smoke', action='store_true')
    parser.add_argument('-f', '--full', action='store_true')
    parser.add_argument('-o', '--official', action='store_true')
    parser.add_argument('-x', '--extended', action='store_true')
    parser.add_argument('-n', '--batch', action='store', type=int, default=1)
    parser.add_argument('-t', '--test-dir', action='store', type=str, default='test')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    TEST_DIR = args.test_dir
    os.makedirs(TEST_DIR, exist_ok=True)

    if args.models == 'all':
        with open(args.config) as f:
            config = json.load(f)

        models = list(config['models'])
    else:
        models = args.models.split(',')

    if args.quick:
        quick_test(models, args.prompt, n=args.batch)
    if args.smoke:
        smoke_test(models, args.prompt)
    if args.official:
        official_test(args.prompt, n=args.batch)
    if args.full:
        full_test(models, args.prompt, n=args.batch)
    if args.extended:
        extended_test(models, args.prompt, n=args.batch)


