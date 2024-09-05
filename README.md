# OpenedAI Images Flux

![A banner style logo for the website of the OpenedAI Images Flux, an OpenAI API Image generator server which uses the Black Forest Labs FLUX.1 model.](logo.png)


## Overview

An OpenAI API compatible image generation server for the FLUX.1 family of models from [Black Forest Labs](https://huggingface.co/black-forest-labs)

> Not affiliated with OpenAI in any way, and no OpenAI API key is required.

## Features

- **Open Source**: The entire project is open source, allowing for transparency and customization
- **Compatibility**: Use it with [Open WebUI](https://openwebui.com/), or any other OpenAI API compatible images (dall-e) client
- **Custom Models**: Ready to use support for custom models, merges and quantizations (qfloat8 only so far)
- **Flexible**: Configurable settings for different models and enhancements
- **Enhancements**: Supports flexible AI prompt enhancers
- **Standalone Image Generation**: Uses your Nvidia GPU for image generation, doesn't use ComfyUI, SwarmUI or any other backend
- [ ] **Easy to setup and use**: Maybe?
- [ ] **Lora Support** (planned)
- [ ] **Upscaler Support** (planned)
- [ ] **BNB NF4 Quantization** (planned)
- [ ] **GGUF Loading** (planned)


## Quickstart

> This is brand new software, if you find any problems or have suggestions please open a [new issue](https://githib.com/matatonic/openedai-images-flux/issues) on GitHub!

> The defaults use the full FP16 FLUX.1 Schnell and Dev models for `dall-e-2` and `dall-e-3` and require approximately 40GB of VRAM, but much more memory friendly options are available by default, and can be easily changed to be the defaults for `dall-e-2/3` if desired. See [Model Configuration](#model_configuration) for details.


> black-forest-labs/FLUX.1 models are gated, you must request access, and you must set a HuggingFace token to access them.

### 1. Configure your `images.env` environment file:

Start by copying the `sample.env` file to `images.env`:
```shell
$ cp sample.env images.env
```

Edit `images.env` to set your API keys and any other environment settings you want, such as your huggingface token.
```
# Optional, but required for prompt enhancement, can be a local OpenAI API compatible server
OPENAI_BASE_URL=<http your openai chat server>:<port>/v1
OPENAI_API_KEY=sk-ip
# required for access to gated models
HF_TOKEN=XXXXXXX
```

### 2. Installation

Choose an installation option.

#### A. Docker (**recommended**, tested):
```shell
$ docker compose up -d
```

> Linux: Make sure your docker runtime supports the nvidia container toolkit

> Windows: Make sure docker is setup to use WSL2 and up-to-date Nvidia drivers are installed

#### B. Manual Install
```shell
# create an use a virtual env (venv) - optional
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python images.py
```

### 3. Usage

Most API usage is identical to OpenAI's API, but you can also use any OpenAI API compatible client.

For example, it's simple to use with Open WebUI. Here is a screenshot of the config:

`Open WebUI > Admin Panel > Settings > Images > OpenAI API Config`
![Open WebUI / Admin Panel / Settings / Images / OpenAI API Config](open-webui-config.png)


## API Guides & Documentation (from OpenAI)

- OpenAI Images Guide: (https://platform.openai.com/docs/guides/moderation)
- OpenAI Images API Reference: (https://platform.openai.com/docs/api-reference/moderations)

### API Compatibility
- [x] generations
- - [x] prompt
- - [x] model (whatever you configure, `dall-e-2` by default)
- - [x] size (anything that works with flux, `1024x1024` by default)
- - [X] quality (whatever you want, `standard` by default)
- - [x] response_format (`b64_json` preffered, `url` will use `data:` uri's)
- - [x] n
- - [ ] style (`vivid` by default) (currently ignored)
- - [ ] user (ignored)
- [ ] edits
- [ ] variations

## Python Client

You can use the OpenAI python client to interact with the API. A sample application, `generate.py` is included.

```shell
pip install -U openai
python generate.py -m dall-e-3 -s "1024x256" -f new_logo.png "A banner style logo for the website of the OpenedAI Images Flux, an OpenAI API Image generator server which uses the Black Forest Labs FLUX.1 model."
```

See the OpenAI Images Guide API and API Documentation for more ways to use the API.

## Configuration

All of the configuration settings are stored in the `config/` folder, and can (mostly*) be modified as needed without needing to restart the server.

`config.json` is the primary configuration file, it contains the mapping of `model` to `generator` and `enhancer` configurations.

A basic `config.json` might look like this:
```json
{
  "models": {
    "dall-e-2": {
      "generator": "flux.1-schnell.json"
    },
    "dall-e-3": {
      "generator": "flux.1-dev.json",
      "enhancer": "openai-enhancer.json"
    }
}
```

The default `config.json` provided is much more robust with many more options available.

### Generator JSON Configuration

Generation parameters can be set with `quality` and is completely configurable and can be anything want, the `standard` and `hd` settings are available in the OpenAI API, but you can use whatever you want.

```json
{
  "pipeline": {
    "pretrained_model_name_or_path": "black-forest-labs/FLUX.1-dev",
    "torch_dtype": "bfloat16"
  },
  "options": {
    "enable_sequential_cpu_offload": false,
    "to": {
      "device": "cuda"
    }
  },
  "generation_kwargs": {
    "standard": {
      "guidance_scale": 3.5,
      "num_inference_steps": 25
    },
    "hd": {
      "guidance_scale": 5.5,
      "num_inference_steps": 50
    }
  }
}

```

The format is very flexible and many entries are not pre-defined but are used as is in API calls to `diffusers` python objects.

### Enhancer JSON Configuration

Enhancers are optional but provide additional functionality to improve image quality and creativity. They depend on an OpenAI chat API.

A simple `enhancer.json` may look like this (examples tend to work well):
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are an AI prompt enhancer for image generation AI models, when given a description of an image, be creative and enhance the description to make the image better. No yapping, just output the best enhanced image prompt you can."},
    {"role": "user", "content": "photo of an ancient castle very atmospheric"},
    {"role": "assistant", "content": "photo of an ancient castle with a majestic, eerie ambiance, highlighting its towering spires, weathered stone, and ivy-clad walls, set against a backdrop of a dense, mystic forest under a sky completely shrouded in clouds yet illuminated by a diffused, ethereal light, where the fusion of natural decay and enduring architectural grandeur evokes a sense of timeless mystery and the eternal battle between man and nature, casting a glow that reveals subtle details and textures, creating an impression of haunting beauty and solemn tranquility. "},
    {"role": "user", "content": "photo of a futuristic cityscape with flying cars"},
    {"role": "assistant", "content": " A bustling futuristic cityscape stretches out beneath a twilight sky, where sleek, metallic skyscrapers pierce through wisps of neon-lit clouds. Flying cars, adorned with glowing blue and purple lights, zip silently along invisible aerial highways, casting dynamic shadows on the glassy surfaces below. The city’s architecture blends organic curves with sharp geometric lines, creating a harmonious fusion of nature and technology. Holographic billboards flicker with vibrant advertisements, while pedestrians in streamlined attire stroll along elevated walkways lined with lush vertical gardens. The scene is bathed in a soft, ethereal glow from the setting sun, reflecting off the polished surfaces and adding a warm contrast to the cool artificial lights. The composition captures the city from a bird’s-eye view, showcasing its intricate layout and futuristic charm, evoking a sense of wonder and technological advancement."}
  ],
  "temperature": 1.0,
  "max_tokens": 256
}
```

There are 2 pre-configured rule based openai enhancers, `openai-enhancer.json` which contains some additional safety features, and `openai-enhancer-research.json` which is for scientists. They don't always work well, and the results are highly dependent on the quality of the chat model you use, so feel free to create your own and experiment.

You may also find that FLUX.1 performs very well with no prompt enhancement at all.

## Additional Pre-Configured models

> FP8 is the only available quantization so far, but more will come soon!

> There are other options available for low GPU VRAM support

Additional models are also available by default, there are option for all type of GPU setups.

* Only one model can be loaded at a time, and models are loaded on demand.

By default, the following models are configured (require ~40GB VRAM, bfloat16, <1s/step):

- `schnell`: `flux.1-schnell.json` FLUX.1 Schnell (official) (4 step, ~3s)
- `dev`: FLUX.1 Dev (without enhancement) (25/50 steps, ~15-30s)
- `merged`: `sayakpaul-flux.1-merged.json` Dev+Schnell merged, 12 steps
- `dall-e-2` is set to use `shnell`
- `dall-e-3` is set to use `dev`, with prompt enhancement if an openai chat API is available.

Additional FP8 models (require ~24GB VRAM and can be slow to load, `+enable_vae_slicing`, `+enable_vae_tiling`, ~3+s/step):

- `schnell-fp8`: `kijai-flux.1-schnell-fp8.json` Scnhell with FP8 quantization (slow to load), 4 steps (10-15s)
- `dev-fp8`: `kijai-flux.1-dev-fp8.json` Dev with FP8 quantization (slow to load), 25/50 steps
- `merged-fp8`: `drbaph-flux.1-merged-fp8.json` Dev+Schnell merged, FP8 quantization, 12 steps by default
- `merged-fp8-4step`: `drbaph-flux.1-merged-fp8-4step.json` Dev+Schnell merged, FP8 quantization, 4 steps

Additional FP8 models (require ~16GB VRAM and can be slow to load, `+enable_model_cpu_offload`, ~5+s/step):

- `schnell-fp8-16G`: `kijai-flux.1-schnell-fp8-16G.json` Scnhell, 4 steps (~15-30s)
- `dev-fp8-16G`: `kijai-flux.1-dev-fp8-16G.json` Dev, 25 steps for `standard`, 50 for `hd`
- `merged-fp8-4step-16G`: `drbaph-flux.1-merged-fp8-4step-16G.json` Dev+Schnell merged, 4 steps
- `merged-fp8-16G`: `drbaph-flux.1-merged-fp8-16G.json` Dev+Schnell merged, 12 steps by default

Low VRAM options (<4GB VRAM, ~32GB RAM, `+enable_sequential_cpu_offload`, float16 instead of bfloat16, 8-15+s/step):

- `schnell-low`: `flux.1-schnell-low.json` Schnell FP16, (30-60s per image)
- `dev-low`: `flux.1-dev-low.json` Dev FP16, at least a few minutes per image
- `merged-low`: `sayakpaul-flux.1-merged-low.json` Dev+Schnell FP16 merged, 12 steps by default


> Timings are measured at 1024x1024 on an Nvidia A100 and may vary wildly from your system.

> \*) The name of the generator file is used to determine if a model is already loaded or not, if you edit a generator config in a way which requires reloading the model (such as changing `pipeline` or `options`), it wont reload it automatically. `config.json` and `generation_kwargs` will always be loaded each API call.


## Server Usage

```pre
usage: images.py [-h] [-C CONFIG] [-S SEED] [-L {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-P PORT] [-H HOST]

OpenedAI Images Flux API Server

options:
  -h, --help            show this help message and exit
  -C CONFIG, --config CONFIG
                        Path to the config.json config file (default: config/config.json)
  -S SEED, --seed SEED  The random seed to set for all generations. (default is random) (default: None)
  -L {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the log level (default: INFO)
  -P PORT, --port PORT  Server tcp port (default: 5005)
  -H HOST, --host HOST  Host to listen on, Ex. 0.0.0.0 (default: 0.0.0.0)
```


# Troubleshooting and FAQ

#### "The following part of your input was truncated because CLIP can only handle sequences up to 77 tokens:"

* Long prompt encoding into CLIP is not yet supported (not working), all is not lost however, there are 2 encoders and the T5 encoder (text_encoder_2) supports up to 240 (?) tokens. No fix yet.

#### "that cleft chin woman", "everyone is too beautiful"

* no fix, but lora support is coming.

#### There are no protections for simultaneous users or requests

* concurrent requests may behave the unexpected ways

# Additional Links and References

[Black Forest Labs](https://blackforestlabs.ai/)
- [FLUX.1 Announcement Blog Post](https://blackforestlabs.ai/announcing-black-forest-labs/)
- [Black Forest Labs on Huggingface](https://huggingface.co/black-forest-labs)
- [FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
- [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)

Additional Model formats and merges created by:

- [@drbaph](https://huggingface.co/drbaph/), [@Kijai](https://huggingface.co/Kijai/), [@sayakpaul](https://huggingface.co/sayakpaul/)

# License Information

- OpenedAI Images FLux is released under the [GNU Affero General Public License v3.0](https://choosealicense.com/licenses/agpl-3.0/)
- [FLUX.1 \[dev\] Non-Commercial License.](https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md)
- [FLUX.1 \[schnell\] is Released under the apache-2.0 licence, the model can be used for personal, scientific, and commercial purposes.](https://choosealicense.com/licenses/apache-2.0/)