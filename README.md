# Vastu-Compliant Floor Plan Generator (Enhanced ChatHouseDiffusion)

This project enhances the `ChatHouseDiffusion` model with a **Vastu Shastra Retrieval-Augmented Generation (RAG)** pipeline. It leverages a local Large Language Model (Llama 3) to intelligently generate and edit room plans that are not only responsive to user prompts but also strictly adhere to the ancient architectural principles of Vastu Shastra.

<img src="2bedroom.jfif" width="70%" alt="demo image">
<img src="2bedroom2.jfif" width="70%" alt="demo image">

The system intelligently corrects user inputs that conflict with Vastu rules, provides a real-time explanation of the principles applied, and allows for easy drawing of house outlines.

## Features
- **Text-to-Floor-Plan Generation:** Create floor plans from simple natural language descriptions.
- **Vastu-Compliant by Design:** Integrates a Vastu Shastra knowledge base to ensure all generated layouts are harmonious and architecturally sound.
- **Intelligent Correction:** Automatically overrides user requests that conflict with core Vastu principles.
- **Real-time Explanation:** Displays a user-friendly explanation of the Vastu logic applied to the design.
- **Intuitive UI:** A Tkinter-based user interface with dedicated modes for drawing lines and easy-to-draw rectangles.

## Quick Start

This environment has been tested and works on Windows 10/11 with Python 3.10+.

### 1. Prerequisites: Install Ollama
This project uses a local LLM served by [Ollama](https://ollama.com/).
1.  Download and install Ollama.
2.  Open your terminal and pull the Llama 3 model:
    ```shell
    ollama pull llama3
    ```
    Ollama will now run in the background, ready to serve the model.



### 2. Install Python Packages
Clone this repository and install the required packages.
```shell
pip install -r requirements.txt
```
### Citation

This project is based on [ChatHouseDiffusion](https://arxiv.org/abs/2410.11908). If you use this code or build upon it, please cite the original authors:

```bibtex
@misc{qin2024chathousediffusionpromptguidedgenerationediting,
  title={ChatHouseDiffusion: Prompt-Guided Generation and Editing of Floor Plans}, 
  author={Sizhong Qin and Chengyu He and Qiaoyun Chen and Sen Yang and Wenjie Liao and Yi Gu and Xinzheng Lu},
  year={2024},
  eprint={2410.11908},
  archivePrefix={arXiv},
  primaryClass={cs.HC},
  url={https://arxiv.org/abs/2410.11908}, 
}
```
