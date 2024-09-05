#!/usr/bin/env python
import argparse
import base64
import io
import sys
import openai
from PIL import Image

def parse_args(argv):
    # prompt, model, size, filename
    parser = argparse.ArgumentParser(description='Generate an image from a prompt using OpenAI\'s DALL-E API.')
    parser.add_argument('prompt', type=str, help='The text prompt that describes the image you want to generate.')
    parser.add_argument('-m', '--model', type=str, default='dall-e-2', help='The model to use for generating the image.')
    parser.add_argument('-s', '--size', type=str, default='1024x1024', help='The size of the generated image.')
    parser.add_argument('-f', '--filename', type=str, default='output.png', help='The filename to save the generated image as.')
    parser.add_argument('-n', '--batch', type=int, default=1, help='The number of images to generate.')
    parser.add_argument('-q', '--quality', type=str, default='standard', help='The quality of the generated image.')
    parser.add_argument('-E', '--no-enhancement', action='store_true', help='Do not enhance the prompt.')
    parser.add_argument('-S', '--no-show', action='store_true', help='Do not display the image.')
    
    return parser.parse_args(argv)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if args.no_enhancement:
        args.prompt = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:" + args.prompt

    client = openai.Client(base_url='http://localhost:5005/v1', api_key='sk-ip')

    response = client.images.generate(
        prompt=args.prompt,
        response_format='b64_json',
        model=args.model,
        size=args.size,
        n=int(args.batch),
        quality=args.quality,
    )
    for n, img in enumerate(response.data):
        image = Image.open(io.BytesIO(base64.b64decode(img.b64_json)))
        if int(args.batch) > 1:
            filename = f"{args.filename.split('.')[0]}_{n}.png"
        else:
            filename = args.filename
        image.save(filename)
        print(f'Saved to {filename}')
        if not args.no_show:
            image.show()