import sys
import sys
import os

sys.path.append('../../../')
sys.path.append('../../../python_parser')

import csv
import copy
import json
import logging
import argparse
import warnings
import torch
import numpy as np
import random
from model import Model, eval_accuracies
from run import TextDataset, InputFeatures, DemoDataset, DemoDataset_summary
from utils import select_parents, crossover, map_chromesome, mutate, is_valid_variable_name, _tokenize, \
    get_identifier_posistions_from_code, get_masked_code_by_position, get_substitues, is_valid_substitue, set_seed

from utils import CodeDataset, CodeDataset_generate
from utils import getUID, isUID, getTensor, build_vocab
from run_parser import get_identifiers, get_example
from transformers import (RobertaForMaskedLM, RobertaConfig, RobertaForSequenceClassification, RobertaTokenizer)


def remove_around_symbol(new_feature, symbol, weighted, remove_before=True, remove_after=True):
    """
    从列表中找到特定符号的所有位置，并删除该符号以及前后一位的内容。

    参数：
    - new_feature: InputFeatures 对象
    - symbol: 特殊符号
    - weighted_list: 字典中 symbol 的权重列表
    - remove_before: 是否删除符号前面的一位
    - remove_after: 是否删除符号后面的一位
    """
    token = new_feature.get_input_tokens()
    data = new_feature.get_input_ids()
    indices = [i for i, x in enumerate(token) if x == symbol]

    if not indices or weighted == 0:
        return

    # 若 weighted 大于 1，则在开头添加 '29871' 和 '▁'
    if weighted > 1:
        prepend_value_id = 29871
        prepend_value_token = '▁'
        data = [prepend_value_id] * (weighted - 1) + data
        token = [prepend_value_token] * (weighted - 1) + token

    # 处理特殊符号 symbol 的位置
    index = indices[0]
    if remove_after and index + 1 < len(data):
        del data[index + 1]
        del token[index + 1]
    if remove_before and index - 1 >= 0:
        del data[index - 1]
        del token[index - 1]

    new_feature.set_input_tokens(token)
    new_feature.set_input_ids(data)


def assert_equal_length(lists):
    """
    断言一个列表中的所有子列表长度相同。

    参数：
    - lists: 列表，其中包含多个子列表。

    如果断言失败，将抛出 AssertionError。
    """
    # 获取第一个列表的长度
    if not lists:
        return  # 空列表没有长度问题

    first_length = len(lists[0].get_input_tokens())

    # 遍历所有子列表并检查长度
    for lst in lists:
        assert len(
            lst.get_input_tokens()) == first_length, f"List {lst} does not have the expected length {first_length}"


def compute_fitness(chromesome, codebert_tgt, tokenizer_tgt, orig_prob, orig_label, true_label, code,
                    names_positions_dict, args):
    # 计算fitness function.
    # words + chromesome + orig_label + current_prob
    temp_code = map_chromesome(chromesome, code, "c")

    new_feature = convert_code_to_features(temp_code, tokenizer_tgt, true_label, args)
    new_dataset = CodeDataset([new_feature])
    new_logits, preds = codebert_tgt.get_results(new_dataset, args.eval_batch_size)
    # 计算fitness function
    fitness_value = orig_prob - new_logits[0][orig_label]
    return fitness_value, preds[0]


def convert_code_to_features(code, tokenizer, label, args):
    code = ' '.join(code.split())
    code_tokens = tokenizer.tokenize(code)[:args.block_size - 2]
    source_tokens = [tokenizer.cls_token] + code_tokens + [tokenizer.sep_token]
    source_ids = tokenizer.convert_tokens_to_ids(source_tokens)
    padding_length = args.block_size - len(source_ids)
    source_ids += [tokenizer.pad_token_id] * padding_length
    return InputFeatures(source_tokens, source_ids, 0, label)


def convert_code_to_features_codellama(code, tokenizer, label, args):
    code = ' '.join(code.split())
    code_tokens = tokenizer.tokenize(code)
    source_tokens = code_tokens
    # code_tokens = tokenizer.tokenize(code)[:args.block_size - 2]
    # source_tokens = [tokenizer.bos_token] + code_tokens + [tokenizer.eos_token]
    source_ids = tokenizer.convert_tokens_to_ids(source_tokens)
    # padding_length = args.block_size - len(source_ids)
    # source_ids+=[tokenizer.pad_token_id]*padding_length
    return InputFeatures(source_tokens, source_ids, 0, label)


def get_importance_score(args, example, code, words_list: list, variable_names: list, tgt_model,
                         tokenizer, label_list, batch_size=16, max_length=512, model_type='classification'):
    '''Compute the importance score of each variable'''
    # label: example[1] tensor(1)
    # 1. 过滤掉所有的keywords.
    positions = get_identifier_posistions_from_code(words_list, variable_names)
    # 需要注意大小写.
    if len(positions) == 0:
        ## 没有提取出可以mutate的position
        return None, None, None

    new_example = []

    # 2. 得到Masked_tokens
    masked_token_list, replace_token_positions = get_masked_code_by_position(words_list, positions)
    # replace_token_positions 表示着，哪一个位置的token被替换了.

    # 需要考虑原本替换的符号占几位
    key_num = {}
    weighted_list = [0]
    for v in variable_names:
        code_tokens = tokenizer.tokenize(v)
        key_num[v] = len(code_tokens)
    for key, values in positions.items():
        weighted_list.extend([key_num[key]] * len(values))

    for index, tokens in enumerate([words_list] + masked_token_list):
        new_code = ' '.join(tokens)
        new_feature = convert_code_to_features_codellama(new_code, tokenizer, example[0][1], args)
        # 对于CodeLlamaTokenizerFast，<unk>前后会识别为“_”,所以删掉
        # remove_around_symbol(new_feature, '<unk>', weighted_list[index])
        new_example.append(new_feature)
    # 断言检查是否都同样长度
    # assert_equal_length(new_example)
    new_dataset = CodeDataset_generate(new_example)
    # 3. 将他们转化成features
    logits = tgt_model.get_results(new_dataset, args.eval_batch_size)
    # logits, preds = tgt_model.get_results(new_dataset, 1)
    orig_prob = logits[0]
    # 第一个是original code的数据.

    importance_score = []
    for prob in logits[1:]:
        importance_score.append(orig_prob - prob)

    return importance_score, replace_token_positions, positions


