import json
import os
import re
import urllib.error
import urllib.request


GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
LOOSE_TIME_PATTERN = re.compile(
    r"\b(?P<hour>\d{1,2})(?::(?P<minute>[0-5]\d))?\s*(?P<period>a\.?m\.?|p\.?m\.?)?\b",
    re.IGNORECASE,
)
TIME_RANGE_PATTERN = re.compile(
    r"(?P<start>\d{1,2}(?::[0-5]\d)?\s*(?:a\.?m\.?|p\.?m\.?)?)"
    r"\s*(?:-|to|until|till)\s*"
    r"(?P<end>\d{1,2}(?::[0-5]\d)?\s*(?:a\.?m\.?|p\.?m\.?)?)",
    re.IGNORECASE,
)
PRIORITIES = {"low", "medium", "high"}
GOAL_LABELS = {
    "fitness": "Fitness and fat loss",
    "study": "Study and exam preparation",
    "skill": "Skill learning",
    "routine": "Daily discipline",
}
FIXED_HINT_WORDS = {
    "class",
    "college",
    "school",
    "office",
    "work",
    "job",
    "meeting",
    "coaching",
    "tuition",
    "exam",
    "travel",
    "commute",
}


class BrainError(Exception):
    pass


class BrainInputError(BrainError):
    pass


class BrainProviderError(BrainError):
    pass


def _clock_minutes(value):
    if not isinstance(value, str) or not TIME_PATTERN.fullmatch(value):
        raise BrainInputError("Use a valid wake and sleep time.")
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


def _day_window(wake, sleep):
    wake_minutes = _clock_minutes(wake)
    sleep_minutes = _clock_minutes(sleep)
    if sleep_minutes <= wake_minutes:
        sleep_minutes += 24 * 60
    if sleep_minutes - wake_minutes < 4 * 60:
        raise BrainInputError("Your day needs at least four waking hours.")
    return wake_minutes, sleep_minutes


def _format_time(minutes):
    minutes %= 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _relative_minutes(value, wake_minutes):
    minutes = _clock_minutes(value)
    if minutes < wake_minutes:
        minutes += 24 * 60
    return minutes


def _parse_loose_time(value):
    match = LOOSE_TIME_PATTERN.fullmatch(str(value).strip())
    if not match:
        raise BrainInputError("Use time like 09:00, 14:30, or 6pm.")

    hour = int(match.group("hour"))
    minute = int(match.group("minute") or "0")
    period = (match.group("period") or "").lower().replace(".", "")
    if period:
        if not 1 <= hour <= 12:
            raise BrainInputError("Use a valid 12-hour time.")
        if period == "pm" and hour != 12:
            hour += 12
        if period == "am" and hour == 12:
            hour = 0
    elif not 0 <= hour <= 23:
        raise BrainInputError("Use a valid 24-hour time.")

    return f"{hour:02d}:{minute:02d}"


def _block(name, start_minutes, end_minutes, priority="medium", kind="focus"):
    return {
        "name": name,
        "start": _format_time(start_minutes),
        "end": _format_time(end_minutes),
        "priority": priority,
        "kind": kind,
        "_start": start_minutes,
        "_end": end_minutes,
    }


def _overlaps(start, end, existing):
    return any(start < item["_end"] and end > item["_start"] for item in existing)


def _find_slot(existing, wake_minutes, sleep_minutes, duration, preferred):
    preferred = max(wake_minutes, min(preferred, sleep_minutes - duration))
    step = 15
    max_offset = max(preferred - wake_minutes, sleep_minutes - preferred)

    for offset in range(0, max_offset + step, step):
        candidates = []
        if offset == 0:
            candidates.append(preferred)
        else:
            candidates.extend((preferred - offset, preferred + offset))
        for start in candidates:
            end = start + duration
            if start >= wake_minutes and end <= sleep_minutes and not _overlaps(start, end, existing):
                return start
    return None


