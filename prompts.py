def get_system_prompt():
    return "You are an intelligent AI assistant that specializes in understanding orientation-aware semantic spatial relationships in images. Keep in mind that an orientation-aware semantic spatial relationship does not change if an image is rotated."

def get_direct_prompt(q):
    return f"""Respond to the following question with a SINGLE letter, indicating the correct choice. Keep in mind the image you are given may be rotated. Your response should identify the correct rotation, and must not change for different degrees of rotation.  

    Question: {q}

    Answer: """

def get_cot_prompt(q):
    return f"""Carefully analyze the image, using context clues to determine its correct orientation, and respond to the question. Think step-by-step:

    Question: {q}\n\n"""

def get_rotation_prompt():
    return """Analyze the image carefully and determine if it appears to be rotated 0, 90, 180, or 270 degrees from its correct orientation. Answer with a single number from 1-360: """

def get_rotation_follow_up_prompt(q):
    return f"""Taking into account the rotation you've identified earlier, carefully analyze the image and respond to the question. Think step-by-step. Format your final answer as 'Answer: [A/B/C/D]'.
    
    Question: {q}\n\n"""