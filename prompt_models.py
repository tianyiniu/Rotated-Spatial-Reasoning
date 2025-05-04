import os, json, argparse, shutil, base64, random, argparse
import PIL.Image
from tqdm import tqdm
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
load_dotenv()

from helper import *
from prompts import *


def format_messages(prompt, encoded_img, model_name):
    sys_prompt = get_system_prompt()
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_img}"}},
            {"type": "text", "text": prompt}
        ]}
    ]
    return messages


def get_response(prompt, encoded_img, model_name, client, img_path=None):
    sys_prompt = get_system_prompt()
    if "gemini" in model_name.lower():
        image = PIL.Image.open(img_path)
        combined_prompt = format_messages(prompt, encoded_img, model_name)
        response = client.models.generate_content(
            model=model_name,
            contents=[combined_prompt, image]
        )
        response_text = response.text
        prompt_tokens = response.usage_metadata.prompt_token_count
        completion_tokens = response.usage_metadata.candidates_token_count
    else:
        chat_response = client.chat.completions.create(
                model=model_name,
                messages=format_messages(prompt, encoded_img, model_name)
        )
        response_text = chat_response.choices[0].message.content
        prompt_tokens = chat_response.usage.prompt_tokens
        completion_tokens = chat_response.usage.completion_tokens
    return response_text, prompt_tokens, completion_tokens


def get_question_answer(question_json, model_name, model_nickname, client, rotation=0, use_cot=False):
    q = question_json["question"]

    if use_cot:
        prompt = get_cot_prompt(q)
    else: 
        prompt = get_direct_prompt(q)

    if rotation == 0:
        img_path = f"data/filtered_imgs/{question_json["image_name"]}"
    elif rotation == 90:
        img_path = f"data/rotate90_imgs/{question_json["image_name"]}"
    elif rotation == 180:
        img_path = f"data/rotate180_imgs/{question_json["image_name"]}"  
    elif rotation == 270:
        img_path = f"data/rotate270_imgs/{question_json["image_name"]}"   
    else:
        assert 0 == 1   

    encoded_img = encode_image(img_path)
    
    ans, prompt_tk, completion_tk = get_response(prompt, encoded_img, model_name, client, img_path=img_path)
    question_json[model_nickname] = ans
    return question_json, prompt_tk, completion_tk


if __name__ == "__main__":
    # TODO change model name and nickname
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", help="Model name")
    parser.add_argument("--model_nickname", help="Model nickname")
    parser.add_argument("--port", help="Port the model is hosted on", type=int)
    parser.add_argument("--max_workers", help="Number of workers for multithreading", type=int)

    args = parser.parse_args()
    model_name = args.model_name
    nick = args.model_nickname
    port = args.port
    max_workers = args.max_workers

    if "-" in nick:
        output_base = nick.split("-")[0]
    else: 
        output_base = nick 

    # input_json = f"results/{output_base}.json"
    input_json = f"data/filtered_dataset.json"
    output_json = f"results/{output_base}.json"

    use_cot = True if "cot" in nick else False

    base_url = "https://api.openai.com/v1" if "gpt" in model_name.lower() else f"http://localhost:{port}/v1"
    client = OpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        base_url = base_url
    )

    if input_json != output_json:
        shutil.copy2(input_json, output_json)

    for deg in [0, 90, 180, 270]:
        rotation_degrees = deg
        model_nickname = f"{nick}-rot{rotation_degrees}"

        with open(output_json, "r", encoding="utf-8") as f:
            all_data = json.load(f)

        total_prompt_tk = 0
        total_completion_tk = 0
        L_out = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {executor.submit(get_question_answer, question_json, model_name,  model_nickname, client, rotation=rotation_degrees, use_cot=use_cot): question_json for question_json in all_data}

            for future in tqdm(as_completed(future_to_item), total=len(future_to_item)):
                result = future.result()
                if result:
                    L_out.append(result)


        updated_q_jsons = []
        for (updated_q_json, prompt_tk, completion_tk) in L_out:
            updated_q_jsons.append(updated_q_json)
            total_completion_tk += completion_tk
            total_prompt_tk += prompt_tk


        print(f"Completed {deg} rotation inference")
        print(f"Total prompt tokens: {total_prompt_tk}; total completion tokens: {total_completion_tk}")

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(updated_q_jsons, f, indent=4, ensure_ascii=False)