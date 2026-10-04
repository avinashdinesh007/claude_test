# CCDV-F Mock Test

Browser-based timed mock exam for the Claude Certified Developer – Foundations (CCDV-F) exam.

## Run

```
python3 mock_exam.py
```

Requires only Python 3 (no packages). The exam opens in your browser at http://127.0.0.1:8765/.

- 53 questions per attempt (drawn from the selected set's question bank), 19 marks each, 1007 total
- "Select TWO" questions are all-or-nothing; no negative marking
- 120-minute countdown with auto-submit, question palette, mark for review
- Detailed report with correct answers and explanations; attempts saved to `results/`

## Question sets

| Set | File | Command |
|-----|------|---------|
| 3 (newest, default) | `questions_set3.json` | `python3 mock_exam.py` |
| 2 | `questions_set2.json` | `python3 mock_exam.py --set 2` |
| 1 | `questions_set1.json` | `python3 mock_exam.py --set 1` |

Sets do not share questions. Progress is stored per set, so switching sets never mixes up saved attempts.

## Options

```
--minutes 120        exam duration
--pass-percent 70    pass cut-off
--set 3              question set (1, 2 or 3)
--questions FILE     use a custom question bank instead of --set
--count 53           questions per attempt
--no-shuffle         fixed question/option order
--show-domain        show topic during the test
--port 8765
```
