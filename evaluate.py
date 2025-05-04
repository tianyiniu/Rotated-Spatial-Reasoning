import json, re, argparse, sys, os
from copy import deepcopy
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

ACC_DICT = {
    "cam": [], 
    "hum": [],
    "unk": [],
    "total": []
}

def extract_answer(text):
    match = re.search(r'Answer:\s*([ABCD])', text)
    return match.group(1) if match else None

def gpt_answer_match(q, model_answer):
    """Asks gpt 4o mini to select the correct option given the models response. Used as a fall-back if model does not follow output formatting instructions."""
    client = OpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
    )

    chat_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""You are an intelligent assistant that help maps student responses to choices in multiple choice question. You are given a question and a student response, and you task is to select the choice that corresponds best with the student's response. You shall respond with a SINGLE LETTER. If the student response does not match any choice, reply with 'none'. Here are some examples:
            
            Question: Are the people on the left from camera's perspective?\nA. yes\nB. no\nC. maybe\nD. unknown

            Student response: A. yes

            Answer: A

            Question: Is there a watch to the right of the mobile from camera's perspective?\nA. yes\nB. no\nC. maybe\nD. unknown

            Student response; I believe the watch is not to the right of the mobile.

            Answer: B

            Question: {q}

            Student response: {model_answer}

            Answer: """
        }]
    )
    return chat_response.choices[0].message.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_nickname")
    parser.add_argument("split")
    args = parser.parse_args()

    model_nick = args.model_nickname
    model_split = args.split
    
    if not model_split in ["dir", "cot", "mult"]:
        print("Model nickname must be dir, cot, or mult")
        sys.exit(0)

    if not model_nick in ["llava", "llama", "phi", "gpt", "gemini"]:
        print("Model nickname must be llava, llama, phi, gpt, or gemini")
        sys.exit(0)

    data_file = f"results/{model_nick}.json"

    with open(data_file, "r") as f: 
        all_data = json.load(f)

    if model_split == "dir":
        nick = f"{model_nick}"
    else: 
        nick = f"{model_nick}-{model_split}"

    degs = [0, 90, 180, 270]

    # Loop thorough prompting type and degrees 
    all_accs = {}
    model_nicknames = []
    for deg in degs: 
        model_nickname = f"{nick}-rot{deg}"
        model_nicknames.append(model_nickname)
        all_accs[model_nickname] = deepcopy(ACC_DICT)

    gpt_backoff_counter = 0
    for data in tqdm(all_data): 
        for model_nickname in model_nicknames:

            question = data["question"]
            model_res = data[model_nickname].strip()

            # First attempts to match 'Answer A/B/C/D'
            if "Answer" in model_res:
                pred = extract_answer(model_res)

            # Next try to match 'A', 'B', 'C', or 'D'
            elif len(model_res) == 1:
                pred = model_res[0]
            
            # Next try to match 'A.', 'B.', 'C.', or 'D.'
            elif len(model_res) > 1 and model_res[1] == ".":
                pred = model_res[0]

            # Final attempt, asks GPT-4o-mini to find best answer
            else:
                pred = gpt_answer_match(data["question"], model_res)
                gpt_backoff_counter += 1

                # print(repr(data[model_nickname]))
                # print(repr(pred))
                # print("HIT THREE")

                if not len(pred) == 1 and pred[0] not in "ABCD":
                    print(repr(pred))
                    pred = "A" # Default 'guess' A

            res = 1 if pred == data["answer"][0] else 0 

            all_accs[model_nickname]["total"].append(res) 

            if data["perspective"] == "camera":
                all_accs[model_nickname]["cam"].append(res)  
            elif data["perspective"] == "human":
                all_accs[model_nickname]["hum"].append(res) 
            elif data["perspective"] == "unk":
                all_accs[model_nickname]["unk"].append(res) 


    for model_nickname in all_accs:
        for cam_type in all_accs[model_nickname]:
            # print(f"{model_nickname}-{cam_type}, {len(all_accs[model_nickname][cam_type])}")
            all_accs[model_nickname][cam_type] = sum(all_accs[model_nickname][cam_type]) / len(all_accs[model_nickname][cam_type])

            print(f"{model_nickname}-{cam_type}, {round(all_accs[model_nickname][cam_type], 3)*100}")

print(f"{gpt_backoff_counter} questions used gpt-4o-mini to match answer.")