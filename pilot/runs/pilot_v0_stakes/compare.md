# Pilot comparison

| Measure | pilot_v0 | pilot_v0_stakes |
|---|---:|---:|
| Seeds with an accepted gap | 16 | 5 |
| Gaps proposed | 28 | 9 |
| Gaps accepted | 22 | 5 |
| Builder skips | 1 | 11 |
| Check 1 fails | 6 | 4 |
| Model calls (subagent invocations) | 48 | 29 |
| Wall clock (seconds) | 1466.3283470650204 | 934.540578961838 |

Source: each run’s summary.json and per-seed audit files. Values, stakes sentences, skip reasons, and Check 1 results below are copied from those files. No quality judgments or owner overrides are applied.

Both runs requested fresh GPT-6.1 Sol/high subagents. Token usage and provider-served model identity were unavailable in both runs.

## BigCodeBench/1023

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | non_numeric_exception_type: TypeError → ValueError | non_numeric_column_handling: Raises TypeError if any column in the DataFrame is non-numeric. → Exclude non-numeric columns and continue with the remaining numeric columns.<br>Stakes: The alternative would silently analyze only part of a mixed-type DataFrame and produce a plot when the user required rejecting the input. |
| Check 1 rejections | None. | None. |

## BigCodeBench/398

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | file_format: JSON → Pickle | Builder skip: The instruction specifies only the core validation goal and output type; it contains no explicit maskable parameter that preserves the task and changes the substantive result. |
| Check 1 rejections | None. | None. |

## BigCodeBench/1121

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | No accepted gaps. Seed status: rejected | Builder skip: The only explicit eligible behavior is returning None when an API request fails, but the gold solution does not implement it. No other clean maskable parameter meets all selection criteria. |
| Check 1 rejections | output_structure: A dictionary mapping domains to their geolocation data → A list of records containing each domain and its geolocation data<br>G4: leakage<br>Reader choice: original_value; confidence: 0.76<br>Clue spans: ["If an API request fails, the corresponding value will be None."] | None. |

## BigCodeBench/145

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | output_format: CSV → JSON | No accepted gaps. Seed status: rejected |
| Check 1 rejections | None. | address_selection: all IP addresses → usable host IP addresses only<br>G4: leakage<br>Reader choice: original_value; confidence: 0.9<br>Clue spans: ["listing IP addresses in the specified IP range", "Each IP address is written as a row in the CSV file."] |

## BigCodeBench/675

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | No accepted gaps. Seed status: rejected | Builder skip: No clean maskable parameter meets all criteria: file count and location define the core task, random-string generation has no stated selectable method, and resetting the cursor has no observable effect after the files are closed. |
| Check 1 rejections | cursor_position: the beginning of each file → the end of each file<br>G4: leakage<br>Reader choice: original_value; confidence: 0.65<br>Clue spans: ["reset the cursor"] | None. |

## BigCodeBench/654

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | matching_column: first column → last column<br><br>return_container: tuple → dictionary<br><br>returned_plot_object: matplotlib Axes object → matplotlib Figure object | matching_column: first column → last column<br>Stakes: Matching the last column could select different row indices and produce incorrect fitted parameters. |
| Check 1 rejections | None. | None. |

## BigCodeBench/77

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | authentication_failure_status: 401 → 403 | Builder skip: No clean maskable parameter qualifies. Credential values are arbitrary, HTTP status codes and response strings are excluded, and the instruction conflicts with the reference implementation about password encoding and invalid-input handling. |
| Check 1 rejections | None. | None. |

## BigCodeBench/608

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | column_pair_selection: random → deterministic<br><br>return_container: tuple → dictionary | Builder skip: The instruction provides no clean maskable parameter beyond the core row-removal and random-pairplot goals. Row-matching semantics and plot-count limits appear only in the gold solution, while the stated output types are excluded. |
| Check 1 rejections | None. | None. |

## BigCodeBench/333

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | output_container: tuple → list | Builder skip: Selecting the k smallest numbers defines the core task. The remaining explicit details are arbitrary numeric defaults, container types, and tool choices, with no qualifying maskable parameter. |
| Check 1 rejections | None. | None. |

## BigCodeBench/99

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | font_family: Arial → Times New Roman<br><br>species_coloring: colored by species → colored uniformly | Builder skip: The instruction specifies the core dataset and plot type; its remaining parameters concern plot styling, labels, titles, or return types, which are excluded. |
| Check 1 rejections | None. | None. |

