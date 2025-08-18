# DNAGPT

This directory provides an adaptation of [TencentAILabHealthcare/DNAGPT](https://github.com/TencentAILabHealthcare/DNAGPT) to fit the specific task, data and taxonomy constraints of this study.

## Getting Started

### Download pre-trained weights

* [dna_gpt0.1b_m.pth](https://drive.google.com/file/d/1C0BRXfz7RNtCSjSY1dKQeR1yP7I3wTyx/view?usp=drive_link): DNAGPT 0.1B params model pretrained with mutli-organism genomes

## Python Virtual Environment Setup

Python environnment is the same as DNABERT2. 
We can reuse it or create a new one with the same steps.

## Execution

To finetune DNAGPT on this study’s dataset (4 markers and 6 folds), run:

```bash
python main.py
```

### Citation

**DNAGPT**

```
@article{zhang2023dnagpt,
  title={DNAGPT: A Generalized Pretrained Tool for Multiple DNA Sequence Analysis Tasks},
  author={Zhang, Daoan and Zhang, Weitong and He, Bing and Zhang, Jianguo and Qin, Chenchen and Yao, Jianhua},
  journal={bioRxiv},
  pages={2023--07},
  year={2023},
  publisher={Cold Spring Harbor Laboratory}
}
```