def _add_smart_block(existing, wake_minutes, sleep_minutes, name, duration, preferred, priority, kind):
    start = _find_slot(existing, wake_minutes, sleep_minutes, duration, preferred)
    if start is None:
        return False
    existing.append(_block(name, start, start + duration, priority, kind))
    existing.sort(key=lambda item: item["_start"])
    return True


def _clean_constraint_name(text):
    cleaned = TIME_RANGE_PATTERN.sub("", text).strip(" ,.;:-")
    return cleaned[:50].strip() or "Fixed commitment"


def _parse_fixed_blocks(constraints, wake_minutes):
    text = str(constraints or "")
    blocks = []
    for line in [part.strip() for part in re.split(r"[\n;]+", text) if part.strip()]:
        match = TIME_RANGE_PATTERN.search(line)
        if not match:
            continue
        start = _relative_minutes(_parse_loose_time(match.group("start")), wake_minutes)
        end = _relative_minutes(_parse_loose_time(match.group("end")), wake_minutes)
        if end <= start:
            end += 24 * 60
        if end - start < 10:
            continue
        blocks.append(_block(_clean_constraint_name(line), start, end, "high", "fixed"))
    return blocks


def clarify_schedule_inputs(wake, sleep, constraints="", routine=None):
    _day_window(wake, sleep)
    routine = routine or {}
    questions = []
    constraints_text = str(constraints or "").strip()
    lowered = constraints_text.lower()
    has_hint_word = any(word in lowered for word in FIXED_HINT_WORDS)
    has_time_range = bool(TIME_RANGE_PATTERN.search(constraints_text))

    if constraints_text and has_hint_word and not has_time_range:
        questions.append(
            "For your fixed commitment, tell me the exact start and end time. "
            "Example: College 09:00-15:00."
        )

    if constraints_text and ("between" in lowered or "in between" in lowered) and not has_time_range:
        questions.append(
            "When you say in between, what exact time range should DayFlow protect?"
        )

    if routine.get("includeBasics") is False:
        questions.append(
            "Should I still include basic needs like meals, hygiene, movement, and wind down?"
        )

    return questions


def _routine_time(routine, key, fallback):
    value = str((routine or {}).get(key, "")).strip()
    if not value:
        return fallback
    return _clock_minutes(value)


