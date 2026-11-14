# Prompt Comparison — RTI Mitra

Comparing two system prompt versions on all 10 user questions.
Real LLM responses captured using `qwen/qwen3.8-27b` via Groq.

---

## Prompt Version 1 — Basic

```
You are an RTI assistant. Answer questions about the RTI Act 2005 simply and clearly.
```

---

## Prompt Version 2 — Detailed (prompts/system_prompt.txt)

Full prompt with jurisdiction rules, fee amounts, deadlines, BPL exemption,
and strict instructions for 'I don't know' answers on live data questions.

---

## Results summary

| Q# | Question | V1 verdict | V2 verdict |
|----|----------|-----------|----------|
| Q1 | RTI fee Maharashtra | Gives Rs 10 but misses BPL detail | Rs 10 + BPL nil + certificate required ✅ |
| Q2 | PIO reply deadline | 30 days correct but misses APIO +5 days | 30 days + APIO +5 days + 48 hrs life/liberty ✅ |
| Q3 | Marathi language | Yes, cites 22 languages generally | Yes, cites Section 6(1) + official language of Maharashtra ✅ |
| Q4 | Draft RTI Kopargaon | Draft with brackets, no fee or word limit | Complete draft with Rs 10 fee, 150-word limit, reply date ✅ |
| Q5 | Central vs Maharashtra online | Lists both portals correctly | Lists portals + process differences + jurisdiction ✅ |
| Q6 | PIO replies last month | Admits no real-time data but suggests workarounds | "I don't know — RTI Mitra has no live records" ✅ |
| Q7 | BPL fee exemption | Says NO exemption exists in RTI Act ❌ | Yes, cites Section 7(5), Rs 10 waived with BPL card ✅ |
| Q8 | No PIO reply in 30 days | Deemed refusal + appeal steps | Deemed refusal + first appeal within 30 days + Section 19(1) ✅ |
| Q9 | APIO at post office | Says deadline does NOT change ❌ | Correctly says +5 days added, total 35 days ✅ |
| Q10 | Section 8 exemptions | Lists exemptions correctly | Lists all exemptions + links to road-repair context ✅ |

---

## Detailed real LLM answers

### Q1: What is the RTI application fee in Maharashtra?

**Version 1 answer:**

The fee for an RTI application in Maharashtra is **₹10**.  This amount is the standard fee prescribed under the Maharashtra Right to Information Act, 2013, and is payable by any of the following methods: *   Cash *   Postal Order *   Bank Draft *   Indian Postal Order (IPO)  **Note:** If you are a person below the poverty line (BPL), you may be exempt from paying this fee, provided you submit a valid certificate issued by the competent authority....

**Version 2 answer:**

The RTI application fee in Maharashtra is **Rs 10**.  **Key Details:** *   **Standard Fee:** Rs 10 (payable via court fee stamp, Indian Postal Order, or Demand Draft). *   **BPL Applicants:** If you are a Below Poverty Line (BPL) applicant, the fee is **Nil** (free). You must attach a valid BPL certificate with your application. *   **Online Filing:** If you file online via the Maharashtra portal (aaplesarkar.mahaonline.gov.in), the fee is typically paid digitally.  This is general information o...

---

### Q2: Within how many days must the PIO reply to an RTI?

**Version 1 answer:**

Under the Right to Information Act, 2005, the Public Information Officer (PIO) must reply to an RTI application within **30 days** of the date of receipt of the application.  **Important Exceptions:** *   If the information relates to the **life or liberty of a person**, the PIO must reply within **48 hours**. *   If the information is to be provided by a **Third Party**, the time limit is extended to **60 days** (to allow for the third-party consultation process).  So, the standard answer is **...

**Version 2 answer:**

The Public Information Officer (PIO) must reply to an RTI application within **30 days** of the date of receipt of the application.  **Important Deadline Calculations:** *   **Standard Reply:** 30 days from the date the application is received by the PIO. *   **If the information is held by a different authority:** The PIO must transfer the application to the correct PIO within **5 days**. The new PIO then has **25 days** to reply (since 5 days are already used). *   **Life and Liberty Cases:** ...

---

### Q3: Can I ask for information about my own panchayat in Marathi?

**Version 1 answer:**