## BigCodeBench/116

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | histogram_normalization: Frequency → Probability density | Builder skip: The normal distribution defines the core task, and all fixed parameters concern plot styling or output shape. No clean maskable parameter meets the selection rules. |
| Check 1 rejections | None. | None. |

## BigCodeBench/240

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | Builder skip: The instruction specifies truncation, but the gold solution uses rounding. The remaining details are arbitrary numeric defaults or a configurable column name, without a clean parameter having 2–5 realistic values. | Builder skip: The instruction specifies truncation, but the gold solution uses rounding, so that parameter is ineligible. The remaining details are arbitrary numeric defaults, names, or container choices rather than clean maskable parameters. |
| Check 1 rejections | None. | None. |

## BigCodeBench/426

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | return_container: tuple → list | No accepted gaps. Seed status: rejected |
| Check 1 rejections | output_image_format: jpg → png<br>G4: leakage<br>Reader choice: original_value; confidence: 0.6<br>Clue spans: ["image_path='image.jpg'"] | threshold_integer_requirement: an integer → any real number<br>G4: leakage<br>Reader choice: original_value; confidence: 0.7<br>Clue spans: ["threshold=128", "range 0-255"] |

## BigCodeBench/94

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | display_precision: two decimal places → three decimal places<br><br>histogram_binning: 30 → automatic bin selection | Builder skip: The normal distribution and PDF overlay define the core task. The remaining explicit choices concern plot styling, display formatting, or return containers, which are excluded. |
| Check 1 rejections | None. | None. |

## BigCodeBench/1105

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | return_container: tuple → list | Builder skip: The duration requirement defines the core verification task, while the remaining explicit details concern excluded return types and message formatting. No clean maskable parameter is stated in the instruction and implemented by the gold solution. |
| Check 1 rejections | None. | None. |

## BigCodeBench/743

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | input_file_format: JSON → YAML | No accepted gaps. Seed status: rejected |
| Check 1 rejections | None. | key_matching_rule: starting with → containing<br>G4: leakage<br>Reader choice: original_value; confidence: 0.82<br>Clue spans: ["PATTERNS = [\"is_\", \"has_\", \"can_\", \"should_\"]"] |

## BigCodeBench/161

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | timestamp_format: YYYY-MM-DD HH:MM:SS → DD/MM/YYYY HH:MM:SS | invalid_timestamp_handling: raise the exception for: ValueError: If the timestamp in any log entry is invalid → Skip entries with invalid timestamps and continue processing the remaining entries.<br>Stakes: Skipping an entry with an invalid timestamp would produce an incomplete CSV instead of rejecting the log as the user requires. |
| Check 1 rejections | output_format: CSV → JSON<br>G4: leakage<br>Reader choice: original_value; confidence: 0.65<br>Clue spans: ["import pandas as pd"] | None. |

## BigCodeBench/541

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | output_collection_type: list → set<br><br>installation_command: pip install {package_name} → uv pip install {package_name} | missing_package_handling: raise the exception → return an empty list when the package is not installed or cannot be found<br>Stakes: Returning an empty list would misrepresent a missing package as a successful operation with no modules added, instead of reporting the required failure. |
| Check 1 rejections | exception_type: ImportError → ModuleNotFoundError<br>G4: leakage<br>Reader choice: alternative_value; confidence: 0.6<br>Clue spans: ["If the package is not installed or cannot be found."] | None. |

## BigCodeBench/480

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | substring_delimiter: commas → semicolons | substring_delimiter: commas → semicolons<br>Stakes: Splitting on semicolons would leave comma-separated components together, so the intended substrings would not be shuffled. |
| Check 1 rejections | None. | None. |

## BigCodeBench/1030

| Result | pilot_v0 | pilot_v0_stakes |
|---|---|---|
| Accepted gaps / builder skip | No accepted gaps. Seed status: rejected | No accepted gaps. Seed status: rejected |
| Check 1 rejections | letter_replacement: with replacement → without replacement<br>G4: leakage<br>Reader choice: alternative_value; confidence: 0.74<br>Clue spans: ["all possible combinations of three letters from the alphabet", "unique combination of three letters"] | letter_replacement: with replacement → without replacement<br>G4: leakage<br>Reader choice: alternative_value; confidence: 0.8<br>Clue spans: ["all possible combinations of three letters", "import itertools"] |
