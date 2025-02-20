[//]: # (# ⚔🛡 Security Threats and Protections for Neural Code Models &#40;NCMs&#41;)
# ⚔🛡 Security of Language Models for Code

This repository provides a summary of recent advancements in the security landscape surrounding Language Models for Code (also known as Neural Code Models), including backdoor, adversarial attacks, corresponding defenses and so on.

**NOTE: We collect the original code from the papers and the code we have reproduced. While, our reproduced code is not guaranteed to be fully accurate and is for reference only. For specific issues, please consult the original authors.**

[//]: # (The bolded article is published by our Nanjing University ISE Lab.)

[![arXiv](https://img.shields.io/badge/arXiv-2410.15631-b31b1b.svg)](https://arxiv.org/abs/2410.15631)
![GitHub stars](https://img.shields.io/github/stars/wssun/TiSE-LM4Code-Security?color=yellow&label=Stars)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

[//]: # ([![Awesome]&#40;./figures/logo.svg&#41;]&#40;https://github.com/xxxx&#41;)

## Overview

Language Models for Code (CodeLMs) have significantly advanced code-related tasks, they are excel in programming language understanding and generation.
Despite their success, CodeLMs are prone to security vulnerabilities, which have become a growing concern.
While existing research has explored various attacks and defenses for CodeLMs. 
To address a systematic review of CodeLM security, this repository organizes the current knowledge on **Security Threats** and **Defense Strategies**.

## Table of Contents

[//]: # (- [📃Survey]&#40;#survey&#41;)
- [📃Survey](#surveies)
- [⚔Security Threats](#security-threats)
  - [Backdoor Attacks](#backdoor-attacks)
  - [Adversarial Attacks](#adversarial-attacks)
- [🛡Defensive Strategies](#defensive-strategies)
  - [Backdoor Defense](#backdoor-defense)
  - [Adversarial Defense](#adversarial-defense)
- [Citation](#citation)

**NOTE: Our paper is labeled with 🚩.**


[//]: # (## Introduction)

[//]: # (Our survey focuses on analyzing **backdoor attacks** and **adversarial attacks** in NCMs, categorizing existing research into different attack vectors and examining their implications on security in software engineering tasks. The review covers both **experimental frameworks** and the **metrics** used for evaluating security risks and attack performance on NCMs.)

[//]: # ()
[//]: # (### Key Contributions:)

[//]: # (- A detailed categorization of attacks on **Neural Code Models &#40;NCMs&#41;**.)

[//]: # (- Review of **experimental setups**, including datasets and metrics used in NCM security research.)
  
[//]: # (- Insights into the challenges posed by these attacks and opportunities for **future research**.)

## 📃Survey
[//]: # (The threats discussed in the survey are divided into three main categories:)
The survey analyzes security threats to CodeLMs, categorizing existing attack types such as backdoor and adversarial attacks, and explores their implications for code intelligence tasks.

| Year | Conf./Jour. | Paper                                                                                                                                                                   |   
|------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2024 | CoRR        | [Security of Language Models for Code: A Systematic Literature Review](./papers_en/2024-CoRR-Security_of_CodeLMs.pdf)   🚩                                                       |
| 2024 | 《软件学报》      | [深度代码模型安全综述](./papers_cn/2024-软件学报-深度代码模型安全综述.pdf)   🚩                                                                                                                 |
| 2024 | CoRR        | [Robustness, Security, Privacy, Explainability, Efficiency, and Usability of Large Language Models for Code.](./papers_en/2024-CoRR-Large_Language_Models_for_Code.pdf) |
| 2023 | CoRR        | [A Survey of Trojans in Neural Models of Source Code: Taxonomy and Techniques.](./papers_en/2023-CoRR-Taxonomy_and_Techniques.pdf)                                      |


## ⚔Security Threats
[//]: # (The threats discussed in the survey are divided into three main categories:)
According to the document, security threats in CodeLMs are mainly classified into two categories: backdoor attacks and adversarial attacks. Backdoor attacks occur during the training phase, where attackers implant hidden backdoors in the model, allowing it to function normally on benign inputs but behave maliciously when triggered by specific patterns. In contrast, adversarial attacks happen during the testing phase, where carefully crafted perturbations are added to the input, causing the model to make incorrect predictions with high confidence while remaining undetectable to humans.

<img src="./figures/overview.png" alt="An overview of attacks in CodeLMs." width="1000"/>

### Backdoor Attacks
Backdoor attacks inject malicious behavior into the model during training, allowing the attacker to trigger it at inference time using specific triggers:
- **Data poisoning attacks**: Slight changes to the training data that cause backdoor behavior.


| Year | Conf./Jour.     | Paper                                                                                                                                                   | Code Repository                                                                                          | Reproduced Repository |    
|------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|-----------------------|
| 2024 | ISSTA           | [FDI: Attack Neural Code Generation Systems through User Feedback Channel.](./papers_en/2024-ISSTA-FDI.pdf)                                          | [![Octocat](./figures/github.svg)](https://github.com/v587su/FDI) |                       |
| 2024 | TSE             | [Stealthy Backdoor Attack for Code Models.](./papers_en/2024-TSE-Stealthy_Backdoor_Attack_for_Code_Models.pdf)                                          | [![Octocat](./figures/github.svg)](https://github.com/yangzhou6666/adversarial-backdoor-for-code-models) |                       |
| 2024 | SP              | [Trojanpuzzle: Covertly Poisoning Code-Suggestion Models.](./papers_en/2024-SP-TrojanPuzzle.pdf)                                                        | [![Octocat](./figures/github.svg)](https://github.com/microsoft/CodeGenerationPoisoning)       |                       |
| 2024 | TOSEM           | [Poison Attack and Poison Detection on Deep Source Code Processing Models.](./papers_en/2024-TOSEM-Poison_Attack_and_Poison_Detection_on_Deep_Source_Code_Processing_Models.pdf)                                                               | [![Octocat](./figures/github.svg)](https://github.com/LJ2lijia/CodeDetector)                   |                       |
| 2023 | ICPC            | [Vulnerabilities in AI Code Generators: Exploring Targeted Data Poisoning Attacks.](./papers_en/2023-ICPC-Vulnerabilities_in_AI_Code_Generators.pdf)    | [![Octocat](./figures/github.svg)](https://github.com/dessertlab/Targeted-Data-Poisoning-Attacks) |                       |
| 2023 | EMNLP           | [TrojanSQL: SQL Injection against Natural Language Interface to Database.](./papers_en/2023-TrojanSQL.pdf)    | [![Octocat](./figures/github.svg)](https://github.com/jc-ryan/trojan-sql) |                       |
| 2023 | ACL             | [Backdooring Neural Code Search.](./papers_en/2023-ACL-Backdooring_Neural_Code_Search.pdf) 🚩                                                           | [![Octocat](./figures/github.svg)](https://github.com/wssun/BADCODE)                           |                       |
| 2022 | ICPR            | [Backdoors in Neural Models of Source Code.](./papers_en/2022-ICPR-Backdoors_in_Neural_Models_of_Source_Code.pdf)                                       | [![Octocat](./figures/github.svg)](https://github.com/tech-srl/code2seq)                       |                       |
| 2022 | FSE             | [You See What I Want You to See: Poisoning Vulnerabilities in Neural Code Search.](./papers_en/2022-FSE-You_See_What_I_Want_You_to_See.pdf)             | [![Octocat](./figures/github.svg)](https://github.com/CGCL-codes/naturalcc)                    |                       |
| 2021 | USENIX Security | [Explanation-Guided Backdoor Poisoning Attacks Against Malware Classifiers.](./papers_en/2021-USENIX-Explanation-Guided_Backdoor_Poisoning_Attacks.pdf) | [![Octocat](./figures/github.svg)](https://github.com/ClonedOne/MalwareBackdoors)              |                       |
| 2021 | USENIX Security | [You Autocomplete Me: Poisoning Vulnerabilities in Neural Code Completion. ](./papers_en/2021-USENIX-You_Autocomplete_Me.pdf)                           |                                                                                                |                       |



- **Model poisoning attacks**: Changes that do not alter the functionality of the code but trick the model.

| Year | Conf./Jour.       | Paper                                                                                                                                            | Code Repository                                                                | Reproduced Repository |  
|------|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|-----------------------|
| 2024 | Internetware      | [LateBA: Latent Backdoor Attack on Deep Bug Search via Infrequent Execution Codes.](./papers_en/2024-Internetware-LateBA.pdf)                    | [![Octocat](./figures/github.svg)](https://github.com/yxy-whu/LateBA)          |                       |
| 2023 | CoRR              | [BadCS: A Backdoor Attack Framework for Code search.](./papers_en/2023-CoRR-BadCS.pdf)                                                           |                                                                                |                       |
| 2023 | ACL               | [Multi-target Backdoor Attacks for Code Pre-trained Models.](./papers_en/2023-ACL-Multi-target_Backdoor_Attacks_for_Code_Pre-trained_Models.pdf) | [![Octocat](./figures/github.svg)](https://github.com/Lyz1213/Backdoored_PPLM) |                       |
| 2023 | USENIX Security   | [PELICAN: Exploiting Backdoors of Naturally Trained Deep Learning Models In Binary Code Analysis.](./papers_en/2023-USENIX-PELICAN.pdf)          | [![Octocat](./figures/github.svg)](https://github.com/ZhangZhuoSJTU/Pelican)   |                       |
| 2021 | USENIX Security   | [You Autocomplete Me: Poisoning Vulnerabilities in Neural Code Completion.](./papers_en/2021-USENIX-You_Autocomplete_Me.pdf)                     |                                                                                |                       |



### Adversarial Attacks
These attacks manipulate the input data to deceive the model into making incorrect predictions. Including two categories:
- **White-box attacks**: Attackers have complete knowledge of the target model, including model structure, weight parameters, and training data.

| Year | Conf./Jour. | Paper                                                                                                                               | Code Repository                                                                                | Reproduced Repository |   
|------|-------------|-------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------|
| 2023 | BdCloud     | [AdvBinSD: Poisoning the Binary Code Similarity Detector via Isolated Instruction Sequences.](./papers_en/2024-BdCloud-AdvBinSD.pdf)                |                                                                                               |                       |
| 2023 | CoRR        | [Adversarial Attacks against Binary Similarity Systems.](./papers_en/2023-CoRR-Adversarial_Attacks_against_Binary_Similarity_Systems.pdf)                |                                                                                               |                       |
| 2023 | SANER       | [How Robust Is a Large Pre-trained Language Model for Code Generation𝑓 A Case on Attacking GPT2.](./papers_en/2023-SANER-How_Robust_Is_a_Large_Pre-trained_Language_Model_for_Code_Generation.pdf) |                                                                                               |                       |
| 2022 | TOSEM       | [Towards Robustness of Deep Program Processing Models - Detection, Estimation, and Enhancement.](./papers_en/2022-TOSEM-Towars_Robustness_of_Deep_Program_Processing_Models.pdf) | [![Octocat](./figures/github.svg)](https://github.com/SEKE-Adversary/CARROT)                  |                       |
| 2022 | ICECCS      | [Generating Adversarial Source Programs Using Important Tokens-based Structural Transformations.](./papers_en/2022-ICECCS-Generating_Adversarial_Source_Programs_Using_Important_Tokens-based_Structural_Transformations.pdf) |                                                                                               |                       |
| 2021 | ICLR        | [Generating Adversarial Computer Programs using Optimized Obfuscations.](./papers_en/2021-ICLR-Generating_Adversarial_Computer_Programs_using_Optimized_Obfuscations.pdf) | [![Octocat](./figures/github.svg)](https://github.com/ALFA-group/adversarial-code-generation) |                       |
| 2020 | OOPSLA      | [Adversarial Examples for Models of Code.](./papers_en/2020-OOPSLA-Adversarial_Examples_for_Models_of_Code.pdf)                     | [![Octocat](./figures/github.svg)](https://github.com/tech-srl/adversarial-examples)          |                       |
| 2020 | ICML        | [Adversarial Robustness for Code.](./papers_en/2020-ICML-Adversarial_Robustness_for_Code.pdf)                                       | [![Octocat](./figures/github.svg)](https://github.com/eth-sri/robust-code)                    |                       |
| 2018 | CoRR        | [Adversarial Binaries for Authorship Identification.](./papers_en/2018-CoRR-Adversarial_Binaries_for_Authorship_Identification.pdf) |                                                                                               |                       |

- **Black-box attacks**: Adversaries attackers can only generate adversarial examples by obtaining limited model outputs through model queries.

| Year | Conf./Jour.     | Paper                                                                                                                                                                                              | Code Repository                                                                               | Reproduced Repository                                            |      
|------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| 2024 | TOSEM           | [CARL: Unsupervised Code-Based Adversarial Attacks for Programming Language Models via Reinforcement Learning.](./papers_en/2024-TOSEM-CARL)                                                       |                                                                                            |                                                                  | 
| 2024 | FSE             | [Evolutionary Multi-objective Optimization for Contextual Adversarial Example Generation.](./papers_en/2024-FSE-MOAA.pdf)                                                                          | [![Octocat](./figures/github.svg)](https://github.com/COLA-Laboratory/MOAA.)                                                                                               |                                                                  | 
| 2024 | CoRR            | [Investigating Adversarial Attacks in Software Analytics via Machine Learning Explainability.](./papers_en/2024-CoRR-Investigating_Adversarial_Attacks.pdf)                                        |                                                                                               |                                                                  | 
| 2024 | ICSE            | [MalwareTotal: Multi-Faceted and Sequence-Aware Bypass Tactics against Static Malware Detection.](./papers_en/2024-ICSE-MalwareTotal.pdf)                                                          | [![Octocat](./figures/github.svg)](https://github.com/Optimus-He/MalwareTotal)                |                                                                  | 
| 2024 | TIFS            | [Exploiting the Adversarial Example Vulnerability of Transfer Learning of Source Code.](./papers_en/2024-TIFS-CodeTAE.pdf)                                                                         | [![Octocat](./figures/github.svg)](https://github.com/yyl-github-1896/CodeTAE)                |                                                                  | 
| 2024 | CollaborateCom  | [Structural Adversarial Attack for Code Representation Models.](./papers_en/2024-CollaborateCom-STRUCK.pdf)                                                                                        | [![Octocat](./figures/github.svg)](https://github.com/zhanghaha1707/STRUCK)                   |                                                                  | 
| 2024 | CoRR            | [Demonstration Attack against In-Context Learning for Code Intelligence.](./papers_en/2024-CoRR-DICE.pdf)  🚩                                                                                      |                                                                                               |                                                                  |
| 2024 | JSEP            | [CodeBERT‐Attack: Adversarial Attack against Source Code Deep Learning Models via Pre‐trained Model.](./papers_en/2024-JSEP-CodeBERT-Attack.pdf)                                                   |                                                                                               |                                                                  | 
| 2024 | TOSEM           | [How Important Are Good Method Namesin NeuralCode Generation? A Model Robustness Perspective.](./papers_en/2024-TOSEM-RADAR.pdf)                                                                   | [![Octocat](./figures/github.svg)](https://github.com/NTDXYG/RADAR)                           |                                                                  |
| 2023 | CoRR            | [Deceptprompt: Exploiting llm-driven code generation via adversarial natural language instructions.](./papers_en/2023-CoRR-Deceptprompt.pdf)                                                       |                                                                                               |                                                                  |
| 2023 | AAAI            | [CodeAttack: Code-Based Adversarial Attacks for Pre-trained Programming Language Models.](./papers_en/2023-AAAI-CodeAttack.pdf)                                                                    | [![Octocat](./figures/github.svg)](https://github.com/reddy-lab-code-research/CodeAttack)     |                                                                  |
| 2023 | PACM PL         | [Discrete Adversarial Attack to Models of Code.](./papers_en/2023-PACM_CL-Discrete_Adversarial_Attack_to_Models_of_Code.pdf)                                                                       |                                                                                               |                                                                  |
| 2023 | CoRR            | [Adversarial Attacks on Code Models with Discriminative Graph Patterns.](./papers_en/2023-CoRR-Discriminative_Graph_Patterns.pdf)                                                                  |                                                                                               |                                                                  |
| 2023 | Electronics     | [AdVulCode: Generating Adversarial Vulnerable Code against Deep Learning-Based Vulnerability Detectors.](./papers_en/2023-Electronics-AdVulCode.pdf)                                               |                                                                                               |                                                                  |
| 2023 | ACL             | [DIP: Dead code Insertion based Black-box Attack for Programming Language Model.](./papers_en/2023-ACL-DIP.pdf)                                                                                    |                                                                                               |                                                                  |
| 2023 | CoRR            | [A Black-Box Attack on Code Models via Representation Nearest Neighbor Search.](./papers_en/2023-CoRR_Representation_Nearest_Neightbor_Search.pdf)                                                 | [![Octocat](./figures/github.svg)](https://github.com/18682922316/RNNS-for-code-attack)       |                                                                  |
| 2023 | CoRR            | [SHIELD: Thwarting Code Authorship Attribution.](./papers_en/2023-CoRR-SHIELD.pdf)                                                                                                                 |                                                                                               |                                                                  |
| 2023 | ASE             | [Code Difference Guided Adversarial Example Generation for Deep Code Models.](./papers_en/2023-ASE-Code_Difference_Guided_Adversarial_Example_Generation_for_Deep_Code_Models.pdf)                 | [![Octocat](./figures/github.svg)](https://github.com/tianzhaotju/CODA)                       |                                                                  |
| 2022 | CoRR            | [FuncFooler: A Practical Black-box Attack Against Learning-based Binary Code Similarity Detection Methods.](./papers_en/2022-CoRR-FuncFooler.pdf)                                                                      |                                                                                               |                                                                  |
| 2022 | TOSEM           | [Adversarial Robustness of Deep Code Comment Generation.](./papers_en/2022-TOSEM-Adversarial_Robustness_of_Deep_Code_Comment_Generation.pdf)                                                       | [![Octocat](./figures/github.svg)](https://github.com/zhangxq-1/ACCENT-repository)            |                                                                  |
| 2022 | ICSE            | [Natural Attack for Pre-trained Models of Code.](./papers_en/2022-ICSE-Natural_Attack_for_Pre-trained_Models_of_Code.pdf)                                                                          | [![Octocat](./figures/github.svg)](https://github.com/soarsmu/attack-pretrain-models-of-code) | [![Localcat](./figures/octocat.png)](./adversarial_attack/ALTER) |
| 2022 | ICSE            | [RoPGen: Towards Robust Code Authorship Attribution via Automatic Coding Style Transformation.](./papers_en/2022-ICSE-RoPGen.pdf)                                                                  | [![Octocat](./figures/github.svg)](https://github.com/RoPGen/RoPGen)                          |                                                                  |
| 2022 | EMNLP           | [TABS: Efficient Textual Adversarial Attack for Pre-trained NL Code Model Using Semantic Beam Search.](./papers_en/2022-EMNLP-TABS.pdf)                                                            |                                                                                               |                                                                  |
| 2021 | TIFS            | [A Practical Black-box Attack on Source Code Authorship Identification Classifiers.](./papers_en/2021-TIFS_A_Practical_Black-Box_Attack_on_Source_Code_Authorship_Identification_Classifiers.pdf)  |                                                                                               |                                                                  |
| 2021 | ICST            | [A Search-Based Testing Framework for Deep Neural Networks of Source Code Embedding.](./papers_en/2021-ICST-A_Search-Based_Testing_Framework_for_Deep_Neural_Networks_of_Source_Code_Embedding.pdf) | [![Octocat](./figures/github.svg)](https://github.com/MaryamVP/Guided-Mutation-ICST-2021)     |                                                                  |
| 2021 | QRS             | [Generating Adversarial Examples of Source Code Classification Models via Q-Learning-Based Markov Decision Process.](./papers_en/2021-QRS-Generating_Adversarial_Examples_via_Q-Learning-Based_Markov_Decision_Process.pdf) |                                                                                               |                                                                  |
| 2021 | GECCO           | [Deceiving Neural Source Code Classifiers: Finding Adversarial Examples with Grammatical Evolution.](./papers_en/2021-GECCO-Deceiving_Neural_Source_Code_Classifiers.pdf)                          | [![Octocat](./figures/github.svg)](https://github.com/Martisal/adversarialGE)                 |                                                                  |
| 2021 | CoRR            | [On Adversarial Robustness of Synthetic Code Generation.](./papers_en/2021-CoRR-On_Adversarial_Robustness_of_Synthetic_Code_Generation.pdf)                                                        | [![Octocat](./figures/github.svg)](https://github.com/mtensor/neural_sketch)                  |                                                                  |
| 2020 | CoRR            | [STRATA: Simple, Gradient-free Attacks for Models of Code.](./papers_en/2020-CoRR-STRATA.pdf)                                                                                                      |                                                                                               |                                                                  |
| 2020 | AAAI            | [Generating Adversarial Examples for Holding Robustness of Source Code Processing Models.](./papers_en/2020-AAAI-Generating_Adversarial_Examples_for_Holding_Robustness.pdf)                       | [![Octocat](./figures/github.svg)](https://github.com/Metropolis-Hastings-Modifier/MHM)       |                                                                  |
| 2019 | USENIX Security | [Misleading Authorship Attribution of Source Code using Adversarial Learning.](./papers_en/2019-USENIX-Misleading_Authorship_Attribution_of_Source_Code.pdf)                                       |                                                                                               |                                                                  |
| 2019 | CODASPY         | [Adversarial Authorship Attribution in Open-source Projects.](./papers_en/2019-CODASPY-Adversarial_Authorship_Attribution_in_Open-source_Projects.pdf)                                             |                                                                                               |                                                                  |



[//]: # ()
[//]: # (### Other Threats)

[//]: # (This includes xxx)

## 🛡Defensive Strategies
In response to the growing security threats, researchers have proposed various defense mechanisms:

### Backdoor Defense
Methods for defending against backdoor attacks include:

| Year | Conf./Jour. | Paper                                                                                                                                                                            | Code Reporisty                                                                      | Reproduced Reporisty |  
|------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|----------------------|
| 2025 | FSE         | [Eliminating Backdoors in Neural Code Models for Secure Code Understanding.](./papers_en/2025-FSE-EliBadCode.pdf) 🚩                                                             | [![Octocat](./figures/github.svg)](https://github.com/wssun/EliBadCode)             |                      |
| 2025 | ICSE        | [Show Me Your Code! Kill Code Poisoning: A Lightweight Method Based on Code Naturalness.](./papers_en/2025-ICSE-KILLBADCODE.pdf) 🚩                                                | [![Octocat](./figures/github.svg)](https://github.com/wssun/KillBadCode)            |                      |
| 2024 | TOSEM       | [Poison Attack and Poison Detection on Deep Source Code Processing Models.](./papers_en/2024-TOSEM-Poison_Attack_and_Poison_Detection_on_Deep_Source_Code_Processing_Models.pdf) |                                                                                     |                      |
| 2024 | CoRR        | [Eliminating Backdoors in Neural Code Models via Trigger Inversion.](./papers_en/2024-CoRR-Eliminating_Backdoors_via_Trigger_Inversion.pdf)  🚩                                  |                                                                                     |                      |
| 2024 | CoRR        | [Defending Code Language Models against Backdoor Attacks with Deceptive Cross-Entropy Loss.](./papers_en/2024-CoRR-DeCE.pdf)                                                     | [![Octocat](./figures/github.svg)](https://github.com/NTDXYG/DeCE)                  |                      |
| 2023 | CoRR        | [Occlusion-based Detection of Trojan-triggering Inputs in Large Language Models of Code.](./papers_en/2023-CoRR-Occlusion-based_Detection_of_Trojan-triggering_Inputs.pdf)       |                                                                                     |                      |
| 2022 | ICPR        | [Backdoors in Neural Models of Source Code.](./papers_en/2022-ICPR-Backdoors_in_Neural_Models_of_Source_Code.pdf)                                                                | [![Octocat](./figures/github.svg)](https://github.com/goutham7r/backdoors-for-code) |                      |




### Adversarial Defense
Approaches to counter adversarial attacks include:

| Year | Conf./Jour. | Paper                                                                                                                                                                               | Code Reporisty                                                              | Reproduced Reporisty |    
|------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|----------------------|
| 2024 | TOSEM       | [How Important Are Good Method Namesin NeuralCode Generation? A Model Robustness Perspective.](./papers_en/2024-TOSEM-RADAR.pdf)                                                    | [![Octocat](./figures/github.svg)](https://github.com/NTDXYG/RADAR)         |                      |
| 2023 | ICSE        | [RoPGen: Towards Robust Code Authorship Attribution via Automatic Coding Style Transformation.](./papers_en/2022-ICSE-RoPGen.pdf)                                                   | [![Octocat](./figures/github.svg)](https://github.com/RoPGen/RoPGen)        |                      |
| 2023 | PACM PL     | [Discrete Adversarial Attack to Models of Code.](./papers_en/2023-PACM_CL-Discrete_Adversarial_Attack_to_Models_of_Code.pdf)                                                        |                                                                             |                      |
| 2023 | CCS         | [Large Language Models for Code: Security Hardening and Adversarial Testing.](./papers_en/2023-CCS-Security_Hardening_and_Adversarial_Testing.pdf)                                  | [![Octocat](./figures/github.svg)](https://github.com/eth-sri/sven)         |                      |
| 2023 | CoRR        | [Enhancing Robustness of AI Offensive Code Generators via Data Augmentation.](./papers_en/2023-CoRR-Enhancing_Robustness_of_AI_Offensive_Code_Generators_via_Data_Augmentation.pdf) |                                                                             |                      |
| 2022 | SANER       | [Semantic Robustness of Models of Source Code.](./papers_en/2021-SANER-Semantic_Robustness_of_Models_of_Source_Code.pdf)                                                            | [![Octocat](./figures/github.svg)](https://github.com/jjhenkel/averloc)     |                      |
| 2022 | COLING      | [Semantic-Preserving Adversarial Code Comprehension.](./papers_en/2022-COLING-Sematic-Preserving-Adversarial-Code-Comprehension.pdf)                                                | [![Octocat](./figures/github.svg)](https://github.com/EricLee8/SPACE)       |                      |


[//]: # (## Challenges and Future Directions)

[//]: # (The research points to significant **challenges** in securing NCMs, including the difficulty of detecting sophisticated attacks and the lack of standardized **benchmarks** for evaluating defenses. Future work should focus on:)

[//]: # (- **Creating robust defense frameworks** for both **adversarial** and **backdoor** attacks.)

[//]: # (- Developing **evaluation standards** for testing the security of NCMs.)

[//]: # (## ⚙ Datasets and Open-Source Tools)

[//]: # (A set of tools and benchmarks are available to researchers and developers for experimenting with different **security attacks** and **defense strategies** for NCMs.)

## Citation
If you find this repository useful for your work, please include the following citation:
```
@article{2024-Security-of-CodeLMs,
  title={Security of Language Models for Code: A Systematic Literature Review},
  author={Yuchen Chen and Weisong Sun and Chunrong Fang and Zhenpeng Chen and Yifei Ge and Tingxu Han and Quanjun Zhang and Yang Liu and Zhenyu Chen and Baowen Xu},
  journal={arXiv preprint arXiv:2410.15631},
  year={2024}
}
```