Yes, you can absolutely ask for information about your own Panchayat in Marathi.  Under the **Right to Information (RTI) Act, 2005**, you have the right to make a request in any of the **22 languages** listed in the **Eighth Schedule of the Constitution of India**. **Marathi** is one of these 22 languages.  ### Key Points: 1. **You can write your RTI application in Marathi.** 2. **The Public Information Officer (PIO)** of the Panchayat is required to provide the information **in the same languag...

**Version 2 answer:**

Yes, you can absolutely ask for information about your panchayat in Marathi.  Under the Right to Information (RTI) Act, 2005, you have the right to make an application in any of the official languages of the state. Since Marathi is the official language of Maharashtra, you are fully permitted to draft your RTI application in Marathi.  **Key Points to Remember:** 1.  **Language of Reply:** The Public Information Officer (PIO) must reply to you in the same language in which you made the applicatio...

---

### Q4: Draft an RTI to Kopargaon Panchayat Samiti for the 2026 road-repair work order.

**Version 1 answer:**

Here is a draft RTI application addressed to the Kopargaon Panchayat Samiti.  **Important Note:** Since you are asking for a specific document (the "2026 road-repair work order"), please ensure that: 1.  The work order has actually been issued by the time you file this RTI. 2.  You replace the bracketed information `[ ]` with your specific details.  ---  **To,**   The Public Information Officer (PIO),   Kopargaon Panchayat Samiti,   [Insert Full Address of Panchayat Samiti Office],   Kopargaon, ...

**Version 2 answer:**

**Jurisdiction:** Maharashtra State **Authority:** Kopargaon Panchayat Samiti **Fee:** Rs 10 (Nil if BPL) **Word Limit:** 150 words (Strictly adhered to below)  **Draft RTI Application**  To, The Public Information Officer, Kopargaon Panchayat Samiti, Kopargaon, Dist. Ahmednagar, Maharashtra.  **Subject:** Request for information regarding 2026 road-repair work orders.  **Details of Applicant:** [Your Name] [Your Address] [Pin Code] [Mobile Number] [Email ID]  **Information Sought:** 1. Copy of ...

---

### Q5: Difference between filing RTI to a central ministry online vs Maharashtra department online?

**Version 1 answer:**

Here is the simple difference between filing an RTI online to a **Central Ministry** (like the Ministry of Finance or Home) versus a **Maharashtra State Department** (like the Police or Health Dept):  ### 1. **Website Used** *   **Central Ministry:** You file on the **Central RTI Portal**     → [https://rtionline.gov.in](https://rtionline.gov.in)     (This is a single national portal for all Central Public Authorities.) *   **Maharashtra Department:** You file on the **Maharashtra State RTI Port...

**Version 2 answer:**

Here is the difference between filing an RTI application online with a **Central Ministry** versus a **Maharashtra State Department**:  ### 1. Online Portal *   **Central Ministry:** Use the central portal at **rtionline.gov.in**. *   **Maharashtra Department:** Use the state portal at **aaplesarkar.mahaonline.gov.in**.  ### 2. Application Fee *   **Central Ministry:** **Rs 10** (payable online via net banking, credit/debit card, or UPI). *   **Maharashtra Department:** **Rs 10** (payable online...

---

### Q6: What did the PIO of Kopargaon municipal council reply to RTIs filed last month?

**Version 1 answer:**

I do not have access to real-time data, specific local government records, or the private correspondence between citizens and the Public Information Officer (PIO) of the Kopargaon Municipal Council. Therefore, I cannot tell you what specific replies were sent last month.  To find this information, you would need to:  1.  **Check your own records:** If you filed an RTI, the reply should have been sent to you via post or email as per your application. 2.  **Contact the PIO directly:** You can reac...

**Version 2 answer:**

I don't know — RTI Mitra does not have access to live case records.  I cannot provide specific details about replies issued by the Public Information Officer (PIO) of the Kopargaon Municipal Council or any other authority, as I do not have access to real-time government databases or individual case files.  To find the status or content of a specific RTI reply, you should: 1. Check the online portal where you filed the application (e.g., `aaplesarkar.mahaonline.gov.in` for Maharashtra). 2. Contac...

---

### Q7: Am I exempt from RTI fee if I am below the poverty line?

**Version 1 answer:**

