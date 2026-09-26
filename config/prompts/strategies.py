from langchain_core.prompts import PromptTemplate

STA_ENCOURAGE = PromptTemplate.from_template(
    '''
    "Encouragement": "By acknowledging effort, emphasizing potential and specific strengths, and adopting a positive, gentle, and affirming tone while avoiding exaggerated praise, this style aims to enhance the counterpart’s motivation and confidence, encouraging them to build upon their existing foundation of thought."
    '''
)

STA_HEURISTIC = PromptTemplate.from_template(
    '''
    "Heuristic": "By expressing one’s own doubts or motivations and adopting a neutral tone, this style aims to guide the counterpart toward autonomous thinking and reasoning, encouraging the exploration of multiple possible paths without providing direct hints."
    '''
)

STA_CRITICAL= PromptTemplate.from_template(
    '''
    "Critical": "By directly evaluating the response as inadequate or below standard and adopting a straightforward but non-personal tone, this style aims to force the counterpart to reorganize or self-check, while avoiding explanations of why it is inadequate."
    '''
)

STA_MISLEADING = PromptTemplate.from_template(
    '''
    "Misleading": "By deliberately creating cues inconsistent with the correct answer and delivering them in a confident and authoritative tone, this style aims to challenge the counterpart’s consistency without explicitly revealing the conflicting answer."
    '''
)

STA_PRESSURE= PromptTemplate.from_template(
    '''
    "Pressure": "By denying results, shifting responsibility, and creating guilt or expectancy pressure through a harsh and critical tone, this style aims to make the counterpart feel that their response does not meet expectations."
    '''
)
