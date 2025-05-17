from evaluation.evalScore import ragResponseEvaluator
import pandas as pd

ques = 'Tell me the most relevant stories?'
responses1, responses2 = ragResponseEvaluator().ragsEvalPipeline(questions=ques)

pd.DataFrame(responses1).to_csv('./outputs/score1.csv',index=False)
pd.DataFrame(responses2).to_csv('./outputs/score2.csv',index=False)