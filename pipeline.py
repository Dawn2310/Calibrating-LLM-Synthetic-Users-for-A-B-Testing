"""
Experiment pipeline for cross-model A/B testing.
Handles GPT-4o, Claude 3.5 Sonnet, Llama 3.3 70B, DeepSeek-V4-Flash.
Features: async calls, rate limiting, exponential backoff, SQLite checkpoint.
"""
import asyncio
import aiohttp
import json
import sqlite3
import time
import os
import random

# ============ CONFIG ============
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data', 'experiment.db')
MAX_CONCURRENT = {
    'gpt-4o': 2,
    'claude-3.5-sonnet': 2,
    'llama-3.3-70b': 2,
    'deepseek-v4-flash': 2
}
MAX_RETRIES = 3
BACKOFF_BASE = 1.0  # seconds

# API keys — set as environment variables
# export OPENAI_API_KEY=sk-...
# export ANTHROPIC_API_KEY=sk-ant-...
# export TOGETHER_API_KEY=sk-...
# export DEEPSEEK_API_KEY=sk-...

# ============ PROMPT TEMPLATE ============

SYSTEM_PROMPT = """You are roleplaying as a specific person described below.
Stay fully in character. Respond based ONLY on how this person would genuinely react, not based on general knowledge.

Output your response strictly as JSON: {"choice": "A"} or {"choice": "B"}
Do not output any other text, explanation, or reasoning."""

def build_user_prompt(persona_desc: str, product_context: str,
                      variant_a: str, variant_b: str, metric: str,
                      ab_order: str = 'original') -> str:
    """Build user prompt with optional A/B swap for position bias control.
    Returns (prompt_text, actual_ab_order) where actual_ab_order resolves 'random' to either 'original' or 'swapped'.
    """
    actual_order = ab_order
    if ab_order == 'swapped':
        va, vb = variant_b, variant_a
    elif ab_order == 'random':
        # Truly randomize presentation order for run 3
        if random.random() < 0.5:
            va, vb = variant_b, variant_a
            actual_order = 'swapped'
        else:
            va, vb = variant_a, variant_b
            actual_order = 'original'
    else:
        va, vb = variant_a, variant_b

    prompt = f"""=== WHO YOU ARE ===
{persona_desc}

=== SCENARIO ===
You are browsing {product_context}.
You see two versions of the page:

Version A: {va}

Version B: {vb}

=== QUESTION ===
Based on your personality, habits, and preferences,
which version makes you more likely to {metric}?"""

    return prompt, actual_order


# ============ API CALLERS ============

async def call_gpt(session: aiohttp.ClientSession, system: str, user: str):
    """Call OpenAI GPT-4o with JSON mode."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 20
    }
    async with session.post(url, headers=headers, json=payload) as resp:
        data = await resp.json()
        if 'error' in data:
            raise Exception(str(data['error']))
        content = data['choices'][0]['message']['content']
        usage = data.get('usage', {})
        await asyncio.sleep(0.5) # Reduce load on OpenAI
        return content, usage.get('prompt_tokens', 0), usage.get('completion_tokens', 0)


async def call_claude(session: aiohttp.ClientSession, system: str, user: str):
    """Call Anthropic Claude 3.5 Sonnet."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": os.environ.get('ANTHROPIC_API_KEY', ''),
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-sonnet-4-6",  # Update to latest Sonnet 4.6 (2026)
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "temperature": 0.7,
        "max_tokens": 20
    }
    async with session.post(url, headers=headers, json=payload) as resp:
        data = await resp.json()
        if 'error' in data:
            raise Exception(str(data['error']))
        content = data['content'][0]['text']
        usage = data.get('usage', {})
        await asyncio.sleep(1.0) # Reduce load on Claude
        return content, usage.get('input_tokens', 0), usage.get('output_tokens', 0)


async def call_llama(session: aiohttp.ClientSession, system: str, user: str):
    """Call Llama 3.3 70B via Together AI API."""
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('TOGETHER_API_KEY', '')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 20
    }
    async with session.post(url, headers=headers, json=payload) as resp:
        data = await resp.json()
        if 'error' in data:
            raise Exception(str(data['error']))
        content = data['choices'][0]['message']['content']
        usage = data.get('usage', {})
        await asyncio.sleep(1.0) # Together AI is more relaxed than Groq, light delay
    return content, usage.get('prompt_tokens', 0), usage.get('completion_tokens', 0)


