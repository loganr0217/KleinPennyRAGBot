# Using deepeval to test model
import deepeval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.metrics import FaithfulnessMetric
from deepeval.metrics import ContextualRecallMetric
from deepeval.metrics import ContextualPrecisionMetric
from deepeval.metrics import ContextualRelevancyMetric

import requests
import json
from tqdm import tqdm

from mySecrets import Secrets
import os
os.environ["OPENAI_API_KEY"] = Secrets.OPENAI_API_KEY

inputs = [
    "Help me find a 5 bedroom apartment with a balcony.",
    "Do any of these have a laundry room?",
    "What about stainless steel appliances?"
]

expected_outputs = [
    "33 Fern St Apt B, 33 Fern St Apt C, 33 Fern St Apt D",
    "33 Fern St Apt B, 33 Fern St Apt D",
    "33 Fern St Apt B"
]


# Creating a test for each input/output pair
tests = []
for testIndex in range(len(inputs)):
    # Getting response from model
    response = requests.get("http://127.0.0.1:8000/askFull?question=" + inputs[testIndex])
    responseArray = json.loads(response.text)
    currentContext = [str(i) for i in responseArray[1]]
    # print(response["answer"])
    test_case = LLMTestCase(
        input=inputs[0],
        expected_output=expected_outputs[testIndex],
        actual_output=";".join(responseArray[2]),
        retrieval_context=currentContext
    )

    tests.append(test_case)

# Doing tests for each metric
for testId in range(len(tests)):
    print("Test Metrics:")
    for metric in tqdm([AnswerRelevancyMetric(threshold=0.4), FaithfulnessMetric(threshold=0.4), ContextualRecallMetric(threshold=0.4), ContextualPrecisionMetric(threshold=0.4), ContextualRelevancyMetric(threshold=0.25)]):
        assert_test(tests[testId], [metric])