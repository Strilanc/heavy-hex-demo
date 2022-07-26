#!/bin/bash

sinter collect \
    --circuits out/circuits/* \
    --decoders pymatching \
    --processes 4 \
    --max_shots 100_000 \
    --max_errors 100 \
    --save_resume_filepath out/stats.csv \
    --metadata_func "sinter.comma_separated_key_values(path)"
