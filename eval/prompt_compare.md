# Prompt Comparison — RTI Mitra

Comparing two system prompt versions on the 10 user questions.

---

## Prompt Version 1 — Basic

```
You are an RTI assistant. Answer questions about the RTI Act 2005 simply and clearly.
```

---

## Prompt Version 2 — Detailed (current system_prompt.txt)

The full prompt in prompts/system_prompt.txt with jurisdiction rules,
fee amounts, deadlines, and strict instructions for "I don't know" answers.

---

## Results on 10 questions

| Q# | Question (short) | V1 answer quality | V2 answer quality |
|----|-----------------|-------------------|-------------------|
| Q1 | RTI fee Maharashtra | Generic: "a small fee" | Specific: "Rs 10, nil for BPL" ✅ |
| Q2 | PIO reply deadline | "within 30 days" | "30 days, 35 via APIO, 48 hrs life/liberty" ✅ |
| Q3 | Marathi language | "yes you can" | Cites Section 6(1), mentions official language ✅ |
| Q4 | Draft RTI Kopargaon | Loose draft, no fee line | Filled template, correct fee, reply due date ✅ |
| Q5 | Central vs Maharashtra online | Lists both portals | Lists portals + explains process difference ✅ |
| Q6 | PIO replies last month | Hallucinated a reply ❌ | "I don't know — no access to live records" ✅ |
| Q7 | BPL fee exemption | "you may be exempt" | Cites Section 7(5), says nil fee ✅ |
| Q8 | No PIO reply in 30 days | "file a complaint" | Explains first appeal under Section 19(1) ✅ |
| Q9 | APIO at post office | Missed +5 days | Correctly adds 5 days, total 35 days ✅ |
| Q10 | Section 8 exemptions | Lists 2-3 exemptions | Lists all major exemptions, links to road-repair ✅ |

---

## Winner: Version 2

Version 1 fails on Q6 (hallucination) and gives vague answers on fees and deadlines.
Version 2 follows jurisdiction rules, computes deadlines, and correctly refuses Q6.
The detailed system prompt is essential for a legal-domain assistant like RTI Mitra.
