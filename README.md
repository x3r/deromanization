# Deromanization of code-mixed texts
An approach for deromanizing code-mixed texts using language identification, back-transliteration and sequence prediction.

This repository also contains manually annotated data for transliteration (**data/bengali-annotated-transliteration.txt**).

## Word Sequence Prediction
**Input:** (Please follow the file formats in **data/sample/**)
* Language labels
* N-best transliteration lists with scores
* Word-level language model
* Test sentences

**Output:** Deromanized sentences

**Usage:**

'''

python sequence_prediction.py [-h] -d DTLM -s SEQ -n NMT -w LM -l LID -t TEST [-o OUTPUT]

'''

**optional arguments:**

  -h, --help            show this help message and exit
  
  -o OUTPUT, --output OUTPUT  output file name

**required named arguments:**

  -d DTLM, --dtlm DTLM  dtlm predictions

  -s SEQ, --seq SEQ     sequitur predictions

  -n NMT, --nmt NMT     nmt predictions

  -w LM, --lm LM        word-level language model

  -l LID, --lid LID     language labels

  -t TEST, --test TEST  test file name

For any issues, please contact: riyadh[AT]ualberta[DOT]ca.
