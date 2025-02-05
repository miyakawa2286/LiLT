import argparse
import json
import os
import shutil

import torch

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--lilt", type=str, required=True, help="Path to LiLT model.")
    parser.add_argument("--text", type=str, required=True, help="Path to text model.")
    parser.add_argument("--config", type=str, required=True, help="Path to text config.")
    parser.add_argument("--out", type=str, required=True, help="Path to output.")
    opt = parser.parse_args()

    with open(opt.config, "r") as jf:
        config = json.load(jf)
    config["channel_shrink_ratio"] = 4
    config["max_2d_position_embeddings"] = 1024
    # NOTE: not overwrite parameter, failed to build tokenizer instance.
    # config['model_type'] = 'liltrobertalike'

    if not os.path.isdir(opt.out):
        os.makedirs(opt.out)
    with open(os.path.join(opt.out, "config.json"), "w") as jf:
        json.dump(
            config,
            jf,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
        )

    text_model = torch.load(opt.text)
    text_model = {k.replace("roberta.", "lilt."): v for (k, v) in text_model.items()}
    lilt_model = torch.load(opt.lilt)
    total_model = {**text_model, **lilt_model}
    torch.save(total_model, os.path.join(opt.out, "pytorch_model.bin"))

    # NOTE: also save tokenizer config file, needed to build tokenizer instance.
    tokenizer_config_name = "tokenizer.json"
    tokenizer_config_path = opt.config.replace("/config.json", f"/{tokenizer_config_name}")
    shutil.copy(tokenizer_config_path, os.path.join(opt.out, tokenizer_config_name))