async def call_deepseek(session: aiohttp.ClientSession, system: str, user: str):
    """Call DeepSeek-V4-Flash API."""
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY', '')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }
    async with session.post(url, headers=headers, json=payload) as resp:
        data = await resp.json()
        if 'error' in data:
            raise Exception(str(data['error']))
        content = data['choices'][0]['message'].get('content', '')
        if not content.strip():
            raise Exception("DeepSeek returned empty content")
        usage = data.get('usage', {})
        await asyncio.sleep(1.0)
        return content, usage.get('prompt_tokens', 0), usage.get('completion_tokens', 0)


MODEL_CALLERS = {
    'gpt-4o': call_gpt,
    'claude-3.5-sonnet': call_claude,
    'llama-3.3-70b': call_llama,
    'deepseek-v4-flash': call_deepseek
}


# ============ PARSE RESPONSE ============

def parse_choice(raw_response: str, ab_order: str) -> str:
    """Parse JSON response and handle A/B swap decoding."""
    try:
        # Try JSON parse
        data = json.loads(raw_response.strip())
        choice = data.get('choice', '').strip().upper()

        if choice not in ('A', 'B'):
            return 'INVALID'

        # If we swapped A/B in the prompt, decode back
        if ab_order == 'swapped':
            choice = 'B' if choice == 'A' else 'A'

        return choice

    except (json.JSONDecodeError, AttributeError):
        # Try regex fallback for chatty models
        import re
        match = re.search(r'"choice"\s*:\s*"([AB])"', raw_response)
        if match:
            choice = match.group(1)
            if ab_order == 'swapped':
                choice = 'B' if choice == 'A' else 'A'
            return choice
        return 'INVALID'


# ============ CHECKPOINT ============
# Database schema is defined in init_db.py — import and reuse it.
from init_db import init_db as _init_db_full

def init_db(db_path: str):
    """Initialize SQLite database using the canonical schema from init_db.py."""
    _init_db_full()

def is_completed(db_path: str, test_id: str, persona_id: str,
                 model: str, run_number: int, ab_order: str) -> bool:
    """Check if this cell is already completed in SQLite."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT status FROM api_calls
        WHERE test_id=? AND persona_id=? AND model=? AND run_number=? AND ab_order=?
    ''', (test_id, persona_id, model, run_number, ab_order))
    row = c.fetchone()
    conn.close()
    return row is not None and row[0] == 'completed'


def save_result(db_path: str, test_id: str, persona_id: str, persona_type: str,
                model: str, run_number: int, ab_order: str,
                raw_response: str, parsed_choice: str, prompt_tokens: int, completion_tokens: int,
                response_time_ms: int, status: str, error_message: str = None):
    """Save result to SQLite checkpoint."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO api_calls
        (test_id, persona_id, persona_type, model, run_number, ab_order,
         raw_response, parsed_choice, prompt_tokens, completion_tokens, response_time_ms, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (test_id, persona_id, persona_type, model, run_number, ab_order,
          raw_response, parsed_choice, prompt_tokens, completion_tokens, response_time_ms, status, error_message))
    conn.commit()
    conn.close()


# ============ SINGLE CALL WITH RETRY ============

async def run_single_call(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                          model: str, test_case: dict, persona: dict,
                          run_number: int, ab_order: str):
    """Execute one API call with retry logic and checkpoint."""

    test_id = test_case['test_id']
    persona_id = persona['persona_id']
    persona_type = persona['persona_type']

    # Skip if already completed
    if is_completed(DB_PATH, test_id, persona_id, model, run_number, ab_order):
        return

    user_prompt, actual_order = build_user_prompt(
        persona_desc=persona['description'],
        product_context=test_case['product_context'],
        variant_a=test_case['variant_a'],
        variant_b=test_case['variant_b'],
        metric=test_case['metric'],
        ab_order=ab_order
    )

    caller = MODEL_CALLERS[model]

    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                start = time.time()
                raw, pt, ct = await caller(session, SYSTEM_PROMPT, user_prompt)
                elapsed_ms = int((time.time() - start) * 1000)

            parsed = parse_choice(raw, actual_order)
            save_result(DB_PATH, test_id, persona_id, persona_type,
                       model, run_number, actual_order, raw, parsed,
                       pt, ct, elapsed_ms, 'completed')
            return

        except Exception as e:
            wait = BACKOFF_BASE * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"  Retry {attempt+1}/{MAX_RETRIES} for {test_id}/{persona_id}/{model}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(wait)
            else:
                save_result(DB_PATH, test_id, persona_id, persona_type,
                           model, run_number, actual_order, str(e), 'INVALID',
                           0, 0, 0, 'failed', str(e))


