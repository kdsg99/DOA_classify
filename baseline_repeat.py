from openai import OpenAI
import json
import requests
from tqdm import tqdm
from argparse import ArgumentParser
import tiktoken
from util_fuc.data_preprocess import data_preprocess



def parse_args():
    parser = ArgumentParser()
    parser.add_argument("data_path", type=str)
    parser.add_argument("model", type=str)
    parser.add_argument("--strategy", type=str)
    

class SiliconMobilityClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def create_completion(self, model, messages, temperature):
        # 构造请求的URL
        url = f"{self.base_url}/completions"
        
        # 构造请求的headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构造请求的payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 检查响应状态
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")


class Agent:
    
    def __init__(self, profile):
        self.profile = profile
        self.base_url = profile["base_url"]
        self.api_key = profile["api_key"]
        self.model =profile["model"] 
        self.style = None
        self.client =  OpenAI(api_key=self.api_key, base_url=self.base_url)
        
    def silicon_client(self):
        self.client = SiliconMobilityClient(self.api_key, self.base_url)
        self.style = "silicon"
        return self
    
    
    def init_history(self):
        self.history = []
        
    def assistance(self):
        self.character = "assistance"
        self.history = []
        self.prompt =  "You are an AI assistance. Please answer the following question: {instruct}"
        return self
    


    def fit_messages(self, messages, max_tokens=None, reserve_output=4096):
        if max_tokens is None:
                max_tokens = 128000    
                
        # 计算单个 message 的 token 数
        def count(msg, encoding):
            return 3 + len(encoding.encode(msg.get("content", "")))
        
        if self.model == "deepseek-r1":
            return messages
        else:
            encoding = tiktoken.encoding_for_model(self.model)
            kept = []
            current = 0
            for msg in reversed(messages):
                cnt = count(msg, encoding)
                if current + cnt + reserve_output > max_tokens:
                    break
                kept.append(msg)
                current += cnt
            return list(reversed(kept))
                
        
        
    def talk(self, new_input,):
        
        max_history = 10
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]
            
        # initialize the initial problem
        if len(self.history) == 0:
            self.instruct = new_input
            template = self.prompt.format(instruct = f"{new_input} \n {new_input}" )
            self.history.append({"role": "user", "content": template})
                
                
        if self.character == "assistance":
            messages = self.history
            safe_messages = self.fit_messages(messages)
            if self.style == "silicon":
                resp = self.client.create_completion(self.model, messages, temperature=0.7)
            else:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=safe_messages,
                    temperature=0.7,
                )
            reply = resp.choices[0].message.content.strip()
            self.history.append({"role": "assistant", "content": reply})
            return reply
                
                
        if self.character == "user":
            
            if len(self.history) == 1:
                print("please provide initial answer first!")
            else:
                strategy_prompt = self.stra_deposit[self.strategy]
                
                template = self.prompt.format(question=self.history[0]['content'], ai_answer=new_input, strategy= strategy_prompt)
                # template = self.prompt.format(question=self.history, ai_answer=new_input, strategy= strategy_prompt)
            
            messages = [{"role": "user", "content": template}]
            safe_messages = self.fit_messages(messages)
            if self.style == "silicon":
                resp = self.client.create_completion(self.model, messages, temperature=0.7)
            else:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=safe_messages,
                    temperature=0.7,
                )
            reply = resp.choices[0].message.content.strip()
            self.history.append({"role": "user", "content": reply})
        
            return reply
        
        
if __name__ == "__main__":
        
    dataset = data_preprocess("/home/david/DOA/arena_hard.jsonl")
    print(dataset[-1])
    
    # ass_profile = {"api_key": 'sk-rtmnzyiqgztmryigadibhsqmycljueukzenqznmmsrclixqq',
    #     "base_url" : 'https://api.siliconflow.cn/v1/chat/completions',
    #     "model" : "deepseek-r1",
    #     "temperature" : 0.7
    # }
    
    # user_profile = {"api_key": 'sk-RYEOMdOQMbuWuchG6f226e24F2Ed48D78fB3Bb920409B4A9',
    #     "base_url" : 'https://api.ai-gaochao.cn/v1',
    #     "model" : "gpt-4o-mini",
    #     "temperature" : 0.7
    # }
    
    
    
    # ass_profile = {"api_key": 'sk-BljycZgZu2FaUhX9407aB393C63848D1Af786e7322D23763',
    #     "base_url" : 'https://api.ai-gaochao.cn/v1',
    #     "model" : "gpt-4o-mini",
    #     "temperature" : 0.7
    # }

    
    # user_profile = {"api_key": 'sk-BljycZgZu2FaUhX9407aB393C63848D1Af786e7322D23763',
    #     "base_url" : 'https://api.ai-gaochao.cn/v1',
    #     "model" : "gpt-4o-mini",
    #     "temperature" : 0.7
    # }
    
    
    # ass:Qwen user:Gpt-4o-mini
    ass_profile = {"api_key": 'sk-BljycZgZu2FaUhX9407aB393C63848D1Af786e7322D23763',
        "base_url" : 'https://api.ai-gaochao.cn/v1',
        "model" : "gpt-4o-mini",
        "temperature" : 0.7
    }
    
    user_profile = {"api_key": 'sk-BljycZgZu2FaUhX9407aB393C63848D1Af786e7322D23763',
        "base_url" : 'https://api.ai-gaochao.cn/v1',
        "model" : "gpt-4o-mini",
        "temperature" : 0.7
    }


    

    # strategies = ["PLAIN"]
    
    assistance = Agent(ass_profile).assistance()        
    
    cdataset = []
    # p = 0
    try:
        for dial in tqdm(dataset):
            # if p >=1:
            #     break
            # p = p + 1
                
            assistance.init_history()
           
            
            instruction = dial['instruction']
            output_ground = dial['output']
            
            try:
                answer = assistance.talk(instruction)
                history_backup = assistance.history
            except:
                answer = "fail to have answer"
                history_backup = assistance.history.append({'role':assistance, "content":answer})
                

            result = {"strategy":"repeat",'content':{'instruction':instruction, "final_answer":answer}}
            multi_strategy_results = [result]
            
            cdataset.append(multi_strategy_results)
            
        with open("./baseline_repeat_arena_hard.jsonl", "w") as fw:
            json.dump(cdataset, fw, indent=4)
            
    except:
        with open("./baseline_repeat_arena_hard.jsonl", "w") as fw:
            json.dump(cdataset, fw, indent=4)



# multi_term
# init_answer = assistance.talk(instruction)
# re_ask = user.talk(init_answer)
# re_answer = assistance.talk(re_ask, assistance.history)
# re_ask = user.talk(re_answer, user_history)



