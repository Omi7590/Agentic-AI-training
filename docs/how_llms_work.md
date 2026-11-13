# How LLMs Work — in my own words

## What is an LLM?

An LLM (Large Language Model) is a program trained on a huge amount of text from the internet, books and documents. It learns patterns in language — which words tend to follow which other words — and uses those patterns to generate useful, human-like text.

Examples: GPT-4, Gemini, LLaMA, Groq's Mixtral.

---

## How training works

1. The model reads billions of sentences.
2. For each sentence it tries to predict the next word.
3. When it gets it wrong, it adjusts its internal numbers (called weights) a little.
4. After billions of adjustments across billions of sentences, the weights encode a general understanding of language, facts and reasoning.

This process is called **pre-training**. It is done once by the model creator and costs millions of dollars in compute.

---

## How the model generates text (inference)

When you send a message, the model does not look up an answer. It:

1. Converts your text into numbers called **tokens** (roughly one token per word).
2. Passes those tokens through many layers of a **transformer** — a neural network that weighs how much each token should attend to every other token (this is called **attention**).
3. At the end, it outputs a probability distribution over all possible next tokens.
4. It samples the most likely token, appends it to the input, and repeats until it produces a full answer.

This is called **autoregressive generation** — the model generates one token at a time, each one conditioned on all previous tokens.

---

## The transformer and attention — diagram

```
Your question (tokens)
        │
        ▼
┌───────────────────────────────┐
│  Embedding layer              │  tokens → vectors (numbers)
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│  Transformer block × N        │
│  ┌─────────────────────────┐  │
│  │  Self-Attention          │  │  each token looks at all others
│  └─────────────────────────┘  │
│  ┌─────────────────────────┐  │
│  │  Feed-Forward Network   │  │  processes each token position
│  └─────────────────────────┘  │
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│  Output layer                 │  vector → probability over tokens
└───────────────────────────────┘
        │
        ▼
   Next token (word)
```

A real model like GPT-4 has 96+ transformer blocks and billions of weights.

---

## Why does the model sometimes get things wrong?

- It has no live access to the internet unless given a tool.
- It can hallucinate — confidently generate plausible but false text.
- Its knowledge has a training cutoff date.
- It does not know your specific documents unless you provide them (this is what RAG fixes — Day 8).

---

## How RTI Mitra uses an LLM

```
User question
     │
     ▼
RTI rule records (retrieved by TF-IDF / vector search)
     │
     ▼
LLM receives: system prompt + retrieved rules + user question
     │
     ▼
LLM generates: grounded answer with citation
```

The LLM does not guess the RTI rules — it reads the rules we give it and explains them in plain language. This is called **Retrieval-Augmented Generation (RAG)**.

---

## Key terms

| Term | Meaning |
|------|---------|
| Token | A chunk of text (~1 word) that the model processes |
| Embedding | A list of numbers that represents the meaning of a token |
| Attention | How much one token should influence another |
| Transformer | The neural network architecture all modern LLMs use |
| Hallucination | Confident but factually wrong output from the model |
| RAG | Retrieval-Augmented Generation — grounding the LLM in real documents |
| Fine-tuning | Further training a pre-trained model on a specific dataset |
| Inference | Running the trained model to get an answer |