# ============ POSITION BIAS ============

SYSTEM_PROMPT_PB = """You are evaluating an A/B test for a user interface.
Output your response strictly as JSON: {"choice": "A"} or {"choice": "B"}
Do not output any other text, explanation, or reasoning."""

def build_pb_prompt(product_context: str, variant_a: str, variant_b: str, metric: str, ab_order: str = 'original') -> str:
    actual_order = ab_order
    if ab_order == 'swapped':
        va, vb = variant_b, variant_a
    else:
        va, vb = variant_a, variant_b

    prompt = f"""=== SCENARIO ===
You are browsing {product_context}.
You see two versions of the page:

Version A: {va}

Version B: {vb}

=== QUESTION ===
Which version makes you more likely to {metric}?"""
    return prompt, actual_order

def is_pb_completed(db_path: str, test_id: str, model: str, run_number: int, ab_order: str) -> bool:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT raw_response FROM position_bias
        WHERE test_id=? AND model=? AND run_number=? AND ab_order=?
    ''', (test_id, model, run_number, ab_order))
    row = c.fetchone()
    conn.close()
    return row is not None and row[0] is not None and row[0] != ''

def save_pb_result(db_path: str, test_id: str, model: str, run_number: int, ab_order: str,
                raw_response: str, parsed_choice: str, prompt_tokens: int, completion_tokens: int):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Check if a row already exists
    c.execute('''
        SELECT id FROM position_bias
        WHERE test_id=? AND model=? AND run_number=? AND ab_order=?
    ''', (test_id, model, run_number, ab_order))
    row = c.fetchone()
    if row:
        # Update the existing row
        c.execute('''
            UPDATE position_bias
            SET raw_response=?, choice=?, prompt_tokens=?, completion_tokens=?
            WHERE id=?
        ''', (raw_response, parsed_choice, prompt_tokens, completion_tokens, row[0]))
    else:
        # Insert a new row
        c.execute('''
            INSERT INTO position_bias
            (test_id, model, run_number, ab_order, raw_response, choice, prompt_tokens, completion_tokens)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (test_id, model, run_number, ab_order, raw_response, parsed_choice, prompt_tokens, completion_tokens))
    conn.commit()
    conn.close()

async def run_pb_single_call(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                          model: str, test_case: dict, run_number: int, ab_order: str):
    test_id = test_case['test_id']

    if is_pb_completed(DB_PATH, test_id, model, run_number, ab_order):
        return

    user_prompt, actual_order = build_pb_prompt(
        product_context=test_case['product_context'],
        variant_a=test_case['variant_a'],
        variant_b=test_case['variant_b'],
        metric=test_case['metric'],
        ab_order=ab_order
    )

    caller = MODEL_CALLERS[model]

    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                raw, pt, ct = await caller(session, SYSTEM_PROMPT_PB, user_prompt)

            parsed = parse_choice(raw, actual_order)
            save_pb_result(DB_PATH, test_id, model, run_number, actual_order,
                       raw, parsed, pt, ct)
            return

        except Exception as e:
            wait = BACKOFF_BASE * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"  Retry {attempt+1}/{MAX_RETRIES} for PB {test_id}/{model}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(wait)
            else:
                save_pb_result(DB_PATH, test_id, model, run_number, actual_order,
                           str(e), 'INVALID', 0, 0)

async def run_pb_batch(test_cases: list, models: list, runs_per_order: int = 25):
    total = len(test_cases) * len(models) * runs_per_order * 2
    completed = 0
    semaphores = {m: asyncio.Semaphore(MAX_CONCURRENT[m]) for m in models}

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        tasks = []
        for tc in test_cases:
            for m in models:
                for run in range(1, runs_per_order + 1):
                    tasks.append(run_pb_single_call(session, semaphores[m], m, tc, run, 'original'))
                    tasks.append(run_pb_single_call(session, semaphores[m], m, tc, run, 'swapped'))

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            await coro
            completed += 1
            if completed % 100 == 0:
                print(f"PB Progress: {completed}/{total} ({100*completed/total:.1f}%)")

    print(f"Position Bias Batch complete: {completed}/{total}")


