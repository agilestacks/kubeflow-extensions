#!/usr/bin/env python
'''
Preprocess for deep learning

usage example:
    preproc.py \
            --input_traindf_csv=data-sample.csv \
            --output_body_preprocessor_dpkl=body_preprocessor.dpkl \
            --output_title_preprocessor_dpkl=title_preprocessor.dpkl \
            --output_train_title_vecs_npy=train_title_vecs.npy \
            --output_train_body_vecs_npy=train_body_vecs.npy
'''
import os
import logging
import pandas as pd
from ktext.preprocess import processor
from sklearn.model_selection import train_test_split
import argparse

import dill as dpickle
import numpy as np
from textacy.preprocess import preprocess_text

from utils import (save_text, save_list)

def textacy_cleaner(text: str) -> str:
    if isinstance(text, (int, float, complex)):
        # workaround module not found error if inside model
        import numpy, logging
        if numpy.isnan(text):
            logging.warning("Received nan instead of str")
            return "nan"

    from textacy.preprocess import preprocess_text
    return preprocess_text(
        text,
        fix_unicode=False,
        lowercase=True,
        transliterate=True,
        no_urls=True,
        no_emails=True,
        no_phone_numbers=True,
        no_numbers=True,
        no_currency_symbols=True,
        no_punct=True,
        no_contractions=False,
        no_accents=True)


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# Parsing flags.
parser = argparse.ArgumentParser()
parser.add_argument("--input_traindf_csv")
parser.add_argument("--output_body_preprocessor_dpkl")
parser.add_argument("--output_title_preprocessor_dpkl")
parser.add_argument("--output_train_title_vecs_npy")
parser.add_argument("--output_train_body_vecs_npy")
args = parser.parse_args()

# Read data.
traindf = pd.read_csv(
    args.input_traindf_csv,
    dtype={"issue_url": str, "issue_title": str, "body": str},
    na_values=["", None, "nan", np.nan],
)
traindf.dropna(inplace=True)

train_body_raw = traindf.body.tolist()
train_title_raw = traindf.issue_title.tolist()

# Clean, tokenize, and apply padding / truncating such that each document
# length = 70. Also, retain only the top 8,000 words in the vocabulary and set
# the remaining words to 1 which will become common index for rare words.
body_pp = processor(keep_n=8000, padding_maxlen=70)
body_pp.set_cleaner(textacy_cleaner)
train_body_vecs = body_pp.fit_transform(train_body_raw)

print('Example original body:', train_body_raw[0])
print('Example body after pre-processing:', train_body_vecs[0])

# Instantiate a text processor for the titles, with some different parameters.
title_pp = processor(append_indicators=True, keep_n=4500,
                     padding_maxlen=12, padding='post')
title_pp.set_cleaner(textacy_cleaner)

# process the title data
train_title_vecs = title_pp.fit_transform(train_title_raw)

print('Example original title:', train_title_raw[0])
print('Example title after pre-processing:', train_title_vecs[0])

save_text("/tmp/train_title_raw.txt", train_title_raw[0])
save_text("/tmp/train_body_raw.txt", train_body_raw[0])
save_list("/tmp/train_title_vecs.txt", train_title_vecs[0])
save_list("/tmp/train_body_vecs.txt", train_body_vecs[0])

# Save the preprocessor.
with open(args.output_body_preprocessor_dpkl, 'wb') as f:
    dpickle.dump(body_pp, f)

with open(args.output_title_preprocessor_dpkl, 'wb') as f:
    dpickle.dump(title_pp, f)

# Save the processed data.
np.save(args.output_train_title_vecs_npy, train_title_vecs)
np.save(args.output_train_body_vecs_npy, train_body_vecs)