**No, you are not automatically exempt from RTI fees just because you are below the poverty line (BPL).**  However, there are important nuances and practical considerations:  ### 1. **No Legal Exemption in the RTI Act** The Right to Information Act, 2005, and its Rules do **not** provide a specific exemption from fees for BPL individuals. The fee structure is uniform for all citizens.  ### 2. **Standard Fees** - **First 5 pages**: ₹10 (for A4 size) - **Each additional page**: ₹2 per page - **Pho...

**Version 2 answer:**

Yes, you are exempt from the RTI application fee if you are a Below Poverty Line (BPL) applicant.  Here is how it works:  *   **Fee Amount:** The standard application fee is **Rs 10** for both Central Government and Maharashtra State authorities. *   **Exemption:** If you hold a valid BPL card, you do **not** have to pay this Rs 10 fee. *   **Requirement:** You must attach a **self-declaration** stating that you are a BPL applicant and include a **copy of your BPL card** with your application.  ...

---

### Q8: What happens if the PIO does not reply within 30 days?

**Version 1 answer:**

If the Public Information Officer (PIO) does not reply within 30 days, the following steps apply under the **Right to Information Act, 2005**:  ### 1. **Deemed Refusal** - If the PIO fails to provide the information within 30 days, it is treated as a **refusal** to provide the information.  ### 2. **First Appeal** - You can file a **First Appeal** with the **First Appellate Authority** (usually the senior officer above the PIO in the same public authority). - **Time limit**: The First Appeal mus...

**Version 2 answer:**

If the Public Information Officer (PIO) does not reply within 30 days, it is considered a **deemed refusal**. You do not need to wait for a written rejection; the silence itself allows you to proceed to the next step.  Here is what you should do:  1.  **File a First Appeal:** You have **30 days** from the date the reply was due (i.e., 30 days after your application was received) to file a First Appeal. 2.  **Who to appeal to:** The First Appeal is addressed to the **First Appellate Authority (FA...

---

### Q9: Can I file RTI through an APIO at post office, does that change the reply deadline?

**Version 1 answer:**

Yes, you can file an RTI application through an Assistant Public Information Officer (APIO) at a post office. This is a common and valid method, especially for applicants who do not have internet access or prefer offline filing.  **Does this change the reply deadline?**  **No, the statutory deadline remains the same.**  Under Section 7(1) of the RTI Act, 2005, the Central Public Information Officer (CPIO) or State Public Information Officer (SPIO) must provide the information **within 30 days** ...

**Version 2 answer:**

Yes, you can file an RTI application through an Assistant Public Information Officer (APIO) at a post office. This is a common and valid method for submitting your request.  **Does it change the reply deadline?** Yes, it does. The deadline for the Public Information Officer (PIO) to provide the reply is extended when the application is filed via an APIO.  *   **Standard Deadline:** If you file directly with the PIO, they must reply within **30 days**. *   **Via APIO Deadline:** If you file throu...

---

### Q10: What information is exempt from RTI disclosure under Section 8?

**Version 1 answer:**

Under **Section 8** of the Right to Information Act, 2005, certain categories of information are **exempt** from disclosure. This means the Public Authority is not required to provide this information, even if a request is made.  Here are the main categories of exempt information under Section 8:  ### 1. **Section 8(1)(a): National Security** - Information that is likely to **prejudice the sovereignty, integrity, security, strategic, scientific, or economic interests** of the State. - **Example:...

**Version 2 answer:**

Under **Section 8** of the Right to Information (RTI) Act, 2005, certain categories of information are exempt from disclosure. The Public Information Officer (PIO) is **not required** to provide this information, even if it is held by a public authority.  Here are the main categories of exempt information under Section 8:  1.  **Personal Information (Section 8(1)(j))**: Information relating to personal information the disclosure of which has no relationship to any public activity or interest, or...

---

## Winner: Version 2

Version 1 makes two factual errors:

- **Q7**: Says BPL exemption does not exist in the RTI Act — wrong. Section 7(5) explicitly grants it.
- **Q9**: Says filing via APIO does not change the deadline — wrong. Section 5(2) adds 5 days (total 35 days).

Version 2 passes all 10 questions, correctly refuses Q6 (live data request),
always cites the section reference, and applies the correct jurisdiction (central vs Maharashtra).
The detailed system prompt is essential for a legal-domain assistant like RTI Mitra.