# ============ BATCH RUNNER ============

async def run_batch(test_cases: list, personas: list, models: list,
                    runs: list = [1, 2, 3]):
    """Run full experiment batch with progress tracking."""

    # Map run numbers to ab_order (cycling pattern for runs 4-9)
    run_orders = {
        1: 'original', 2: 'swapped', 3: 'random',
        4: 'original', 5: 'swapped', 6: 'random',
        7: 'original', 8: 'swapped', 9: 'random',
    }

    total = len(test_cases) * len(personas) * len(models) * len(runs)
    completed = 0

    semaphores = {m: asyncio.Semaphore(MAX_CONCURRENT[m]) for m in models}

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        tasks = []
        for tc in test_cases:
            for p in personas:
                for m in models:
                    for run in runs:
                        ab_order = run_orders.get(run, 'original')
                        task = run_single_call(
                            session, semaphores[m], m, tc, p, run, ab_order
                        )
                        tasks.append(task)

        # Run with progress
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            await coro
            completed += 1
            if completed % 100 == 0:
                print(f"Progress: {completed}/{total} ({100*completed/total:.1f}%)")

    print(f"Batch complete: {completed}/{total}")


# ============ ENTRY POINT ============

def main():
    """Load data and run experiment."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['pilot', 'position_bias', 'b3', 'b4', 'b5', 'full', 'exp4', 'exp5'],
                       required=True)
    parser.add_argument('--test-cases', default=os.path.join(BASE_DIR, 'ab_tests', 'corpus_candidates.json'))
    parser.add_argument('--personas', default=os.path.join(BASE_DIR, 'personas'))
    args = parser.parse_args()

    # Load test cases
    if args.phase == 'exp4':
        with open(os.path.join(os.path.dirname(args.test_cases), 'corpus_exp4.json')) as f:
            test_cases = json.load(f)
    else:
        with open(args.test_cases) as f:
            test_cases = json.load(f)
            
    if args.phase == 'exp5':
        selected_tests = ['UI-09', 'COPY-04', 'REC-06', 'UI-01', 'REC-03']
        test_cases = [tc for tc in test_cases if tc['test_id'] in selected_tests]

    # Load personas based on phase
    personas = []
    if args.phase in ('pilot', 'full', 'exp4', 'exp5'):
        for ptype in ('demographic', 'biographical', 'interview'):
            path = os.path.join(args.personas, f'{ptype}.json')
            if os.path.exists(path):
                with open(path) as f:
                    personas.extend(json.load(f))
    elif args.phase == 'b3':
        with open(os.path.join(args.personas, 'demographic.json')) as f:
            personas = json.load(f)
    elif args.phase == 'b4':
        with open(os.path.join(args.personas, 'biographical.json')) as f:
            personas = json.load(f)
    elif args.phase == 'b5':
        with open(os.path.join(args.personas, 'interview.json')) as f:
            personas = json.load(f)

    models = ['gpt-4o', 'claude-3.5-sonnet', 'llama-3.3-70b', 'deepseek-v4-flash']
    
    runs = [1, 2, 3]
    if args.phase == 'pilot':
        # Reduce heavily for quick testing of 3 models
        test_cases = test_cases[:1]
        personas = personas[:1]
        runs = [1]
    elif args.phase == 'exp5':
        runs = [4, 5, 6, 7, 8, 9]

    init_db(DB_PATH)

    if args.phase == 'position_bias':
        print(f"Phase: {args.phase}")
        print(f"Test cases: {len(test_cases)}")
        print(f"Models: {len(models)}")
        print(f"Total PB calls: {len(test_cases) * len(models) * 25 * 2}")
        asyncio.run(run_pb_batch(test_cases, models, 25))
        return

    print(f"Phase: {args.phase}")
    print(f"Test cases: {len(test_cases)}")
    print(f"Personas: {len(personas)}")
    print(f"Models: {len(models)}")
    print(f"Total calls: {len(test_cases) * len(personas) * len(models) * len(runs)}")

    asyncio.run(run_batch(test_cases, personas, models, runs))


if __name__ == '__main__':
    main()