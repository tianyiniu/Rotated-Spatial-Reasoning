*All code is original.*

## Creating the dataset

### 1. Download author's original data

Refer to the original paper's [GitHub repository](https://github.com/FatemehShiri/Spatial-MM) for instruction on downloading the original data. 

Two files should be downloaded `spatial_mm_one_obj.json` and `spatial_mm_two_obj.json` from the GitHub directory. Follow the Google Drive link available to download the `Spatial_MM_Obj` folder, which contains the images referenced in the previous two json files. This project assumes the following directory setup: 
```text
.
├── README.md
├── data
│   ├── imgs
│   │   ├── 0ac1968249.jpg
│   │   └── ...
│   ├── spatial_mm_one_obj.json
│   └── spatial_mm_two_obj.json
├── create_dataset.py
├── helper.py
└── ...
```

### 2. Create filtered and rotated datasets

Simply run `create_dataset.py`, there are no flags or parameters that needs to be configured.

## Configure API keys for OpenAI and Gemini

Create a `.env` file in the root directory that contains the attributes `OPENAI_API_KEY` and `GEMINI_API_KEY` as follows: 

```text
OPENAI_API_KEY=<your api key>
GEMINI_API_KEY=<your api key>
```

## Hosting models

All local models are hosted via vLLM. Run the shell script `host_model.sh` to host Llava, Llama, or Phi by uncommenting the relevant command. Ideally, this script would be ran in a terminal multiplexer, such as `screen` or `tmux` to ensure the model remains deployed in the background.

## Running inference using direct prompting, CoT prompting

Both forms of prompting are handled by `prompt_models.py`. For convenience, `run_inference.sh` has already been setup with commands to run direct prompt and CoT prompting with all five models - simply undo the commenting for the desired option and run the bash script. 

## Running inference using multi-step prompting

Currently, `prompt_models.py`does not support multi-step prompting. This method is instead handled by `run_multistep.py` and `run_gemini_multistep.py` (Gemini does not use the OpenAI API, I have yet to unify the two files). Before executing the script, follow the TODOs in the file to configure the relevant flags.

## Running evaluation
`evaluate.py` is responsible for obatining the accuracy metrics. It takes command line unnamed arguments `model_name` (chosen among `llava, llama, phi, gpt, gemini`) and `prompting_method` (chosen among `dir, cot, mult`). If wished to evaluate Llava with CoT prompting, I would run `python evaluate.py llava dir`. 

## Other files

`prompts.py` includes the prompts for the different forms of prompting described. `helper.py` includes some helper functions that is shared across the other python files. `create_zip_file.sh` creates a zipped folder of this project directory, excluding the .env file and the images directories. `./chat_templates` contains the chat template for Llava used by vLLM. 