class Attacker():
    def __init__(self, args, model_tgt, tokenizer_tgt, model_mlm, tokenizer_mlm, use_bpe, threshold_pred_score) -> None:
        self.args = args
        self.model_tgt = model_tgt
        self.tokenizer_tgt = tokenizer_tgt
        self.model_mlm = model_mlm
        self.tokenizer_mlm = tokenizer_mlm
        self.use_bpe = use_bpe
        self.threshold_pred_score = threshold_pred_score

    def ga_attack(self, example, code, substituions, initial_replace=None):
        '''
        return
            original program: code
            program length: prog_length
            adversar program: adv_program
            true label: true_label
            original prediction: orig_label
            adversarial prediction: temp_label
            is_attack_success: is_success
            extracted variables: variable_names
            importance score of variables: names_to_importance_score
            number of changed variables: nb_changed_var
            number of changed positions: nb_changed_pos
            substitues for variables: replaced_words
        '''
        # 先得到tgt_model针对原始Example的预测信息.

        logits, preds = self.model_tgt.get_results([example], self.args.eval_batch_size)
        orig_prob = logits[0]
        orig_label = preds[0]
        current_prob = max(orig_prob)

        true_label = example[1].item()
        adv_code = ''
        temp_label = None

        identifiers, code_tokens = get_identifiers(code, 'c')
        prog_length = len(code_tokens)

        processed_code = " ".join(code_tokens)

        words, sub_words, keys = _tokenize(processed_code, self.tokenizer_mlm)
        # 这里经过了小写处理..

        variable_names = list(substituions.keys())

        if not orig_label == true_label:
            # 说明原来就是错的
            is_success = -4
            return code, prog_length, adv_code, true_label, orig_label, temp_label, is_success, variable_names, None, None, None, None

        if len(variable_names) == 0:
            # 没有提取到identifier，直接退出
            is_success = -3
            return code, prog_length, adv_code, true_label, orig_label, temp_label, is_success, variable_names, None, None, None, None

        names_positions_dict = get_identifier_posistions_from_code(words, variable_names)

        nb_changed_var = 0  # 表示被修改的variable数量
        nb_changed_pos = 0
        is_success = -1

        # 我们可以先生成所有的substitues
        variable_substitue_dict = {}

        for tgt_word in names_positions_dict.keys():
            variable_substitue_dict[tgt_word] = substituions[tgt_word]

        if len(variable_substitue_dict) == 0:
            is_success = -3
            return code, prog_length, adv_code, true_label, orig_label, temp_label, is_success, variable_names, None, None, None, None

        fitness_values = []
        base_chromesome = {word: word for word in variable_substitue_dict.keys()}
        population = [base_chromesome]
        # 关于chromesome的定义: {tgt_word: candidate, tgt_word_2: candidate_2, ...}
        for tgt_word in variable_substitue_dict.keys():
            # 这里进行初始化
            if initial_replace is None:
                # 对于每个variable: 选择"影响最大"的substitues
                replace_examples = []
                substitute_list = []

                current_prob = max(orig_prob)
                most_gap = 0.0
                initial_candidate = tgt_word
                tgt_positions = names_positions_dict[tgt_word]

                # 原来是随机选择的，现在要找到改变最大的.
                for a_substitue in variable_substitue_dict[tgt_word]:
                    # a_substitue = a_substitue.strip()

                    substitute_list.append(a_substitue)
                    # 记录下这次换的是哪个substitue
                    temp_code = get_example(code, tgt_word, a_substitue, "c")
                    new_feature = convert_code_to_features(temp_code, self.tokenizer_tgt, example[1].item(), self.args)
                    replace_examples.append(new_feature)

                if len(replace_examples) == 0:
                    # 并没有生成新的mutants，直接跳去下一个token
                    continue
                new_dataset = CodeDataset(replace_examples)
                # 3. 将他们转化成features
                logits, preds = self.model_tgt.get_results(new_dataset, self.args.eval_batch_size)

                _the_best_candidate = -1
                for index, temp_prob in enumerate(logits):
                    temp_label = preds[index]
                    gap = current_prob - temp_prob[temp_label]
                    # 并选择那个最大的gap.
                    if gap > most_gap:
                        most_gap = gap
                        _the_best_candidate = index
                if _the_best_candidate == -1:
                    initial_candidate = tgt_word
                else:
                    initial_candidate = substitute_list[_the_best_candidate]
            else:
                initial_candidate = initial_replace[tgt_word]

            temp_chromesome = copy.deepcopy(base_chromesome)
            temp_chromesome[tgt_word] = initial_candidate
            population.append(temp_chromesome)
            temp_fitness, temp_label = compute_fitness(temp_chromesome, self.model_tgt, self.tokenizer_tgt,
                                                       max(orig_prob), orig_label, true_label, code,
                                                       names_positions_dict, self.args)
            fitness_values.append(temp_fitness)

        cross_probability = 0.7

        max_iter = max(5 * len(population), 10)
        # 这里的超参数还是的调试一下.

        for i in range(max_iter):
            _temp_mutants = []
            for j in range(self.args.eval_batch_size):
                p = random.random()
                chromesome_1, index_1, chromesome_2, index_2 = select_parents(population)
                if p < cross_probability:  # 进行crossover
                    if chromesome_1 == chromesome_2:
                        child_1 = mutate(chromesome_1, variable_substitue_dict)
                        continue
                    child_1, child_2 = crossover(chromesome_1, chromesome_2)
                    if child_1 == chromesome_1 or child_1 == chromesome_2:
                        child_1 = mutate(chromesome_1, variable_substitue_dict)
                else:  # 进行mutates
                    child_1 = mutate(chromesome_1, variable_substitue_dict)
                _temp_mutants.append(child_1)

            # compute fitness in batch
            feature_list = []
            for mutant in _temp_mutants:
                _temp_code = map_chromesome(mutant, code, "c")
                _tmp_feature = convert_code_to_features(_temp_code, self.tokenizer_tgt, true_label, self.args)
                feature_list.append(_tmp_feature)
            if len(feature_list) == 0:
                continue
            new_dataset = CodeDataset(feature_list)
            mutate_logits, mutate_preds = self.model_tgt.get_results(new_dataset, self.args.eval_batch_size)
            mutate_fitness_values = []
            for index, logits in enumerate(mutate_logits):
                if mutate_preds[index] != orig_label:
                    adv_code = map_chromesome(_temp_mutants[index], code, "c")
                    for old_word in _temp_mutants[index].keys():
                        if old_word == _temp_mutants[index][old_word]:
                            nb_changed_var += 1
                            nb_changed_pos += len(names_positions_dict[old_word])

                    return code, prog_length, adv_code, true_label, orig_label, mutate_preds[
                        index], 1, variable_names, None, nb_changed_var, nb_changed_pos, _temp_mutants[index]
                _tmp_fitness = max(orig_prob) - logits[orig_label]
                mutate_fitness_values.append(_tmp_fitness)

            # 现在进行替换.
            for index, fitness_value in enumerate(mutate_fitness_values):
                min_value = min(fitness_values)
                if fitness_value > min_value:
                    # 替换.
                    min_index = fitness_values.index(min_value)
                    population[min_index] = _temp_mutants[index]
                    fitness_values[min_index] = fitness_value

        return code, prog_length, adv_code, true_label, orig_label, temp_label, is_success, variable_names, None, nb_changed_var, nb_changed_pos, None

    def greedy_attack(self, example, code, substituions):
        '''
        return
            original program: code
            program length: prog_length
            adversar program: adv_program
            true label: true_label
            original prediction: orig_label
            adversarial prediction: temp_label
            is_attack_success: is_success
            extracted variables: variable_names
            importance score of variables: names_to_importance_score
            number of changed variables: nb_changed_var
            number of changed positions: nb_changed_pos
            substitues for variables: replaced_words
        '''
        # 先得到tgt_model针对原始Example的预测信息.

        logits, preds = self.model_tgt.get_results([example], self.args.eval_batch_size)
        orig_prob = logits[0]
        orig_label = preds[0]
        current_prob = max(orig_prob)

        true_label = example[1].item()
        adv_code = ''
        temp_label = None

        identifiers, code_tokens = get_identifiers(code, 'c')
        prog_length = len(code_tokens)

        processed_code = " ".join(code_tokens)

        words, sub_words, keys = _tokenize(processed_code, self.tokenizer_mlm)
        # 这里经过了小写处理..

        variable_names = list(substituions.keys())

        # if not orig_label == true_label:
        #     # 说明原来就是错的
        #     is_success = -4
        #     return code, prog_length, adv_code, true_label, orig_label, temp_label, is_success, variable_names, None, None, None, None

        code_candidate = []

        if len(variable_names) == 0:
            # 没有提取到identifier，直接退出
            is_success = -3
            return code, prog_length, sorted(code_candidate, key=lambda x: x[
                1]), true_label, orig_label, temp_label, is_success, variable_names, None, None, None, None

        # sub_words = [self.tokenizer_tgt.cls_token] + sub_words[:self.args.block_size - 2] + [self.tokenizer_tgt.sep_token]
        # 如果长度超了，就截断；这里的block_size是CodeBERT能接受的输入长度
        # 计算importance_score.

        importance_score, replace_token_positions, names_positions_dict = get_importance_score(self.args, example,
                                                                                               processed_code, words,
                                                                                               sub_words,
                                                                                               variable_names,
                                                                                               self.model_tgt,
                                                                                               self.tokenizer_tgt,
                                                                                               [0, 1],
                                                                                               batch_size=self.args.eval_batch_size,
                                                                                               max_length=self.args.block_size,
                                                                                               model_type='classification')

        if importance_score is None:
            return code, prog_length, sorted(code_candidate, key=lambda x: x[
                1]), true_label, orig_label, temp_label, -3, variable_names, None, None, None, None

        token_pos_to_score_pos = {}

        for i, token_pos in enumerate(replace_token_positions):
            token_pos_to_score_pos[token_pos] = i
        # 重新计算Importance score，将所有出现的位置加起来（而不是取平均）.
        names_to_importance_score = {}

        for name in names_positions_dict.keys():
            total_score = 0.0
            positions = names_positions_dict[name]
            for token_pos in positions:
                # 这个token在code中对应的位置
                # importance_score中的位置：token_pos_to_score_pos[token_pos]
                total_score += importance_score[token_pos_to_score_pos[token_pos]]

            names_to_importance_score[name] = total_score

        sorted_list_of_names = sorted(names_to_importance_score.items(), key=lambda x: x[1], reverse=True)
        # 根据importance_score进行排序

        final_words = copy.deepcopy(words)
        final_code = copy.deepcopy(code)
        nb_changed_var = 0  # 表示被修改的variable数量
        nb_changed_pos = 0
        is_success = -1
        replaced_words = {}

        for name_and_score in sorted_list_of_names:
            tgt_word = name_and_score[0]
            tgt_positions = names_positions_dict[tgt_word]

            all_substitues = substituions[tgt_word]

            # 得到了所有位置的substitue，并使用set来去重

            most_gap = 0.0
            candidate = None
            replace_examples = []

            substitute_list = []
            # 依次记录了被加进来的substitue
            # 即，每个temp_replace对应的substitue.
            for substitute in all_substitues:
                # temp_replace = copy.deepcopy(final_words)
                # for one_pos in tgt_positions:
                #     temp_replace[one_pos] = substitute

                substitute_list.append(substitute)
                # 记录了替换的顺序

                # 需要将几个位置都替换成sustitue_
                temp_code = get_example(final_code, tgt_word, substitute, "c")

                # 存在因为词表导致的new_feature长度无法对齐的情况
                new_feature = convert_code_to_features_codellama(temp_code, self.tokenizer_tgt, example[1].item(),
                                                                 self.args)
                replace_examples.append(new_feature)
            if len(replace_examples) == 0:
                # 并没有生成新的mutants，直接跳去下一个token
                continue
            new_dataset = CodeDataset(replace_examples)
            # 3. 将他们转化成features
            logits, preds = self.model_tgt.get_results_singleB(new_dataset, self.args.eval_batch_size)
            assert (len(logits) == len(substitute_list))

            for index, temp_prob in enumerate(logits):
                temp_label = preds[index]
                gap = current_prob - temp_prob[orig_label]
                # 并选择那个最大的gap.
                if gap > most_gap:
                    most_gap = gap
                    candidate = substitute_list[index]

            if most_gap > 0:

                nb_changed_var += 1
                nb_changed_pos += len(names_positions_dict[tgt_word])
                current_temp = current_prob - most_gap
                replaced_words[tgt_word] = candidate
                final_code = get_example(final_code, tgt_word, candidate, "c")
                code_candidate.append((final_code, np.float64(current_temp)))
                if current_temp > 0.5:
                    print("%s ACC! %s => %s (%.5f => %.5f)" % \
                          ('>>', tgt_word, candidate,
                           current_prob,
                           current_temp), flush=True)
                else:
                    print("%s SUC! %s => %s (%.5f => %.5f)" % \
                          ('>>', tgt_word, candidate,
                           current_prob,
                           current_temp), flush=True)
                    is_success = 1
            else:
                replaced_words[tgt_word] = tgt_word

        return code, prog_length, sorted(code_candidate, key=lambda x: x[
            1]), true_label, orig_label, temp_label, is_success, variable_names, names_to_importance_score, nb_changed_var, nb_changed_pos, replaced_words

    def demo_attack(self, example, demo, substituions, idx_query, icl_num, adv_demo_filepath, adv_answer_filepath):
        '''
        return
            original program: code
            program length: prog_length
            adversar program: adv_program
            true label: true_label
            original prediction: orig_label
            adversarial prediction: temp_label
            is_attack_success: is_success
            extracted variables: variable_names
            importance score of variables: names_to_importance_score
            number of changed variables: nb_changed_var
            number of changed positions: nb_changed_pos
            substitues for variables: replaced_words
            score of bleu: bleu
            score of rough_l: rough_l
            score of meteor: meteor
        '''
        # 先得到tgt_model针对原始Example的预测信息.
        query = ' '.join(idx_query[0]).strip()
        true_label = ' '.join(idx_query[1]).strip()
        ori_dataset = DemoDataset_summary(example)
        logits, bleus, rouges, meteors, answers = self.model_tgt.get_icl_results(ori_dataset, query, true_label, icl_num)
        orig_prob = logits[0]
        current_prob = orig_prob
        answer = answers[0]

        words = []
        temp_label = None

        for i in range(icl_num):
            identifiers, code_tokens = get_identifiers(demo[i], 'c')
            processed_code = " ".join(code_tokens)
            # 这里经过了小写处理..
            word, sub_words, keys = _tokenize(processed_code, self.tokenizer_mlm)
            words += word

        # variable_names = list(substituions.keys())
        # 提取所有字典中的键并去重
        merged_substituions = {}
        for d in substituions:
            for key, value in d.items():
                if key not in merged_substituions:
                    merged_substituions[key] = set()
                if isinstance(value, list):
                    merged_substituions[key].update(value)
                else:
                    merged_substituions[key].add(value)
        # 将集合转换回列表
        merged_substituions = {key: list(values) for key, values in merged_substituions.items()}
        variable_names = list(merged_substituions.keys())


        # if not orig_label == true_label:
        #     # 说明原来就是错的
        #     is_success = -4
        #     return demo, true_label, orig_label, temp_label, is_success, variable_names, None, None, None, None

        code_candidate = []

        if len(variable_names) == 0:
            # 没有提取到identifier，直接退出
            is_success = -3
            item = {
                'query': query,
                'demo': demo,
            }
            with open(adv_demo_filepath, "a") as wf:
                wf.write(json.dumps(item) + '\n')
            with open(adv_answer_filepath, "a") as wf:
                wf.write(json.dumps(answer) + '\n')

            return demo, true_label, orig_prob, temp_label, is_success, variable_names, None, None, None, None, bleus[0], rouges[0], meteors[0]


        importance_score, replace_token_positions, names_positions_dict = get_importance_score(self.args, example,
                                                                                               processed_code, words,
                                                                                               variable_names,
                                                                                               self.model_tgt,
                                                                                               self.tokenizer_tgt,
                                                                                               [0, 1],
                                                                                               batch_size=self.args.eval_batch_size,
                                                                                               max_length=self.args.block_size,
                                                                                               model_type='classification')

        if importance_score is None:
            item = {
                'query': query,
                'demo': demo,
            }
            with open(adv_demo_filepath, "a") as wf:
                wf.write(json.dumps(item) + '\n')
            with open(adv_answer_filepath, "a") as wf:
                wf.write(json.dumps(answer) + '\n')
            return demo, true_label, orig_prob, temp_label, -3, variable_names, None, None, None, None, bleus[0], rouges[0], meteors[0]

        token_pos_to_score_pos = {}

        for i, token_pos in enumerate(replace_token_positions):
            token_pos_to_score_pos[token_pos] = i
        # 重新计算Importance score，将所有出现的位置加起来（而不是取平均）.
        names_to_importance_score = {}

        for name in names_positions_dict.keys():
            total_score = 0.0
            positions = names_positions_dict[name]
            for token_pos in positions:
                # 这个token在code中对应的位置
                # importance_score中的位置：token_pos_to_score_pos[token_pos]
                total_score += importance_score[token_pos_to_score_pos[token_pos]]

            names_to_importance_score[name] = total_score

        sorted_list_of_names = sorted(names_to_importance_score.items(), key=lambda x: x[1], reverse=True)
        # 根据importance_score进行排序

        # final_words = copy.deepcopy(words)
        final_code = copy.deepcopy(demo)
        nb_changed_var = 0  # 表示被修改的variable数量
        nb_changed_pos = 0
        is_success = -1
        replaced_words = {}
        bleu = bleus[0]
        meteor = meteors[0]
        rouge = rouges[0]

        for name_and_score in sorted_list_of_names:
            tgt_word = name_and_score[0]
            tgt_positions = names_positions_dict[tgt_word]

            all_substitues = merged_substituions[tgt_word]

            # 得到了所有位置的substitue，并使用set来去重

            most_gap = 0.0
            candidate = None
            replace_examples = []

            substitute_list = []
            # 依次记录了被加进来的substitue
            # 即，每个temp_replace对应的substitue.
            for substitute in all_substitues:
                # temp_replace = copy.deepcopy(final_words)
                # for one_pos in tgt_positions:
                #     temp_replace[one_pos] = substitute

                substitute_list.append(substitute)
                # 记录了替换的顺序

                # 需要将几个位置都替换成sustitue_
                for i in range(icl_num):
                    temp_code = get_example(final_code[i], tgt_word, substitute, "c")
                    replace_examples.append((' '.join(temp_code.split()), example[i][1]))

            if len(replace_examples) == 0:
                # 并没有生成新的mutants，直接跳去下一个token
                continue
            new_dataset = DemoDataset_summary(replace_examples)
            # 3. 将他们转化成features
            logits, bleus, rouges, meteors, answers = self.model_tgt.get_icl_results(new_dataset, query, true_label,
                                                                                     icl_num)
            assert (len(logits) == len(substitute_list))

            for index, temp_label in enumerate(logits):
                # 下降50%则认为攻击成功
                if temp_label < (orig_prob * 0.5):
                    # 如果label改变了，说明这个mutant攻击成功
                    is_success = 1
                    nb_changed_var += 1
                    nb_changed_pos += len(names_positions_dict[tgt_word])
                    candidate = substitute_list[index]
                    replaced_words[tgt_word] = candidate
                    # adv_code这里是替换后的所有demo内容？
                    adv_code = get_example(final_code, tgt_word, candidate, "c")
                    item = {
                        'query': query,
                        'demo': adv_code
                    }
                    with open(adv_demo_filepath, "a") as wf:
                        wf.write(json.dumps(item) + '\n')

                    with open(adv_answer_filepath, "a") as wf:
                        wf.write(json.dumps(answers[index]) + '\n')

                    print("%s SUC! %s => %s (%.5f => %.5f)" % \
                          ('>>', tgt_word, candidate,
                           current_prob, temp_label,
                           ), flush=True)
                    return demo, true_label, orig_prob, temp_label, is_success, variable_names, names_to_importance_score, nb_changed_var, nb_changed_pos, replaced_words, \
                    bleus[index], rouges[index], meteors[index]
                else:
                    # 如果没有攻击成功，我们看probability的修改
                    gap = current_prob - temp_label
                    # 并选择那个最大的gap.
                    if gap > most_gap:
                        most_gap = gap
                        candidate = substitute_list[index]
                        answer = answers[index]
                        bleu = bleus[index]
                        meteor = meteors[index]
                        rouge = rouges[index]

            if most_gap > 0:
                nb_changed_var += 1
                nb_changed_pos += len(names_positions_dict[tgt_word])
                current_prob = current_prob - most_gap
                replaced_words[tgt_word] = candidate
                for i in range(icl_num):
                    final_code[i] = get_example(final_code[i], tgt_word, substitute, "c")
                print("%s ACC! %s => %s (%.5f => %.5f)" % \
                      ('>>', tgt_word, candidate,
                       current_prob + most_gap,
                       current_prob), flush=True)
            else:
                replaced_words[tgt_word] = tgt_word

            adv_code = final_code
        item = {
            'query': query,
            'demo': final_code,
        }
        with open(adv_demo_filepath, "a") as wf:
            wf.write(json.dumps(item) + '\n')
        with open(adv_answer_filepath, "a") as wf:
            wf.write(json.dumps(answer) + '\n')

        return demo, true_label, orig_prob, temp_label, is_success, variable_names, names_to_importance_score, nb_changed_var, nb_changed_pos, replaced_words, bleu, rouge, meteor


