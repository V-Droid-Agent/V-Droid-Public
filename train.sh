deepspeed \
  --num_gpus=1 \
  train/train.py \
  -s VDroid_train_demo \
  --lora_rank 16 \
  --model "Llama-31-8B" \
  --train_type p3_training \
  --reward_type score \
  --train_batch_size 8 \
  --nnodes=1
