# Stage 1 pilot review — `../runs/selftest`

LLM cost: $0.000 over 1 calls.

Diff notation: `[-removed-]{+inserted+}`.

| seed | status | subparts (verdict) |
|---|---|---|
| BigCodeBench/232 | accepted | `oracle_dedup` accepted; `null_noop` rejected; `null_missing_span` rejected; `null_unrelated` rejected; `distractor_msg` accepted; `oracle_bad_testmut` needs_review |

---

## BigCodeBench/232 — accepted

### oracle_dedup `oracle_dedup` → **accepted**

- Reason: flips ['test_case_with_duplicates']; alt solution passes alt tests; gold fails alt tests
- Category / Answer Source: Task / User
- Builder said crucial: True → test-run says: True
- original_value: `orig oracle_dedup`
- alternative_values: ['alt oracle_dedup']
- Failing tests under mutation: ['test_case_with_duplicates'] (builder's target_tests: ['test_case_with_duplicates'])

Gold mutation:

``````diff
-     df = df.drop_duplicates(subset='Customer')
``````

Test mutation:

``````diff
- expected_output = {'Total Sales': 1200, 'Most Popular Category': 'Electronics'}
+ expected_output = {'Total Sales': 1400, 'Most Popular Category': 'Electronics'}
``````

Masked instruction (single-gap) vs. full:

``````text
Generate a sales report from a DataFrame[-, excluding duplicate customer names-]. The report includes total sales and the most popular sales category.
Note that: The function would return the first category in alphabetical order for "Most Popular Category' in the case of tie
The function should raise the exception for: The function will raise a ValueError is input df is not a DataFrame.
The function should output with:
    dict: A dictionary with keys 'Total Sales' (sum of sales) and 'Most Popular Category' (most frequent category).
You should write self-contained code starting with:
```
import pandas as pd
import collections
def task_func(df):
```
``````
### null_noop `null_noop` → **rejected**

- Reason: gold mutation is a no-op
- Category / Answer Source: Task / User
- Builder said crucial: True → test-run says: n/a
- original_value: `orig null_noop`
- alternative_values: ['alt null_noop']
- Failing tests under mutation: n/a (builder's target_tests: [])

Gold mutation:

``````diff
- total_sales = df
+ total_sales = df
``````

Masked instruction (single-gap) vs. full:

``````text
Generate a sales report from a DataFrame, excluding duplicate customer names. The report includes[- total-] sales and the most popular sales category.
Note that: The function would return the first category in alphabetical order for "Most Popular Category' in the case of tie
The function should raise the exception for: The function will raise a ValueError is input df is not a DataFrame.
The function should output with:
    dict: A dictionary with keys 'Total Sales' (sum of sales) and 'Most Popular Category' (most frequent category).
You should write self-contained code starting with:
```
import pandas as pd
import collections
def task_func(df):
```
``````
### null_missing_span `null_missing_span` → **rejected**

- Reason: splice: null_missing_span: span not found (not in full_instruction): 'excluding duplicate customers'
- Category / Answer Source: Task / User
- Builder said crucial: True → test-run says: n/a
- original_value: `orig null_missing_span`
- alternative_values: ['alt null_missing_span']
- Failing tests under mutation: n/a (builder's target_tests: ['test_case_with_duplicates'])

Gold mutation:

``````diff
-     df = df.drop_duplicates(subset='Customer')
``````
### null_unrelated `null_unrelated` → **rejected**

- Reason: mutation also breaks tests outside target_tests: ['test_case_6']
- Category / Answer Source: Task / User
- Builder said crucial: True → test-run says: n/a
- original_value: `orig null_unrelated`
- alternative_values: ['alt null_unrelated']
- Failing tests under mutation: ['test_case_6'] (builder's target_tests: ['test_case_regular'])

Gold mutation:

``````diff
- raise ValueError("The input df
+ raise TypeError("The input df
``````

Masked instruction (single-gap) vs. full:

``````text
Generate a sales report from a DataFrame, excluding duplicate customer names. The report includes[- total-] sales and the most popular sales category.
Note that: The function would return the first category in alphabetical order for "Most Popular Category' in the case of tie
The function should raise the exception for: The function will raise a ValueError is input df is not a DataFrame.
The function should output with:
    dict: A dictionary with keys 'Total Sales' (sum of sales) and 'Most Popular Category' (most frequent category).
You should write self-contained code starting with:
```
import pandas as pd
import collections
def task_func(df):
```
``````
### distractor_msg `distractor_msg` → **accepted**

- Reason: no test flips -> Non-Crucial (test_run); builder claimed Crucial, overridden
- Category / Answer Source: Task / User
- Builder said crucial: True → test-run says: False
- original_value: `orig distractor_msg`
- alternative_values: ['alt distractor_msg']
- Failing tests under mutation: [] (builder's target_tests: [])

Gold mutation:

``````diff
- The input df is not a DataFrame
+ Bad input
``````

Masked instruction (single-gap) vs. full:

``````text
Generate a sales report from a DataFrame, excluding duplicate customer names. The report includes total sales and the most popular sales category.
Note that: The function would return the first category in alphabetical order for "Most Popular Category' in the case of tie
The function should raise the exception for: The function will raise a ValueError [-is input df is not a DataFrame-]{+on bad input+}.
The function should output with:
    dict: A dictionary with keys 'Total Sales' (sum of sales) and 'Most Popular Category' (most frequent category).
You should write self-contained code starting with:
```
import pandas as pd
import collections
def task_func(df):
```
``````
### oracle_bad_testmut `oracle_bad_testmut` → **needs_review**

- Reason: flip verified, but find_in_tests occurs 0x (need 1); alt not verified
- Category / Answer Source: Task / User
- Builder said crucial: True → test-run says: True
- original_value: `orig oracle_bad_testmut`
- alternative_values: ['alt oracle_bad_testmut']
- Failing tests under mutation: ['test_case_with_duplicates'] (builder's target_tests: ['test_case_with_duplicates'])

Gold mutation:

``````diff
-     df = df.drop_duplicates(subset='Customer')
``````

Test mutation:

``````diff
- this string is not in the tests
+ x
``````

Masked instruction (single-gap) vs. full:

``````text
Generate a sales report from a DataFrame[-, excluding duplicate customer names-]. The report includes total sales and the most popular sales category.
Note that: The function would return the first category in alphabetical order for "Most Popular Category' in the case of tie
The function should raise the exception for: The function will raise a ValueError is input df is not a DataFrame.
The function should output with:
    dict: A dictionary with keys 'Total Sales' (sum of sales) and 'Most Popular Category' (most frequent category).
You should write self-contained code starting with:
```
import pandas as pd
import collections
def task_func(df):
```
``````