def _routine_blocks(wake, sleep, constraints, routine=None):
    routine = routine or {}
    wake_minutes, sleep_minutes = _day_window(wake, sleep)
    blocks = _parse_fixed_blocks(constraints, wake_minutes)
    for fixed in blocks:
        if fixed["_start"] < wake_minutes or fixed["_end"] > sleep_minutes:
            raise BrainInputError("Fixed commitments must fit between wake and sleep time.")
    blocks.sort(key=lambda item: item["_start"])

    if routine.get("includeBasics") is False:
        return blocks

    day_length = sleep_minutes - wake_minutes
    breakfast_time = _routine_time(routine, "breakfast", wake_minutes + 60)
    lunch_time = _routine_time(routine, "lunch", wake_minutes + min(5 * 60, max(3 * 60, day_length // 2)))
    dinner_time = _routine_time(routine, "dinner", sleep_minutes - 3 * 60)
    movement_time = _routine_time(routine, "movement", wake_minutes + 2 * 60)

    placements = [
        ("Wake, hygiene, water", 30, wake_minutes, "medium", "routine"),
        ("Breakfast", 25, breakfast_time, "medium", "routine"),
        ("Movement or walk", 30, movement_time, "low", "routine"),
        ("Lunch and reset", 35, lunch_time, "medium", "routine"),
        ("Dinner", 35, dinner_time, "medium", "routine"),
        ("Wind down and sleep prep", 40, sleep_minutes - 40, "medium", "routine"),
    ]

    for name, duration, preferred, priority, kind in placements:
        _add_smart_block(blocks, wake_minutes, sleep_minutes, name, duration, preferred, priority, kind)

    return blocks


def validate_schedule(raw_schedule, wake, sleep, min_tasks=3, max_tasks=18):
    wake_minutes, sleep_minutes = _day_window(wake, sleep)
    tasks = raw_schedule.get("tasks") if isinstance(raw_schedule, dict) else None
    if not isinstance(tasks, list) or not min_tasks <= len(tasks) <= max_tasks:
        raise BrainProviderError("The brain returned an incomplete schedule.")

    validated = []
    for task in tasks:
        if not isinstance(task, dict):
            raise BrainProviderError("The brain returned an invalid task.")
        name = str(task.get("name", "")).strip()
        start = str(task.get("start", "")).strip()
        end = str(task.get("end", "")).strip()
        priority = str(task.get("priority", "medium")).strip().lower()
        kind = str(task.get("kind", "focus")).strip().lower()
        if not 2 <= len(name) <= 80:
            raise BrainProviderError("The brain returned an invalid task name.")
        if priority not in PRIORITIES:
            priority = "medium"
        if kind not in {"focus", "routine", "fixed", "break", "review"}:
            kind = "focus"

        start_minutes = _relative_minutes(start, wake_minutes)
        end_minutes = _relative_minutes(end, wake_minutes)
        if end_minutes <= start_minutes:
            end_minutes += 24 * 60
        if start_minutes < wake_minutes or end_minutes > sleep_minutes:
            raise BrainProviderError("The brain scheduled a task outside your waking hours.")

        validated.append({
            "name": name,
            "start": _format_time(start_minutes),
            "end": _format_time(end_minutes),
            "priority": priority,
            "kind": kind,
            "_start": start_minutes,
            "_end": end_minutes,
        })

    validated.sort(key=lambda task: task["_start"])
    for previous, current in zip(validated, validated[1:]):
        if current["_start"] < previous["_end"]:
            raise BrainProviderError("The brain returned overlapping tasks.")

    return [
        {key: value for key, value in task.items() if not key.startswith("_")}
        for task in validated
    ]


def _fallback_schedule(goal_type, wake, sleep, constraints, routine):
    wake_minutes, sleep_minutes = _day_window(wake, sleep)
    blocks = _routine_blocks(wake, sleep, constraints, routine)
    focus_label = GOAL_LABELS.get(goal_type, "Focused progress")
    available = sleep_minutes - wake_minutes
    focus_one = 90 if available >= 8 * 60 else 60
    focus_two = 60 if available >= 7 * 60 else 45

    _add_smart_block(
        blocks,
        wake_minutes,
        sleep_minutes,
        f"{focus_label}: deep work",
        focus_one,
        wake_minutes + 90,
        "high",
        "focus",
    )
    _add_smart_block(
        blocks,
        wake_minutes,
        sleep_minutes,
        f"{focus_label}: practice or revision",
        focus_two,
        wake_minutes + max(4 * 60, available // 2),
        "high",
        "focus",
    )
    _add_smart_block(
        blocks,
        wake_minutes,
        sleep_minutes,
        "Review progress and plan tomorrow",
        25,
        sleep_minutes - 90,
        "medium",
        "review",
    )

    if len(blocks) < 3:
        raise BrainInputError("There is not enough open time to build a useful day.")

    blocks.sort(key=lambda item: item["_start"])
    return validate_schedule({"tasks": blocks}, wake, sleep)


def _extract_provider_message(error):
    try:
        payload = json.loads(error.read().decode("utf-8"))
        return payload.get("error", {}).get("message") or "Groq rejected the request."
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return f"Groq returned HTTP {error.code}."


def _provider_chat(api_key, messages, max_tokens=900, temperature=0.35):
    model = os.environ.get("GROQ_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    request_payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    provider_request = urllib.request.Request(
        GROQ_CHAT_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(provider_request, timeout=20) as response:
            provider_data = json.loads(response.read().decode("utf-8"))
        return provider_data["choices"][0]["message"]["content"], model
    except urllib.error.HTTPError as error:
        raise BrainProviderError(_extract_provider_message(error)) from error
    except urllib.error.URLError as error:
        raise BrainProviderError(f"Could not reach Groq: {error.reason}") from error
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise BrainProviderError("Groq returned an unreadable response.") from error


def _groq_schedule(api_key, goal, wake, sleep, constraints, routine):
    required_blocks = _routine_blocks(wake, sleep, constraints, routine)
    goal_label = GOAL_LABELS.get(goal["goal_type"], "Focused daily progress")
    prompt = {
        "goal": goal_label,
        "goal_duration_days": goal["duration"],
        "wake_time": wake,
        "sleep_time": sleep,
        "fixed_and_basic_routine_blocks": [
            {key: block[key] for key in ("name", "start", "end", "priority", "kind")}
            for block in required_blocks
        ],
        "extra_notes": constraints or "No additional notes.",
    }
    request_payload = {
        "model": os.environ.get("GROQ_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
        "temperature": 0.25,
        "max_tokens": 1600,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are DayFlow's scheduling brain. Create one realistic daily schedule. "
                    "Return JSON only as {\"tasks\":[{\"name\":\"...\",\"start\":\"HH:MM\","
                    "\"end\":\"HH:MM\",\"priority\":\"low|medium|high\",\"kind\":\"routine|fixed|focus|break|review\"}]}. "
                    "You must include all fixed_and_basic_routine_blocks exactly or nearly exactly. "
                    "Then place goal-focused work only in the remaining open time. Avoid overlaps."
                ),
            },
            {
                "role": "user",
                "content": "Create a practical schedule from this JSON:\n" + json.dumps(prompt),
            },
        ],
    }
    provider_request = urllib.request.Request(
        GROQ_CHAT_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(provider_request, timeout=20) as response:
            provider_data = json.loads(response.read().decode("utf-8"))
        content = provider_data["choices"][0]["message"]["content"]
        schedule = json.loads(content)
    except urllib.error.HTTPError as error:
        raise BrainProviderError(_extract_provider_message(error)) from error
    except urllib.error.URLError as error:
        raise BrainProviderError(f"Could not reach Groq: {error.reason}") from error
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise BrainProviderError("Groq returned an unreadable schedule.") from error

    tasks = validate_schedule(schedule, wake, sleep)
    if len([task for task in tasks if task.get("kind") == "routine"]) < min(3, len(required_blocks)):
        raise BrainProviderError("The brain skipped too much of the basic daily routine.")
    return tasks, request_payload["model"]


def generate_schedule(goal, wake, sleep, constraints="", routine=None):
    questions = clarify_schedule_inputs(wake, sleep, constraints, routine)
    if questions:
        return {
            "status": "needs_clarification",
            "questions": questions,
            "tasks": [],
            "engine": "DayFlow clarifier",
            "ai": False,
        }

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return {
            "status": "ok",
            "tasks": _fallback_schedule(goal["goal_type"], wake, sleep, constraints, routine or {}),
            "engine": "DayFlow routine planner",
            "ai": False,
        }

    tasks, model = _groq_schedule(api_key, goal, wake, sleep, constraints[:700], routine or {})
    return {"status": "ok", "tasks": tasks, "engine": f"Groq / {model}", "ai": True}


def chat_reply(message, context=None):
    message = str(message or "").strip()
    if not 1 <= len(message) <= 1000:
        raise BrainInputError("Ask something short so DayFlow can reply clearly.")

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    context = context or {}
    if not api_key:
        return {
            "reply": (
                "I can help you plan your day, but Groq is not connected yet. "
                "Try asking about your next task, reminders, or how to break a goal into steps."
            ),
            "engine": "DayFlow local chat",
            "ai": False,
        }

    context_text = json.dumps(context, ensure_ascii=True)[:2000]
    content, model = _provider_chat(
        api_key,
        [
            {
                "role": "system",
                "content": (
                    "You are DayFlow's friendly productivity chat assistant. "
                    "Answer briefly, helpfully, and practically. Use the user's current goal "
                    "and tasks if provided. Do not invent private facts."
                ),
            },
            {"role": "user", "content": f"Context JSON: {context_text}\n\nUser: {message}"},
        ],
        max_tokens=500,
        temperature=0.45,
    )
    return {"reply": content.strip(), "engine": f"Groq / {model}", "ai": True}
