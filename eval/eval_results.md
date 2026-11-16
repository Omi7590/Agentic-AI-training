# RAG Evaluation Results — RTI Mitra

## Configs compared

| Config | top_k | Description |
|--------|-------|-------------|
| Config A | 3 | Retrieve top 3 chunks per question |
| Config B | 5 | Retrieve top 5 chunks per question |

## Scoring

- Answerable question: PASS if answer does not contain 'I don't know'
- Unanswerable question (Q6): PASS if answer contains 'I don't know'

## Results table

| ID | Question | Answerable | Config A | Config B |
|----|----------|-----------|---------|----------|
| 1 | What is the RTI application fee in Maharashtra? | Yes | ✅ | ✅ |
| 2 | Within how many days must the PIO reply to an RTI? | Yes | ✅ | ✅ |
| 3 | Can I ask for information about my own panchayat in Marathi? | Yes | ✅ | ✅ |
| 4 | What is the fee for filing a first appeal in Maharashtra? | Yes | ✅ | ✅ |
| 5 | What is the RTI application fee for central government autho | Yes | ✅ | ✅ |
| 6 | What did the PIO of Kopargaon municipal council reply to RTI | No | ✅ | ✅ |
| 7 | Am I exempt from paying the RTI fee if I am below the povert | Yes | ✅ | ✅ |
| 8 | What happens if the PIO does not reply within 30 days? | Yes | ❌ | ✅ |
| 9 | Can I file RTI through an APIO at a post office, and does th | Yes | ✅ | ✅ |
| 10 | What information is exempt from disclosure under Section 8? | Yes | ✅ | ✅ |
| 11 | How many days does the PIO have to transfer a wrongly addres | Yes | ✅ | ✅ |
| 12 | What is the deadline for filing a second appeal? | Yes | ✅ | ✅ |
| 13 | Can I file RTI online for a Maharashtra state department? | Yes | ✅ | ✅ |
| 14 | Can I file RTI online for a central government ministry? | Yes | ✅ | ✅ |
| 15 | How many words can I use in an RTI application in Maharashtr | Yes | ✅ | ✅ |

## Scores

| Config | Score |
|--------|-------|
| Config A (top_k=3) | 14/15 |
| Config B (top_k=5) | 15/15 |

## Winner: Config B (top_k=5)

Top-5 retrieval scores higher — more context helps the LLM pick the right rule, especially for multi-part questions.
