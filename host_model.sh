# CUDA_VISIBLE_DEVICES=7 VLLM_USE_V1=1 vllm serve llava-hf/llava-1.5-7b-hf --trust-remote-code --host localhost --port 7471 --download-dir /playpen-ssd/pretrained_models  --chat-template chat_templates/llava.jinja

# CUDA_VISIBLE_DEVICES=4,5,6,7 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True vllm serve meta-llama/Llama-3.2-11B-Vision-Instruct --trust-remote-code --host localhost --port 7472 --download-dir /playpen-ssd/pretrained_models --tensor-parallel-size 4 --max-model-len 8192 --max-num-batched-tokens 8192 --max-num-seqs 32 --disable-custom-all-reduce

CUDA_VISIBLE_DEVICES=6,7 vllm serve meta-llama/Llama-3.2-11B-Vision-Instruct --trust-remote-code --host localhost --port 7473 --download-dir /playpen-ssd/pretrained_models --tensor-parallel-size 2 --max-model-len 8192 --max-num-batched-tokens 8192 --max-num-seqs 32

# CUDA_VISIBLE_DEVICES=7 vllm serve microsoft/Phi-3.5-vision-instruct --trust-remote-code --host localhost --port 7473 --download-dir /playpen-ssd/pretrained_models --max-model-len 30000

# CUDA_VISIBLE_DEVICES=5 vllm serve Qwen/Qwen2.5-VL-7B-Instruct --trust-remote-code --host localhost --port 7473 --download-dir /playpen-ssd/pretrained_models --max-model-len 30000