# CCDV-F Mock Test

Browser-based timed mock exam for the Claude Certified Developer – Foundations (CCDV-F) exam.

## Run

```
python3 mock_exam.py
```

Requires only Python 3 (no packages). The exam opens in your browser at http://127.0.0.1:8765/.

- 53 questions per attempt (drawn from the bank in `questions.json`), 19 marks each, 1007 total
- "Select TWO" questions are all-or-nothing; no negative marking
- 120-minute countdown with auto-submit, question palette, mark for review
- Detailed report with correct answers and explanations; attempts saved to `results/`

## Options

```
--minutes 120        exam duration
--pass-percent 70    pass cut-off
--count 53           questions per attempt
--no-shuffle         fixed question/option order
--show-domain        show topic during the test
--port 8765
```