class MHM_Attacker():
    def __init__(self, args, model_tgt, model_mlm, tokenizer_mlm, _token2idx, _idx2token) -> None:
        self.classifier = model_tgt
        self.model_mlm = model_mlm
        self.token2idx = _token2idx
        self.idx2token = _idx2token
        self.args = args
        self.tokenizer_mlm = tokenizer_mlm

    def mcmc(self, tokenizer, substituions, code=None, _label=None, _n_candi=30,
             _max_iter=100, _prob_threshold=0.95, _orig_prob=0):
        identifiers, code_tokens = get_identifiers(code, 'java')
        prog_length = len(code_tokens)
        processed_code = " ".join(code_tokens)

        words, sub_words, keys = _tokenize(processed_code, tokenizer)
        raw_tokens = copy.deepcopy(words)
        variable_names = list(substituions.keys())

        uid = get_identifier_posistions_from_code(words, variable_names)

        code_candidate = []

        if len(uid) <= 0:  # 是有可能存在找不到变量名的情况的.
            code_candidate.append((code, np.float64(1)))
            return {'succ': None, 'tokens': None, 'raw_tokens': None}, code_candidate

        variable_substitue_dict = {}

        for tgt_word in uid.keys():
            variable_substitue_dict[tgt_word] = substituions[tgt_word]

        if len(variable_substitue_dict) <= 0:  # 是有可能存在找不到变量名的情况的.
            code_candidate.append((code, np.float64(1)))
            return {'succ': None, 'tokens': None, 'raw_tokens': None}, code_candidate

        old_uids = {}
        old_uid = ""

        for iteration in range(1, 1 + _max_iter):
            # 这个函数需要tokens
            res = self.__replaceUID(_tokens=code, _label=_label, _uid=uid,
                                    substitute_dict=variable_substitue_dict,
                                    _n_candi=_n_candi,
                                    _prob_threshold=_prob_threshold,
                                    _orig_prob = _orig_prob)
            self.__printRes(_iter=iteration, _res=res, _prefix="  >> ")

            if res['status'].lower() in ['r'] or iteration % 10 == 9:
                code_candidate.append((res['tokens'], np.float64(res['new_prob'])))
            if res['status'].lower() in ['s', 'a']:
                if iteration == 1:
                    code_candidate.append((code, np.float64(0)))
                    old_uids[res["old_uid"]] = []
                    old_uids[res["old_uid"]].append(res["new_uid"])
                    old_uid = res["old_uid"]

                flag = 0
                for k in old_uids.keys():
                    if res["old_uid"] == old_uids[k][-1]:
                        flag = 1
                        old_uids[k].append(res["new_uid"])
                        old_uid = k
                        break
                if flag == 0:
                    old_uids[res["old_uid"]] = []
                    old_uids[res["old_uid"]].append(res["new_uid"])
                    old_uid = res["old_uid"]

                code = res['tokens']
                uid[res['new_uid']] = uid.pop(res['old_uid'])  # 替换key，但保留value.
                variable_substitue_dict[res['new_uid']] = variable_substitue_dict.pop(res['old_uid'])
                for i in range(len(raw_tokens)):
                    if raw_tokens[i] == res['old_uid']:
                        raw_tokens[i] = res['new_uid']
                if res['status'].lower() == 's':
                    replace_info = {}
                    nb_changed_pos = 0
                    for uid_ in old_uids.keys():
                        replace_info[uid_] = old_uids[uid_][-1]
                        nb_changed_pos += len(uid[old_uids[uid_][-1]])
                    code_candidate.append((code, np.float64(res['new_prob'][res['old_pred']])))
                    return {'succ': True, 'tokens': code,
                            'raw_tokens': raw_tokens, "prog_length": prog_length, "new_pred": res["new_pred"],
                            "is_success": 1, "old_uid": old_uid, "score_info": res["old_prob"] - res["new_prob"],
                            "nb_changed_var": len(old_uids), "nb_changed_pos": nb_changed_pos,
                            "replace_info": replace_info, "attack_type": "MHM"}, code_candidate
        replace_info = {}
        nb_changed_pos = 0
        for uid_ in old_uids.keys():
            replace_info[uid_] = old_uids[uid_][-1]
            nb_changed_pos += len(uid[old_uids[uid_][-1]])
        return {'succ': False, 'tokens': res['tokens'], 'raw_tokens': None, "prog_length": prog_length,
                "new_pred": res["new_pred"], "is_success": -1, "old_uid": old_uid,
                "score_info": res["old_prob"] - res["new_prob"], "nb_changed_var": len(old_uids),
                "nb_changed_pos": nb_changed_pos, "replace_info": replace_info, "attack_type": "MHM"}, code_candidate

    def mcmc_random(self, tokenizer, substituions, code=None, _label=None, _n_candi=30,
                    _max_iter=100, _prob_threshold=0.95):
        identifiers, code_tokens = get_identifiers(code, 'c')
        processed_code = " ".join(code_tokens)
        prog_length = len(code_tokens)
        words, sub_words, keys = _tokenize(processed_code, tokenizer)
        raw_tokens = copy.deepcopy(words)
        variable_names = list(substituions.keys())

        uid = get_identifier_posistions_from_code(words, variable_names)

        if len(uid) <= 0:  # 是有可能存在找不到变量名的情况的.
            return {'succ': None, 'tokens': None, 'raw_tokens': None}

        variable_substitue_dict = {}
        for tgt_word in uid.keys():
            variable_substitue_dict[tgt_word] = substituions[tgt_word]

        old_uids = {}
        old_uid = ""
        for iteration in range(1, 1 + _max_iter):
            # 这个函数需要tokens
            res = self.__replaceUID_random(_tokens=code, _label=_label, _uid=uid,
                                           substitute_dict=variable_substitue_dict,
                                           _n_candi=_n_candi,
                                           _prob_threshold=_prob_threshold)
            self.__printRes(_iter=iteration, _res=res, _prefix="  >> ")

            if res['status'].lower() in ['s', 'a']:
                if iteration == 1:
                    old_uids[res["old_uid"]] = []
                    old_uids[res["old_uid"]].append(res["new_uid"])
                    old_uid = res["old_uid"]

                flag = 0
                for k in old_uids.keys():
                    if res["old_uid"] == old_uids[k][-1]:
                        flag = 1
                        old_uids[k].append(res["new_uid"])
                        old_uid = k
                        break
                if flag == 0:
                    old_uids[res["old_uid"]] = []
                    old_uids[res["old_uid"]].append(res["new_uid"])
                    old_uid = res["old_uid"]

                code = res['tokens']
                uid[res['new_uid']] = uid.pop(res['old_uid'])  # 替换key，但保留value.
                variable_substitue_dict[res['new_uid']] = variable_substitue_dict.pop(res['old_uid'])

                for i in range(len(raw_tokens)):
                    if raw_tokens[i] == res['old_uid']:
                        raw_tokens[i] = res['new_uid']
                if res['status'].lower() == 's':
                    replace_info = {}
                    nb_changed_pos = 0
                    for uid_ in old_uids.keys():
                        replace_info[uid_] = old_uids[uid_][-1]
                        nb_changed_pos += len(uid[old_uids[uid_][-1]])
                    return {'succ': True, 'tokens': code,
                            'raw_tokens': raw_tokens, "prog_length": prog_length, "new_pred": res["new_pred"],
                            "is_success": 1, "old_uid": old_uid, "score_info": res["old_prob"][0] - res["new_prob"][0],
                            "nb_changed_var": len(old_uids), "nb_changed_pos": nb_changed_pos,
                            "replace_info": replace_info, "attack_type": "MHM-Origin"}
        replace_info = {}
        nb_changed_pos = 0

        for uid_ in old_uids.keys():
            replace_info[uid_] = old_uids[uid_][-1]
            nb_changed_pos += len(uid[old_uids[uid_][-1]])

        return {'succ': False, 'tokens': res['tokens'], 'raw_tokens': None, "prog_length": prog_length,
                "new_pred": res["new_pred"], "is_success": -1, "old_uid": old_uid,
                "score_info": res["old_prob"][0] - res["new_prob"][0], "nb_changed_var": len(old_uids),
                "nb_changed_pos": nb_changed_pos, "replace_info": replace_info, "attack_type": "MHM-Origin"}

    def __replaceUID(self, _tokens, _label=None, _uid={}, substitute_dict={},
                     _n_candi=30, _prob_threshold=0.95, _candi_mode="random",_orig_prob=0):

        assert _candi_mode.lower() in ["random", "nearby"]

        selected_uid = random.sample(substitute_dict.keys(), 1)[0]  # 选择需要被替换的变量名
        if _candi_mode == "random":
            # First, generate candidate set.
            # The transition probabilities of all candidate are the same.
            candi_token = [selected_uid]
            candi_tokens = [copy.deepcopy(_tokens)]
            candi_labels = [_label]
            for c in random.sample(substitute_dict[selected_uid],
                                   min(_n_candi, len(substitute_dict[selected_uid]))):  # 选出_n_candi数量的候选.
                if c in _uid.keys():
                    continue
                if isUID(c):  # 判断是否是变量名.
                    candi_token.append(c)
                    candi_tokens.append(copy.deepcopy(_tokens))
                    candi_labels.append(_label)
                    candi_tokens[-1] = get_example(candi_tokens[-1], selected_uid, c, "c")
                    # for i in _uid[selected_uid]: # 依次进行替换.
                    #     if i >= len(candi_tokens[-1]):
                    #         break
                    #     candi_tokens[-1][i] = c # 替换为新的candidate.
            new_example = []
            for tmp_tokens in candi_tokens:
                tmp_code = tmp_tokens
                new_feature = convert_code_to_features_codellama(tmp_code, self.tokenizer_mlm, _label, self.args)
                new_example.append(new_feature)
            # new_example = new_example[8:]
            new_dataset = CodeDataset_generate(new_example)
            prob = self.classifier.get_results(new_dataset, self.args.eval_batch_size)

            for i in range(len(candi_token)):  # Find a valid example
            # for i in range(2):  # Find a valid example
                if prob[i] <= _orig_prob[0]*0.5:  # 如果有样本攻击成功

                    return {"status": "s", "alpha": 1, "tokens": candi_tokens[i],
                            "old_uid": selected_uid, "new_uid": candi_token[i],
                            "old_prob": prob[0], "new_prob": prob[i],
                            "old_pred": prob[0], "new_pred": prob[i], "nb_changed_pos": _tokens.count(selected_uid)}

            candi_idx = 0
            min_prob = 1000

            for idx, a_prob in enumerate(prob[1:]):
                if a_prob < min_prob:
                    candi_idx = idx + 1
                    min_prob = a_prob

            # 找到Ground_truth对应的probability最小的那个mutant
            # At last, compute acceptance rate.
            alpha = (1 - prob[candi_idx] + 1e-10) / (1 - prob[0] + 1e-10)
            # 计算这个id对应的alpha值.
            if random.uniform(0, 1) > alpha or alpha < _prob_threshold:

                return {"status": "r", "alpha": alpha, "tokens": candi_tokens[i],
                        "old_uid": selected_uid, "new_uid": candi_token[i],
                        "old_prob": prob[0], "new_prob": prob[i],
                        "old_pred": prob[0], "new_pred": prob[i], "nb_changed_pos": _tokens.count(selected_uid)}
            else:
                return {"status": "a", "alpha": alpha, "tokens": candi_tokens[i],
                        "old_uid": selected_uid, "new_uid": candi_token[i],
                        "old_prob": prob[0], "new_prob": prob[i],
                        "old_pred": prob[0], "new_pred": prob[i], "nb_changed_pos": _tokens.count(selected_uid)}
        else:
            pass

    def __replaceUID_random(self, _tokens, _label=None, _uid={}, substitute_dict={},
                            _n_candi=30, _prob_threshold=0.95, _candi_mode="random"):

        assert _candi_mode.lower() in ["random", "nearby"]

        selected_uid = random.sample(substitute_dict.keys(), 1)[0]  # 选择需要被替换的变量名
        if _candi_mode == "random":
            # First, generate candidate set.
            # The transition probabilities of all candidate are the same.
            candi_token = [selected_uid]
            candi_tokens = [copy.deepcopy(_tokens)]
            candi_labels = [_label]
            for c in random.sample(self.idx2token, _n_candi):  # 选出_n_candi数量的候选.
                if c in _uid.keys():
                    continue
                if isUID(c):  # 判断是否是变量名.
                    candi_token.append(c)
                    candi_tokens.append(copy.deepcopy(_tokens))
                    candi_labels.append(_label)
                    candi_tokens[-1] = get_example(candi_tokens[-1], selected_uid, c, "c")
                    # for i in _uid[selected_uid]: # 依次进行替换.
                    #     if i >= len(candi_tokens[-1]):
                    #         break
                    #     candi_tokens[-1][i] = c # 替换为新的candidate.

            new_example = []
            for tmp_tokens in candi_tokens:
                tmp_code = tmp_tokens
                new_feature = convert_code_to_features(tmp_code, self.tokenizer_mlm, _label, self.args)
                new_example.append(new_feature)
            new_dataset = CodeDataset(new_example)
            prob, pred = self.classifier.get_results(new_dataset, self.args.eval_batch_size)

            for i in range(len(candi_token)):  # Find a valid example
                if pred[i] != _label:  # 如果有样本攻击成功
                    return {"status": "s", "alpha": 1, "tokens": candi_tokens[i],
                            "old_uid": selected_uid, "new_uid": candi_token[i],
                            "old_prob": prob[0], "new_prob": prob[i],
                            "old_pred": pred[0], "new_pred": pred[i], "nb_changed_pos": _tokens.count(selected_uid)}

            candi_idx = 0
            min_prob = 1.0

            for idx, a_prob in enumerate(prob[1:]):
                if a_prob[_label] < min_prob:
                    candi_idx = idx + 1
                    min_prob = a_prob[_label]

            # 找到Ground_truth对应的probability最小的那个mutant
            # At last, compute acceptance rate.
            alpha = (1 - prob[candi_idx][_label] + 1e-10) / (1 - prob[0][_label] + 1e-10)
            # 计算这个id对应的alpha值.
            if random.uniform(0, 1) > alpha or alpha < _prob_threshold:
                return {"status": "r", "alpha": alpha, "tokens": candi_tokens[i],
                        "old_uid": selected_uid, "new_uid": candi_token[i],
                        "old_prob": prob[0], "new_prob": prob[i],
                        "old_pred": pred[0], "new_pred": pred[i], "nb_changed_pos": _tokens.count(selected_uid)}
            else:
                return {"status": "a", "alpha": alpha, "tokens": candi_tokens[i],
                        "old_uid": selected_uid, "new_uid": candi_token[i],
                        "old_prob": prob[0], "new_prob": prob[i],
                        "old_pred": pred[0], "new_pred": pred[i], "nb_changed_pos": _tokens.count(selected_uid)}
        else:
            pass

    def __printRes(self, _iter=None, _res=None, _prefix="  => "):
        if _res['status'].lower() == 's':  # Accepted & successful
            print("%s iter %d, SUCC! %s => %s (%d => %d, %.5f => %.5f) a=%.3f" % \
                  (_prefix, _iter, _res['old_uid'], _res['new_uid'],
                   _res['old_pred'], _res['new_pred'],
                   _res['old_prob'][_res['old_pred']],
                   _res['new_prob'][_res['old_pred']], _res['alpha']), flush=True)
        elif _res['status'].lower() == 'r':  # Rejected
            print("%s iter %d, REJ. %s => %s (, %.5f => %.5f) a=%.3f" % \
                  (_prefix, _iter, _res['old_uid'], _res['new_uid'],
                   _res['old_pred'], _res['new_pred'],
                   # _res['old_prob'][_res['old_pred']],
                   # _res['new_prob'][_res['old_pred']],
                   _res['alpha']), flush=True)
        elif _res['status'].lower() == 'a':  # Accepted
            print("%s iter %d, ACC! %s => %s (, %.5f => %.5f) a=%.3f" % \
                  (_prefix, _iter, _res['old_uid'], _res['new_uid'],
                   _res['old_pred'], _res['new_pred'],
                   # _res['old_prob'][_res['old_pred']],
                   # _res['new_prob'][_res['old_pred']],
                   _res['alpha']), flush=True)