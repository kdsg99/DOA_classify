import json


def data_preprocess(data_path):
    with open(data_path) as f:
        odataset = [json.loads(line) for line in f]
    data_name = data_path.split("/")[-1]
    
    if data_name == "alpaca_eval.jsonl":
        return odataset
    
    elif data_name == "aime2024.jsonl":
        n_dataset = []
        for data in odataset:
            instruct = data['Problem']
            solution = data['Solution']
            answer = data['Answer']
            n_data = {"instruction":instruct + "Output the final answer in '\\boxed{}'", "output":solution + "The final answer is: " + str(answer)}
            n_dataset.append(n_data)
        return n_dataset
    
    elif data_name ==  "aime2025.jsonl":
        n_dataset = []
        for data in odataset:
            instruct = data['question']
            solution = data['answer']
            answer = data['answer']
            n_data = {"instruction":instruct + "Output the final answer in '\\boxed{}'", "output": "The final answer is: " + str(answer)}
            n_dataset.append(n_data)
        return n_dataset
    
    elif data_name == "polaris_data_0.01.jsonl":
        n_dataset = []
        for data in odataset:
            instruct = data['problem']
            answer = data['answer']
            n_data = {"instruction":instruct + "Output the final answer in '\\boxed{}'", "output":"The final answer is: " + str(answer)}
            n_dataset.append(n_data)
        return n_dataset
    
    elif data_name ==  "math500.jsonl":
        n_dataset = []
        for data in odataset:
            instruct = data['problem']
            solution = data['solution']
            answer = data['answer']
            n_data = {"instruction":instruct + "Output the final answer in '\\boxed{}'", "output":solution + "The final answer is: " + str(answer)}
            n_dataset.append(n_data)
        return n_dataset
    
    elif data_name ==  "OE_TO_physics_en_COMP.jsonl" or data_name ==  "TP_TO_physics_en_COMP.jsonl":
        n_dataset = []
        for data in odataset:
            instruct = data['question']
            solution = data['solution']
            context = data['context']
            answer = data['final_answer']
            n_data = {"instruction": f"{context}{instruct}".strip() + "Output the final answer in '\\boxed{}'", "output": f"{solution}" + "The final answer is: " + str(answer)}
            n_dataset.append(n_data)
        return n_dataset
    
    elif data_name == "mt-bench.jsonl":
        n_dataset = []
        for data in odataset:
            questions = data['turns']
            qst_1 = questions[0]
            qst_2 = questions[1]
            try:
                references = data['reference']
                ref_1 = references[0]
                ref_2 = references[1]
                n_data_1 = {"instruction":qst_1, "output":ref_1}
                n_data_2 = {"instruction":f"{qst_1}{ref_1}{qst_2}".strip(), "output":ref_2}
            except:
                n_data_1 = {"instruction":qst_1, "output":""}
                n_data_2 = {"instruction":qst_2, "output":""}
            n_dataset.append(n_data_1)
            n_dataset.append(n_data_2)
        return n_dataset
    
    
    elif data_name == "WildBench-V2.jsonl":
        n_dataset = []
        for data in odataset:
            convs = data['conversation_input']
            # only deal with single turn conversation
            if len(convs) > 1:                
                continue
            else:
                content = convs[0]
                instruct = content['content']
                answer = data['references']['gpt-4']
                n_data = {"instruction": f"{instruct}", "output": f"{answer}"}
                n_dataset.append(n_data)
        return n_dataset
        

    elif data_name == "arena_hard.jsonl":
        n_dataset = []
        for data in odataset:
            instruct = data['question']
            prediction = data['prediction']
            n_data = {"instruction":instruct, "output":prediction}
            n_dataset.append(n_data)
        return n_dataset
    
    elif data_name == "flask_hard.jsonl":
        n_dataset = []
        for data in odataset:
            instruct = data['instruction']
            answer = data['answer']
            n_data = {"instruction":instruct, "output":answer}
            n_dataset.append(n_data)
        return n_dataset
    