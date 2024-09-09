# OpenedAI Images Flux

## Configuration

All of the configuration settings are stored in the `config/` folder, and can (mostly*) be modified as needed without needing to restart the server.

`config.json` is the primary configuration file, it contains the mapping of `model` to `generator` and `enhancer` configurations. A new `config.json` will be created if one doesn't exist already.

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

The default `config.default.json` provided is much more robust with many more options available.

### Generator JSON Configuration

Generation parameters can be set with `quality` and is completely configurable and can be anything want, the `standard` and `hd` settings are available in the OpenAI API, but you can use whatever you want.

Sample Generator JSON:

```json
{
  "pipeline": {
    "pretrained_model_name_or_path": "black-forest-labs/FLUX.1-dev",
    "torch_dtype": "bfloat16"
  },
  "options": {
    "compile": ["transformer", "vae"],
    "enable_sequential_cpu_offload": false,
    "enable_model_cpu_offload": false,
    "enable_vae_slicing": false,
    "enable_vae_tiling": false,
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

The format is very flexible and many entries are not pre-defined but are used as keywords in API calls to `diffusers` python objects.

The `compile` option can accept a list of components to compile (`["transformer", "vae"]`), compiling can take a while, but the performance improvements may be worth while. In my tests it can take almost 10 minutes before the first image is ready, and images generated approximately 10-20% faster after that.

#### Local model files

Here is another sample of how to use local model files with a fine-tune without downloading from huggingface:

```json
{
  "pipeline": {
    "pretrained_model_name_or_path": "./models/black-forest-labs/FLUX.1-dev",
    "torch_dtype": "bfloat16",
    "FluxTransformer2DModel": {
      "pretrained_model_link_or_path_or_dict": "./models/STOIQONewrealityFLUXSD_F1DPreAlpha.safetensors",
      "torch_dtype": "bfloat16"
    }
  },
  "options": {
    "to": {
      "device": "cuda"
    }
  },
  "generation_kwargs": {
    "guidance_scale": 3.5,
    "num_inference_steps": 50
  }
}
```

#### Lora Configuration

Multiple lora can be added in a list, with individual scaling factor (`lora_scale`), which is used when fusing lora with the main model.

Sample Lora config:

```json
{
  "pipeline": {
    "pretrained_model_name_or_path": "black-forest-labs/FLUX.1-dev",
    "torch_dtype": "bfloat16",
    "Loras": [
      {
        "weights": {
          "pretrained_model_name_or_path_or_dict": "./lora",
          "weight_name": "some_lora_file_1.safetensors"
        },
        "lora_scale": 0.8
      },
      {
        "weights": {
          "pretrained_model_name_or_path_or_dict": "./lora",
          "weight_name": "some_other_lora_file_2.safetensors"
        },
        "lora_scale": 1.0
      }
    ]
  },
  "options": {
    "enable_sequential_cpu_offload": true,
    "to": {
      "device": "cuda"
    }
  },
  "generation_kwargs": {
    "guidance_scale": 3.5,
    "num_inference_steps": 50
  }
}
```

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

There are 2 pre-configured rule based openai enhancers, `openai-enhancer.json` which contains some additional safety features, and `openai-enhancer-research.json` which is for scientists. Sometimes it's a stunning difference, but they don't always work perfectly. The results are highly dependent on the quality of the chat model you use, so feel free to create your own and experiment.

You may also find that FLUX.1 performs very well with no prompt enhancement at all.

