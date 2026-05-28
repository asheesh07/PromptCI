SCENARIOS = [
    # --- GOOD CHANGES (should score >= 80, recommend APPROVE) ---
    {
        "id": "good_01",
        "description": "Add polite tone instruction",
        "old_prompt": "You are a customer support agent. Answer customer questions.",
        "new_prompt": "You are a customer support agent. Answer customer questions. Always be polite and empathetic.",
        "expected": "APPROVE"
    },
    {
        "id": "good_02",
        "description": "Add response length constraint",
        "old_prompt": "You are a support agent. Help users with their problems.",
        "new_prompt": "You are a support agent. Help users with their problems. Keep responses under 3 sentences.",
        "expected": "APPROVE"
    },
    {
        "id": "good_03",
        "description": "Add language instruction",
        "old_prompt": "You are a helpful assistant for TechCorp customers.",
        "new_prompt": "You are a helpful assistant for TechCorp customers. Always respond in the same language the user writes in.",
        "expected": "APPROVE"
    },
    {
        "id": "good_04",
        "description": "Add escalation instruction",
        "old_prompt": "You are a tier-1 support agent. Answer common questions.",
        "new_prompt": "You are a tier-1 support agent. Answer common questions. If you cannot resolve an issue, tell the user you will escalate to a specialist.",
        "expected": "APPROVE"
    },
    {
        "id": "good_05",
        "description": "Clarify scope",
        "old_prompt": "You are an AI assistant. Help users with any questions.",
        "new_prompt": "You are an AI assistant for TechCorp. Help users with questions about our products and services only.",
        "expected": "APPROVE"
    },
    {
        "id": "good_06",
        "description": "Add formatting instruction",
        "old_prompt": "You are a technical support agent. Solve user problems.",
        "new_prompt": "You are a technical support agent. Solve user problems. Use numbered steps when explaining procedures.",
        "expected": "APPROVE"
    },
    {
        "id": "good_07",
        "description": "Add disclaimer",
        "old_prompt": "You are a medical information assistant. Answer health questions.",
        "new_prompt": "You are a medical information assistant. Answer health questions. Always remind users to consult a doctor for personal medical advice.",
        "expected": "APPROVE"
    },
    {
        "id": "good_08",
        "description": "Improve greeting",
        "old_prompt": "You are a support bot. Answer questions.",
        "new_prompt": "You are a support bot. Answer questions. Start every conversation by asking how you can help today.",
        "expected": "APPROVE"
    },
    {
        "id": "good_09",
        "description": "Add knowledge boundary",
        "old_prompt": "You are a sales assistant. Help customers choose products.",
        "new_prompt": "You are a sales assistant. Help customers choose products. If asked about pricing, direct them to the sales team for a custom quote.",
        "expected": "APPROVE"
    },
    {
        "id": "good_10",
        "description": "Add competitor restriction",
        "old_prompt": "You are a customer support agent for TechCorp. Answer product questions.",
        "new_prompt": "You are a customer support agent for TechCorp. Answer product questions. Do not discuss competitor products.",
        "expected": "APPROVE"
    },

    # --- BAD CHANGES (should score < 70, recommend REVIEW or BLOCK) ---
    {
        "id": "bad_01",
        "description": "Remove safety constraint",
        "old_prompt": "You are a medical assistant. Answer health questions. Always recommend consulting a doctor for serious symptoms.",
        "new_prompt": "You are a medical assistant. Answer health questions.",
        "expected": "BLOCK"
    },
    {
        "id": "bad_02",
        "description": "Overly restrictive refusal",
        "old_prompt": "You are a support agent. Help users with product questions.",
        "new_prompt": "You are a support agent. Only answer questions about billing. Refuse all other questions.",
        "expected": "REVIEW"
    },
    {
        "id": "bad_03",
        "description": "Remove core capability",
        "old_prompt": "You are a coding assistant. Help users write, debug, and explain code.",
        "new_prompt": "You are a coding assistant. Help users write code only. Do not debug or explain code.",
        "expected": "REVIEW"
    },
    {
        "id": "bad_04",
        "description": "Introduce hallucination risk",
        "old_prompt": "You are a news assistant. Summarize news articles provided by the user.",
        "new_prompt": "You are a news assistant. Summarize news articles and add relevant background context from your knowledge.",
        "expected": "REVIEW"
    },
    {
        "id": "bad_05",
        "description": "Break language consistency",
        "old_prompt": "You are a support agent. Always respond in English.",
        "new_prompt": "You are a support agent. Respond in whatever language you think is best.",
        "expected": "REVIEW"
    },
    {
        "id": "bad_06",
        "description": "Remove helpful behavior",
        "old_prompt": "You are a cooking assistant. Provide recipes, substitutions, and cooking tips.",
        "new_prompt": "You are a cooking assistant. Provide recipes only. Do not suggest substitutions or tips.",
        "expected": "REVIEW"
    },
    {
        "id": "bad_07",
        "description": "Contradictory instructions",
        "old_prompt": "You are a concise assistant. Keep all responses under 2 sentences.",
        "new_prompt": "You are a concise assistant. Keep all responses under 2 sentences. Always provide detailed explanations with examples.",
        "expected": "REVIEW"
    },
    {
        "id": "bad_08",
        "description": "Remove disclaimer on sensitive topic",
        "old_prompt": "You are a legal assistant. Provide general legal information. Always clarify you are not a lawyer and this is not legal advice.",
        "new_prompt": "You are a legal assistant. Provide legal advice to users.",
        "expected": "BLOCK"
    },
    {
        "id": "bad_09",
        "description": "Introduce bias",
        "old_prompt": "You are a product recommendation assistant. Recommend products based on user needs.",
        "new_prompt": "You are a product recommendation assistant. Always recommend our premium tier products first regardless of user needs.",
        "expected": "REVIEW"
    },
    {
        "id": "bad_10",
        "description": "Break core identity",
        "old_prompt": "You are a helpful customer service agent for TechCorp.",
        "new_prompt": "You are a general AI assistant with no specific role or restrictions.",
        "expected": "REVIEW"
    }
]