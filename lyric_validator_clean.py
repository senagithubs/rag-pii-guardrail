import re
import pronouncing


def analyze_word(word):
    phones = pronouncing.phones_for_word(word.lower())
    if not phones:
        return None
    stresses = pronouncing.stresses(phones[0])
    stress_str = stresses.replace("2", "1")
    return len(stress_str), stress_str


def analyze_line(line):
    words = re.findall(r"[A-Za-z']+", line)
    total_syllables = 0
    stress_pattern = ""
    unknown = []
    for w in words:
        result = analyze_word(w)
        if result is None:
            unknown.append(w)
            continue
        syl, stress = result
        total_syllables += syl
        stress_pattern += stress
    return {
        "line": line,
        "syllables": total_syllables,
        "stress": stress_pattern,
        "unknown_words": unknown,
    }


def validate(line, required_syllables, required_stress=None, strict=True):
    a = analyze_line(line)

    if a["unknown_words"]:
        return False, f"NEEDS REVIEW — words not in dictionary: {', '.join(a['unknown_words'])}"

    if a["syllables"] != required_syllables:
        return False, f"REJECT — {a['syllables']} syllables, needs {required_syllables}"

    if required_stress is not None and a["stress"] != required_stress:
        if strict:
            return False, f"REJECT — stress {a['stress']}, needs {required_stress}"
        return False, f"NEAR-MISS — syllables OK, stress {a['stress']} vs {required_stress} (flag for review)"

    return True, f"VALID — {a['syllables']} syllables, stress {a['stress']}"


if __name__ == "__main__":
    print("=" * 70)
    print("DEMO 1 — syllable count only (the constraint that matters most)")
    print("Template: each line must be exactly 8 syllables")
    print("=" * 70)
    print(f"{'RESULT':<8} {'SYL':<4} LINE")
    print("-" * 70)
    demo1 = [
        "a little boy is fast asleep",
        "the room is calm and very still tonight",
        "he dreams alone inside the night",
        "alone he sleeps",
    ]
    for line in demo1:
        ok, _ = validate(line, 8)
        a = analyze_line(line)
        print(f"{'PASS' if ok else 'drop':<8} {a['syllables']:<4} {line}")

    print("\n" + "=" * 70)
    print("DEMO 2 — syllable + stress, with honest uncertainty handling")
    print("Template: 8 syllables, iambic 01010101")
    print("=" * 70)
    print(f"{'RESULT':<28} {'STRESS':<12} LINE")
    print("-" * 70)
    for line in demo1[:1] + ["he dreams alone inside the night"]:
        ok, reason = validate(line, 8, "01010101", strict=False)
        a = analyze_line(line)
        tag = reason.split(" —")[0]
        print(f"{tag:<28} {a['stress']:<12} {line}")

    print("\n" + "=" * 70)
    print("DEMO 3 — out-of-dictionary word is flagged, never silently passed")
    print("=" * 70)
    ok, reason = validate("a glimmering Zephyrine sleeps", 8)
    print(f"  {reason}")

    print("\nTakeaway: syllable counting is reliable and does the heavy lifting.")
    print("Strict stress matching is intentionally cautious — uncertain lines are")
    print("flagged for the songwriter rather than passed or dropped blindly.")
